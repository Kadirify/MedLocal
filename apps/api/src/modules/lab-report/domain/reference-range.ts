export type Flag = 'LOW' | 'NORMAL' | 'HIGH';

// laboratories disagree on limits by tens of percent, never by a factor of three
const MAX_SCALE_RATIO = 3;

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

  /**
   * False when the two ranges differ by more than a unit conversion could hide, for example
   * hemoglobin printed in g/L (129-167) against a catalog kept in g/dL (13.2-16.6).
   */
  isOnTheScaleOf(other: ReferenceRange): boolean {
    const ratio = this.representative() / other.representative();
    return ratio > 1 / MAX_SCALE_RATIO && ratio < MAX_SCALE_RATIO;
  }

  private representative(): number {
    return this.high ?? this.low ?? Number.NaN;
  }

  describe(decimals: number): string {
    if (this.low === null) return `up to ${this.high?.toFixed(decimals)}`;
    if (this.high === null) return `${this.low.toFixed(decimals)} or higher`;
    return `${this.low.toFixed(decimals)} to ${this.high.toFixed(decimals)}`;
  }
}
