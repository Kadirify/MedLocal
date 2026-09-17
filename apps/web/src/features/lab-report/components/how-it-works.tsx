import type { ComponentType } from "react";
import type { Messages } from "../messages";
import { ChatIcon, DocumentIcon, RulerIcon } from "@/components/icons";

const ICONS: ComponentType<{ className?: string }>[] = [DocumentIcon, RulerIcon, ChatIcon];

export function HowItWorks({ messages }: { messages: Messages }) {
  return (
    <ol className="grid gap-4 sm:grid-cols-3">
      {messages.steps.map((step, index) => {
        const StepIcon = ICONS[index] ?? DocumentIcon;
        return (
          <li key={step.title} className="rounded-xl border border-line bg-surface/70 p-4">
            <div className="flex items-center gap-2">
              <span className="grid size-8 place-items-center rounded-lg bg-accent-soft text-accent">
                <StepIcon className="size-4.5" />
              </span>
              <span className="text-xs font-semibold text-muted">{index + 1}</span>
            </div>
            <h3 className="mt-3 text-sm font-semibold">{step.title}</h3>
            <p className="mt-1 text-sm leading-6 text-muted">{step.text}</p>
          </li>
        );
      })}
    </ol>
  );
}
