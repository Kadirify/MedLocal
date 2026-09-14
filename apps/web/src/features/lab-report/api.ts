import type { Language } from "./messages";
import type { ExplanationFooter, LabReport, Sex } from "./types";

// same origin: next.config.ts proxies /api to the API server
const API_URL = "/api";

/** `serverMessage` is already in the reader's language; without one the caller words the failure. */
export class ApiError extends Error {
  constructor(
    readonly serverMessage: string | null,
    readonly status: number | null,
  ) {
    super(serverMessage ?? `request failed (${status ?? "unreachable"})`);
  }
}

export async function uploadLabReport(
  file: File,
  sex: Sex,
  age: number,
  language: Language,
): Promise<LabReport> {
  const form = new FormData();
  form.set("file", file);
  form.set("sex", sex);
  form.set("age", String(age));
  form.set("language", language);

  const response = await request("/lab-reports", { method: "POST", body: form });
  return (await response.json()) as LabReport;
}

interface ExplanationHandlers {
  onText: (text: string) => void;
  onDone: (footer: ExplanationFooter) => void;
}

export async function streamExplanation(
  report: LabReport,
  language: Language,
  handlers: ExplanationHandlers,
  signal: AbortSignal,
): Promise<void> {
  const response = await request("/lab-reports/explanation", {
    method: "POST",
    signal,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      sex: report.sex,
      age: report.age,
      language,
      results: report.results.map(({ analyte, value, low, high }) => ({ analyte, value, low, high })),
    }),
  });
  if (!response.body) throw new ApiError(null, response.status);

  const decoder = new TextDecoder();
  let pending = "";
  for await (const bytes of response.body as unknown as AsyncIterable<Uint8Array>) {
    pending += decoder.decode(bytes, { stream: true });
    const events = pending.split("\n\n");
    pending = events.pop() ?? "";
    events.forEach((event) => dispatch(event, handlers));
  }
}

function dispatch(event: string, handlers: ExplanationHandlers): void {
  const name = /^event: (.+)$/m.exec(event)?.[1] ?? "message";
  const data = /^data: (.+)$/m.exec(event)?.[1];
  if (!data) return;

  const payload = JSON.parse(data) as { text?: string; message?: string } & ExplanationFooter;
  if (name === "error") throw new ApiError(payload.message ?? null, null);
  if (name === "done") handlers.onDone(payload);
  else if (payload.text) handlers.onText(payload.text);
}

async function request(path: string, init: RequestInit): Promise<Response> {
  const response = await fetch(`${API_URL}${path}`, init).catch(() => {
    throw new ApiError(null, null);
  });
  if (response.ok) return response;

  const body = (await response.json().catch(() => null)) as { message?: string | string[] } | null;
  const message = Array.isArray(body?.message) ? body.message.join(", ") : body?.message;
  throw new ApiError(message ?? null, response.status);
}
