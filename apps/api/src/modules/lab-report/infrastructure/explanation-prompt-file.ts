import { readFileSync } from 'node:fs';
import { z } from 'zod';
import { ExplanationPrompt } from '../application/explanation-prompt.js';

const wording = z.object({
  system: z.string().min(1),
  templates: z.object({
    patient: z.string(),
    sexes: z.object({ male: z.string(), female: z.string() }),
    flags: z.object({ LOW: z.string(), NORMAL: z.string(), HIGH: z.string() }),
    result: z.string(),
    reference: z.string(),
    up_to: z.string(),
    at_least: z.string(),
    between: z.string(),
  }),
});

const schema = z.object({
  version: z.number().int().positive(),
  languages: z.object({ en: wording, tr: wording }),
});

export function readExplanationPrompt(file: string): ExplanationPrompt {
  const { version, languages } = schema.parse(JSON.parse(readFileSync(file, 'utf8')));
  return new ExplanationPrompt(version, languages);
}
