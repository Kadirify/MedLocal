import { describe, expect, it } from 'vitest';
import { InvalidReferenceRangeError, ReferenceRange } from './reference-range.js';

describe('ReferenceRange', () => {
  const potassium = new ReferenceRange(3.6, 5.2);

  it.each([
    [3.5, 'LOW'],
    [3.6, 'NORMAL'],
    [4.4, 'NORMAL'],
    [5.2, 'NORMAL'],
    [5.3, 'HIGH'],
  ] as const)('flags %s as %s, treating the bounds themselves as normal', (value, flag) => {
    expect(potassium.flag(value)).toBe(flag);
  });

  it('never flags low without a low bound', () => {
    expect(new ReferenceRange(null, 99).flag(0)).toBe('NORMAL');
  });

  it('never flags high without a high bound', () => {
    expect(new ReferenceRange(40, null).flag(500)).toBe('NORMAL');
  });

  it('rejects a range without bounds', () => {
    expect(() => new ReferenceRange(null, null)).toThrow(InvalidReferenceRangeError);
  });

  it('rejects bounds that are not ordered', () => {
    expect(() => new ReferenceRange(5, 5)).toThrow(InvalidReferenceRangeError);
  });

  it.each([
    [new ReferenceRange(11.6, 15), 1, '11.6 to 15.0'],
    [new ReferenceRange(null, 99), 0, 'up to 99'],
    [new ReferenceRange(50, null), 0, '50 or higher'],
  ])('describes itself the way the training prompts do', (range, decimals, text) => {
    expect(range.describe(decimals)).toBe(text);
  });
});
