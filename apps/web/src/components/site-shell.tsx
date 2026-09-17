"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ReactNode } from "react";
import type { Language } from "@/i18n/language";
import { SITE_MESSAGES } from "@/i18n/site-messages";
import { useLanguage } from "@/i18n/use-language";
import { LogoMark, ShieldIcon } from "./icons";
import { LanguageSwitch } from "./language-switch";

const REPOSITORY = "https://github.com/Kadirify/MedLocal";

interface Props {
  children: (language: Language) => ReactNode;
}

export function SiteShell({ children }: Props) {
  const [language, chooseLanguage] = useLanguage();
  const messages = SITE_MESSAGES[language];
  const pathname = usePathname();

  const links = [
    { href: "/", label: messages.home },
    { href: "/about", label: messages.about },
  ];

  return (
    <div className="flex min-h-screen flex-col">
      <header className="border-b border-line/70 bg-surface/80 backdrop-blur">
        <div className="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-x-4 gap-y-2 px-4 py-3">
          <div className="flex items-center gap-6">
            <Link href="/" className="flex items-center gap-2.5">
              <LogoMark className="size-8 text-accent" />
              <span className="text-lg font-semibold tracking-tight">MedLocal</span>
            </Link>
            <nav className="flex gap-1 text-sm">
              {links.map(({ href, label }) => (
                <Link
                  key={href}
                  href={href}
                  aria-current={pathname === href ? "page" : undefined}
                  className={`rounded-md px-3 py-1.5 font-medium ${
                    pathname === href ? "bg-accent-soft text-accent" : "text-muted hover:text-ink"
                  }`}
                >
                  {label}
                </Link>
              ))}
            </nav>
          </div>
          <div className="flex items-center gap-3">
            <span className="hidden items-center gap-1.5 rounded-full bg-accent-soft px-3 py-1 text-xs font-medium text-accent md:flex">
              <ShieldIcon className="size-3.5" />
              {messages.localBadge}
            </span>
            <LanguageSwitch language={language} onChange={chooseLanguage} />
          </div>
        </div>
      </header>

      <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col gap-6 px-4 py-10">
        {children(language)}
      </main>

      <footer className="border-t border-line/70 px-4 py-5 text-center text-xs text-muted">
        <p>{messages.notADevice}</p>
        <a href={REPOSITORY} className="mt-1 inline-block underline underline-offset-4">
          {messages.sourceCode}
        </a>
      </footer>
    </div>
  );
}
