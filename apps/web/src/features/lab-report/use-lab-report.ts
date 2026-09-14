"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { ApiError, streamExplanation, uploadLabReport } from "./api";
import type { Language } from "./messages";
import type { ExplanationFooter, LabReport, Sex } from "./types";

type Status = "idle" | "reading" | "explaining" | "done" | "failed";

interface Submission {
  file: File;
  sex: Sex;
  age: number;
}

interface State {
  status: Status;
  report: LabReport | null;
  explanation: string;
  footer: ExplanationFooter | null;
  error: ApiError | null;
}

const INITIAL: State = { status: "idle", report: null, explanation: "", footer: null, error: null };

export function useLabReport(language: Language) {
  const [state, setState] = useState<State>(INITIAL);
  const inFlight = useRef<AbortController | null>(null);
  const last = useRef<Submission | null>(null);

  const run = useCallback(async ({ file, sex, age }: Submission, language: Language) => {
    inFlight.current?.abort();
    const controller = new AbortController();
    inFlight.current = controller;
    setState({ ...INITIAL, status: "reading" });

    try {
      const report = await uploadLabReport(file, sex, age, language);
      const explainable = report.results.length > 0 && !report.criticalMessage;
      setState({ ...INITIAL, report, status: explainable ? "explaining" : "done" });
      if (!explainable) return;

      await streamExplanation(
        report,
        language,
        {
          onText: (text) => setState((s) => ({ ...s, explanation: s.explanation + text })),
          onDone: (footer) => setState((s) => ({ ...s, footer, status: "done" })),
        },
        controller.signal,
      );
    } catch (error) {
      if (controller.signal.aborted) return;
      const failure = error instanceof ApiError ? error : new ApiError(null, null);
      setState((s) => ({ ...s, status: "failed", error: failure }));
    }
  }, []);

  const submit = useCallback(
    (file: File, sex: Sex, age: number) => {
      last.current = { file, sex, age };
      void run(last.current, language);
    },
    [run, language],
  );

  // names, fixed messages and the explanation all come from the API in one language,
  // so a report that is on screen is read again when the reader switches
  const shownIn = useRef(language);
  useEffect(() => {
    if (shownIn.current === language) return;
    shownIn.current = language;
    if (last.current) void run(last.current, language);
  }, [language, run]);

  return { ...state, submit };
}
