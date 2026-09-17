"use client";

import type { ReactNode } from "react";
import { ChatIcon } from "@/components/icons";
import { SiteShell } from "@/components/site-shell";
import type { Language } from "@/i18n/language";
import type { ApiError } from "../api";
import { MESSAGES, type Messages } from "../messages";
import { useLabReport } from "../use-lab-report";
import { HowItWorks } from "./how-it-works";
import { ResultSummary } from "./result-summary";
import { ResultsTable } from "./results-table";
import { UploadForm } from "./upload-form";

export function LabReportScreen() {
  return <SiteShell>{(language) => <LabReportFlow language={language} />}</SiteShell>;
}

function LabReportFlow({ language }: { language: Language }) {
  const messages = MESSAGES[language];
  const { status, report, explanation, footer, error, submit } = useLabReport(language);
  const busy = status === "reading" || status === "explaining";

  return (
    <>
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
    </>
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
