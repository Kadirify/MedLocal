import { Injectable } from '@nestjs/common';
import { Sex } from '../domain/analyte.js';
import { LabReport, LabResult } from '../domain/lab-report.js';
import { AnalyteCatalog, LabReportParser } from './ports.js';

export interface ReadLabReportResult {
  readonly report: LabReport;
  readonly unrecognizedLabels: readonly string[];
}

@Injectable()
export class ReadLabReport {
  constructor(
    private readonly parser: LabReportParser,
    private readonly catalog: AnalyteCatalog,
  ) {}

  async execute(file: Uint8Array, sex: Sex, age: number): Promise<ReadLabReportResult> {
    const rows = await this.parser.parse(file);
    const results: LabResult[] = [];
    const unrecognizedLabels: string[] = [];

    for (const row of rows) {
      const analyte = this.catalog.findByLabel(row.label);
      if (!analyte) {
        unrecognizedLabels.push(row.label);
        continue;
      }
      // the laboratory that ran the test knows its own method; its printed interval wins
      results.push(new LabResult(analyte, row.value, row.printedRange ?? analyte.rangeFor(sex)));
    }

    return { report: new LabReport(sex, age, results), unrecognizedLabels };
  }
}
