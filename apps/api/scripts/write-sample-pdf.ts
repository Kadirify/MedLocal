import { mkdirSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { renderLabReportPdf } from '../test/sample-lab-report.ts';

const output = resolve(import.meta.dirname, '../../web/public/sample-lab-report.pdf');

const pdf = await renderLabReportPdf([
  ['Hemoglobin', '10.8', 'g/dL', '11.6 - 15.0'],
  ['Hematokrit', '33.1', '%', '35.5 - 44.9'],
  ['MCV', '74', 'fL', '80 - 100'],
  ['WBC', '6.2', '10^3/µL', '3.4 - 9.6'],
  ['Trombosit', '262', '10^3/µL', '150 - 400'],
  ['Ferritin', '8', 'ng/mL', '11 - 307'],
  ['B12 Vitamini', '412', 'pg/mL', '180 - 914'],
  ['25-OH Vitamin D', '14', 'ng/mL', '20 - 50'],
  ['Glukoz', '92', 'mg/dL', '70 - 99'],
  ['LDL Kolesterol', '131', 'mg/dL', '< 100'],
  ['HDL Kolesterol', '62', 'mg/dL', '> 50'],
  ['TSH', '2.10', 'mIU/L', '0.30 - 4.20'],
]);

mkdirSync(resolve(output, '..'), { recursive: true });
writeFileSync(output, pdf);
console.log(output);
