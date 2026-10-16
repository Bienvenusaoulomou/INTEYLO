export type User = {
  id: string;
  email: string;
  full_name: string;
  is_platform_admin: boolean;
};

export type MembershipSummary = {
  organization: { id: string; name: string; status: string };
  roles: string[];
  permissions: string[];
};

export type Me = { user: User; memberships: MembershipSummary[] };

export type Organization = {
  id: string;
  name: string;
  status: string;
  locale: string;
  timezone: string;
  created_at: string;
};

export type Member = {
  membership_id: string;
  user: { id: string; email: string; full_name: string };
  status: "active" | "disabled";
  roles: string[];
  joined_at: string;
};

export type Role = { key: string; rank: number; permissions: string[]; assignable: boolean };

export type Invitation = {
  id: string;
  email: string;
  role: string;
  status: "pending" | "accepted" | "revoked" | "expired";
  created_at: string;
  expires_at: string;
  invited_by_name: string | null;
};

export type InvitationCreated = Invitation & { accept_url: string };

export type InvitationPreview = {
  organization_name: string;
  email: string;
  role: string;
  expires_at: string;
  account_exists: boolean;
};

export type AuditEvent = {
  id: string;
  created_at: string;
  action: string;
  outcome: "success" | "denied" | "failure";
  actor_email: string | null;
  target_type: string | null;
  target_id: string | null;
  details: Record<string, unknown>;
  ip_address: string | null;
};

export type AuditPage = { items: AuditEvent[]; limit: number; offset: number };

export type SessionInfo = {
  id: string;
  created_at: string;
  last_seen_at: string;
  expires_at: string;
  ip_address: string | null;
  user_agent: string | null;
  current: boolean;
};

export type PlatformOrganization = {
  id: string;
  name: string;
  status: string;
  created_at: string;
  active_members: number;
};
