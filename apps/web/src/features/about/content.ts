import type { Language } from "@/i18n/language";

interface Section {
  title: string;
  paragraphs: string[];
}

interface Fact {
  value: string;
  label: string;
}

interface Question {
  question: string;
  answer: string;
}

export interface AboutContent {
  eyebrow: string;
  headline: string;
  lead: string;
  purpose: Section;
  audience: { title: string; items: string[] };
  principles: { title: string; items: { title: string; text: string }[] };
  privacy: Section;
  model: { title: string; lead: string; facts: Fact[]; note: string };
  limits: { title: string; items: string[] };
  questions: { title: string; items: Question[] };
  callToAction: string;
}

export const ABOUT: Record<Language, AboutContent> = {
  tr: {
    eyebrow: "Hakkında",
    headline: "Tahlil raporlarını hızla değerlendirin, hasta verisini dışarı çıkarmadan",
    lead:
      "MedLocal, laboratuvar raporundaki değerleri okuyan, aralık dışı sonuçları işaretleyen ve " +
      "hasta bilgilendirmesi için hazır bir özet üreten açık kaynaklı bir klinik destek aracıdır. " +
      "Her şey kendi bilgisayarınızda çalışır.",
    purpose: {
      title: "Neden var?",
      paragraphs: [
        "Yoğun poliklinik saatlerinde bir doktor onlarca tahlil raporunu değerlendirmek zorundadır. " +
          "Her raporun tek tek incelenmesi, aralık dışı değerlerin bulunması ve hastaya anlaşılır " +
          "şekilde aktarılması zaman alır.",
        "MedLocal bu süreci hızlandırır: rapordan değerleri otomatik okur, aralık dışı olanları " +
          "kod ile belirler ve hastaya aktarılabilecek sade bir özet oluşturur. Doktorun klinik " +
          "kararını almaz; ön değerlendirme ve hasta iletişimi için zaman kazandırır.",
        "Sağlık verisi en hassas kişisel veridir. Bu yüzden proje baştan "bulutsuz" tasarlandı: " +
          "hasta raporu hiçbir sunucuya gönderilmez.",
      ],
    },
    audience: {
      title: "Kimler için?",
      items: [
        "Yoğun poliklinikte tahlil sonuçlarını hızla değerlendirmek isteyen hekimler",
        "Hasta verisini dışarı çıkaramayan klinikler ve sağlık kuruluşları",
        "Hasta bilgilendirme sürecini kolaylaştırmak isteyen aile hekimleri",
        "Yerel dil modeli eğitmeyi ve sağlık alanında uygulamayı görmek isteyen geliştiriciler",
      ],
    },
    principles: {
      title: "Üç tasarım ilkesi",
      items: [
        {
          title: "Sayıya model karar vermez",
          text: "Bir değerin düşük, normal ya da yüksek olduğuna kod karar verir; önce raporda basılı aralığa, o yoksa kataloğa bakar. Dil modeli yalnızca sonucu söze döker.",
        },
        {
          title: "Kritik değerler modele gitmez",
          text: "Beklenen aralığın çok dışındaki bir değer için sabit bir uyarı mesajı gösterilir; yapay zekâ hiç çalıştırılmaz.",
        },
        {
          title: "Bilgi ezberden değil, kaynaktan gelir",
          text: "Model her bayraklı sonuç için katalogdaki doğrulanmış notu görür ve onu sade dille anlatır. Tanımadığı satırları tahmin etmez, açıkça listeler.",
        },
      ],
    },
    privacy: {
      title: "Gizlilik ve veri güvenliği",
      paragraphs: [
        "PDF dosyası bu bilgisayardaki API tarafından bellekte işlenir, diske yazılmaz ve kayıtlara geçmez. " +
          "Dil modeli de aynı bilgisayarda, Ollama üzerinde çalışır. Hasta verisi hiçbir dış sunucuya iletilmez.",
        "Sayfa hiçbir dış kaynaktan font, ikon ya da analiz betiği yüklemez. İnternet bağlantısı olmadan da " +
          "çalışır; bu sayede kapalı ağlardaki kliniklerde bile kullanılabilir.",
      ],
    },
    model: {
      title: "Model nasıl eğitildi?",
      lead:
        "Tahlil raporu ile sade dilde açıklama içeren hazır bir veri seti yoktur. Bu yüzden veri yerelde üretildi: " +
        "58 tahlillik iki dilli bir katalogdan sentetik raporlar çıkarıldı, daha büyük bir yerel model açıklamaları yazdı, " +
        "on bir güvenlik kuralından geçemeyenler elendi. Küçük model bu veriyle tek bir tüketici ekran kartında eğitildi.",
      facts: [
        { value: "4B", label: "parametreli taban model (Qwen3)" },
        { value: "2.556", label: "sentetik eğitim ve test örneği, yarısı Türkçe" },
        { value: "%20 → %92", label: "tüm kurallara uyan Türkçe açıklama oranı" },
        { value: "≈ 80 dk", label: "eğitim süresi, 12 GB ekran kartında" },
      ],
      note:
        "Bu oranlar sentetik raporlarda kurallara uyumu ölçer, tıbbi doğruluğu değil. Gerçek bir raporda bulunan bir " +
        "bilgi hatası, modelin bilgiyi hatırlamak yerine katalogdan okumasına geçilmesinin sebebidir.",
    },
    limits: {
      title: "Ne yapmaz?",
      items: [
        "Tanı koymaz, tedavi ya da ilaç önermez — klinik karar her zaman hekimindir.",
        "Tıbbi cihaz değildir; hiçbir çıktısı klinik validasyondan geçmemiştir.",
        "Taranmış ya da fotoğrafı çekilmiş raporları okuyamaz; PDF seçilebilir metin içermelidir.",
        "Katalogdaki referans aralıkları genel yetişkin değerleridir; laboratuvarınızın aralığı her zaman önceliklidir.",
        "Türkçe açıklamalarda zaman zaman tutuk ifadeler görülebilir.",
      ],
    },
    questions: {
      title: "Sık sorulanlar",
      items: [
        {
          question: "Hasta raporu bir yere gönderiliyor mu?",
          answer: "Hayır. Dosya yalnızca bu bilgisayardaki API'ye gider; oradan da aynı bilgisayardaki modele. Hiçbir veri dışarı çıkmaz.",
        },
        {
          question: "Üretilen açıklamayı doğrudan hastaya verebilir miyim?",
          answer:
            "Açıklama bir ön taslak niteliğindedir. Son kararı veren hekimdir; " +
            "açıklamayı kendi klinik değerlendirmenizle birlikte kullanmanız önerilir.",
        },
        {
          question: "Bazı satırlar neden "tanınmayan" olarak listeleniyor?",
          answer:
            "Katalogda olmayan bir tahlili tahmin etmek yerine açıkça belirtmeyi tercih ediyoruz. Katalog zamanla genişletilebilir.",
        },
        {
          question: "Kliniğimize kurabilir miyiz?",
          answer: "Evet. Kaynak kodu açıktır; kurulum adımları depodaki README dosyasındadır. İnternet bağlantısı gerektirmez.",
        },
      ],
    },
    callToAction: "Bir raporla deneyin",
  },
  en: {
    eyebrow: "About",
    headline: "Review lab reports faster, without patient data leaving the building",
    lead:
      "MedLocal is an open-source clinical support tool that reads a laboratory report, flags " +
      "out-of-range values, and produces a plain-language summary ready for patient communication. " +
      "Everything runs on your own machine.",
    purpose: {
      title: "Why it exists",
      paragraphs: [
        "In a busy outpatient clinic a physician reviews dozens of lab reports each day. " +
          "Scanning each one for out-of-range values and explaining them to patients in plain language takes time.",
        "MedLocal speeds up that workflow: it reads values from the PDF automatically, flags abnormal " +
          "results with deterministic code, and drafts a patient-friendly summary. It does not make " +
          "clinical decisions; it saves time on preliminary review and patient communication.",
        "Health data is the most sensitive personal data there is. That is why the project was designed " +
          "without a cloud from the start: patient reports are never sent to a server.",
      ],
    },
    audience: {
      title: "Who it is for",
      items: [
        "Physicians who need to review lab results quickly during busy clinic hours",
        "Clinics and healthcare facilities that cannot let patient data leave the network",
        "Primary care doctors looking to streamline patient communication",
        "Developers who want to see a local language model trained and deployed in healthcare",
      ],
    },
    principles: {
      title: "Three design principles",
      items: [
        {
          title: "The model never judges a number",
          text: "Whether a value is low, normal or high is decided by code, from the range printed on the report or, failing that, the catalog. The language model only puts the result into words.",
        },
        {
          title: "Critical values bypass the model",
          text: "A value far outside the expected range gets a fixed alert message. The AI is not run at all.",
        },
        {
          title: "Knowledge comes from a source, not from memory",
          text: "For every flagged result the model is shown the catalog's vetted note and restates it plainly. Rows it does not know are listed openly instead of being guessed.",
        },
      ],
    },
    privacy: {
      title: "Privacy and data security",
      paragraphs: [
        "The PDF is processed in memory by the API on this computer. It is not written to disk and not logged. " +
          "The language model runs on the same machine, through Ollama. No patient data is transmitted externally.",
        "The page loads no fonts, icons or analytics scripts from anywhere else. It works without an internet " +
          "connection, making it suitable for air-gapped clinic networks.",
      ],
    },
    model: {
      title: "How the model was trained",
      lead:
        "There is no public dataset of lab reports paired with plain-language explanations, so the data was built locally: " +
        "synthetic reports were drawn from a bilingual catalog of 58 tests, a larger local model wrote the explanations, and " +
        "those failing any of eleven safety rules were discarded. The small model was then trained on a single consumer GPU.",
      facts: [
        { value: "4B", label: "parameter base model (Qwen3)" },
        { value: "2,556", label: "synthetic training and test examples, half in Turkish" },
        { value: "64% → 89%", label: "English explanations passing every rule" },
        { value: "≈ 80 min", label: "of training on a 12 GB graphics card" },
      ],
      note:
        "These percentages measure rule compliance on synthetic reports, not medical accuracy. A factual error found on a " +
        "real report is the reason the model now reads its knowledge from the catalog instead of recalling it.",
    },
    limits: {
      title: "What it does not do",
      items: [
        "It does not diagnose, recommend treatment or medicine — the clinical decision is always yours.",
        "It is not a medical device, and none of its output has been clinically validated.",
        "It cannot read scanned or photographed reports; the PDF has to contain selectable text.",
        "The catalog's reference ranges are general adult values; your laboratory's range always takes precedence.",
        "Turkish explanations occasionally contain stiff phrasing.",
      ],
    },
    questions: {
      title: "Common questions",
      items: [
        {
          question: "Is patient data sent anywhere?",
          answer: "No. The file goes only to the API on this computer, and from there to the model on the same machine. Nothing leaves the network.",
        },
        {
          question: "Can I give the summary directly to a patient?",
          answer:
            "The summary is a draft. The final call is the physician's; it is meant to be used " +
            "alongside your own clinical assessment.",
        },
        {
          question: "Why are some rows listed as not recognised?",
          answer:
            "We prefer to say openly that a test is not in the catalog rather than guess at it. The catalog can grow over time.",
        },
        {
          question: "Can we deploy it in our clinic?",
          answer: "Yes. The source code is open, and the setup steps are in the repository's README. No internet connection is required.",
        },
      ],
    },
    callToAction: "Try it with a report",
  },
};
