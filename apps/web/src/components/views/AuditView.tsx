"use client";

import { useTranslations } from "next-intl";
import { useCallback, useEffect, useState } from "react";
import { useOrganization } from "@/components/views/useOrganization";
import { Button, EmptyState, ErrorMessage, Loading, PageHeader, StatusBadge } from "@/components/ui";
import { api } from "@/lib/api";
import { catalogKey, formatDateTime } from "@/lib/format";
import type { AuditPage } from "@/lib/types";

const PAGE_SIZE = 50;

export function AuditView({ orgId }: { orgId: string }) {
  const t = useTranslations();
  const { org } = useOrganization(orgId);
  const [page, setPage] = useState<AuditPage | null>(null);
  const [offset, setOffset] = useState(0);
  const [error, setError] = useState<unknown>(null);

  const load = useCallback(async () => {
    try {
      setPage(await api<AuditPage>(`/v1/orgs/${orgId}/audit?limit=${PAGE_SIZE}&offset=${offset}`));
    } catch (err) {
      setError(err);
    }
  }, [orgId, offset]);

  useEffect(() => {
    void load();
  }, [load]);

  if (error) return <ErrorMessage error={error} />;
  if (!page || !org) return <Loading />;

  return (
    <>
      <PageHeader title={t("audit.title")} description={t("audit.description", { timezone: org.timezone })} />
      <section className="panel">
        {page.items.length === 0 ? (
          <EmptyState title={t("audit.empty")} />
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th scope="col">{t("audit.columns.date")}</th>
                  <th scope="col">{t("audit.columns.action")}</th>
                  <th scope="col">{t("audit.columns.outcome")}</th>
                  <th scope="col">{t("audit.columns.actor")}</th>
                  <th scope="col">{t("audit.columns.ip")}</th>
                </tr>
              </thead>
              <tbody>
                {page.items.map((e) => (
                  <tr key={e.id}>
                    <td className="nowrap">{formatDateTime(e.created_at, org.timezone)}</td>
                    <td>{t(`auditActions.${catalogKey(e.action)}`)}</td>
                    <td>
                      <StatusBadge kind="outcome" value={e.outcome} />
                    </td>
                    <td>{e.actor_email ?? t("audit.systemActor")}</td>
                    <td className="cell-mono">{e.ip_address ?? t("common.emptyValue")}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        <div className="pager">
          <Button variant="secondary" disabled={offset === 0} onClick={() => setOffset(Math.max(0, offset - PAGE_SIZE))}>
            {t("audit.previous")}
          </Button>
          <Button variant="secondary" disabled={page.items.length < PAGE_SIZE} onClick={() => setOffset(offset + PAGE_SIZE)}>
            {t("audit.next")}
          </Button>
        </div>
      </section>
    </>
  );
}
