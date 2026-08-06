import { getDocument } from 'pdfjs-dist/legacy/build/pdf.mjs';
import { LabReportParser, ParsedRow, UnreadableLabReportError } from '../application/ports.js';
import { parseResultLine } from './result-line.js';

interface PositionedText {
  readonly text: string;
  readonly x: number;
  readonly y: number;
}

// text items of one printed row share a baseline to within a couple of points
const SAME_LINE_TOLERANCE = 2;

/** Reads PDFs that carry a text layer. Scanned reports need OCR and are rejected as unreadable. */
export class PdfTextLabReportParser extends LabReportParser {
  async parse(file: Uint8Array): Promise<readonly ParsedRow[]> {
    const lines = await this.readLines(file);
    const rows = lines.map(parseResultLine).filter((row) => row !== null);

    if (rows.length === 0) {
      throw new UnreadableLabReportError('no result rows were found in the PDF');
    }
    return rows;
  }

  private async readLines(file: Uint8Array): Promise<string[]> {
    const loading = getDocument({ data: new Uint8Array(file), useSystemFonts: true });
    try {
      const document = await loading.promise.catch((error: unknown) => {
        throw new UnreadableLabReportError(`the file is not a readable PDF: ${String(error)}`);
      });

      const lines: string[] = [];
      for (let number = 1; number <= document.numPages; number++) {
        const page = await document.getPage(number);
        const content = await page.getTextContent();
        const items = content.items.flatMap((item): PositionedText[] =>
          'str' in item && item.str.trim()
            ? [{ text: item.str, x: item.transform[4] as number, y: item.transform[5] as number }]
            : [],
        );
        lines.push(...groupIntoLines(items));
      }
      return lines;
    } finally {
      await loading.destroy();
    }
  }
}

function groupIntoLines(items: readonly PositionedText[]): string[] {
  const rows: PositionedText[][] = [];
  for (const item of [...items].sort((a, b) => b.y - a.y)) {
    const row = rows.at(-1);
    if (row?.[0] && Math.abs(row[0].y - item.y) <= SAME_LINE_TOLERANCE) {
      row.push(item);
    } else {
      rows.push([item]);
    }
  }
  return rows.map((row) =>
    [...row]
      .sort((a, b) => a.x - b.x)
      .map((item) => item.text.trim())
      .join(' '),
  );
}
