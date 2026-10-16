"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import type { FormEvent } from "react";
import { useState } from "react";
import { AuthCard } from "@/components/auth/AuthCard";
import { Button, ErrorMessage, TextField } from "@/components/ui";
import { ApiError, post } from "@/lib/api";

export function SignupForm() {
  const t = useTranslations();
  const router = useRouter();
  const [error, setError] = useState<unknown>(null);
  const [busy, setBusy] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    setBusy(true);
    setError(null);
    try {
      await post("/v1/auth/signup", {
        full_name: form.get("full_name"),
        email: form.get("email"),
        password: form.get("password"),
        organization_name: form.get("organization_name"),
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC",
      });
      router.replace("/espace");
    } catch (err) {
      setError(err);
      setBusy(false);
    }
  }

  const fieldError = (name: string) => (error instanceof ApiError ? error.fieldMessage(name) : undefined);

  return (
    <AuthCard
      title={t("auth.signup.title")}
      subtitle={t("auth.signup.subtitle")}
      footer={
        <>
          {t("auth.signup.hasAccount")} <Link href="/connexion">{t("auth.signup.login")}</Link>
        </>
      }
    >
      <form onSubmit={onSubmit} noValidate>
        <ErrorMessage error={error} />
        <TextField label={t("auth.fields.fullName")} name="full_name" autoComplete="name" required error={fieldError("full_name")} />
        <TextField label={t("auth.fields.email")} name="email" type="email" autoComplete="email" required error={fieldError("email")} />
        <TextField
          label={t("auth.fields.password")}
          name="password"
          type="password"
          autoComplete="new-password"
          minLength={12}
          required
          hint={t("auth.fields.passwordHint")}
          error={fieldError("password")}
        />
        <TextField
          label={t("auth.fields.organizationName")}
          name="organization_name"
          autoComplete="organization"
          required
          error={fieldError("organization_name")}
        />
        <Button type="submit" busy={busy}>
          {busy ? t("auth.signup.submitting") : t("auth.signup.submit")}
        </Button>
      </form>
    </AuthCard>
  );
}
