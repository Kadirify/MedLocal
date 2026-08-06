import { ParsedRow } from '../application/ports.js';
import { ReferenceRange } from '../domain/reference-range.js';

const NUMBER = String.raw`\d+(?:[.,]\d+)?`;

// "<label> <value> [H|L|*] [unit] <low - high | < high | > low>"
const RESULT_LINE = new RegExp(
  String.raw`^(?<label>.+?)\s+(?<value>${NUMBER})(?:\s+[HL*])?(?:\s+(?<unit>\S+))?\s+` +
    String.raw`(?:(?<low>${NUMBER})\s*[-–]\s*(?<high>${NUMBER})|(?<sign>[<>≤≥])=?\s*(?<bound>${NUMBER}))\s*$`,
  'u',
);

export function parseResultLine(line: string): ParsedRow | null {
  const groups = RESULT_LINE.exec(line.trim())?.groups;
  if (!groups?.label || !groups.value) return null;

  return {
    label: groups.label,
    value: toNumber(groups.value),
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
