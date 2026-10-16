"use client";

import { useTranslations } from "next-intl";
import type { FormEvent } from "react";
import { useState } from "react";
import { can, useMe, useMembership } from "@/components/MeProvider";
import { useOrganization } from "@/components/views/useOrganization";
import {
  Alert,
  Button,
  ErrorMessage,
  Loading,
  PageHeader,
  PermissionLabel,
  RoleBadge,
  TextField,
} from "@/components/ui";
import { ApiError, patch } from "@/lib/api";
import { formatDate } from "@/lib/format";
import type { Organization } from "@/lib/types";

// Modules du blueprint, présentés honnêtement : aucun n'est encore disponible en phase 1.
const UPCOMING_MODULES = [
  "connectorHub",
  "businessGraph",
  "metricRegistry",
  "evidenceEngine",
  "opportunityRadar",
  "decisionSimulator",
  "actionEngine",
  "decisionMemory",
] as const;

export function OverviewView({ orgId }: { orgId: string }) {
  const t = useTranslations();
  const { refresh } = useMe();
  const membership = useMembership(orgId);
  const { org, setOrg, error } = useOrganization(orgId);
  const [saveError, setSaveError] = useState<unknown>(null);
  const [saved, setSaved] = useState(false);
  const [busy, setBusy] = useState(false);

  if (error) return <ErrorMessage error={error} />;
  if (!org || !membership) return <Loading />;

  async function onSave(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    setBusy(true);
    setSaveError(null);
    setSaved(false);
    try {
      const updated = await patch<Organization>(`/v1/orgs/${orgId}`, {
        name: form.get("name"),
        timezone: form.get("timezone"),
      });
      setOrg(updated);
      setSaved(true);
      await refresh();
    } catch (err) {
      setSaveError(err);
    } finally {
      setBusy(false);
    }
  }

  const fieldError = (name: string) =>
    saveError instanceof ApiError ? saveError.fieldMessage(name) : undefined;

  return (
    <>
      <PageHeader title={org.name} description={t("organization.description")} />
      <section className="panel-grid">
        <div className="panel">
          <h2>{t("organization.identity.title")}</h2>
          <dl className="facts">
            <dt>{t("organization.identity.createdAt")}</dt>
            <dd>{formatDate(org.created_at, org.timezone)}</dd>
            <dt>{t("organization.identity.timezone")}</dt>
            <dd>{org.timezone}</dd>
            <dt>{t("organization.identity.yourRoles")}</dt>
            <dd className="badges">
              {membership.roles.map((r) => (
                <RoleBadge key={r} role={r} />
              ))}
            </dd>
          </dl>
        </div>
        <div className="panel">
          <h2>{t("organization.permissions.title")}</h2>
          <ul className="permission-list">
            {membership.permissions.map((p) => (
              <li key={p}>
                <PermissionLabel permission={p} />
              </li>
            ))}
          </ul>
        </div>
      </section>

      {can(membership, "organizations.manage") ? (
        <section className="panel">
          <h2>{t("organization.settings.title")}</h2>
          <form className="inline-form" onSubmit={onSave} noValidate>
            <TextField label={t("organization.settings.name")} name="name" defaultValue={org.name} error={fieldError("name")} />
            <TextField
              label={t("organization.settings.timezone")}
              name="timezone"
              defaultValue={org.timezone}
              hint={t("organization.settings.timezoneHint")}
              error={fieldError("timezone")}
            />
            <Button type="submit" busy={busy}>
              {t("common.save")}
            </Button>
          </form>
          <ErrorMessage error={saveError} />
          {saved ? <Alert tone="success">{t("organization.settings.saved")}</Alert> : null}
        </section>
      ) : null}

      <section className="panel">
        <h2>{t("organization.modules.title")}</h2>
        <p className="muted">{t("organization.modules.description")}</p>
        <ul className="module-list">
          {UPCOMING_MODULES.map((key) => (
            <li key={key}>
              <span>{t(`modules.${key}`)}</span>
              <span className="badge badge-soon">{t("organization.modules.soon")}</span>
            </li>
          ))}
        </ul>
      </section>
    </>
  );
}
