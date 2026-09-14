import type { Messages } from "../messages";
import type { Flag, LabResult } from "../types";

const FLAG_STYLE: Record<Flag, string> = {
  LOW: "bg-low/10 text-low",
  NORMAL: "bg-canvas text-muted",
  HIGH: "bg-high/10 text-high",
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
        <thead className="border-b border-line text-xs uppercase tracking-wide text-muted">
          <tr>
            <th className="py-2 pr-4 font-medium">{columns.test}</th>
            <th className="py-2 pr-4 text-right font-medium">{columns.result}</th>
            <th className="py-2 pr-4 font-medium">{columns.unit}</th>
            <th className="py-2 pr-4 font-medium">{columns.reference}</th>
            <th className="py-2 font-medium">{columns.status}</th>
          </tr>
        </thead>
        <tbody>
          {results.map((result) => (
            <tr key={result.analyte} className="border-b border-line/60 last:border-0">
              <td className="py-2 pr-4 font-medium">{result.name}</td>
              <td className="py-2 pr-4 text-right tabular-nums">
                {result.value.toFixed(result.decimals)}
              </td>
              <td className="py-2 pr-4 text-muted">{result.unit}</td>
              <td className="py-2 pr-4 tabular-nums text-muted">
                {describe(result)}
                {result.referenceSource === "catalog" && <sup className="ml-0.5 text-high">*</sup>}
              </td>
              <td className="py-2">
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
  return <span className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${style}`}>{label}</span>;
}

function describe({ low, high, decimals }: LabResult): string {
  if (low === null) return `≤ ${high?.toFixed(decimals)}`;
  if (high === null) return `≥ ${low.toFixed(decimals)}`;
  return `${low.toFixed(decimals)} – ${high.toFixed(decimals)}`;
}
