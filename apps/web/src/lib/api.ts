/**
 * Client de l'API INTEYLO. Les messages d'erreur reçus sont déjà en français
 * (l'API garantit un message français pour chaque code).
 */

export type FieldError = { field: string; message: string };

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly code: string,
    message: string,
    public readonly details: FieldError[] = [],
  ) {
    super(message);
  }

  fieldMessage(field: string): string | undefined {
    return this.details.find((d) => d.field === field)?.message;
  }
}

/** Erreur réseau : le libellé est fourni par le catalogue, pas par ce module. */
export class NetworkError extends Error {}

export async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
  const method = (init.method ?? "GET").toUpperCase();
  const headers = new Headers(init.headers);
  if (init.body !== undefined) headers.set("content-type", "application/json");
  if (method !== "GET") headers.set("x-inteylo-client", "web");
  let response: Response;
  try {
    response = await fetch(`/api${path}`, { ...init, method, headers, credentials: "same-origin" });
  } catch {
    throw new NetworkError();
  }
  const isJson = response.headers.get("content-type")?.includes("application/json");
  const body: unknown = isJson ? await response.json() : null;
  if (!response.ok) {
    const err = (body as { error?: { code: string; message: string; details?: FieldError[] } })
      ?.error;
    if (!err) throw new NetworkError();
    throw new ApiError(response.status, err.code, err.message, err.details ?? []);
  }
  return body as T;
}

export const post = <T>(path: string, data?: unknown) =>
  api<T>(path, { method: "POST", body: data === undefined ? undefined : JSON.stringify(data) });
export const put = <T>(path: string, data: unknown) =>
  api<T>(path, { method: "PUT", body: JSON.stringify(data) });
export const patch = <T>(path: string, data: unknown) =>
  api<T>(path, { method: "PATCH", body: JSON.stringify(data) });
export const del = <T>(path: string) => api<T>(path, { method: "DELETE" });
