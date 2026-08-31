import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { describe, expect, it } from 'vitest';
import type { Sex } from '../domain/analyte.js';
import type { Language } from '../domain/language.js';
import { LabReport, LabResult } from '../domain/lab-report.js';
import { readExplanationPrompt } from '../infrastructure/explanation-prompt-file.js';
import { YamlAnalyteCatalog } from '../infrastructure/yaml-analyte-catalog.js';

const REFERENCE = resolve(import.meta.dirname, '../../../../../../reference');

interface Contract {
  example: { sex: Sex; age: number; results: { analyte: string; value: number }[] };
  languages: Record<Language, { system: string; user: string }>;
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

  it.each(['en', 'tr'] as const)(
    'renders a report in %s exactly as the training pipeline does',
    (language) => {
      expect(prompt.render(report, language)).toBe(contract.languages[language].user);
    },
  );

  it.each(['en', 'tr'] as const)(
    'sends the %s system text the model was trained with',
    (language) => {
      expect(prompt.messagesFor(report, language)).toEqual([
        { role: 'system', content: contract.languages[language].system },
        { role: 'user', content: contract.languages[language].user },
      ]);
    },
  );
});
