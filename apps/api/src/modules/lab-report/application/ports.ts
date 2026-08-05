import { Analyte } from '../domain/analyte.js';
import { ReferenceRange } from '../domain/reference-range.js';

export abstract class AnalyteCatalog {
  abstract findByKey(key: string): Analyte | undefined;
  abstract findByLabel(label: string): Analyte | undefined;
}

export interface ParsedRow {
  readonly label: string;
  readonly value: number;
  readonly printedRange: ReferenceRange | null;
}

export class UnreadableLabReportError extends Error {}

export abstract class LabReportParser {
  /** Rejects with UnreadableLabReportError when the file holds no result rows. */
  abstract parse(file: Uint8Array): Promise<readonly ParsedRow[]>;
}
