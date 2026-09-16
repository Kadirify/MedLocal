import type { Messages } from "../messages";
import type { Flag, LabResult } from "../types";
import { RangeBar } from "./range-bar";

const FLAG_STYLE: Record<Flag, string> = {
  LOW: "bg-low-soft text-low",
  NORMAL: "bg-ok-soft text-ok",
  HIGH: "bg-high-soft text-high",
};

interface Props {
  results: LabResult[];
  messages: Messages;
}

export function ResultsTable({ results, messages }: Props) {
  const { columns } = messages;

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-sm">
        <thead className="text-xs uppercase tracking-wide text-muted">
          <tr className="border-b border-line">
            <th className="py-2.5 pr-4 font-medium">{columns.test}</th>
            <th className="py-2.5 pr-4 text-right font-medium">{columns.result}</th>
            <th className="hidden py-2.5 pr-4 font-medium sm:table-cell">{columns.range}</th>
            <th className="hidden py-2.5 pr-4 font-medium sm:table-cell">{columns.reference}</th>
            <th className="py-2.5 font-medium">{columns.status}</th>
          </tr>
        </thead>
        <tbody>
          {results.map((result) => (
            <tr
              key={result.analyte}
              className={`border-b border-line/60 last:border-0 ${
                result.flag === "NORMAL" ? "" : "bg-canvas/60"
              }`}
            >
              <td className="py-2.5 pr-3 font-medium">
                {result.name}
                <span className="block text-xs font-normal tabular-nums text-muted sm:hidden">
                  {describe(result)}
                  {result.referenceSource === "catalog" && <sup className="text-high">*</sup>}
                </span>
              </td>
              <td className="whitespace-nowrap py-2.5 pr-3 text-right tabular-nums">
                <span className="font-semibold">{result.value.toFixed(result.decimals)}</span>{" "}
                <span className="text-xs text-muted">{result.unit}</span>
              </td>
              <td className="hidden py-2.5 pr-4 sm:table-cell">
                <RangeBar result={result} />
              </td>
              <td className="hidden whitespace-nowrap py-2.5 pr-4 tabular-nums text-muted sm:table-cell">
                {describe(result)}
                {result.referenceSource === "catalog" && <sup className="ml-0.5 text-high">*</sup>}
              </td>
              <td className="py-2.5">
                <Badge result={result} messages={messages} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {results.some((result) => result.referenceSource === "catalog") && (
        <p className="mt-3 text-xs text-muted">
          <span className="text-high">*</span> {messages.catalogRange}
        </p>
      )}
    </div>
  );
}

function Badge({ result, messages }: { result: LabResult; messages: Messages }) {
  const style = result.critical ? "bg-critical text-white" : FLAG_STYLE[result.flag];
  const label = result.critical ? messages.critical : messages.flags[result.flag];
  return (
    <span className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-semibold ${style}`}>
      {label}
    </span>
  );
}

function describe({ low, high, decimals }: LabResult): string {
  if (low === null) return `≤ ${high?.toFixed(decimals)}`;
  if (high === null) return `≥ ${low.toFixed(decimals)}`;
  return `${low.toFixed(decimals)} – ${high.toFixed(decimals)}`;
}
