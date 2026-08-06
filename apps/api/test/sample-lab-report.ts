import PDFDocument from 'pdfkit';

export type SampleRow = readonly [label: string, value: string, unit: string, reference: string];

const COLUMNS = [50, 250, 330, 420] as const;

/** A text-layer PDF laid out like a typical printed lab report: one result per row, in columns. */
export function renderLabReportPdf(rows: readonly SampleRow[]): Promise<Uint8Array> {
  return new Promise((resolve, reject) => {
    const document = new PDFDocument({ size: 'A4', margin: 50 });
    const chunks: Buffer[] = [];
    document.on('data', (chunk: Buffer) => chunks.push(chunk));
    document.on('end', () => {
      resolve(new Uint8Array(Buffer.concat(chunks)));
    });
    document.on('error', reject);

    document.fontSize(14).text('Example Laboratory', 50, 50);
    document.fontSize(10).text('Patient: SYNTHETIC SAMPLE   Collected: 2026-09-19 08:30', 50, 75);

    let y = 110;
    drawRow(document, ['Test', 'Result', 'Unit', 'Reference'], y);
    for (const row of rows) {
      y += 22;
      drawRow(document, row, y);
    }
    document.end();
  });
}

function drawRow(document: PDFKit.PDFDocument, cells: readonly string[], y: number): void {
  cells.forEach((cell, index) => {
    document.text(cell, COLUMNS[index] ?? 50, y, { lineBreak: false });
  });
}
