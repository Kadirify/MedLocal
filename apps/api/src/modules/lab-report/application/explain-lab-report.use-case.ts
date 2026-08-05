import { Injectable } from '@nestjs/common';
import { TextGenerator } from '../../../shared/llm/text-generator.js';
import { LabReport } from '../domain/lab-report.js';
import { ExplanationPrompt } from './explanation-prompt.js';

export class CriticalValueError extends Error {}

export class NothingToExplainError extends Error {}

@Injectable()
export class ExplainLabReport {
  constructor(
    private readonly generator: TextGenerator,
    private readonly prompt: ExplanationPrompt,
  ) {}

  get modelVersion(): string {
    return `${this.generator.model} (prompt v${this.prompt.version})`;
  }

  execute(report: LabReport, signal?: AbortSignal): AsyncIterable<string> {
    if (report.results.length === 0) {
      throw new NothingToExplainError('the report has no recognised results');
    }
    // critical values get a fixed message from the caller and never reach the model
    if (report.criticalResults.length > 0) {
      const names = report.criticalResults.map((result) => result.analyte.name).join(', ');
      throw new CriticalValueError(`critical values present: ${names}`);
    }
    return this.generator.stream(this.prompt.messagesFor(report), signal);
  }
}
