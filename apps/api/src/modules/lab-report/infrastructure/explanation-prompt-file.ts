import { readFileSync } from 'node:fs';
import { z } from 'zod';
import { ExplanationPrompt } from '../application/explanation-prompt.js';

const schema = z.object({ version: z.number().int().positive(), system: z.string().min(1) });

export function readExplanationPrompt(file: string): ExplanationPrompt {
  const { version, system } = schema.parse(JSON.parse(readFileSync(file, 'utf8')));
  return new ExplanationPrompt(version, system);
}
