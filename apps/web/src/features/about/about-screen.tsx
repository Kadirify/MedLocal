"use client";

import Link from "next/link";
import type { ReactNode } from "react";
import { SiteShell } from "@/components/site-shell";
import { ABOUT } from "./content";

export function AboutScreen() {
  return (
    <SiteShell>
      {(language) => {
        const about = ABOUT[language];
        return (
          <article className="mx-auto flex w-full max-w-3xl flex-col gap-12">
            <header>
              <p className="text-sm font-semibold uppercase tracking-wide text-accent">
                {about.eyebrow}
              </p>
              <h1 className="mt-2 text-3xl font-semibold tracking-tight sm:text-4xl">
                {about.headline}
              </h1>
              <p className="mt-4 text-lg leading-8 text-muted">{about.lead}</p>
            </header>

            <Block title={about.purpose.title}>
              {about.purpose.paragraphs.map((paragraph) => (
                <p key={paragraph}>{paragraph}</p>
              ))}
            </Block>

            <Block title={about.audience.title}>
              <List items={about.audience.items} />
            </Block>

            <Block title={about.principles.title}>
              <ol className="grid gap-4 sm:grid-cols-3">
                {about.principles.items.map((item, index) => (
                  <li key={item.title} className="rounded-xl border border-line bg-surface p-4 shadow-card">
                    <span className="text-xs font-semibold text-accent">0{index + 1}</span>
                    <h3 className="mt-1 text-sm font-semibold text-ink">{item.title}</h3>
                    <p className="mt-2 text-sm leading-6">{item.text}</p>
                  </li>
                ))}
              </ol>
            </Block>

            <Block title={about.privacy.title}>
              {about.privacy.paragraphs.map((paragraph) => (
                <p key={paragraph}>{paragraph}</p>
              ))}
            </Block>

            <Block title={about.model.title}>
              <p>{about.model.lead}</p>
              <dl className="grid grid-cols-2 gap-3 sm:grid-cols-4">
                {about.model.facts.map((fact) => (
                  <div key={fact.label} className="rounded-xl bg-accent-soft p-4">
                    <dd className="text-xl font-semibold tabular-nums text-accent">{fact.value}</dd>
                    <dt className="mt-1 text-xs leading-5 text-ink/70">{fact.label}</dt>
                  </div>
                ))}
              </dl>
              <p className="rounded-lg border-l-4 border-high/60 bg-high-soft/60 p-3 text-sm">
                {about.model.note}
              </p>
            </Block>

            <Block title={about.limits.title}>
              <List items={about.limits.items} />
            </Block>

            <Block title={about.questions.title}>
              <div className="divide-y divide-line rounded-xl border border-line bg-surface">
                {about.questions.items.map((item) => (
                  <details key={item.question} className="group p-4">
                    <summary className="cursor-pointer list-none text-sm font-semibold text-ink">
                      <span className="mr-2 inline-block text-accent transition group-open:rotate-90">
                        ›
                      </span>
                      {item.question}
                    </summary>
                    <p className="mt-2 pl-5 text-sm leading-6">{item.answer}</p>
                  </details>
                ))}
              </div>
            </Block>

            <Link
              href="/"
              className="self-start rounded-lg bg-accent px-6 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:brightness-110"
            >
              {about.callToAction}
            </Link>
          </article>
        );
      }}
    </SiteShell>
  );
}

function Block({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="flex flex-col gap-4 text-[15px] leading-7 text-muted">
      <h2 className="text-xl font-semibold tracking-tight text-ink">{title}</h2>
      {children}
    </section>
  );
}

function List({ items }: { items: string[] }) {
  return (
    <ul className="flex flex-col gap-2">
      {items.map((item) => (
        <li key={item} className="flex gap-3">
          <span className="mt-2.5 size-1.5 shrink-0 rounded-full bg-accent" />
          <span>{item}</span>
        </li>
      ))}
    </ul>
  );
}
