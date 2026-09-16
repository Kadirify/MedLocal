"use client";

import type { ReactNode } from "react";
import type { ApiError } from "../api";
import { MESSAGES, type Messages } from "../messages";
import { useLabReport } from "../use-lab-report";
import { useLanguage } from "../use-language";
import { HowItWorks } from "./how-it-works";
import { ChatIcon, LogoMark, ShieldIcon } from "./icons";
import { LanguageSwitch } from "./language-switch";
import { ResultSummary } from "./result-summary";
import { ResultsTable } from "./results-table";
import { UploadForm } from "./upload-form";

const REPOSITORY = "https://github.com/Kadirify/MedLocal";

export function LabReportScreen() {
  const [language, chooseLanguage] = useLanguage();
  const messages = MESSAGES[language];
  const { status, report, explanation, footer, error, submit } = useLabReport(language);
  const busy = status === "reading" || status === "explaining";

  return (
    <div className="flex min-h-screen flex-col">
      <header className="border-b border-line/70 bg-surface/80 backdrop-blur">
        <div className="mx-auto flex max-w-5xl items-center justify-between gap-4 px-4 py-3">
          <div className="flex items-center gap-2.5">
            <LogoMark className="size-8 text-accent" />
            <span className="text-lg font-semibold tracking-tight">MedLocal</span>
          </div>
          <div className="flex items-center gap-3">
            <span className="hidden items-center gap-1.5 rounded-full bg-accent-soft px-3 py-1 text-xs font-medium text-accent sm:flex">
              <ShieldIcon className="size-3.5" />
              {messages.localBadge}
            </span>
            <LanguageSwitch language={language} onChange={chooseLanguage} />
          </div>
        </div>
      </header>

      <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col gap-6 px-4 py-10">
        <section className="max-w-2xl">
          <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">{messages.headline}</h1>
          <p className="mt-3 text-base leading-7 text-muted">{messages.tagline}</p>
        </section>

        <Card>
          <UploadForm busy={busy} messages={messages} onSubmit={submit} />
        </Card>

        {status === "idle" && <HowItWorks messages={messages} />}

        {error && (
          <p role="alert" className="rise rounded-xl border border-critical/30 bg-critical/5 p-4 text-sm">
            {describe(error, messages)}
          </p>
        )}

        {status === "reading" && <Skeleton />}

        {report && (
          <Card title={messages.results} className="rise">
            {report.results.length > 0 ? (
              <div className="flex flex-col gap-5">
                <ResultSummary results={report.results} messages={messages} />
                <ResultsTable results={report.results} messages={messages} />
              </div>
            ) : (
              <p className="text-sm text-muted">{messages.nothingRecognised}</p>
            )}
            {report.differentUnitLabels.length > 0 && (
              <Note label={messages.differentUnit} items={report.differentUnitLabels} />
            )}
            {report.unrecognizedLabels.length > 0 && (
              <Note label={messages.unrecognised} items={report.unrecognizedLabels} />
            )}
          </Card>
        )}

        {report?.criticalMessage && (
          <p role="alert" className="rise rounded-xl bg-critical p-5 text-sm font-medium leading-6 text-white">
            {report.criticalMessage}
          </p>
        )}

        {(explanation || status === "explaining") && (
          <Card
            title={messages.explanation}
            icon={<ChatIcon className="size-4 text-accent" />}
            className="rise"
          >
            <p className="whitespace-pre-line text-[15px] leading-7">
              {explanation}
              {status === "explaining" && <span className="animate-pulse text-accent"> ▍</span>}
            </p>
            {footer && (
              <footer className="mt-5 rounded-lg bg-canvas p-3 text-xs leading-5 text-muted">
                <p>{footer.disclaimer}</p>
                <p className="mt-1 font-mono text-[11px]">
                  {messages.model}: {footer.model}
                </p>
              </footer>
            )}
          </Card>
        )}
      </main>

      <footer className="border-t border-line/70 py-5 text-center text-xs text-muted">
        <p>{messages.notADevice}</p>
        <a href={REPOSITORY} className="mt-1 inline-block underline underline-offset-4">
          {messages.sourceCode}
        </a>
      </footer>
    </div>
  );
}

function describe(error: ApiError, messages: Messages): string {
  if (error.serverMessage) return error.serverMessage;
  return error.status === null ? messages.unreachable : messages.requestFailed(error.status);
}

interface CardProps {
  title?: string;
  icon?: ReactNode;
  className?: string;
  children: ReactNode;
}

function Card({ title, icon, className = "", children }: CardProps) {
  return (
    <section className={`rounded-2xl border border-line bg-surface p-5 shadow-card sm:p-6 ${className}`}>
      {title && (
        <h2 className="mb-4 flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-muted">
          {icon}
          {title}
        </h2>
      )}
      {children}
    </section>
  );
}

function Note({ label, items }: { label: string; items: string[] }) {
  return (
    <details className="mt-4 text-xs text-muted">
      <summary className="cursor-pointer select-none">
        {label} ({items.length})
      </summary>
      <p className="mt-2 leading-5">{items.join(", ")}</p>
    </details>
  );
}

function Skeleton() {
  return (
    <div className="animate-pulse rounded-2xl border border-line bg-surface p-6" aria-hidden>
      <div className="h-3 w-24 rounded bg-line" />
      <div className="mt-5 grid grid-cols-3 gap-3">
        <div className="h-16 rounded-xl bg-canvas" />
        <div className="h-16 rounded-xl bg-canvas" />
        <div className="h-16 rounded-xl bg-canvas" />
      </div>
      <div className="mt-5 space-y-3">
        <div className="h-3 rounded bg-canvas" />
        <div className="h-3 w-5/6 rounded bg-canvas" />
        <div className="h-3 w-2/3 rounded bg-canvas" />
      </div>
    </div>
  );
}
