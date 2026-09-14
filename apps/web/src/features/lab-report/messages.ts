import type { Flag } from "./types";

export type Language = "tr" | "en";

export const LANGUAGES: readonly Language[] = ["tr", "en"];

export interface Messages {
  tagline: string;
  file: string;
  chooseFile: string;
  nothingChosen: string;
  noFile: string;
  trySample: string;
  sex: string;
  female: string;
  male: string;
  age: string;
  submit: string;
  working: string;
  results: string;
  nothingRecognised: string;
  unrecognised: string;
  differentUnit: string;
  catalogRange: string;
  explanation: string;
  model: string;
  columns: { test: string; result: string; unit: string; reference: string; status: string };
  flags: Record<Flag, string>;
  critical: string;
  unreachable: string;
  requestFailed: (status: number) => string;
}

export const MESSAGES: Record<Language, Messages> = {
  tr: {
    tagline: "Tahlil sonuçlarınızı sade bir dille açıklar. Dosyanız bu bilgisayardan dışarı çıkmaz.",
    file: "Tahlil raporu (PDF)",
    chooseFile: "Dosya seç",
    nothingChosen: "Dosya seçilmedi",
    noFile: "Elinizde rapor yok mu? ",
    trySample: "Örnek raporla deneyin",
    sex: "Cinsiyet",
    female: "Kadın",
    male: "Erkek",
    age: "Yaş",
    submit: "Açıkla",
    working: "İşleniyor…",
    results: "Sonuçlar",
    nothingRecognised: "Bu raporda tanınan bir tahlil bulunamadı.",
    unrecognised: "Tanınmayan ve açıklamaya dahil edilmeyen satırlar: ",
    differentUnit: "Farklı bir birimle basıldığı için değerlendirilmeyen satırlar: ",
    catalogRange:
      "Raporunuzda bu tahlil için aralık basılmamış. Genel yetişkin aralığı kullanıldı; " +
      "laboratuvarınızın aralığı yaşa veya yönteme göre farklı olabilir.",
    explanation: "Açıklama",
    model: "Model",
    columns: { test: "Tahlil", result: "Sonuç", unit: "Birim", reference: "Referans", status: "Durum" },
    flags: { LOW: "Düşük", NORMAL: "Normal", HIGH: "Yüksek" },
    critical: "Kritik",
    unreachable: "API'ye ulaşılamıyor. Sunucunun çalıştığından emin olun.",
    requestFailed: (status) => `İstek başarısız oldu (${status}).`,
  },
  en: {
    tagline: "Explains your lab results in plain language. Your file never leaves this computer.",
    file: "Lab report (PDF)",
    chooseFile: "Choose file",
    nothingChosen: "No file chosen",
    noFile: "No report at hand? ",
    trySample: "Try the sample report",
    sex: "Sex",
    female: "Female",
    male: "Male",
    age: "Age",
    submit: "Explain",
    working: "Working…",
    results: "Results",
    nothingRecognised: "No known test was found in this report.",
    unrecognised: "Rows that were not recognised and are left out of the explanation: ",
    differentUnit: "Rows set aside because they are printed in a different unit: ",
    catalogRange:
      "Your report prints no range for this test. A general adult range was used; your " +
      "laboratory's range may differ with age or method.",
    explanation: "Explanation",
    model: "Model",
    columns: { test: "Test", result: "Result", unit: "Unit", reference: "Reference", status: "Status" },
    flags: { LOW: "Low", NORMAL: "Normal", HIGH: "High" },
    critical: "Critical",
    unreachable: "The API cannot be reached. Make sure the server is running.",
    requestFailed: (status) => `The request failed (${status}).`,
  },
};
