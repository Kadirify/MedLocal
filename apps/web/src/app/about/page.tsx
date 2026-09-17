import type { Metadata } from "next";
import { AboutScreen } from "@/features/about/about-screen";

export const metadata: Metadata = {
  title: "About · Hakkında | MedLocal",
};

export default function About() {
  return <AboutScreen />;
}
