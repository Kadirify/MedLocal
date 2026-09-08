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
import { ExplanationPrompt, PromptWording } from './explanation-prompt.js';

class RecordingGenerator extends TextGenerator {
  readonly model = 'fake';
  received: readonly ChatMessage[] = [];

  async *stream(messages: readonly ChatMessage[]): AsyncIterable<string> {
    this.received = messages;
    yield* await Promise.resolve(['Your potassium ', 'is low.']);
  }
}

const templates: PromptWording['templates'] = {
  patient: 'Patient: {sex}, {age}',
  sexes: { male: 'male', female: 'female' },
  flags: { LOW: 'LOW', NORMAL: 'NORMAL', HIGH: 'HIGH' },
  result: '- {name}: {value} {unit} ({reference} {range}) {flag}',
  reference: 'reference',
  up_to: 'up to {high}',
  at_least: '{low} or higher',
  between: '{low} to {high}',
  background_header: 'Background:',
  background_line: '- {name} measures {measures}. A {side} result {context}.',
  sides: { LOW: 'low', HIGH: 'high' },
};
const prompt = new ExplanationPrompt(1, {
  en: { system: 'system text', templates },
  tr: { system: 'sistem metni', templates },
});

const range = new ReferenceRange(3.6, 5.2);
const critical = { low: 2.5, high: 6.5 };
const potassium = new Analyte(
  'potassium',
  'Potassium',
  'Potasyum',
  'mmol/L',
  1,
  { any: range },
  critical,
  {
    measures: { en: 'a mineral', tr: 'bir minerali' },
    low: { en: 'can be seen with vomiting', tr: 'kusmayla görülebilir' },
    high: { en: 'can be seen with some medicines', tr: 'bazı ilaçlarla görülebilir' },
  },
);
const reportWith = (value: number) =>
  new LabReport('female', 40, [new LabResult(potassium, value, range)]);

describe('ExplainLabReport', () => {
  it('streams the model reply for an ordinary report', async () => {
    const generator = new RecordingGenerator();
    const useCase = new ExplainLabReport(generator, prompt);

    const pieces: string[] = [];
    for await (const piece of useCase.execute(reportWith(3.2), 'en')) pieces.push(piece);

    expect(pieces.join('')).toBe('Your potassium is low.');
    expect(generator.received[0]).toEqual({ role: 'system', content: 'system text' });
    expect(generator.received[1]?.content).toContain('- Potassium: 3.2 mmol/L');
  });

  it('hands the model the vetted background of every flagged result', async () => {
    const generator = new RecordingGenerator();
    const useCase = new ExplainLabReport(generator, prompt);

    const pieces: string[] = [];
    for await (const piece of useCase.execute(reportWith(3.2), 'en')) pieces.push(piece);

    expect(generator.received[1]?.content).toContain(
      'Background:\n- Potassium measures a mineral. A low result can be seen with vomiting.',
    );
  });

  it('adds no background when nothing is flagged', async () => {
    const generator = new RecordingGenerator();
    const useCase = new ExplainLabReport(generator, prompt);

    const pieces: string[] = [];
    for await (const piece of useCase.execute(reportWith(4.4), 'en')) pieces.push(piece);

    expect(generator.received[1]?.content).not.toContain('Background:');
  });

  it('asks in the language of the reader', async () => {
    const generator = new RecordingGenerator();
    const useCase = new ExplainLabReport(generator, prompt);

    const pieces: string[] = [];
    for await (const piece of useCase.execute(reportWith(3.2), 'tr')) pieces.push(piece);

    expect(generator.received[0]?.content).toBe('sistem metni');
    expect(generator.received[1]?.content).toContain('- Potasyum: 3.2 mmol/L');
  });

  it.each([2.5, 2.1, 6.5, 7])('never sends a critical value (%s) to the model', (value) => {
    const generator = new RecordingGenerator();
    const useCase = new ExplainLabReport(generator, prompt);

    expect(() => useCase.execute(reportWith(value), 'en')).toThrow(CriticalValueError);
    expect(generator.received).toEqual([]);
  });

  it('refuses a report without recognised results', () => {
    const useCase = new ExplainLabReport(new RecordingGenerator(), prompt);

    expect(() => useCase.execute(new LabReport('male', 30, []), 'en')).toThrow(
      NothingToExplainError,
    );
  });
});
