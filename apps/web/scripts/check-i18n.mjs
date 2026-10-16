#!/usr/bin/env node
// Contrôle linguistique bloquant (prompt maître §14.4).
// 1. Chaque valeur du catalogue fr est une chaîne non vide, au format ICU valide, sans texte anglais de secours.
// 2. Chaque clé utilisée statiquement dans src/ existe ; chaque préfixe dynamique `t(`x.${…}`)` existe.
// 3. Chaque identifiant du contrat partagé (rôles, permissions, audit, statuts, états) a son libellé.
// Sortie non nulle à la moindre violation.
import { readFileSync, readdirSync, statSync } from "node:fs";
import { dirname, join, relative } from "node:path";
import { fileURLToPath } from "node:url";
import { parse } from "@formatjs/icu-messageformat-parser";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const catalog = JSON.parse(readFileSync(join(root, "messages/fr.json"), "utf8"));
const contract = JSON.parse(readFileSync(join(root, "../../contracts/identity.json"), "utf8"));
const errors = [];

// Mots anglais révélateurs d'une valeur non traduite. Les noms propres (INTEYLO) ne sont pas concernés.
const ENGLISH = /\b(the|and|with|your|please|save|cancel|delete|loading|error|sign in|sign up|log ?in|log ?out|settings|members?|password|email address|submit|invalid|required|not found|welcome|account|dashboard|workspace|search|create|update|failed|success)\b/i;
const ALLOWED_ENGLISH_KEYS = new Set(["brand.name", "meta.title"]);

function flatten(obj, prefix = "", out = new Map()) {
  for (const [key, value] of Object.entries(obj)) {
    const path = prefix ? `${prefix}.${key}` : key;
    if (value !== null && typeof value === "object") flatten(value, path, out);
    else out.set(path, value);
  }
  return out;
}

const leaves = flatten(catalog);
const hasNode = (path) => {
  let node = catalog;
  for (const part of path.split(".")) {
    if (node === null || typeof node !== "object" || !(part in node)) return false;
    node = node[part];
  }
  return true;
};

// 1. Valeurs du catalogue
for (const [key, value] of leaves) {
  if (typeof value !== "string" || value.trim() === "") {
    errors.push(`Traduction vide ou non textuelle : ${key}`);
    continue;
  }
  if (/\bTODO\b|\bFIXME\b|\bTBD\b/.test(value)) errors.push(`Marqueur de brouillon dans ${key} : « ${value} »`);
  if (!ALLOWED_ENGLISH_KEYS.has(key) && ENGLISH.test(value.replace(/\{[^}]*\}/g, ""))) {
    errors.push(`Texte anglais probable dans ${key} : « ${value} »`);
  }
  try {
    parse(value);
  } catch (e) {
    errors.push(`Message ICU invalide dans ${key} : ${e.message}`);
  }
}

// 2. Clés utilisées dans le code
function* walk(dir) {
  for (const entry of readdirSync(dir)) {
    const full = join(dir, entry);
    if (statSync(full).isDirectory()) yield* walk(full);
    else if (/\.(ts|tsx)$/.test(entry)) yield full;
  }
}
const STATIC_KEY = /\bt(?:\.rich|\.markup|\.raw)?\(\s*["']([^"']+)["']/g;
const DYNAMIC_KEY = /\bt\(\s*`([^`$]*)\$\{/g;
let used = 0;
for (const file of walk(join(root, "src"))) {
  const source = readFileSync(file, "utf8");
  const rel = relative(root, file);
  for (const [, key] of source.matchAll(STATIC_KEY)) {
    used += 1;
    if (!leaves.has(key)) errors.push(`Clé absente du catalogue : ${key} (${rel})`);
  }
  for (const [, prefix] of source.matchAll(DYNAMIC_KEY)) {
    const ns = prefix.replace(/\.$/, "");
    if (ns && !hasNode(ns)) errors.push(`Préfixe dynamique absent du catalogue : ${ns} (${rel})`);
  }
}

// 3. Couverture du contrat partagé
const toKey = (id) => id.replaceAll(".", "_");
const required = [
  ...[...contract.organizationRoles, ...contract.platformRoles].map((r) => `roles.${r}`),
  ...[...contract.organizationPermissions, ...contract.platformPermissions].map((p) => `permissions.${toKey(p)}`),
  ...contract.auditActions.map((a) => `auditActions.${toKey(a)}`),
  ...contract.auditOutcomes.map((s) => `statuses.outcome.${s}`),
  ...contract.invitationStatuses.map((s) => `statuses.invitation.${s}`),
  ...contract.memberStatuses.map((s) => `statuses.member.${s}`),
  ...contract.organizationStatuses.map((s) => `statuses.organization.${s}`),
  ...contract.actionStates.map((s) => `actionStates.${s}`),
  ...(contract.connectorStates ?? []).map((s) => `connectorStates.${s}`),
];
for (const key of required) if (!leaves.has(key)) errors.push(`Libellé manquant pour le contrat : ${key}`);

if (errors.length) {
  console.error(`Contrôle linguistique : ${errors.length} violation(s)\n`);
  for (const e of errors) console.error(`  ✗ ${e}`);
  process.exit(1);
}
console.log(
  `Contrôle linguistique réussi : ${leaves.size} libellés, ${used} usages statiques, ${required.length} identifiants du contrat couverts.`,
);
