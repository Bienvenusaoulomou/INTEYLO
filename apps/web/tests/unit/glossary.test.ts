import { readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import fr from "../../messages/fr.json";

// Le glossaire d'affichage (docs/phase-0/07-glossaire.md) est la source des libellés.
// Ce test garantit que le catalogue l'applique mot pour mot.
const glossary = readFileSync(join(__dirname, "../../../../docs/phase-0/07-glossaire.md"), "utf8");

function rows(section: string): Array<[string, string]> {
  const block = glossary.split(`## ${section}`)[1]?.split("\n## ")[0] ?? "";
  return block
    .split("\n")
    .filter((l) => l.startsWith("| `"))
    .map((l) => l.split("|").map((c) => c.trim()))
    .map((cells) => [(cells[1] ?? "").replaceAll("`", ""), cells[2] ?? ""] as [string, string]);
}

describe("glossaire d'affichage", () => {
  it("applique les libellés des rôles", () => {
    for (const [key, label] of rows("Rôles")) {
      if (key.startsWith("permission")) continue;
      expect(fr.roles[key as keyof typeof fr.roles], key).toBe(label);
    }
    expect(fr.roles.approver).toBe("Approbateur");
  });

  it("applique les libellés des états d'action", () => {
    const states = rows("États des actions");
    expect(states).toHaveLength(11);
    for (const [key, label] of states) {
      expect(fr.actionStates[key as keyof typeof fr.actionStates], key).toBe(label);
    }
  });

  it("applique les libellés des états de connecteur", () => {
    const states = rows("États des connecteurs (§7.2)");
    expect(states).toHaveLength(10);
    for (const [key, label] of states) {
      expect(fr.connectorStates[key as keyof typeof fr.connectorStates], key).toBe(label);
    }
  });
});
