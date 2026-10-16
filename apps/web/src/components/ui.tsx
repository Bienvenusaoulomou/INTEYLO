"use client";

import { useTranslations } from "next-intl";
import type { ButtonHTMLAttributes, InputHTMLAttributes, ReactNode, SelectHTMLAttributes } from "react";
import { useId } from "react";
import { ApiError, NetworkError } from "@/lib/api";
import { catalogKey } from "@/lib/format";

export function Button({
  variant = "primary",
  busy = false,
  children,
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary" | "danger" | "ghost";
  busy?: boolean;
}) {
  return (
    <button
      className={`btn btn-${variant}`}
      disabled={busy || props.disabled}
      aria-busy={busy || undefined}
      {...props}
    >
      {children}
    </button>
  );
}

export function TextField({
  label,
  error,
  hint,
  ...props
}: InputHTMLAttributes<HTMLInputElement> & { label: string; error?: string; hint?: string }) {
  const id = useId();
  const describedBy = [error ? `${id}-error` : null, hint ? `${id}-hint` : null]
    .filter(Boolean)
    .join(" ");
  return (
    <div className="field">
      <label htmlFor={id}>{label}</label>
      <input
        id={id}
        aria-invalid={error ? true : undefined}
        aria-describedby={describedBy || undefined}
        {...props}
      />
      {hint && !error ? (
        <p id={`${id}-hint`} className="field-hint">
          {hint}
        </p>
      ) : null}
      {error ? (
        <p id={`${id}-error`} className="field-error" role="alert">
          {error}
        </p>
      ) : null}
    </div>
  );
}

export function SelectField({
  label,
  children,
  ...props
}: SelectHTMLAttributes<HTMLSelectElement> & { label: string; children: ReactNode }) {
  const id = useId();
  return (
    <div className="field">
      <label htmlFor={id}>{label}</label>
      <select id={id} {...props}>
        {children}
      </select>
    </div>
  );
}

export function Alert({ tone = "error", children }: { tone?: "error" | "success" | "info"; children: ReactNode }) {
  return (
    <div className={`alert alert-${tone}`} role={tone === "error" ? "alert" : "status"}>
      {children}
    </div>
  );
}

/** Affiche le message français d'une erreur API, ou un message générique du catalogue. */
export function ErrorMessage({ error }: { error: unknown }) {
  const t = useTranslations();
  if (!error) return null;
  const message =
    error instanceof ApiError
      ? error.message
      : error instanceof NetworkError
        ? t("common.networkError")
        : t("common.unexpectedError");
  return <Alert>{message}</Alert>;
}

export function RoleBadge({ role }: { role: string }) {
  const t = useTranslations();
  return <span className={`badge badge-role badge-${role}`}>{t(`roles.${role}`)}</span>;
}

export function StatusBadge({ kind, value }: { kind: "member" | "invitation" | "outcome" | "organization"; value: string }) {
  const t = useTranslations();
  return <span className={`badge badge-status badge-${value}`}>{t(`statuses.${kind}.${value}`)}</span>;
}

export function PermissionLabel({ permission }: { permission: string }) {
  const t = useTranslations();
  return <>{t(`permissions.${catalogKey(permission)}`)}</>;
}

export function PageHeader({ title, description, actions }: { title: string; description?: string; actions?: ReactNode }) {
  return (
    <header className="page-header">
      <div>
        <h1>{title}</h1>
        {description ? <p className="page-description">{description}</p> : null}
      </div>
      {actions ? <div className="page-actions">{actions}</div> : null}
    </header>
  );
}

export function Loading() {
  const t = useTranslations();
  return (
    <p className="loading" role="status">
      {t("common.loading")}
    </p>
  );
}

export function EmptyState({ title, description }: { title: string; description?: string }) {
  return (
    <div className="empty-state">
      <p className="empty-title">{title}</p>
      {description ? <p className="empty-description">{description}</p> : null}
    </div>
  );
}
