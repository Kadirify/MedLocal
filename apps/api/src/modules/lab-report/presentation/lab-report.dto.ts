import { Type } from 'class-transformer';
import {
  ArrayMaxSize,
  ArrayMinSize,
  IsIn,
  IsInt,
  IsNumber,
  IsOptional,
  IsString,
  Max,
  Min,
  ValidateNested,
} from 'class-validator';
import type { Sex } from '../domain/analyte.js';
import { LabReport, LabResult } from '../domain/lab-report.js';

const SEXES: readonly Sex[] = ['male', 'female'];

export class PatientDto {
  @IsIn(SEXES)
  sex!: Sex;

  @Type(() => Number)
  @IsInt()
  @Min(18)
  @Max(120)
  age!: number;
}

export class ResultInputDto {
  @IsString()
  analyte!: string;

  @IsNumber()
  value!: number;

  @IsOptional()
  @IsNumber()
  low?: number | null;

  @IsOptional()
  @IsNumber()
  high?: number | null;
}

export class ExplanationRequestDto extends PatientDto {
  @ValidateNested({ each: true })
  @Type(() => ResultInputDto)
  @ArrayMinSize(1)
  @ArrayMaxSize(60)
  results!: ResultInputDto[];
}

export interface ResultView {
  readonly analyte: string;
  readonly name: string;
  readonly value: number;
  readonly unit: string;
  readonly decimals: number;
  readonly low: number | null;
  readonly high: number | null;
  readonly reference: string;
  readonly referenceSource: string;
  readonly flag: string;
  readonly critical: boolean;
}

export interface LabReportView {
  readonly sex: Sex;
  readonly age: number;
  readonly results: readonly ResultView[];
  readonly unrecognizedLabels: readonly string[];
  readonly differentUnitLabels: readonly string[];
  readonly criticalMessage: string | null;
  readonly disclaimer: string;
}

export function toResultView(result: LabResult): ResultView {
  const { analyte, reference } = result;
  return {
    analyte: analyte.key,
    name: analyte.name,
    value: result.value,
    unit: result.printedUnit ?? analyte.unit,
    decimals: analyte.decimals,
    low: reference.low,
    high: reference.high,
    reference: reference.describe(analyte.decimals),
    referenceSource: result.referenceSource,
    flag: result.flag,
    critical: result.isCritical,
  };
}

export function toResultViews(report: LabReport): ResultView[] {
  return report.results.map(toResultView);
}
