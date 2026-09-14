"use client";

import { useCallback, useSyncExternalStore } from "react";
import { LANGUAGES, type Language } from "./messages";

const STORAGE_KEY = "medlocal.language";
const FALLBACK: Language = "tr";
const CHANGED = "medlocal:language";

function read(): Language {
  const stored = window.localStorage.getItem(STORAGE_KEY);
  if (LANGUAGES.includes(stored as Language)) return stored as Language;
  return navigator.language.toLowerCase().startsWith("tr") ? "tr" : "en";
}

function subscribe(onChange: () => void): () => void {
  window.addEventListener(CHANGED, onChange);
  window.addEventListener("storage", onChange);
  return () => {
    window.removeEventListener(CHANGED, onChange);
    window.removeEventListener("storage", onChange);
  };
}

/** The reader's language: their stored choice, else the browser's, else Turkish on the server. */
export function useLanguage(): [Language, (language: Language) => void] {
  const language = useSyncExternalStore(subscribe, read, () => FALLBACK);

  const choose = useCallback((next: Language) => {
    window.localStorage.setItem(STORAGE_KEY, next);
    document.documentElement.lang = next;
    window.dispatchEvent(new Event(CHANGED));
  }, []);

  return [language, choose];
}
