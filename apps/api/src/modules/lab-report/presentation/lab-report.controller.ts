import {
  BadRequestException,
  Body,
  Controller,
  PayloadTooLargeException,
  Post,
  Res,
  UnprocessableEntityException,
  UploadedFile,
  UseInterceptors,
} from '@nestjs/common';
import { FileInterceptor } from '@nestjs/platform-express';
import type { Response } from 'express';
import {
  CriticalValueError,
  ExplainLabReport,
} from '../application/explain-lab-report.use-case.js';
import { AnalyteCatalog, UnreadableLabReportError } from '../application/ports.js';
import { ReadLabReport } from '../application/read-lab-report.use-case.js';
import { SAFETY_MESSAGES } from '../application/safety-messages.js';
import { LabReport, LabResult } from '../domain/lab-report.js';
import { ReferenceRange } from '../domain/reference-range.js';
import {
  ExplanationRequestDto,
  LabReportView,
  PatientDto,
  ResultInputDto,
  toResultViews,
} from './lab-report.dto.js';

const MAX_PDF_BYTES = 10 * 1024 * 1024;

@Controller('lab-reports')
export class LabReportController {
  constructor(
    private readonly readLabReport: ReadLabReport,
    private readonly explainLabReport: ExplainLabReport,
    private readonly catalog: AnalyteCatalog,
  ) {}

  @Post()
  @UseInterceptors(FileInterceptor('file'))
  async read(
    @UploadedFile() file: Express.Multer.File | undefined,
    @Body() patient: PatientDto,
  ): Promise<LabReportView> {
    // Nest's file pipes answer in English before the reader's language is known
    const messages = SAFETY_MESSAGES[patient.language];
    if (!file) throw new BadRequestException(messages.missingFile);
    if (file.size > MAX_PDF_BYTES) throw new PayloadTooLargeException(messages.fileTooLarge);

    try {
      const { report, unrecognizedLabels, differentUnitLabels } = await this.readLabReport.execute(
        file.buffer,
        patient.sex,
        patient.age,
      );
      return {
        sex: report.sex,
        age: report.age,
        results: toResultViews(report, patient.language),
        unrecognizedLabels,
        differentUnitLabels,
        criticalMessage: report.criticalResults.length > 0 ? messages.criticalValue : null,
        disclaimer: messages.disclaimer,
      };
    } catch (error) {
      if (error instanceof UnreadableLabReportError) {
        throw new UnprocessableEntityException(messages.unreadableReport);
      }
      throw error;
    }
  }

  @Post('explanation')
  async explain(@Body() body: ExplanationRequestDto, @Res() response: Response): Promise<void> {
    const report = new LabReport(
      body.sex,
      body.age,
      body.results.map((row) => this.toResult(row, body)),
    );

    const messages = SAFETY_MESSAGES[body.language];
    const aborted = new AbortController();
    response.on('close', () => {
      aborted.abort();
    });

    let pieces: AsyncIterable<string>;
    try {
      pieces = this.explainLabReport.execute(report, body.language, aborted.signal);
    } catch (error) {
      if (error instanceof CriticalValueError) {
        throw new UnprocessableEntityException(messages.criticalValue);
      }
      throw error;
    }

    response.setHeader('Content-Type', 'text/event-stream');
    response.setHeader('Cache-Control', 'no-cache');
    response.flushHeaders();

    try {
      for await (const text of pieces) {
        response.write(`data: ${JSON.stringify({ text })}\n\n`);
      }
      const done = { model: this.explainLabReport.modelVersion, disclaimer: messages.disclaimer };
      response.write(`event: done\ndata: ${JSON.stringify(done)}\n\n`);
    } catch {
      if (!aborted.signal.aborted) {
        const failure = { message: messages.generationFailed };
        response.write(`event: error\ndata: ${JSON.stringify(failure)}\n\n`);
      }
    } finally {
      response.end();
    }
  }

  private toResult(row: ResultInputDto, patient: PatientDto): LabResult {
    const analyte = this.catalog.findByKey(row.analyte);
    if (!analyte) throw new BadRequestException(`unknown analyte "${row.analyte}"`);

    const printed = row.low != null || row.high != null;
    const reference = printed
      ? new ReferenceRange(row.low ?? null, row.high ?? null)
      : analyte.rangeFor(patient.sex);
    return new LabResult(analyte, row.value, reference);
  }
}
