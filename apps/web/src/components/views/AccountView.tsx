"use client";

import { useTranslations } from "next-intl";
import { useCallback, useEffect, useState } from "react";
import { useMe } from "@/components/MeProvider";
import { Alert, Button, ErrorMessage, Loading, PageHeader } from "@/components/ui";
import { api, del, post } from "@/lib/api";
import { formatDateTime } from "@/lib/format";
import type { SessionInfo } from "@/lib/types";

export function AccountView() {
  const t = useTranslations();
  const { me } = useMe();
  const [sessions, setSessions] = useState<SessionInfo[] | null>(null);
  const [error, setError] = useState<unknown>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const timeZone = Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC";

  const load = useCallback(async () => {
    try {
      setSessions(await api<SessionInfo[]>("/v1/auth/sessions"));
    } catch (err) {
      setError(err);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  async function revoke(id: string) {
    try {
      await del(`/v1/auth/sessions/${id}`);
      await load();
    } catch (err) {
      setError(err);
    }
  }

  async function revokeOthers() {
    try {
      const { revoked } = await post<{ revoked: number }>("/v1/auth/sessions/revoke-others");
      setNotice(t("account.sessions.revokedOthers", { count: revoked }));
      await load();
    } catch (err) {
      setError(err);
    }
  }

  return (
    <>
      <PageHeader title={t("account.title")} description={t("account.description")} />
      <section className="panel">
        <h2>{t("account.profile.title")}</h2>
        <dl className="facts">
          <dt>{t("account.profile.name")}</dt>
          <dd>{me.user.full_name}</dd>
          <dt>{t("account.profile.email")}</dt>
          <dd>{me.user.email}</dd>
        </dl>
      </section>
      <section className="panel">
        <div className="panel-heading">
          <h2>{t("account.sessions.title")}</h2>
          <Button variant="secondary" onClick={() => void revokeOthers()}>
            {t("account.sessions.revokeOthers")}
          </Button>
        </div>
        <p className="muted">{t("account.sessions.description")}</p>
        <ErrorMessage error={error} />
        {notice ? <Alert tone="success">{notice}</Alert> : null}
        {!sessions ? (
          <Loading />
        ) : (
          <ul className="session-list">
            {sessions.map((s) => (
              <li key={s.id}>
                <div>
                  <span className="cell-strong">
                    {s.current ? t("account.sessions.current") : t("account.sessions.other")}
                  </span>
                  <span className="cell-sub">
                    {t("account.sessions.lastSeen", { date: formatDateTime(s.last_seen_at, timeZone) })}
                  </span>
                  <span className="cell-sub cell-mono">{s.ip_address ?? t("common.emptyValue")}</span>
                </div>
                {!s.current ? (
                  <Button variant="ghost" onClick={() => void revoke(s.id)}>
                    {t("account.sessions.revoke")}
                  </Button>
                ) : null}
              </li>
            ))}
          </ul>
        )}
      </section>
    </>
  );
}
