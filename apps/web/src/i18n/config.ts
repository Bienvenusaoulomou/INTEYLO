import type { IntlError } from "next-intl";

export const LOCALE = "fr";
export const DEFAULT_TIME_ZONE = "Europe/Paris";

/** En développement et en test, une clé manquante est une erreur bloquante. */
export function onIntlError(error: IntlError): void {
  if (process.env.NODE_ENV !== "production") {
    throw error;
  }
  console.error("intl", error.code);
}

/** Ne jamais afficher une clé de traduction brute à l'utilisateur. */
export function intlFallback(): string {
  return "";
}
