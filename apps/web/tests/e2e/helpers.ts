import { expect, type Page } from "@playwright/test";

// Mots anglais qui ne doivent jamais apparaître dans l'interface (§14 du prompt maître).
const ENGLISH =
  /\b(the|and|your|please|save|cancel|delete|loading|error|sign in|sign up|log ?in|log ?out|settings|members|password|submit|invalid|required|not found|welcome|account|dashboard|search|failed|success|organization)\b/i;
// Une clé de catalogue non traduite ressemble à « section.sousCle ».
const RAW_KEY = /\b[a-z]+(?:\.[a-zA-Z_]+){1,4}\b/;

/** Vérifie qu'aucun texte anglais ni aucune clé brute n'est visible sur la page. */
export async function expectFrenchOnly(page: Page) {
  await expect(page.locator("html")).toHaveAttribute("lang", "fr");
  const text = await page.locator("body").innerText();
  // Les adresses e-mail et URL saisies par les tests sont des données, pas des libellés.
  const visible = text
    .replace(/[\w.+-]+@[\w.-]+/g, " ")
    .replace(/https?:\/\/\S+/g, " ");
  expect(visible, "texte anglais visible").not.toMatch(ENGLISH);
  expect(visible, "clé de traduction visible").not.toMatch(RAW_KEY);
  const title = await page.title();
  expect(title).not.toMatch(ENGLISH);
}

export function uniqueEmail(prefix: string) {
  return `${prefix}.${Date.now()}.${Math.floor(Math.random() * 1e6)}@exemple.fr`;
}

export async function signup(page: Page, data: { name: string; email: string; org: string }) {
  await page.goto("/inscription");
  await page.getByLabel("Nom complet").fill(data.name);
  await page.getByLabel("Adresse e-mail").fill(data.email);
  await page.getByLabel("Mot de passe").fill("motdepasse-solide-2026");
  await page.getByLabel("Nom de l'organisation").fill(data.org);
  await page.getByRole("button", { name: "Créer mon compte" }).click();
  await expect(page).toHaveURL(/\/espace$/);
}
