"use client";

import Link from "next/link";
import { useTranslations } from "next-intl";
import { useMe } from "@/components/MeProvider";
import { EmptyState, PageHeader, RoleBadge, StatusBadge } from "@/components/ui";

export function WorkspaceView() {
  const t = useTranslations();
  const { me } = useMe();
  return (
    <>
      <PageHeader
        title={t("workspace.title", { name: me.user.full_name })}
        description={t("workspace.description")}
      />
      {me.memberships.length === 0 ? (
        <EmptyState title={t("workspace.empty.title")} description={t("workspace.empty.description")} />
      ) : (
        <ul className="card-grid">
          {me.memberships.map((m) => (
            <li key={m.organization.id}>
              <Link className="card card-link" href={`/organisations/${m.organization.id}`}>
                <span className="card-title">{m.organization.name}</span>
                <span className="card-meta">
                  {m.roles.map((r) => (
                    <RoleBadge key={r} role={r} />
                  ))}
                  {m.organization.status !== "active" ? (
                    <StatusBadge kind="organization" value={m.organization.status} />
                  ) : null}
                </span>
                <span className="card-cta">{t("workspace.open")}</span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </>
  );
}
