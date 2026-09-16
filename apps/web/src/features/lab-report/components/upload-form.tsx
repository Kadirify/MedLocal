"use client";

import { useState, type DragEvent, type FormEvent } from "react";
import type { Messages } from "../messages";
import type { Sex } from "../types";
import { DocumentIcon } from "./icons";

interface Props {
  busy: boolean;
  messages: Messages;
  onSubmit: (file: File, sex: Sex, age: number) => void;
}

const SAMPLE_URL = "/sample-lab-report.pdf";
const FIELD =
  "rounded-lg border border-line bg-surface px-3 py-2 text-sm outline-none " +
  "focus-visible:border-accent focus-visible:ring-2 focus-visible:ring-accent/20";

export function UploadForm({ busy, messages, onSubmit }: Props) {
  const [file, setFile] = useState<File | null>(null);
  const [dragging, setDragging] = useState(false);
  const [sex, setSex] = useState<Sex>("female");
  const [age, setAge] = useState("35");

  const parsedAge = Number(age);
  const ready = file !== null && Number.isInteger(parsedAge) && parsedAge >= 18 && parsedAge <= 120;

  async function loadSample() {
    const response = await fetch(SAMPLE_URL);
    setFile(new File([await response.blob()], "sample-lab-report.pdf", { type: "application/pdf" }));
  }

  function handleDrop(event: DragEvent) {
    event.preventDefault();
    setDragging(false);
    const dropped = event.dataTransfer.files[0];
    if (dropped?.type === "application/pdf") setFile(dropped);
  }

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (file && ready) onSubmit(file, sex, parsedAge);
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-5">
      {/* the native control words itself in the language of the operating system */}
      <label
        onDragOver={(event) => {
          event.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        className={`flex cursor-pointer flex-col items-center gap-2 rounded-xl border-2 border-dashed px-6 py-8 text-center transition-colors focus-within:border-accent ${
          dragging ? "border-accent bg-accent-soft" : "border-line hover:border-accent/60"
        }`}
      >
        <input
          type="file"
          accept="application/pdf"
          onChange={(event) => setFile(event.target.files?.[0] ?? null)}
          className="sr-only"
        />
        <DocumentIcon className="size-8 text-accent" />
        {file ? (
          <>
            <span className="max-w-full truncate text-sm font-semibold">{file.name}</span>
            <span className="text-xs text-muted">{messages.changeFile}</span>
          </>
        ) : (
          <>
            <span className="text-sm font-semibold">{messages.dropHere}</span>
            <span className="text-xs text-muted">{messages.fileHint}</span>
          </>
        )}
      </label>

      <div className="flex flex-wrap items-end gap-4">
        <label className="flex flex-col gap-1 text-xs font-medium text-muted">
          {messages.sex}
          <select
            value={sex}
            onChange={(event) => setSex(event.target.value as Sex)}
            className={`${FIELD} text-ink`}
          >
            <option value="female">{messages.female}</option>
            <option value="male">{messages.male}</option>
          </select>
        </label>

        <label className="flex flex-col gap-1 text-xs font-medium text-muted">
          {messages.age}
          <input
            type="number"
            min={18}
            max={120}
            value={age}
            onChange={(event) => setAge(event.target.value)}
            className={`${FIELD} w-24 text-ink`}
          />
        </label>

        <button
          type="button"
          onClick={loadSample}
          className="ml-auto text-sm font-medium text-accent underline-offset-4 hover:underline"
        >
          {messages.trySample}
        </button>

        <button
          type="submit"
          disabled={!ready || busy}
          className="rounded-lg bg-accent px-6 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-40"
        >
          {busy ? messages.working : messages.submit}
        </button>
      </div>
    </form>
  );
}
