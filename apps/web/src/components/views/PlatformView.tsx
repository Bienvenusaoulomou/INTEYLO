"use client";

import { useTranslations } from "next-intl";
import { useCallback, useEffect, useState } from "react";
import { useMe } from "@/components/MeProvider";
import { Alert, Button, ErrorMessage, Loading, PageHeader, StatusBadge } from "@/components/ui";
import { api, post } from "@/lib/api";
import { formatDate, formatNumber } from "@/lib/format";
import type { PlatformOrganization } from "@/lib/types";

export function PlatformView() {
  const t = useTranslations();
  const { me } = useMe();
  const [orgs, setOrgs] = useState<PlatformOrganization[] | null>(null);
  const [error, setError] = useState<unknown>(null);
  const timeZone = Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC";

  const load = useCallback(async () => {
    try {
      setOrgs(await api<PlatformOrganization[]>("/v1/platform/organizations"));
    } catch (err) {
      setError(err);
    }
  }, []);

  useEffect(() => {
    if (me.user.is_platform_admin) void load();
  }, [load, me.user.is_platform_admin]);

  if (!me.user.is_platform_admin) return <Alert>{t("platform.forbidden")}</Alert>;

  async function setStatus(id: string, action: "suspend" | "reactivate") {
    try {
      await post(`/v1/platform/organizations/${id}/${action}`);
      await load();
    } catch (err) {
      setError(err);
    }
  }

  return (
    <>
      <PageHeader title={t("platform.title")} description={t("platform.description")} />
      <ErrorMessage error={error} />
      {!orgs ? (
        <Loading />
      ) : (
        <section className="panel">
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th scope="col">{t("platform.columns.name")}</th>
                  <th scope="col">{t("platform.columns.status")}</th>
                  <th scope="col">{t("platform.columns.members")}</th>
                  <th scope="col">{t("platform.columns.createdAt")}</th>
                  <th scope="col">
                    <span className="visually-hidden">{t("members.list.actions")}</span>
                  </th>
                </tr>
              </thead>
              <tbody>
                {orgs.map((o) => (
                  <tr key={o.id}>
                    <td className="cell-strong">{o.name}</td>
                    <td>
                      <StatusBadge kind="organization" value={o.status} />
                    </td>
                    <td>{formatNumber(o.active_members)}</td>
                    <td>{formatDate(o.created_at, timeZone)}</td>
                    <td className="row-actions">
                      {o.status === "active" ? (
                        <Button variant="danger" onClick={() => void setStatus(o.id, "suspend")}>
                          {t("platform.suspend")}
                        </Button>
                      ) : (
                        <Button variant="secondary" onClick={() => void setStatus(o.id, "reactivate")}>
                          {t("platform.reactivate")}
                        </Button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </>
  );
}
