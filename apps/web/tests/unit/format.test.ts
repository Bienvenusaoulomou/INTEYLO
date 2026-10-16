import { describe, expect, it } from "vitest";
import { catalogKey, formatDate, formatDateTime, formatMoney, formatNumber } from "../../src/lib/format";

// Intl insère des espaces insécables (U+00A0 ou U+202F) : on les normalise pour comparer.
const plain = (s: string) => s.replace(/[\u00a0\u202f]/g, " ");

describe("formats français", () => {
  it("affiche les dates au format JJ/MM/AAAA", () => {
    expect(formatDate("2026-10-16T08:00:00Z", "Africa/Tunis")).toBe("16/10/2026");
  });

  it("applique le fuseau de l'organisation", () => {
    // 23 h 30 UTC le 15 = 00 h 30 le 16 à Tunis (UTC+1)
    expect(formatDate("2026-10-15T23:30:00Z", "Africa/Tunis")).toBe("16/10/2026");
    expect(formatDate("2026-10-15T23:30:00Z", "America/New_York")).toBe("15/10/2026");
  });

  it("utilise l'horloge sur 24 heures", () => {
    expect(formatDateTime("2026-10-16T13:05:00Z", "UTC")).toBe("16/10/2026 13:05");
  });

  it("formate les nombres avec la virgule décimale et l'espace des milliers", () => {
    expect(plain(formatNumber(1234.56))).toBe("1 234,56");
  });

  it("affiche la devise de la donnée, jamais une devise par défaut", () => {
    expect(plain(formatMoney(12.5, "EUR"))).toBe("12,50 €");
    expect(plain(formatMoney(12.5, "TND"))).toBe("12,500 TND");
    expect(plain(formatMoney(1000, "USD"))).toBe("1 000,00 $US");
  });

  it("convertit un identifiant technique en clé de catalogue", () => {
    expect(catalogKey("users.read")).toBe("users_read");
    expect(catalogKey("platform.organizations.suspend")).toBe("platform_organizations_suspend");
  });
});
