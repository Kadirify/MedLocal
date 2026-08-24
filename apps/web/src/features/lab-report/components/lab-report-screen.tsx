"use client";

import type { ReactNode } from "react";
import { useLabReport } from "../use-lab-report";
import { ResultsTable } from "./results-table";
import { UploadForm } from "./upload-form";

export function LabReportScreen() {
  const { status, report, explanation, footer, error, submit } = useLabReport();
  const busy = status === "reading" || status === "explaining";

  return (
    <main className="mx-auto flex max-w-4xl flex-col gap-6 px-4 py-10">
      <header>
        <h1 className="text-2xl font-semibold">MedLocal</h1>
        <p className="mt-1 text-sm text-muted">
          Tahlil sonuçlarınızı sade bir dille açıklar. Dosyanız bu bilgisayardan dışarı çıkmaz.
        </p>
      </header>

      <Card>
        <UploadForm busy={busy} onSubmit={submit} />
      </Card>

      {error && (
        <p role="alert" className="rounded-md border border-critical/30 bg-critical/5 p-4 text-sm">
          {error}
        </p>
      )}

      {report && (
        <Card title="Sonuçlar">
          {report.results.length > 0 ? (
            <ResultsTable results={report.results} />
          ) : (
            <p className="text-sm text-muted">Bu raporda tanınan bir tahlil bulunamadı.</p>
          )}
          {report.differentUnitLabels.length > 0 && (
            <p className="mt-4 text-xs text-muted">
              Farklı bir birimle basıldığı için değerlendirilmeyen satırlar:{" "}
              {report.differentUnitLabels.join(", ")}
            </p>
          )}
          {report.unrecognizedLabels.length > 0 && (
            <p className="mt-4 text-xs text-muted">
              Tanınmayan ve açıklamaya dahil edilmeyen satırlar:{" "}
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
        <Card title="Açıklama">
          <p className="whitespace-pre-line text-[15px] leading-7">
            {explanation}
            {status === "explaining" && <span className="animate-pulse text-accent"> ▍</span>}
          </p>
          {footer && (
            <footer className="mt-5 border-t border-line pt-3 text-xs text-muted">
              <p>{footer.disclaimer}</p>
              <p className="mt-1">Model: {footer.model}</p>
            </footer>
          )}
        </Card>
      )}
    </main>
  );
}

function Card({ title, children }: { title?: string; children: ReactNode }) {
  return (
    <section className="rounded-lg border border-line bg-surface p-5 shadow-sm">
      {title && <h2 className="mb-3 text-sm font-semibold text-muted">{title}</h2>}
      {children}
    </section>
  );
}
