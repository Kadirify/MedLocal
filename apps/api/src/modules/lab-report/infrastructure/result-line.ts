import { ParsedRow } from '../application/ports.js';
import { ReferenceRange } from '../domain/reference-range.js';

const NUMBER = String.raw`\d+(?:[.,]\d+)?`;

const RANGE = String.raw`(?:(?<low>${NUMBER})\s*[-–]\s*(?<high>${NUMBER})|(?<sign>[<>≤≥])=?\s*(?<bound>${NUMBER}))`;

// "<label> <value> [H|L|*] [unit] [low - high | < high | > low]"
// A unit may start with a digit ("10^3/µL") but must not swallow a range printed without spaces.
const RESULT_LINE = new RegExp(
  String.raw`^(?<label>.+?)\s+(?<value>${NUMBER})(?:\s+[HL*])?` +
    String.raw`(?:\s+(?<unit>(?!${NUMBER}\s*[-–])\S+))?(?:\s+${RANGE})?\s*$`,
  'u',
);

export function parseResultLine(line: string): ParsedRow | null {
  const groups = RESULT_LINE.exec(line.trim())?.groups;
  if (!groups?.label || !groups.value) return null;

  return {
    label: groups.label,
    value: toNumber(groups.value),
    unit: groups.unit ?? null,
    printedRange: toRange(groups),
  };
}

function toRange(groups: Record<string, string | undefined>): ReferenceRange | null {
  if (groups.low && groups.high) {
    const low = toNumber(groups.low);
    const high = toNumber(groups.high);
    return low < high ? new ReferenceRange(low, high) : null;
  }
  if (!groups.bound) return null;

  const bound = toNumber(groups.bound);
  return groups.sign === '<' || groups.sign === '≤'
    ? new ReferenceRange(null, bound)
    : new ReferenceRange(bound, null);
}

function toNumber(text: string): number {
  return Number(text.replace(',', '.'));
}
