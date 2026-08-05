export type Flag = 'LOW' | 'NORMAL' | 'HIGH';

export class InvalidReferenceRangeError extends Error {}

export class ReferenceRange {
  constructor(
    readonly low: number | null,
    readonly high: number | null,
  ) {
    if (low === null && high === null) {
      throw new InvalidReferenceRangeError('a reference range needs at least one bound');
    }
    if (low !== null && high !== null && low >= high) {
      throw new InvalidReferenceRangeError(`low ${low} is not below high ${high}`);
    }
  }

  flag(value: number): Flag {
    if (this.low !== null && value < this.low) return 'LOW';
    if (this.high !== null && value > this.high) return 'HIGH';
    return 'NORMAL';
  }

  describe(decimals: number): string {
    if (this.low === null) return `up to ${this.high?.toFixed(decimals)}`;
    if (this.high === null) return `${this.low.toFixed(decimals)} or higher`;
    return `${this.low.toFixed(decimals)} to ${this.high.toFixed(decimals)}`;
  }
}
