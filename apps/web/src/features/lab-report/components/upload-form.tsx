"use client";

import { useState, type FormEvent } from "react";
import type { Messages } from "../messages";
import type { Sex } from "../types";

interface Props {
  busy: boolean;
  messages: Messages;
  onSubmit: (file: File, sex: Sex, age: number) => void;
}

const SAMPLE_URL = "/sample-lab-report.pdf";
const FIELD = "rounded-md border border-line bg-surface px-3 py-2 text-sm";

export function UploadForm({ busy, messages, onSubmit }: Props) {
  const [file, setFile] = useState<File | null>(null);
  const [sex, setSex] = useState<Sex>("female");
  const [age, setAge] = useState("35");

  const parsedAge = Number(age);
  const ready = file !== null && Number.isInteger(parsedAge) && parsedAge >= 18 && parsedAge <= 120;

  async function loadSample() {
    const response = await fetch(SAMPLE_URL);
    setFile(new File([await response.blob()], "sample-lab-report.pdf", { type: "application/pdf" }));
  }

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (file && ready) onSubmit(file, sex, parsedAge);
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-wrap items-end gap-4">
      <div className="flex min-w-64 flex-1 flex-col gap-1 text-sm font-medium">
        {messages.file}
        {/* the native control words itself in the language of the operating system */}
        <label className={`${FIELD} flex cursor-pointer items-center gap-3`}>
          <input
            type="file"
            accept="application/pdf"
            onChange={(event) => setFile(event.target.files?.[0] ?? null)}
            className="sr-only"
          />
          <span className="rounded bg-canvas px-3 py-1">{messages.chooseFile}</span>
          <span className="truncate font-normal text-muted">
            {file ? file.name : messages.nothingChosen}
          </span>
        </label>
        {!file && (
          <span className="text-xs font-normal text-muted">
            {messages.noFile}
            <button type="button" onClick={loadSample} className="text-accent underline">
              {messages.trySample}
            </button>
          </span>
        )}
      </div>

      <label className="flex flex-col gap-1 text-sm font-medium">
        {messages.sex}
        <select value={sex} onChange={(e) => setSex(e.target.value as Sex)} className={FIELD}>
          <option value="female">{messages.female}</option>
          <option value="male">{messages.male}</option>
        </select>
      </label>

      <label className="flex flex-col gap-1 text-sm font-medium">
        {messages.age}
        <input
          type="number"
          min={18}
          max={120}
          value={age}
          onChange={(event) => setAge(event.target.value)}
          className={`${FIELD} w-24`}
        />
      </label>

      <button
        type="submit"
        disabled={!ready || busy}
        className="rounded-md bg-accent px-5 py-2 text-sm font-semibold text-white disabled:opacity-40"
      >
        {busy ? messages.working : messages.submit}
      </button>
    </form>
  );
}
