import type { Language } from "./language";

export interface SiteMessages {
  home: string;
  about: string;
  localBadge: string;
  notADevice: string;
  sourceCode: string;
}

export const SITE_MESSAGES: Record<Language, SiteMessages> = {
  tr: {
    home: "Tahlil açıkla",
    about: "Hakkında",
    localBadge: "Tamamen yerel çalışır",
    notADevice:
      "MedLocal bir araştırma projesidir; tıbbi cihaz değildir, tanı veya tedavi önerisi vermez.",
    sourceCode: "Kaynak kodu",
  },
  en: {
    home: "Explain a report",
    about: "About",
    localBadge: "Runs entirely on this machine",
    notADevice:
      "MedLocal is a research project. It is not a medical device and gives no diagnosis or treatment advice.",
    sourceCode: "Source code",
  },
};
