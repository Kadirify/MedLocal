import { Analyte, Sex } from './analyte.js';
import { Flag, ReferenceRange } from './reference-range.js';

/** Whether the range came from the report itself or from our catalog of typical adult values. */
export type ReferenceSource = 'report' | 'catalog';

export class LabResult {
  constructor(
    readonly analyte: Analyte,
    readonly value: number,
    readonly reference: ReferenceRange,
    readonly printedUnit: string | null = null,
    readonly referenceSource: ReferenceSource = 'catalog',
  ) {}

  get flag(): Flag {
    return this.reference.flag(this.value);
  }

  get isCritical(): boolean {
    return this.analyte.isCritical(this.value);
  }
}

export class LabReport {
  constructor(
    readonly sex: Sex,
    readonly age: number,
    readonly results: readonly LabResult[],
  ) {}

  get criticalResults(): readonly LabResult[] {
    return this.results.filter((result) => result.isCritical);
  }
}
