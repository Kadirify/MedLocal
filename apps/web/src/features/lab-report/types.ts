export type Sex = "male" | "female";
export type Flag = "LOW" | "NORMAL" | "HIGH";

export interface LabResult {
  analyte: string;
  name: string;
  value: number;
  unit: string;
  decimals: number;
  low: number | null;
  high: number | null;
  reference: string;
  flag: Flag;
  critical: boolean;
}

export interface LabReport {
  sex: Sex;
  age: number;
  results: LabResult[];
  unrecognizedLabels: string[];
  criticalMessage: string | null;
  disclaimer: string;
}

export interface ExplanationFooter {
  model: string;
  disclaimer: string;
}
