"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useTranslations } from "next-intl";
import type { FormEvent } from "react";
import { useState } from "react";
import { AuthCard } from "@/components/auth/AuthCard";
import { Button, ErrorMessage, TextField } from "@/components/ui";
import { ApiError, post } from "@/lib/api";

export function LoginForm() {
  const t = useTranslations();
  const router = useRouter();
  const params = useSearchParams();
  const [error, setError] = useState<unknown>(null);
  const [busy, setBusy] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    setBusy(true);
    setError(null);
    try {
      await post("/v1/auth/login", { email: form.get("email"), password: form.get("password") });
      router.replace(params.get("retour") === "invitation" ? "/invitation" : "/espace");
    } catch (err) {
      setError(err);
      setBusy(false);
    }
  }

  const fieldError = (name: string) => (error instanceof ApiError ? error.fieldMessage(name) : undefined);

  return (
    <AuthCard
      title={t("auth.login.title")}
      subtitle={t("auth.login.subtitle")}
      footer={
        <>
          {t("auth.login.noAccount")} <Link href="/inscription">{t("auth.login.createAccount")}</Link>
        </>
      }
    >
      <form onSubmit={onSubmit} noValidate>
        <ErrorMessage error={error} />
        <TextField label={t("auth.fields.email")} name="email" type="email" autoComplete="email" required error={fieldError("email")} />
        <TextField label={t("auth.fields.password")} name="password" type="password" autoComplete="current-password" required error={fieldError("password")} />
        <Button type="submit" busy={busy}>
          {busy ? t("auth.login.submitting") : t("auth.login.submit")}
        </Button>
      </form>
    </AuthCard>
  );
}
