"use client";

import { LANGUAGES, type Language } from "../messages";

interface Props {
  language: Language;
  onChange: (language: Language) => void;
}

export function LanguageSwitch({ language, onChange }: Props) {
  return (
    <div role="group" aria-label="Language" className="flex rounded-md border border-line text-xs">
      {LANGUAGES.map((option) => (
        <button
          key={option}
          type="button"
          aria-pressed={option === language}
          onClick={() => onChange(option)}
          className={`px-3 py-1.5 font-semibold uppercase first:rounded-l-md last:rounded-r-md ${
            option === language ? "bg-accent text-white" : "bg-surface text-muted"
          }`}
        >
          {option}
        </button>
      ))}
    </div>
  );
}
