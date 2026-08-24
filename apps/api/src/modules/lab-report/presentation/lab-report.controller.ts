import {
  BadRequestException,
  Body,
  Controller,
  ParseFilePipeBuilder,
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
import { CRITICAL_VALUE_MESSAGE, DISCLAIMER } from '../application/safety-messages.js';
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
    @UploadedFile(
      new ParseFilePipeBuilder()
        .addFileTypeValidator({ fileType: 'application/pdf' })
        .addMaxSizeValidator({ maxSize: MAX_PDF_BYTES })
        .build(),
    )
    file: Express.Multer.File,
    @Body() patient: PatientDto,
  ): Promise<LabReportView> {
    try {
      const { report, unrecognizedLabels, differentUnitLabels } = await this.readLabReport.execute(
        file.buffer,
        patient.sex,
        patient.age,
      );
      return {
        sex: report.sex,
        age: report.age,
        results: toResultViews(report),
        unrecognizedLabels,
        differentUnitLabels,
        criticalMessage: report.criticalResults.length > 0 ? CRITICAL_VALUE_MESSAGE : null,
        disclaimer: DISCLAIMER,
      };
    } catch (error) {
      if (error instanceof UnreadableLabReportError) {
        throw new UnprocessableEntityException(error.message);
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

    const aborted = new AbortController();
    response.on('close', () => {
      aborted.abort();
    });

    let pieces: AsyncIterable<string>;
    try {
      pieces = this.explainLabReport.execute(report, aborted.signal);
    } catch (error) {
      if (error instanceof CriticalValueError) {
        throw new UnprocessableEntityException(CRITICAL_VALUE_MESSAGE);
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
      const done = { model: this.explainLabReport.modelVersion, disclaimer: DISCLAIMER };
      response.write(`event: done\ndata: ${JSON.stringify(done)}\n\n`);
    } catch (error) {
      if (!aborted.signal.aborted) {
        const message = error instanceof Error ? error.message : 'generation failed';
        response.write(`event: error\ndata: ${JSON.stringify({ message })}\n\n`);
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
