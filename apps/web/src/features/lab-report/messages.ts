import type { Flag } from "./types";

export type Language = "tr" | "en";

export const LANGUAGES: readonly Language[] = ["tr", "en"];

interface Step {
  title: string;
  text: string;
}

export interface Messages {
  headline: string;
  tagline: string;
  localBadge: string;
  dropHere: string;
  fileHint: string;
  changeFile: string;
  trySample: string;
  sex: string;
  female: string;
  male: string;
  age: string;
  submit: string;
  working: string;
  steps: [Step, Step, Step];
  results: string;
  nothingRecognised: string;
  unrecognised: string;
  differentUnit: string;
  catalogRange: string;
  explanation: string;
  model: string;
  columns: { test: string; result: string; range: string; reference: string; status: string };
  flags: Record<Flag, string>;
  critical: string;
  unreachable: string;
  requestFailed: (status: number) => string;
  notADevice: string;
  sourceCode: string;
}

export const MESSAGES: Record<Language, Messages> = {
  tr: {
    headline: "Tahlil sonuçlarınızı anlayın",
    tagline:
      "PDF raporunuzu yükleyin; hangi değerlerin aralık dışında olduğunu görün ve sade bir dille " +
      "açıklamasını okuyun. Dosyanız bu bilgisayardan dışarı çıkmaz.",
    localBadge: "Tamamen yerel çalışır",
    dropHere: "PDF raporunuzu buraya sürükleyin veya seçmek için tıklayın",
    fileHint: "Seçilebilir metin içeren PDF, en fazla 10 MB",
    changeFile: "Değiştirmek için tıklayın",
    trySample: "Örnek raporla deneyin",
    sex: "Cinsiyet",
    female: "Kadın",
    male: "Erkek",
    age: "Yaş",
    submit: "Açıkla",
    working: "İşleniyor…",
    steps: [
      {
        title: "Rapor okunur",
        text: "Tahlil adları, değerler ve raporda basılı referans aralıkları PDF'ten çıkarılır.",
      },
      {
        title: "Kurallar karar verir",
        text: "Bir değerin düşük mü yüksek mi olduğuna yapay zekâ değil, kod karar verir. Kritik değerlerde model hiç çalışmaz.",
      },
      {
        title: "Model anlatır",
        text: "Bu bilgisayarda çalışan küçük bir dil modeli, doğrulanmış notlara dayanarak sonuçları sade dille açıklar.",
      },
    ],
    results: "Sonuçlar",
    nothingRecognised: "Bu raporda tanınan bir tahlil bulunamadı.",
    unrecognised: "Tanınmayan ve açıklamaya dahil edilmeyen satırlar",
    differentUnit: "Farklı bir birimle basıldığı için değerlendirilmeyen satırlar",
    catalogRange:
      "Raporunuzda bu tahlil için aralık basılmamış. Genel yetişkin aralığı kullanıldı; " +
      "laboratuvarınızın aralığı yaşa veya yönteme göre farklı olabilir.",
    explanation: "Açıklama",
    model: "Model",
    columns: { test: "Tahlil", result: "Sonuç", range: "Aralıkta yeri", reference: "Referans", status: "Durum" },
    flags: { LOW: "Düşük", NORMAL: "Normal", HIGH: "Yüksek" },
    critical: "Kritik",
    unreachable: "API'ye ulaşılamıyor. Sunucunun çalıştığından emin olun.",
    requestFailed: (status) => `İstek başarısız oldu (${status}).`,
    notADevice: "MedLocal bir araştırma projesidir; tıbbi cihaz değildir, tanı veya tedavi önerisi vermez.",
    sourceCode: "Kaynak kodu",
  },
  en: {
    headline: "Understand your lab results",
    tagline:
      "Upload your PDF report, see which values fall outside their range, and read a " +
      "plain-language explanation. Your file never leaves this computer.",
    localBadge: "Runs entirely on this machine",
    dropHere: "Drop your PDF report here, or click to choose one",
    fileHint: "PDF with selectable text, up to 10 MB",
    changeFile: "Click to change",
    trySample: "Try the sample report",
    sex: "Sex",
    female: "Female",
    male: "Male",
    age: "Age",
    submit: "Explain",
    working: "Working…",
    steps: [
      {
        title: "The report is read",
        text: "Test names, values and the reference ranges printed on the report are taken from the PDF.",
      },
      {
        title: "Rules decide",
        text: "Whether a value is low or high is decided by code, not by AI. For critical values the model never runs.",
      },
      {
        title: "The model explains",
        text: "A small language model running on this machine explains the results in plain words, grounded in vetted notes.",
      },
    ],
    results: "Results",
    nothingRecognised: "No known test was found in this report.",
    unrecognised: "Rows that were not recognised and are left out of the explanation",
    differentUnit: "Rows set aside because they are printed in a different unit",
    catalogRange:
      "Your report prints no range for this test. A general adult range was used; your " +
      "laboratory's range may differ with age or method.",
    explanation: "Explanation",
    model: "Model",
    columns: { test: "Test", result: "Result", range: "Within range", reference: "Reference", status: "Status" },
    flags: { LOW: "Low", NORMAL: "Normal", HIGH: "High" },
    critical: "Critical",
    unreachable: "The API cannot be reached. Make sure the server is running.",
    requestFailed: (status) => `The request failed (${status}).`,
    notADevice:
      "MedLocal is a research project. It is not a medical device and gives no diagnosis or treatment advice.",
    sourceCode: "Source code",
  },
};
