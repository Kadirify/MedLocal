import { Module } from '@nestjs/common';
import { AppConfig } from '../../config/app-config.js';
import { OllamaTextGenerator } from './ollama-text-generator.js';
import { TextGenerator } from './text-generator.js';

@Module({
  providers: [
    {
      provide: TextGenerator,
      inject: [AppConfig],
      useFactory: (config: AppConfig) =>
        new OllamaTextGenerator(config.ollamaUrl, config.ollamaModel, config.ollamaTimeoutMs),
    },
  ],
  exports: [TextGenerator],
})
export class LlmModule {}
