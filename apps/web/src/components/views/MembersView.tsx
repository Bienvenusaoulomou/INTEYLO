"use client";

import { useTranslations } from "next-intl";
import type { FormEvent } from "react";
import { useCallback, useEffect, useState } from "react";
import { can, useMe, useMembership } from "@/components/MeProvider";
import { useOrganization } from "@/components/views/useOrganization";
import {
  Alert,
  Button,
  EmptyState,
  ErrorMessage,
  Loading,
  PageHeader,
  RoleBadge,
  SelectField,
  StatusBadge,
  TextField,
} from "@/components/ui";
import { ApiError, api, del, post, put } from "@/lib/api";
import { formatDate, formatDateTime } from "@/lib/format";
import type { Invitation, InvitationCreated, Member, Role } from "@/lib/types";

export function MembersView({ orgId }: { orgId: string }) {
  const t = useTranslations();
  const { me } = useMe();
  const membership = useMembership(orgId);
  const { org } = useOrganization(orgId);
  const [members, setMembers] = useState<Member[] | null>(null);
  const [roles, setRoles] = useState<Role[]>([]);
  const [invitations, setInvitations] = useState<Invitation[]>([]);
  const [error, setError] = useState<unknown>(null);
  const [actionError, setActionError] = useState<unknown>(null);
  const [created, setCreated] = useState<InvitationCreated | null>(null);
  const [copied, setCopied] = useState(false);
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    try {
      const [m, r, i] = await Promise.all([
        api<Member[]>(`/v1/orgs/${orgId}/members`),
        api<Role[]>(`/v1/orgs/${orgId}/roles`),
        api<Invitation[]>(`/v1/orgs/${orgId}/invitations`),
      ]);
      setMembers(m);
      setRoles(r);
      setInvitations(i);
    } catch (err) {
      setError(err);
    }
  }, [orgId]);

  useEffect(() => {
    void load();
  }, [load]);

  if (error) return <ErrorMessage error={error} />;
  if (!members || !membership || !org) return <Loading />;

  const assignable = roles.filter((r) => r.assignable);
  const canInvite = can(membership, "users.invite");
  const canManageRoles = can(membership, "roles.manage");
  const canManageUsers = can(membership, "users.manage");

  async function run(action: () => Promise<unknown>) {
    setActionError(null);
    try {
      await action();
      await load();
    } catch (err) {
      setActionError(err);
    }
  }

  async function onInvite(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const formElement = event.currentTarget;
    const form = new FormData(formElement);
    setBusy(true);
    setActionError(null);
    setCreated(null);
    setCopied(false);
    try {
      const invitation = await post<InvitationCreated>(`/v1/orgs/${orgId}/invitations`, {
        email: form.get("email"),
        role: form.get("role"),
      });
      setCreated(invitation);
      formElement.reset();
      await load();
    } catch (err) {
      setActionError(err);
    } finally {
      setBusy(false);
    }
  }

  async function copyLink() {
    if (!created) return;
    await navigator.clipboard.writeText(created.accept_url);
    setCopied(true);
  }

  const inviteFieldError = (name: string) =>
    actionError instanceof ApiError ? actionError.fieldMessage(name) : undefined;

  return (
    <>
      <PageHeader title={t("members.title")} description={t("members.description")} />
      <ErrorMessage error={actionError} />

      {canInvite ? (
        <section className="panel">
          <h2>{t("members.invite.title")}</h2>
          <form className="inline-form" onSubmit={onInvite} noValidate>
            <TextField label={t("members.invite.email")} name="email" type="email" required error={inviteFieldError("email")} />
            <SelectField label={t("members.invite.role")} name="role" defaultValue={assignable.at(-1)?.key}>
              {assignable.map((r) => (
                <option key={r.key} value={r.key}>
                  {t(`roles.${r.key}`)}
                </option>
              ))}
            </SelectField>
            <Button type="submit" busy={busy}>
              {t("members.invite.submit")}
            </Button>
          </form>
          {created ? (
            <Alert tone="success">
              <p>{t("members.invite.created", { email: created.email })}</p>
              <p className="muted">{t("members.invite.linkHelp")}</p>
              <div className="copy-row">
                <input readOnly value={created.accept_url} aria-label={t("members.invite.linkLabel")} />
                <Button type="button" variant="secondary" onClick={() => void copyLink()}>
                  {copied ? t("common.copied") : t("common.copy")}
                </Button>
              </div>
            </Alert>
          ) : null}
        </section>
      ) : null}

      <section className="panel">
        <h2>{t("members.list.title", { count: members.length })}</h2>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th scope="col">{t("members.list.name")}</th>
                <th scope="col">{t("members.list.roles")}</th>
                <th scope="col">{t("members.list.status")}</th>
                <th scope="col">{t("members.list.joinedAt")}</th>
                <th scope="col">
                  <span className="visually-hidden">{t("members.list.actions")}</span>
                </th>
              </tr>
            </thead>
            <tbody>
              {members.map((m) => {
                const isSelf = m.user.id === me.user.id;
                return (
                  <tr key={m.membership_id}>
                    <td>
                      <span className="cell-strong">{m.user.full_name}</span>
                      <span className="cell-sub">{m.user.email}</span>
                    </td>
                    <td className="badges">
                      {m.roles.map((r) => (
                        <RoleBadge key={r} role={r} />
                      ))}
                    </td>
                    <td>
                      <StatusBadge kind="member" value={m.status} />
                    </td>
                    <td>{formatDate(m.joined_at, org.timezone)}</td>
                    <td className="row-actions">
                      {isSelf ? (
                        <span className="muted">{t("members.list.you")}</span>
                      ) : (
                        <>
                          {canManageRoles && assignable.length ? (
                            <select
                              aria-label={t("members.list.changeRole", { name: m.user.full_name })}
                              value=""
                              onChange={(e) =>
                                e.target.value &&
                                void run(() => put(`/v1/orgs/${orgId}/members/${m.membership_id}/roles`, { roles: [e.target.value] }))
                              }
                            >
                              <option value="">{t("members.list.changeRolePlaceholder")}</option>
                              {assignable.map((r) => (
                                <option key={r.key} value={r.key}>
                                  {t(`roles.${r.key}`)}
                                </option>
                              ))}
                            </select>
                          ) : null}
                          {canManageUsers ? (
                            m.status === "active" ? (
                              <Button variant="danger" onClick={() => void run(() => post(`/v1/orgs/${orgId}/members/${m.membership_id}/disable`))}>
                                {t("members.list.disable")}
                              </Button>
                            ) : (
                              <Button variant="secondary" onClick={() => void run(() => post(`/v1/orgs/${orgId}/members/${m.membership_id}/enable`))}>
                                {t("members.list.enable")}
                              </Button>
                            )
                          ) : null}
                        </>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>

      <section className="panel">
        <h2>{t("members.invitations.title")}</h2>
        {invitations.length === 0 ? (
          <EmptyState title={t("members.invitations.empty")} />
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th scope="col">{t("members.invitations.email")}</th>
                  <th scope="col">{t("members.invitations.role")}</th>
                  <th scope="col">{t("members.invitations.status")}</th>
                  <th scope="col">{t("members.invitations.expiresAt")}</th>
                  <th scope="col">
                    <span className="visually-hidden">{t("members.list.actions")}</span>
                  </th>
                </tr>
              </thead>
              <tbody>
                {invitations.map((i) => (
                  <tr key={i.id}>
                    <td>
                      <span className="cell-strong">{i.email}</span>
                      {i.invited_by_name ? (
                        <span className="cell-sub">{t("members.invitations.invitedBy", { name: i.invited_by_name })}</span>
                      ) : null}
                    </td>
                    <td>
                      <RoleBadge role={i.role} />
                    </td>
                    <td>
                      <StatusBadge kind="invitation" value={i.status} />
                    </td>
                    <td>{formatDateTime(i.expires_at, org.timezone)}</td>
                    <td className="row-actions">
                      {i.status === "pending" && canInvite ? (
                        <Button variant="ghost" onClick={() => void run(() => del(`/v1/orgs/${orgId}/invitations/${i.id}`))}>
                          {t("members.invitations.revoke")}
                        </Button>
                      ) : null}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </>
  );
}
