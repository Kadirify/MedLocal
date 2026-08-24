import { Injectable } from '@nestjs/common';
import { Sex } from '../domain/analyte.js';
import { LabReport, LabResult } from '../domain/lab-report.js';
import { AnalyteCatalog, LabReportParser } from './ports.js';

export interface ReadLabReportResult {
  readonly report: LabReport;
  readonly unrecognizedLabels: readonly string[];
  readonly differentUnitLabels: readonly string[];
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
    const differentUnitLabels: string[] = [];

    for (const row of rows) {
      const analyte = this.catalog.findByLabel(row.label);
      if (!analyte) {
        // a line without a range that names nothing we know is page furniture, not a result
        if (row.printedRange) unrecognizedLabels.push(row.label);
        continue;
      }

      const catalogRange = analyte.rangeFor(sex);
      if (row.printedRange && !row.printedRange.isOnTheScaleOf(catalogRange)) {
        differentUnitLabels.push(row.label);
        continue;
      }
      // the laboratory that ran the test knows its own method; its printed interval wins
      results.push(
        row.printedRange
          ? new LabResult(analyte, row.value, row.printedRange, row.unit, 'report')
          : new LabResult(analyte, row.value, catalogRange, row.unit, 'catalog'),
      );
    }

    return { report: new LabReport(sex, age, results), unrecognizedLabels, differentUnitLabels };
  }
}
