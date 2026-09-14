"use client";

import type { ReactNode } from "react";
import type { ApiError } from "../api";
import { MESSAGES, type Messages } from "../messages";
import { useLabReport } from "../use-lab-report";
import { useLanguage } from "../use-language";
import { LanguageSwitch } from "./language-switch";
import { ResultsTable } from "./results-table";
import { UploadForm } from "./upload-form";

export function LabReportScreen() {
  const [language, chooseLanguage] = useLanguage();
  const messages = MESSAGES[language];
  const { status, report, explanation, footer, error, submit } = useLabReport(language);
  const busy = status === "reading" || status === "explaining";

  return (
    <main className="mx-auto flex max-w-4xl flex-col gap-6 px-4 py-10">
      <header className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold">MedLocal</h1>
          <p className="mt-1 text-sm text-muted">{messages.tagline}</p>
        </div>
        <LanguageSwitch language={language} onChange={chooseLanguage} />
      </header>

      <Card>
        <UploadForm busy={busy} messages={messages} onSubmit={submit} />
      </Card>

      {error && (
        <p role="alert" className="rounded-md border border-critical/30 bg-critical/5 p-4 text-sm">
          {describe(error, messages)}
        </p>
      )}

      {report && (
        <Card title={messages.results}>
          {report.results.length > 0 ? (
            <ResultsTable results={report.results} messages={messages} />
          ) : (
            <p className="text-sm text-muted">{messages.nothingRecognised}</p>
          )}
          {report.differentUnitLabels.length > 0 && (
            <p className="mt-4 text-xs text-muted">
              {messages.differentUnit}
              {report.differentUnitLabels.join(", ")}
            </p>
          )}
          {report.unrecognizedLabels.length > 0 && (
            <p className="mt-4 text-xs text-muted">
              {messages.unrecognised}
              {report.unrecognizedLabels.join(", ")}
            </p>
          )}
        </Card>
      )}

      {report?.criticalMessage && (
        <p role="alert" className="rounded-md bg-critical p-4 text-sm font-medium text-white">
          {report.criticalMessage}
        </p>
      )}

      {(explanation || status === "explaining") && (
        <Card title={messages.explanation}>
          <p className="whitespace-pre-line text-[15px] leading-7">
            {explanation}
            {status === "explaining" && <span className="animate-pulse text-accent"> ▍</span>}
          </p>
          {footer && (
            <footer className="mt-5 border-t border-line pt-3 text-xs text-muted">
              <p>{footer.disclaimer}</p>
              <p className="mt-1">
                {messages.model}: {footer.model}
              </p>
            </footer>
          )}
        </Card>
      )}
    </main>
  );
}

function describe(error: ApiError, messages: Messages): string {
  if (error.serverMessage) return error.serverMessage;
  return error.status === null ? messages.unreachable : messages.requestFailed(error.status);
}

function Card({ title, children }: { title?: string; children: ReactNode }) {
  return (
    <section className="rounded-lg border border-line bg-surface p-5 shadow-sm">
      {title && <h2 className="mb-3 text-sm font-semibold text-muted">{title}</h2>}
      {children}
    </section>
  );
}
