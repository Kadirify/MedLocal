import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { describe, expect, it } from 'vitest';
import type { Sex } from '../domain/analyte.js';
import { LabReport, LabResult } from '../domain/lab-report.js';
import { readExplanationPrompt } from '../infrastructure/explanation-prompt-file.js';
import { YamlAnalyteCatalog } from '../infrastructure/yaml-analyte-catalog.js';

const REFERENCE = resolve(import.meta.dirname, '../../../../../../reference');

interface Contract {
  system: string;
  example: { sex: Sex; age: number; user: string; results: { analyte: string; value: number }[] };
}

describe('ExplanationPrompt', () => {
  const contractFile = resolve(REFERENCE, 'explainer-prompt.json');
  const contract = JSON.parse(readFileSync(contractFile, 'utf8')) as Contract;
  const catalog = new YamlAnalyteCatalog(resolve(REFERENCE, 'analytes.yaml'));
  const prompt = readExplanationPrompt(contractFile);

  const { example } = contract;
  const report = new LabReport(
    example.sex,
    example.age,
    example.results.map(({ analyte: key, value }) => {
      const analyte = catalog.findByKey(key);
      if (!analyte) throw new Error(`contract uses unknown analyte ${key}`);
      return new LabResult(analyte, value, analyte.rangeFor(example.sex));
    }),
  );

  it('renders a report exactly as the training pipeline does', () => {
    expect(prompt.render(report)).toBe(example.user);
  });

  it('sends the system text the model was trained with', () => {
    expect(prompt.messagesFor(report)).toEqual([
      { role: 'system', content: contract.system },
      { role: 'user', content: example.user },
    ]);
  });
});
