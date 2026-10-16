"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import type { FormEvent } from "react";
import { useEffect, useState } from "react";
import { AuthCard } from "@/components/auth/AuthCard";
import { Alert, Button, ErrorMessage, Loading, TextField } from "@/components/ui";
import { ApiError, api, post } from "@/lib/api";
import type { InvitationPreview, Me } from "@/lib/types";

const STORAGE_KEY = "inteylo.invitation";

/** Le jeton arrive dans le fragment (#) : il n'est jamais transmis au serveur web ni journalisé. */
function readToken(): string | null {
  const fromHash = window.location.hash.slice(1);
  if (fromHash) {
    sessionStorage.setItem(STORAGE_KEY, fromHash);
    history.replaceState(null, "", window.location.pathname);
    return fromHash;
  }
  return sessionStorage.getItem(STORAGE_KEY);
}

export function InvitationAccept() {
  const t = useTranslations();
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [preview, setPreview] = useState<InvitationPreview | null>(null);
  const [me, setMe] = useState<Me | null>(null);
  const [error, setError] = useState<unknown>(null);
  const [loaded, setLoaded] = useState(false);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    const value = readToken();
    setToken(value);
    if (!value) {
      setLoaded(true);
      return;
    }
    (async () => {
      try {
        setPreview(await post<InvitationPreview>("/v1/invitations/inspect", { token: value }));
        try {
          setMe(await api<Me>("/v1/auth/me"));
        } catch {
          setMe(null);
        }
      } catch (err) {
        setError(err);
      } finally {
        setLoaded(true);
      }
    })();
  }, []);

  async function accept(body: Record<string, unknown>) {
    setBusy(true);
    setError(null);
    try {
      await post("/v1/invitations/accept", { token, ...body });
      sessionStorage.removeItem(STORAGE_KEY);
      router.replace("/espace");
    } catch (err) {
      setError(err);
      setBusy(false);
    }
  }

  function onCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    void accept({ full_name: form.get("full_name"), password: form.get("password") });
  }

  const fieldError = (name: string) => (error instanceof ApiError ? error.fieldMessage(name) : undefined);

  if (!loaded) return <AuthCard title={t("invitation.title")}><Loading /></AuthCard>;
  if (!token || !preview) {
    return (
      <AuthCard title={t("invitation.title")}>
        {error ? <ErrorMessage error={error} /> : <Alert>{t("invitation.missingToken")}</Alert>}
        <Link href="/connexion">{t("invitation.goToLogin")}</Link>
      </AuthCard>
    );
  }

  const intro = t("invitation.intro", {
    organization: preview.organization_name,
    role: t(`roles.${preview.role}`),
  });

  return (
    <AuthCard title={t("invitation.title")} subtitle={intro}>
      <p className="muted">{t("invitation.forEmail", { email: preview.email })}</p>
      <ErrorMessage error={error} />
      {me ? (
        me.user.email === preview.email ? (
          <Button busy={busy} onClick={() => void accept({})}>
            {t("invitation.acceptAsCurrent")}
          </Button>
        ) : (
          <Alert>{t("invitation.wrongAccount", { email: me.user.email })}</Alert>
        )
      ) : preview.account_exists ? (
        <>
          <p>{t("invitation.loginFirst")}</p>
          <Link className="btn btn-primary" href="/connexion?retour=invitation">
            {t("invitation.goToLogin")}
          </Link>
        </>
      ) : (
        <form onSubmit={onCreate} noValidate>
          <TextField label={t("auth.fields.fullName")} name="full_name" autoComplete="name" required error={fieldError("full_name")} />
          <TextField
            label={t("auth.fields.password")}
            name="password"
            type="password"
            autoComplete="new-password"
            required
            hint={t("auth.fields.passwordHint")}
            error={fieldError("password")}
          />
          <Button type="submit" busy={busy}>
            {t("invitation.createAndJoin")}
          </Button>
        </form>
      )}
    </AuthCard>
  );
}
