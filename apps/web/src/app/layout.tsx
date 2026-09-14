import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "MedLocal",
  description: "Explains lab results in plain language, on your own computer. Tahlil sonuçlarınızı kendi bilgisayarınızda açıklar.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="tr" className="h-full antialiased">
      <body className="min-h-full">{children}</body>
    </html>
  );
}
