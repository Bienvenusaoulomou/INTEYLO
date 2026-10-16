import { defineConfig, devices } from "@playwright/test";

// Tests de bout en bout : vraie API FastAPI + vrai PostgreSQL + build de production Next.js.
// La base est préparée par apps/api/scripts/bootstrap_db.py (voir docs/testing/README.md).
// Variables : E2E_DATABASE_URL (rôle applicatif), E2E_API_PYTHON (interpréteur de l'API).
const apiPort = 8000;
const webPort = 3100;
const python = process.env.E2E_API_PYTHON ?? "../api/.venv/bin/python";
const databaseUrl =
  process.env.E2E_DATABASE_URL ??
  "postgresql+psycopg://inteylo_app:app-dev-password@127.0.0.1:5432/inteylo_e2e";

export default defineConfig({
  testDir: "tests/e2e",
  fullyParallel: false,
  workers: 1,
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? [["list"], ["html", { open: "never" }]] : "list",
  use: {
    baseURL: `http://127.0.0.1:${webPort}`,
    locale: "fr-FR",
    timezoneId: "Africa/Tunis",
    trace: "retain-on-failure",
    launchOptions: process.env.PLAYWRIGHT_CHROMIUM_PATH
      ? { executablePath: process.env.PLAYWRIGHT_CHROMIUM_PATH }
      : {},
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: [
    {
      command: `${python} -m uvicorn app.main:app --host 127.0.0.1 --port ${apiPort}`,
      cwd: "../api",
      url: `http://127.0.0.1:${apiPort}/health/live`,
      reuseExistingServer: !process.env.CI,
      timeout: 60_000,
      env: {
        INTEYLO_ENVIRONMENT: "test",
        INTEYLO_DATABASE_URL: databaseUrl,
        INTEYLO_COOKIE_SECURE: "false",
        INTEYLO_PUBLIC_WEB_URL: `http://127.0.0.1:${webPort}`,
        INTEYLO_LOG_LEVEL: "WARNING",
      },
    },
    {
      command: `npx next build && npx next start -H 127.0.0.1 -p ${webPort}`,
      url: `http://127.0.0.1:${webPort}`,
      reuseExistingServer: !process.env.CI,
      timeout: 240_000,
      env: { API_INTERNAL_URL: `http://127.0.0.1:${apiPort}`, NEXT_TELEMETRY_DISABLED: "1" },
    },
  ],
});
