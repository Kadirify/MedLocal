import { resolve } from 'node:path';
import { z } from 'zod';

const schema = z.object({
  PORT: z.coerce.number().int().positive().default(3001),
  WEB_ORIGIN: z.string().default('http://localhost:3000'),
  // "localhost" costs two seconds per request on Windows while IPv6 is tried first
  OLLAMA_URL: z.url().default('http://127.0.0.1:11434'),
  OLLAMA_MODEL: z.string().default('medlocal-lab:q8_0'),
  OLLAMA_TIMEOUT_MS: z.coerce.number().int().positive().default(120_000),
  REFERENCE_DIR: z.string().default('../../reference'),
});

export class AppConfig {
  readonly port: number;
  readonly webOrigin: string;
  readonly ollamaUrl: string;
  readonly ollamaModel: string;
  readonly ollamaTimeoutMs: number;
  readonly catalogFile: string;
  readonly promptFile: string;

  constructor(env: NodeJS.ProcessEnv) {
    const values = schema.parse(env);
    const referenceDir = resolve(values.REFERENCE_DIR);

    this.port = values.PORT;
    this.webOrigin = values.WEB_ORIGIN;
    this.ollamaUrl = values.OLLAMA_URL.replace(/\/$/, '');
    this.ollamaModel = values.OLLAMA_MODEL;
    this.ollamaTimeoutMs = values.OLLAMA_TIMEOUT_MS;
    this.catalogFile = resolve(referenceDir, 'analytes.yaml');
    this.promptFile = resolve(referenceDir, 'explainer-prompt.json');
  }
}
