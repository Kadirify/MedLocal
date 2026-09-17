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
    headline: "Tahlil kâğıdını anlaşılır kılmak, veriyi evden çıkarmadan",
    lead:
      "MedLocal, laboratuvar raporunuzdaki değerleri okuyan, hangilerinin aralık dışında olduğunu " +
      "gösteren ve bunları sade bir Türkçeyle açıklayan açık kaynaklı bir projedir. Her şey kendi " +
      "bilgisayarınızda çalışır.",
    purpose: {
      title: "Neden var?",
      paragraphs: [
        "Tahlil sonucunu alan çoğu kişi bir sayı listesiyle baş başa kalır: “Ferritin 8, MCV 74, LDL 131.” " +
          "Doktor randevusu günler sonradır; arada internette yapılan aramalar çoğu zaman gereksiz kaygı üretir.",
        "MedLocal bu boşluğu doldurmayı amaçlar: tanı koymadan, ilaç önermeden, yalnızca “bu test neyi ölçer, " +
          "bu yöndeki bir sonuç genel olarak nelerle ilişkili olabilir” sorusunu yanıtlar. Amaç doktorun yerini " +
          "almak değil, doktora daha hazırlıklı gitmenizi sağlamaktır.",
        "Sağlık verisi en hassas kişisel veridir. Bu yüzden proje baştan “bulutsuz” tasarlandı: raporunuz " +
          "hiçbir sunucuya gönderilmez.",
      ],
    },
    audience: {
      title: "Kimler için?",
      items: [
        "Tahlil sonucunu doktor görüşmesinden önce anlamak isteyen herkes",
        "Hasta verisini dışarı çıkaramayan klinikler ve araştırmacılar için bir başlangıç noktası",
        "Yerel dil modeli eğitmeyi ve ürünleştirmeyi uçtan uca görmek isteyen geliştiriciler",
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
          text: "Beklenen aralığın çok dışındaki bir değer için sabit bir “hemen doktorunuza başvurun” mesajı gösterilir; yapay zekâ hiç çalıştırılmaz.",
        },
        {
          title: "Bilgi ezberden değil, kaynaktan gelir",
          text: "Model her bayraklı sonuç için katalogdaki doğrulanmış notu görür ve onu sade dille anlatır. Tanımadığı satırları tahmin etmez, açıkça listeler.",
        },
      ],
    },
    privacy: {
      title: "Gizlilik",
      paragraphs: [
        "PDF dosyanız bu bilgisayardaki API tarafından bellekte işlenir, diske yazılmaz ve kayıtlara geçmez. " +
          "Dil modeli de aynı bilgisayarda, Ollama üzerinde çalışır.",
        "Sayfa hiçbir dış kaynaktan font, ikon ya da analiz betiği yüklemez. İnternet bağlantınızı kapatıp " +
          "deneyebilirsiniz; uygulama çalışmaya devam eder.",
      ],
    },
    model: {
      title: "Model nasıl eğitildi?",
      lead:
        "Tahlil raporu ile hasta diliyle açıklama içeren hazır bir veri seti yoktur. Bu yüzden veri yerelde üretildi: " +
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
        "Tanı koymaz, tedavi ya da ilaç önermez, genel sağlık durumunuz hakkında hüküm vermez.",
        "Tıbbi cihaz değildir; hiçbir çıktısı bir hekim tarafından gözden geçirilmemiştir.",
        "Taranmış ya da fotoğrafı çekilmiş raporları okuyamaz; PDF seçilebilir metin içermelidir.",
        "Katalogdaki referans aralıkları genel yetişkin değerleridir; laboratuvarınızın aralığı her zaman önceliklidir.",
        "Türkçe açıklamalarda zaman zaman tutuk ifadeler görülebilir.",
      ],
    },
    questions: {
      title: "Sık sorulanlar",
      items: [
        {
          question: "Raporum bir yere gönderiliyor mu?",
          answer: "Hayır. Dosya yalnızca bu bilgisayardaki API'ye gider; oradan da aynı bilgisayardaki modele.",
        },
        {
          question: "Açıklamaya güvenebilir miyim?",
          answer:
            "Açıklama, doktorunuzla konuşmanıza hazırlık içindir. Bir değerin sizin için ne anlama geldiğine yalnızca " +
            "sizi tanıyan bir hekim karar verebilir.",
        },
        {
          question: "Bazı satırlar neden “tanınmayan” olarak listeleniyor?",
          answer:
            "Katalogda olmayan bir tahlili tahmin etmek yerine açıkça belirtmeyi tercih ediyoruz. Katalog zamanla genişletilebilir.",
        },
        {
          question: "Kendi bilgisayarıma kurabilir miyim?",
          answer: "Evet. Kaynak kodu açıktır; kurulum adımları depodaki README dosyasındadır.",
        },
      ],
    },
    callToAction: "Bir raporla deneyin",
  },
  en: {
    eyebrow: "About",
    headline: "Making a lab report readable, without the data leaving home",
    lead:
      "MedLocal is an open-source project that reads the values on your laboratory report, shows which " +
      "fall outside their range, and explains them in plain language. Everything runs on your own computer.",
    purpose: {
      title: "Why it exists",
      paragraphs: [
        "Most people who receive lab results are left alone with a list of numbers: “Ferritin 8, MCV 74, LDL 131.” " +
          "The doctor's appointment is days away, and searching the internet in between mostly produces needless worry.",
        "MedLocal aims to fill that gap. Without diagnosing and without recommending medicine, it answers one question: " +
          "what does this test measure, and what can a result in this direction be associated with in general? " +
          "The goal is not to replace the doctor but to help you arrive better prepared.",
        "Health data is the most sensitive personal data there is. That is why the project was designed without a cloud " +
          "from the start: your report is never sent to a server.",
      ],
    },
    audience: {
      title: "Who it is for",
      items: [
        "Anyone who wants to understand their results before seeing a doctor",
        "A starting point for clinics and researchers who cannot let patient data leave the building",
        "Developers who want to see a local language model trained and shipped end to end",
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
          text: "A value far outside the expected range gets a fixed “contact your doctor now” message. The AI is not run at all.",
        },
        {
          title: "Knowledge comes from a source, not from memory",
          text: "For every flagged result the model is shown the catalog's vetted note and restates it plainly. Rows it does not know are listed openly instead of being guessed.",
        },
      ],
    },
    privacy: {
      title: "Privacy",
      paragraphs: [
        "Your PDF is processed in memory by the API on this computer. It is not written to disk and not logged. " +
          "The language model runs on the same machine, through Ollama.",
        "The page loads no fonts, icons or analytics scripts from anywhere else. You can switch off your internet " +
          "connection and the app keeps working.",
      ],
    },
    model: {
      title: "How the model was trained",
      lead:
        "There is no public dataset of lab reports paired with patient-friendly explanations, so the data was built locally: " +
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
        "It does not diagnose, recommend treatment or medicine, or pass a verdict on your overall health.",
        "It is not a medical device, and none of its output has been reviewed by a clinician.",
        "It cannot read scanned or photographed reports; the PDF has to contain selectable text.",
        "The catalog's reference ranges are general adult values; your laboratory's range always takes precedence.",
        "Turkish explanations occasionally contain stiff phrasing.",
      ],
    },
    questions: {
      title: "Common questions",
      items: [
        {
          question: "Is my report sent anywhere?",
          answer: "No. The file goes only to the API on this computer, and from there to the model on the same machine.",
        },
        {
          question: "Can I rely on the explanation?",
          answer:
            "It is meant to prepare you for a conversation with your doctor. Only a clinician who knows you can decide what a value means for you.",
        },
        {
          question: "Why are some rows listed as not recognised?",
          answer:
            "We prefer to say openly that a test is not in the catalog rather than guess at it. The catalog can grow over time.",
        },
        {
          question: "Can I run it on my own computer?",
          answer: "Yes. The source code is open, and the setup steps are in the repository's README.",
        },
      ],
    },
    callToAction: "Try it with a report",
  },
};
