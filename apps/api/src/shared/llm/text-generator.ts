export interface ChatMessage {
  readonly role: 'system' | 'user' | 'assistant';
  readonly content: string;
}

export class TextGenerationError extends Error {}

export abstract class TextGenerator {
  abstract readonly model: string;

  /** Yields the reply piece by piece. Rejects with TextGenerationError. */
  abstract stream(messages: readonly ChatMessage[], signal?: AbortSignal): AsyncIterable<string>;
}
