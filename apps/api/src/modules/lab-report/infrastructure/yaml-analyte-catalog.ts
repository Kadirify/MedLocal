import { readFileSync } from 'node:fs';
import { parse } from 'yaml';
import { z } from 'zod';
import { AnalyteCatalog } from '../application/ports.js';
import { Analyte } from '../domain/analyte.js';
import { ReferenceRange } from '../domain/reference-range.js';

const bound = z.number().nullable();
const rangeSchema = z.object({ low: bound, high: bound });

const analyteSchema = z.object({
  name: z.string(),
  unit: z.string(),
  decimals: z.number().int().nonnegative(),
  aliases: z.array(z.string()).default([]),
  ranges: z.object({
    any: rangeSchema.optional(),
    male: rangeSchema.optional(),
    female: rangeSchema.optional(),
  }),
  critical: z.object({ low: bound.default(null), high: bound.default(null) }).optional(),
});

const catalogSchema = z.object({ analytes: z.record(z.string(), analyteSchema) });

type RangeInput = z.infer<typeof rangeSchema> | undefined;

export class YamlAnalyteCatalog extends AnalyteCatalog {
  private readonly byKey = new Map<string, Analyte>();
  private readonly byLabel = new Map<string, Analyte>();

  constructor(file: string) {
    super();
    const { analytes } = catalogSchema.parse(parse(readFileSync(file, 'utf8')));

    for (const [key, entry] of Object.entries(analytes)) {
      const analyte = new Analyte(
        key,
        entry.name,
        entry.unit,
        entry.decimals,
        {
          any: toRange(entry.ranges.any),
          male: toRange(entry.ranges.male),
          female: toRange(entry.ranges.female),
        },
        entry.critical ?? { low: null, high: null },
      );
      this.byKey.set(key, analyte);
      for (const label of [entry.name, ...entry.aliases]) {
        this.byLabel.set(normalize(label), analyte);
      }
    }
  }

  findByKey(key: string): Analyte | undefined {
    return this.byKey.get(key);
  }

  findByLabel(label: string): Analyte | undefined {
    return this.byLabel.get(normalize(label));
  }
}

function toRange(input: RangeInput): ReferenceRange | undefined {
  return input ? new ReferenceRange(input.low, input.high) : undefined;
}

function normalize(label: string): string {
  return label.toLocaleLowerCase('tr').replace(/\s+/g, ' ').trim();
}
