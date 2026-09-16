import type { Messages } from "../messages";
import type { LabResult } from "../types";

export function ResultSummary({ results, messages }: { results: LabResult[]; messages: Messages }) {
  const low = results.filter((result) => result.flag === "LOW").length;
  const high = results.filter((result) => result.flag === "HIGH").length;
  const normal = results.length - low - high;

  return (
    <dl className="grid grid-cols-3 gap-3">
      <Tile label={messages.flags.NORMAL} count={normal} tone="bg-ok-soft text-ok" />
      <Tile label={messages.flags.LOW} count={low} tone="bg-low-soft text-low" />
      <Tile label={messages.flags.HIGH} count={high} tone="bg-high-soft text-high" />
    </dl>
  );
}

function Tile({ label, count, tone }: { label: string; count: number; tone: string }) {
  return (
    <div className={`rounded-xl px-4 py-3 ${tone}`}>
      <dd className="text-2xl font-semibold tabular-nums">{count}</dd>
      <dt className="text-xs font-medium">{label}</dt>
    </div>
  );
}
