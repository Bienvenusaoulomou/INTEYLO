/**
 * Formats d'affichage : toujours via Intl, avec la locale et le fuseau de l'organisation.
 * Aucune devise par défaut : la devise est celle de la donnée.
 */

export const DEFAULT_LOCALE = "fr";

export function formatDate(iso: string, timeZone: string, locale = DEFAULT_LOCALE): string {
  return new Intl.DateTimeFormat(locale, {
    timeZone,
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  }).format(new Date(iso));
}

export function formatDateTime(iso: string, timeZone: string, locale = DEFAULT_LOCALE): string {
  return new Intl.DateTimeFormat(locale, {
    timeZone,
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    hourCycle: "h23",
  }).format(new Date(iso));
}

export function formatNumber(value: number, locale = DEFAULT_LOCALE): string {
  return new Intl.NumberFormat(locale).format(value);
}

export function formatMoney(amount: number, currency: string, locale = DEFAULT_LOCALE): string {
  return new Intl.NumberFormat(locale, { style: "currency", currency }).format(amount);
}

/** Clé de catalogue pour un identifiant technique contenant des points (ex. users.read). */
export function catalogKey(technicalId: string): string {
  return technicalId.replaceAll(".", "_");
}
