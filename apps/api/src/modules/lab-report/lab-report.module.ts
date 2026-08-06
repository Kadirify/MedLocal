import { Module } from '@nestjs/common';
import { AppConfig } from '../../config/app-config.js';
import { LlmModule } from '../../shared/llm/llm.module.js';
import { ExplainLabReport } from './application/explain-lab-report.use-case.js';
import { ExplanationPrompt } from './application/explanation-prompt.js';
import { AnalyteCatalog, LabReportParser } from './application/ports.js';
import { ReadLabReport } from './application/read-lab-report.use-case.js';
import { readExplanationPrompt } from './infrastructure/explanation-prompt-file.js';
import { PdfTextLabReportParser } from './infrastructure/pdf-text-lab-report-parser.js';
import { YamlAnalyteCatalog } from './infrastructure/yaml-analyte-catalog.js';
import { LabReportController } from './presentation/lab-report.controller.js';

@Module({
  imports: [LlmModule],
  controllers: [LabReportController],
  providers: [
    ReadLabReport,
    ExplainLabReport,
    { provide: LabReportParser, useClass: PdfTextLabReportParser },
    {
      provide: AnalyteCatalog,
      inject: [AppConfig],
      useFactory: (config: AppConfig) => new YamlAnalyteCatalog(config.catalogFile),
    },
    {
      provide: ExplanationPrompt,
      inject: [AppConfig],
      useFactory: (config: AppConfig) => readExplanationPrompt(config.promptFile),
    },
  ],
})
export class LabReportModule {}
