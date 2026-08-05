import { describe, expect, it } from 'vitest';
import { ChatMessage, TextGenerator } from '../../../shared/llm/text-generator.js';
import { Analyte } from '../domain/analyte.js';
import { LabReport, LabResult } from '../domain/lab-report.js';
import { ReferenceRange } from '../domain/reference-range.js';
import {
  CriticalValueError,
  ExplainLabReport,
  NothingToExplainError,
} from './explain-lab-report.use-case.js';
import { ExplanationPrompt } from './explanation-prompt.js';

class RecordingGenerator extends TextGenerator {
  readonly model = 'fake';
  received: readonly ChatMessage[] = [];

  async *stream(messages: readonly ChatMessage[]): AsyncIterable<string> {
    this.received = messages;
    yield* await Promise.resolve(['Your potassium ', 'is low.']);
  }
}

const range = new ReferenceRange(3.6, 5.2);
const potassium = new Analyte(
  'potassium',
  'Potassium',
  'mmol/L',
  1,
  { any: range },
  {
    low: 2.5,
    high: 6.5,
  },
);
const reportWith = (value: number) =>
  new LabReport('female', 40, [new LabResult(potassium, value, range)]);

describe('ExplainLabReport', () => {
  it('streams the model reply for an ordinary report', async () => {
    const generator = new RecordingGenerator();
    const useCase = new ExplainLabReport(generator, new ExplanationPrompt(1, 'system text'));

    const pieces: string[] = [];
    for await (const piece of useCase.execute(reportWith(3.2))) pieces.push(piece);

    expect(pieces.join('')).toBe('Your potassium is low.');
    expect(generator.received[0]).toEqual({ role: 'system', content: 'system text' });
    expect(generator.received[1]?.content).toContain('Potassium: 3.2 mmol/L');
  });

  it.each([2.5, 2.1, 6.5, 7])('never sends a critical value (%s) to the model', (value) => {
    const generator = new RecordingGenerator();
    const useCase = new ExplainLabReport(generator, new ExplanationPrompt(1, 'system text'));

    expect(() => useCase.execute(reportWith(value))).toThrow(CriticalValueError);
    expect(generator.received).toEqual([]);
  });

  it('refuses a report without recognised results', () => {
    const useCase = new ExplainLabReport(new RecordingGenerator(), new ExplanationPrompt(1, 's'));

    expect(() => useCase.execute(new LabReport('male', 30, []))).toThrow(NothingToExplainError);
  });
});
