import { ChatMessage, TextGenerationError, TextGenerator } from './text-generator.js';

const MAX_TOKENS = 500;

interface OllamaChunk {
  readonly message?: { readonly content?: string };
  readonly error?: string;
}

export class OllamaTextGenerator extends TextGenerator {
  constructor(
    private readonly baseUrl: string,
    readonly model: string,
    private readonly timeoutMs: number,
  ) {
    super();
  }

  async *stream(messages: readonly ChatMessage[], signal?: AbortSignal): AsyncIterable<string> {
    const timeout = AbortSignal.timeout(this.timeoutMs);
    const response = await fetch(`${this.baseUrl}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      signal: signal ? AbortSignal.any([signal, timeout]) : timeout,
      body: JSON.stringify({
        model: this.model,
        messages,
        stream: true,
        think: false,
        options: { temperature: 0, num_predict: MAX_TOKENS },
      }),
    }).catch((error: unknown) => {
      throw new TextGenerationError(`Ollama is unreachable at ${this.baseUrl}: ${String(error)}`);
    });

    if (!response.ok || !response.body) {
      throw new TextGenerationError(`Ollama answered ${response.status}: ${await response.text()}`);
    }

    for await (const line of readLines(response.body)) {
      const chunk = JSON.parse(line) as OllamaChunk;
      if (chunk.error) throw new TextGenerationError(chunk.error);
      if (chunk.message?.content) yield chunk.message.content;
    }
  }
}

async function* readLines(body: ReadableStream<Uint8Array>): AsyncIterable<string> {
  const decoder = new TextDecoder();
  let pending = '';

  for await (const bytes of body) {
    pending += decoder.decode(bytes, { stream: true });
    const lines = pending.split('\n');
    pending = lines.pop() ?? '';
    yield* lines.filter((line) => line.trim());
  }
  if (pending.trim()) yield pending;
}
