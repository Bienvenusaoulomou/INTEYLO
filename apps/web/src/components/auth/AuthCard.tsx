"use client";

import Link from "next/link";
import { useTranslations } from "next-intl";
import type { ReactNode } from "react";

export function AuthCard({ title, subtitle, children, footer }: {
  title: string;
  subtitle?: string;
  children: ReactNode;
  footer?: ReactNode;
}) {
  const t = useTranslations();
  return (
    <main className="auth-page">
      <div className="auth-card">
        <Link href="/" className="brand brand-dark">
          <span className="brand-mark" aria-hidden="true" />
          <span className="brand-name">{t("brand.name")}</span>
        </Link>
        <h1>{title}</h1>
        {subtitle ? <p className="auth-subtitle">{subtitle}</p> : null}
        {children}
        {footer ? <div className="auth-footer">{footer}</div> : null}
      </div>
    </main>
  );
}
