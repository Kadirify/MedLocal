import type { ExplanationFooter, LabReport, Sex } from "./types";

// "localhost" costs two seconds per request on Windows while IPv6 is tried first
const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:3001";

export class ApiError extends Error {}

export async function uploadLabReport(file: File, sex: Sex, age: number): Promise<LabReport> {
  const form = new FormData();
  form.set("file", file);
  form.set("sex", sex);
  form.set("age", String(age));

  const response = await request("/lab-reports", { method: "POST", body: form });
  return (await response.json()) as LabReport;
}

interface ExplanationHandlers {
  onText: (text: string) => void;
  onDone: (footer: ExplanationFooter) => void;
}

export async function streamExplanation(
  report: LabReport,
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
      results: report.results.map(({ analyte, value, low, high }) => ({ analyte, value, low, high })),
    }),
  });
  if (!response.body) throw new ApiError("the server sent an empty reply");

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
  if (name === "error") throw new ApiError(payload.message ?? "generation failed");
  if (name === "done") handlers.onDone(payload);
  else if (payload.text) handlers.onText(payload.text);
}

async function request(path: string, init: RequestInit): Promise<Response> {
  const response = await fetch(`${API_URL}${path}`, init).catch(() => {
    throw new ApiError("API'ye ulaşılamıyor. Sunucunun çalıştığından emin olun.");
  });
  if (response.ok) return response;

  const body = (await response.json().catch(() => null)) as { message?: string | string[] } | null;
  const message = Array.isArray(body?.message) ? body.message.join(", ") : body?.message;
  throw new ApiError(message ?? `İstek başarısız oldu (${response.status}).`);
}
