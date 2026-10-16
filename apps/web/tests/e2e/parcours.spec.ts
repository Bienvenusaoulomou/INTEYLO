import { expect, test } from "@playwright/test";
import { expectFrenchOnly, signup, uniqueEmail } from "./helpers";

test("la page d'accueil est entièrement en français", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { level: 1 })).toHaveText(
    "L'intelligence opérationnelle de votre organisation",
  );
  await expectFrenchOnly(page);
});

test("une erreur de connexion est affichée en français", async ({ page }) => {
  await page.goto("/connexion");
  await expectFrenchOnly(page);
  await page.getByLabel("Adresse e-mail").fill(uniqueEmail("inconnu"));
  await page.getByLabel("Mot de passe").fill("mauvais-mot-de-passe");
  await page.getByRole("button", { name: "Se connecter" }).click();
  await expect(page.getByRole("alert")).toBeVisible();
  await expectFrenchOnly(page);
});

test("une erreur de validation est traduite par l'API", async ({ page }) => {
  await page.goto("/inscription");
  await page.getByLabel("Nom complet").fill("Awa Diallo");
  await page.getByLabel("Adresse e-mail").fill(uniqueEmail("court"));
  await page.getByLabel("Mot de passe").fill("court");
  await page.getByLabel("Nom de l'organisation").fill("Atelier Court");
  await page.getByRole("button", { name: "Créer mon compte" }).click();
  await expect(page.getByRole("alert").first()).toBeVisible();
  await expect(page).toHaveURL(/\/inscription$/);
  await expectFrenchOnly(page);
});

test("inscription, invitation d'un analyste et droits limités", async ({ page }) => {
  const ownerEmail = uniqueEmail("proprietaire");
  const analystEmail = uniqueEmail("analyste");
  await signup(page, { name: "Mariama Bah", email: ownerEmail, org: "Comptoir Conakry" });
  await expectFrenchOnly(page);

  // Ouvrir l'organisation : le propriétaire voit ses rôles en français.
  await page.getByRole("link", { name: /Comptoir Conakry/ }).click();
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("Comptoir Conakry");
  await expect(page.getByText("Propriétaire de l'organisation").first()).toBeVisible();
  await expectFrenchOnly(page);

  // Inviter un analyste.
  await page.getByRole("link", { name: "Membres" }).click();
  await page.getByLabel("Adresse e-mail").fill(analystEmail);
  await page.getByLabel("Rôle").selectOption({ label: "Analyste" });
  await page.getByRole("button", { name: "Créer l'invitation" }).click();
  const link = await page.getByLabel("Lien d'invitation").inputValue();
  expect(link).toContain("/invitation#");
  await expectFrenchOnly(page);

  // Le journal d'audit enregistre l'invitation.
  await page.getByRole("link", { name: "Audit et incidents" }).click();
  await expect(page.getByRole("cell", { name: "Invitation créée" })).toBeVisible();
  await expectFrenchOnly(page);

  await page.getByRole("button", { name: "Se déconnecter" }).click();
  await expect(page).toHaveURL(/\/connexion$/);

  // L'invité crée son compte depuis le lien.
  await page.goto(link.replace(/^https?:\/\/[^/]+/, ""));
  await expect(page.getByText("Comptoir Conakry", { exact: false }).first()).toBeVisible();
  await expectFrenchOnly(page);
  await page.getByLabel("Nom complet").fill("Ibrahima Sow");
  await page.getByLabel("Mot de passe").fill("motdepasse-solide-2026");
  await page.getByRole("button", { name: "Créer mon compte et rejoindre l'organisation" }).click();
  await expect(page).toHaveURL(/\/espace$/);

  // L'analyste voit l'organisation, sans audit ni formulaire d'invitation.
  await page.getByRole("link", { name: /Comptoir Conakry/ }).click();
  await expect(page.getByText("Analyste").first()).toBeVisible();
  await expect(page.getByRole("link", { name: "Audit et incidents" })).toHaveCount(0);
  await page.getByRole("link", { name: "Membres" }).click();
  await expect(page.getByRole("button", { name: "Créer l'invitation" })).toHaveCount(0);
  await expect(page.getByRole("cell", { name: /^Mariama Bah/ })).toBeVisible();
  await expectFrenchOnly(page);
});
