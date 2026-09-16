import type { LabResult } from "../types";

const MARKER: Record<LabResult["flag"], string> = {
  LOW: "bg-low",
  NORMAL: "bg-ok",
  HIGH: "bg-high",
};

/** Where a value sits relative to its reference range; the shaded band is the range itself. */
export function RangeBar({ result }: { result: LabResult }) {
  const { start, end, position } = layout(result);

  return (
    <div className="relative h-1.5 w-28 rounded-full bg-line" aria-hidden>
      <div
        className="absolute inset-y-0 rounded-full bg-ok/25"
        style={{ left: `${start}%`, width: `${end - start}%` }}
      />
      <div
        className={`absolute top-1/2 size-2.5 -translate-x-1/2 -translate-y-1/2 rounded-full ring-2 ring-surface ${
          result.critical ? "bg-critical" : MARKER[result.flag]
        }`}
        style={{ left: `${position}%` }}
      />
    </div>
  );
}

function layout({ low, high, value }: LabResult) {
  // the scale leaves room on the open side of a one-sided range and on both sides of a closed one
  const [min, max] =
    low !== null && high !== null
      ? [low - (high - low) / 2, high + (high - low) / 2]
      : high !== null
        ? [0, high * 1.5]
        : [(low ?? 0) / 2, (low ?? 0) * 2];

  const percent = (x: number) => Math.min(97, Math.max(3, ((x - min) / (max - min)) * 100));
  return {
    start: low === null ? 0 : percent(low),
    end: high === null ? 100 : percent(high),
    position: percent(value),
  };
}
