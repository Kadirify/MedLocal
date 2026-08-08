import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "MedLocal",
  description: "Tahlil sonuçlarınızı kendi bilgisayarınızda, sade bir dille açıklar.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="tr" className="h-full antialiased">
      <body className="min-h-full">{children}</body>
    </html>
  );
}
