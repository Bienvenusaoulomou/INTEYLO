import { afterEach, describe, expect, it, vi } from "vitest";
import { ApiError, NetworkError, api, post } from "../../src/lib/api";

function mockFetch(response: Response | Error) {
  const fn = vi.fn(async () => {
    if (response instanceof Error) throw response;
    return response;
  });
  vi.stubGlobal("fetch", fn);
  return fn;
}

const json = (status: number, body: unknown) =>
  new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json" } });

afterEach(() => vi.unstubAllGlobals());

describe("client API", () => {
  it("préfixe les chemins par /api et envoie les cookies du même site", async () => {
    const fetchFn = mockFetch(json(200, { ok: true }));
    await api("/v1/auth/me");
    const [url, init] = fetchFn.mock.calls[0] as unknown as [string, RequestInit];
    expect(url).toBe("/api/v1/auth/me");
    expect(init.credentials).toBe("same-origin");
    expect(new Headers(init.headers).has("x-inteylo-client")).toBe(false);
  });

  it("ajoute l'en-tête anti-CSRF sur les requêtes modifiantes", async () => {
    const fetchFn = mockFetch(json(200, { ok: true }));
    await post("/v1/auth/logout");
    const [, init] = fetchFn.mock.calls[0] as unknown as [string, RequestInit];
    expect(new Headers(init.headers).get("x-inteylo-client")).toBe("web");
  });

  it("restitue le code et le message français de l'API", async () => {
    mockFetch(
      json(422, {
        error: {
          code: "validation_error",
          message: "Certaines informations sont invalides.",
          details: [{ field: "email", message: "Adresse e-mail invalide." }],
        },
      }),
    );
    const error = await api("/v1/auth/signup").catch((e: unknown) => e);
    expect(error).toBeInstanceOf(ApiError);
    const apiError = error as ApiError;
    expect(apiError.status).toBe(422);
    expect(apiError.code).toBe("validation_error");
    expect(apiError.message).toBe("Certaines informations sont invalides.");
    expect(apiError.fieldMessage("email")).toBe("Adresse e-mail invalide.");
  });

  it("signale une panne réseau sans texte technique", async () => {
    mockFetch(new TypeError("Failed to fetch"));
    await expect(api("/v1/auth/me")).rejects.toBeInstanceOf(NetworkError);
  });

  it("traite une réponse d'erreur non JSON comme une panne réseau", async () => {
    mockFetch(new Response("Bad Gateway", { status: 502 }));
    await expect(api("/v1/auth/me")).rejects.toBeInstanceOf(NetworkError);
  });
});
