import { ChatMessage } from '../../../shared/llm/text-generator.js';
import type { Sex } from '../domain/analyte.js';
import type { Language } from '../domain/language.js';
import { LabReport, LabResult } from '../domain/lab-report.js';
import type { Flag, ReferenceRange } from '../domain/reference-range.js';

export interface PromptWording {
  readonly system: string;
  readonly templates: {
    readonly patient: string;
    readonly sexes: Readonly<Record<Sex, string>>;
    readonly flags: Readonly<Record<Flag, string>>;
    readonly result: string;
    readonly reference: string;
    readonly up_to: string;
    readonly at_least: string;
    readonly between: string;
    readonly background_header: string;
    readonly background_line: string;
    readonly sides: Readonly<Record<'LOW' | 'HIGH', string>>;
  };
}

/**
 * The prompt the explainer model was fine-tuned on. Any difference from the training format
 * degrades the model silently, so every piece of wording comes from
 * reference/explainer-prompt.json, which the training pipeline writes, and the rendering is
 * pinned by a test against the example in that file.
 */
export class ExplanationPrompt {
  constructor(
    readonly version: number,
    private readonly wording: Readonly<Record<Language, PromptWording>>,
  ) {}

  messagesFor(report: LabReport, language: Language): ChatMessage[] {
    return [
      { role: 'system', content: this.wording[language].system },
      { role: 'user', content: this.render(report, language) },
    ];
  }

  render(report: LabReport, language: Language): string {
    const { templates } = this.wording[language];
    const header = fill(templates.patient, {
      sex: templates.sexes[report.sex],
      age: String(report.age),
    });
    const lines = report.results.map((result) => this.renderResult(result, language));
    const notes = report.results.flatMap((result) => this.renderBackground(result, language));
    const results = [header, ...lines].join('\n');
    if (notes.length === 0) return results;
    return [results, '', templates.background_header, ...notes].join('\n');
  }

  private renderResult(result: LabResult, language: Language): string {
    const { templates } = this.wording[language];
    const { analyte } = result;
    return fill(templates.result, {
      name: analyte.nameIn(language),
      value: result.value.toFixed(analyte.decimals),
      unit: analyte.unit,
      reference: templates.reference,
      range: this.describe(result.reference, analyte.decimals, language),
      flag: templates.flags[result.flag],
    });
  }

  private renderBackground(result: LabResult, language: Language): string[] {
    const { flag, analyte } = result;
    if (flag === 'NORMAL') return [];

    const { templates } = this.wording[language];
    const context = flag === 'LOW' ? analyte.background.low : analyte.background.high;
    if (!context) throw new Error(`${analyte.key} has no ${flag} background`);
    return [
      fill(templates.background_line, {
        name: analyte.nameIn(language),
        measures: analyte.background.measures[language],
        side: templates.sides[flag],
        context: context[language],
      }),
    ];
  }

  private describe(range: ReferenceRange, decimals: number, language: Language): string {
    const { templates } = this.wording[language];
    const low = range.low?.toFixed(decimals) ?? '';
    const high = range.high?.toFixed(decimals) ?? '';
    if (range.low === null) return fill(templates.up_to, { high });
    if (range.high === null) return fill(templates.at_least, { low });
    return fill(templates.between, { low, high });
  }
}

function fill(template: string, values: Readonly<Record<string, string>>): string {
  return template.replace(/\{(\w+)\}/g, (placeholder, key: string) => values[key] ?? placeholder);
}
