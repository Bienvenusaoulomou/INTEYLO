"use client";

import Link from "next/link";
import { useParams, usePathname, useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import type { ReactNode } from "react";
import { post } from "@/lib/api";
import { can, useMe } from "@/components/MeProvider";

export function AppShell({ children }: { children: ReactNode }) {
  const t = useTranslations();
  const { me } = useMe();
  const pathname = usePathname();
  const router = useRouter();
  const params = useParams<{ orgId?: string }>();
  const orgId = params.orgId;
  const membership = me.memberships.find((m) => m.organization.id === orgId);

  async function logout() {
    try {
      await post("/v1/auth/logout");
    } finally {
      router.replace("/connexion");
    }
  }

  const link = (href: string, label: string) => (
    <Link href={href} className="nav-link" aria-current={pathname === href ? "page" : undefined}>
      {label}
    </Link>
  );

  return (
    <div className="shell">
      <a className="skip-link" href="#contenu">
        {t("nav.skipToContent")}
      </a>
      <aside className="sidebar">
        <Link href="/espace" className="brand">
          <span className="brand-mark" aria-hidden="true" />
          <span className="brand-name">{t("brand.name")}</span>
        </Link>
        <nav aria-label={t("nav.mainNavigation")}>
          {link("/espace", t("nav.workspace"))}
          {membership && orgId ? (
            <div className="nav-group">
              <p className="nav-group-title">{membership.organization.name}</p>
              {link(`/organisations/${orgId}`, t("nav.overview"))}
              {can(membership, "users.read") ? link(`/organisations/${orgId}/membres`, t("nav.members")) : null}
              {can(membership, "audit.read") ? link(`/organisations/${orgId}/audit`, t("nav.audit")) : null}
            </div>
          ) : null}
          {me.user.is_platform_admin ? link("/plateforme", t("nav.platform")) : null}
        </nav>
        <div className="sidebar-footer">
          {link("/compte", t("nav.account"))}
          <p className="sidebar-user">{me.user.full_name}</p>
          <button type="button" className="btn btn-ghost" onClick={logout}>
            {t("common.logout")}
          </button>
        </div>
      </aside>
      <main id="contenu" className="content">
        {children}
      </main>
    </div>
  );
}
