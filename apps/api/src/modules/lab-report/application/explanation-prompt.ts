import { ChatMessage } from '../../../shared/llm/text-generator.js';
import { LabReport, LabResult } from '../domain/lab-report.js';

/**
 * The prompt the explainer model was fine-tuned on. Any difference from the training format
 * degrades the model silently, so the system text comes from reference/explainer-prompt.json
 * and the rendering is pinned by a test against the example in that file.
 */
export class ExplanationPrompt {
  constructor(
    readonly version: number,
    private readonly system: string,
  ) {}

  messagesFor(report: LabReport): ChatMessage[] {
    return [
      { role: 'system', content: this.system },
      { role: 'user', content: this.render(report) },
    ];
  }

  render(report: LabReport): string {
    const lines = report.results.map((result) => this.renderResult(result));
    return `Patient: ${report.sex}, ${report.age} years old\nResults:\n${lines.join('\n')}`;
  }

  private renderResult(result: LabResult): string {
    const { analyte } = result;
    const value = result.value.toFixed(analyte.decimals);
    const reference = result.reference.describe(analyte.decimals);
    return `- ${analyte.name}: ${value} ${analyte.unit} (reference ${reference}) ${result.flag}`;
  }
}
