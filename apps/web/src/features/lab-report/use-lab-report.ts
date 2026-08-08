"use client";

import { useCallback, useRef, useState } from "react";
import { streamExplanation, uploadLabReport } from "./api";
import type { ExplanationFooter, LabReport, Sex } from "./types";

type Status = "idle" | "reading" | "explaining" | "done" | "failed";

interface State {
  status: Status;
  report: LabReport | null;
  explanation: string;
  footer: ExplanationFooter | null;
  error: string | null;
}

const INITIAL: State = { status: "idle", report: null, explanation: "", footer: null, error: null };

export function useLabReport() {
  const [state, setState] = useState<State>(INITIAL);
  const inFlight = useRef<AbortController | null>(null);

  const submit = useCallback(async (file: File, sex: Sex, age: number) => {
    inFlight.current?.abort();
    const controller = new AbortController();
    inFlight.current = controller;
    setState({ ...INITIAL, status: "reading" });

    try {
      const report = await uploadLabReport(file, sex, age);
      const explainable = report.results.length > 0 && !report.criticalMessage;
      setState({ ...INITIAL, report, status: explainable ? "explaining" : "done" });
      if (!explainable) return;

      await streamExplanation(
        report,
        {
          onText: (text) => setState((s) => ({ ...s, explanation: s.explanation + text })),
          onDone: (footer) => setState((s) => ({ ...s, footer, status: "done" })),
        },
        controller.signal,
      );
    } catch (error) {
      if (controller.signal.aborted) return;
      const message = error instanceof Error ? error.message : "Beklenmeyen bir hata oluştu.";
      setState((s) => ({ ...s, status: "failed", error: message }));
    }
  }, []);

  return { ...state, submit };
}
