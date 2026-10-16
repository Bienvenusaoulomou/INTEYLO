// Lint du frontend. La règle i18next bloque tout texte littéral dans le JSX :
// les textes visibles doivent provenir du catalogue messages/fr.json.
import js from "@eslint/js";
import i18next from "eslint-plugin-i18next";
import reactHooks from "eslint-plugin-react-hooks";
import tseslint from "typescript-eslint";

export default tseslint.config(
  { ignores: [".next/**", "node_modules/**", "playwright-report/**", "test-results/**", "next-env.d.ts"] },
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    files: ["src/**/*.{ts,tsx}"],
    plugins: { "react-hooks": reactHooks, i18next },
    rules: {
      ...reactHooks.configs.recommended.rules,
      "i18next/no-literal-string": [
        "error",
        {
          mode: "jsx-only",
          "jsx-attributes": {
            include: ["alt", "aria-label", "aria-description", "title", "placeholder", "label"],
          },
          callees: { exclude: ["t", "useTranslations", "getTranslations", "can", "link"] },
          // Caractères purement typographiques autorisés (séparateurs, flèches).
          words: { exclude: ["^[\\s·•—–:/|()→←…\\-]*$"] },
        },
      ],
    },
  },
  {
    files: ["tests/**/*.ts", "*.config.{ts,mjs}", "scripts/**/*.mjs"],
    languageOptions: { globals: { console: "readonly", process: "readonly", __dirname: "readonly" } },
    rules: { "i18next/no-literal-string": "off" },
  },
);
