import type { Flag, LabResult } from "../types";

const FLAG_LABEL: Record<Flag, string> = { LOW: "Düşük", NORMAL: "Normal", HIGH: "Yüksek" };
const FLAG_STYLE: Record<Flag, string> = {
  LOW: "bg-low/10 text-low",
  NORMAL: "bg-canvas text-muted",
  HIGH: "bg-high/10 text-high",
};

export function ResultsTable({ results }: { results: LabResult[] }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-sm">
        <thead className="border-b border-line text-xs uppercase tracking-wide text-muted">
          <tr>
            <th className="py-2 pr-4 font-medium">Tahlil</th>
            <th className="py-2 pr-4 text-right font-medium">Sonuç</th>
            <th className="py-2 pr-4 font-medium">Birim</th>
            <th className="py-2 pr-4 font-medium">Referans</th>
            <th className="py-2 font-medium">Durum</th>
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
              <td className="py-2 pr-4 tabular-nums text-muted">{describe(result)}</td>
              <td className="py-2">
                <Badge result={result} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function Badge({ result }: { result: LabResult }) {
  const style = result.critical ? "bg-critical text-white" : FLAG_STYLE[result.flag];
  const label = result.critical ? "Kritik" : FLAG_LABEL[result.flag];
  return <span className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${style}`}>{label}</span>;
}

function describe({ low, high, decimals }: LabResult): string {
  if (low === null) return `≤ ${high?.toFixed(decimals)}`;
  if (high === null) return `≥ ${low.toFixed(decimals)}`;
  return `${low.toFixed(decimals)} – ${high.toFixed(decimals)}`;
}
