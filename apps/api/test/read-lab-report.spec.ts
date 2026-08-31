import { resolve } from 'node:path';
import { describe, expect, it } from 'vitest';
import { UnreadableLabReportError } from '../src/modules/lab-report/application/ports.js';
import { ReadLabReport } from '../src/modules/lab-report/application/read-lab-report.use-case.js';
import { PdfTextLabReportParser } from '../src/modules/lab-report/infrastructure/pdf-text-lab-report-parser.js';
import { YamlAnalyteCatalog } from '../src/modules/lab-report/infrastructure/yaml-analyte-catalog.js';
import { renderLabReportPdf } from './sample-lab-report.js';

const catalog = new YamlAnalyteCatalog(
  resolve(import.meta.dirname, '../../../reference/analytes.yaml'),
);
const readLabReport = new ReadLabReport(new PdfTextLabReportParser(), catalog);

describe('reading a lab report PDF', () => {
  it('turns printed rows into flagged results', async () => {
    const pdf = await renderLabReportPdf([
      ['Hemoglobin', '10.8', 'g/dL', '11.6 - 15.0'],
      ['Ferritin', '8', 'ng/mL', '11 - 307'],
      ['LDL Kolesterol', '131', 'mg/dL', '< 100'],
      ['TSH', '2.10', 'mIU/L', '0.30 - 4.20'],
    ]);

    const { report } = await readLabReport.execute(pdf, 'female', 34);

    expect(report.results.map((r) => [r.analyte.key, r.value, r.flag])).toEqual([
      ['hemoglobin', 10.8, 'LOW'],
      ['ferritin', 8, 'LOW'],
      ['ldl_cholesterol', 131, 'HIGH'],
      ['tsh', 2.1, 'NORMAL'],
    ]);
  });

  it('prefers the range printed by the laboratory over the catalog', async () => {
    const pdf = await renderLabReportPdf([['Potasyum', '5.3', 'mmol/L', '3.5 - 5.5']]);

    const { report } = await readLabReport.execute(pdf, 'male', 50);

    expect(report.results[0]?.flag).toBe('NORMAL');
  });

  it('reports labels it does not know instead of guessing', async () => {
    const pdf = await renderLabReportPdf([
      ['Sodyum', '139', 'mmol/L', '135 - 145'],
      ['Troponin I', '0.01', 'ng/mL', '< 0.04'],
    ]);

    const { report, unrecognizedLabels } = await readLabReport.execute(pdf, 'male', 50);

    expect(report.results).toHaveLength(1);
    expect(unrecognizedLabels).toEqual(['Troponin I']);
  });

  it('marks critical values', async () => {
    const pdf = await renderLabReportPdf([['Potassium', '6.8', 'mmol/L', '3.6 - 5.2']]);

    const { report } = await readLabReport.execute(pdf, 'female', 61);

    expect(report.criticalResults.map((r) => r.analyte.key)).toEqual(['potassium']);
  });

  it('matches labels the way Turkish hospital laboratories print them', async () => {
    const pdf = await renderLabReportPdf([
      ['HGB (Hemoglobin)', '16,1', 'g/dL', '12,9-16,7'],
      ['Kreatinin (Serum/Plazma)', '1,04', 'mg/dL', '0,6-1,2'],
      ['AST ( SGOT)', '23', 'U/L', '11-34'],
      ['RBC (Eritrosit Sayisi)', '5,90 H', '10^6/uL', '4,3-5,7'],
      ['IG% (Immatur Granulosit Orani)', '0,3', '%', '0-0,6'],
    ]);

    const { report, unrecognizedLabels } = await readLabReport.execute(pdf, 'male', 30);

    expect(report.results.map((r) => [r.analyte.key, r.value, r.flag])).toEqual([
      ['hemoglobin', 16.1, 'NORMAL'],
      ['creatinine', 1.04, 'NORMAL'],
      ['ast', 23, 'NORMAL'],
      ['red_blood_cells', 5.9, 'HIGH'],
    ]);
    expect(unrecognizedLabels).toEqual(['IG% (Immatur Granulosit Orani)']);
  });

  it('falls back to the catalog when a row prints no range', async () => {
    const pdf = await renderLabReportPdf([
      ['Alkalen fosfataz (ALP) (Serum/Plazma)', '138,4', 'U/L', ''],
    ]);

    const { report } = await readLabReport.execute(pdf, 'male', 30);

    expect(report.results.map((r) => [r.analyte.key, r.flag, r.referenceSource])).toEqual([
      ['alp', 'HIGH', 'catalog'],
    ]);
  });

  it('keeps the unit printed on the report', async () => {
    const pdf = await renderLabReportPdf([['WBC', '7,51', '10^3/uL', '3,8-9,99']]);

    const { report } = await readLabReport.execute(pdf, 'male', 30);

    expect(report.results[0]?.printedUnit).toBe('10^3/uL');
  });

  it('sets aside a result printed in a different unit instead of misjudging it', async () => {
    const pdf = await renderLabReportPdf([
      ['Hemoglobin', '161', 'g/L', '129-167'],
      ['Sodyum', '139', 'mmol/L', '135-145'],
    ]);

    const { report, differentUnitLabels } = await readLabReport.execute(pdf, 'male', 30);

    expect(report.results.map((r) => r.analyte.key)).toEqual(['sodium']);
    expect(differentUnitLabels).toEqual(['Hemoglobin']);
  });

  it('ignores page furniture that happens to contain numbers', async () => {
    const pdf = await renderLabReportPdf([
      ['Sayfa', '1/3', '', ''],
      ['Sodyum', '139', 'mmol/L', '135-145'],
    ]);

    const { report, unrecognizedLabels } = await readLabReport.execute(pdf, 'male', 30);

    expect(report.results).toHaveLength(1);
    expect(unrecognizedLabels).toEqual([]);
  });

  it('rejects a file that is not a PDF', async () => {
    const notPdf = new TextEncoder().encode('hello');

    await expect(readLabReport.execute(notPdf, 'male', 40)).rejects.toThrow(
      UnreadableLabReportError,
    );
  });
});
