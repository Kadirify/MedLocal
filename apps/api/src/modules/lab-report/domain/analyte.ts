import { ReferenceRange } from './reference-range.js';

export type Sex = 'male' | 'female';

export interface CriticalLimits {
  readonly low: number | null;
  readonly high: number | null;
}

export class Analyte {
  constructor(
    readonly key: string,
    readonly name: string,
    readonly unit: string,
    readonly decimals: number,
    private readonly ranges: Readonly<Partial<Record<Sex | 'any', ReferenceRange>>>,
    readonly critical: CriticalLimits,
  ) {}

  rangeFor(sex: Sex): ReferenceRange {
    const range = this.ranges.any ?? this.ranges[sex];
    if (!range) throw new Error(`${this.key} has no reference range for ${sex}`);
    return range;
  }

  isCritical(value: number): boolean {
    const { low, high } = this.critical;
    return (low !== null && value <= low) || (high !== null && value >= high);
  }
}
