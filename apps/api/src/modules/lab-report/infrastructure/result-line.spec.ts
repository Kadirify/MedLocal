import { describe, expect, it } from 'vitest';
import { parseResultLine } from './result-line.js';

describe('parseResultLine', () => {
  it('reads label, value and a two-sided range', () => {
    const row = parseResultLine('Hemoglobin 10.8 g/dL 11.6 - 15.0');

    expect(row).toMatchObject({ label: 'Hemoglobin', value: 10.8 });
    expect(row?.printedRange).toMatchObject({ low: 11.6, high: 15 });
  });

  it('keeps digits that belong to the label', () => {
    expect(parseResultLine('Vitamin B12 478 pg/mL 180 - 914')).toMatchObject({
      label: 'Vitamin B12',
      value: 478,
    });
    expect(parseResultLine('25-OH Vitamin D 14 ng/mL 20 - 50')).toMatchObject({
      label: '25-OH Vitamin D',
      value: 14,
    });
  });

  it('reads one-sided ranges', () => {
    expect(parseResultLine('LDL Kolesterol 131 mg/dL < 100')?.printedRange).toMatchObject({
      low: null,
      high: 100,
    });
    expect(parseResultLine('HDL Kolesterol 62 mg/dL > 50')?.printedRange).toMatchObject({
      low: 50,
      high: null,
    });
  });

  it('accepts decimal commas, abnormal markers and units that start with a digit', () => {
    const row = parseResultLine('WBC 12,7 H 10^3/µL 3,4 - 9,6');

    expect(row).toMatchObject({ label: 'WBC', value: 12.7 });
    expect(row?.printedRange).toMatchObject({ low: 3.4, high: 9.6 });
  });

  it('reads a line without a unit', () => {
    expect(parseResultLine('TSH 2.10 0.30 - 4.20')).toMatchObject({ label: 'TSH', value: 2.1 });
  });

  it('reads a range printed without spaces and keeps the unit apart from it', () => {
    const row = parseResultLine('TSH 2,10 0,30-4,20');

    expect(row).toMatchObject({ label: 'TSH', value: 2.1, unit: null });
    expect(row?.printedRange).toMatchObject({ low: 0.3, high: 4.2 });
  });

  it('reads a row without a range', () => {
    expect(parseResultLine('Alkalen fosfataz (ALP) (Serum/Plazma) 138,4 U/L')).toMatchObject({
      label: 'Alkalen fosfataz (ALP) (Serum/Plazma)',
      value: 138.4,
      unit: 'U/L',
      printedRange: null,
    });
  });

  it.each(['Patient: Jane Doe', 'Test Result Unit Reference', ''])('ignores "%s"', (line) => {
    expect(parseResultLine(line)).toBeNull();
  });
});
