"use client";

import { useRouter } from "next/navigation";
import type { ReactNode } from "react";
import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { ApiError, api } from "@/lib/api";
import type { Me, MembershipSummary } from "@/lib/types";
import { ErrorMessage, Loading } from "@/components/ui";

type MeContextValue = { me: Me; refresh: () => Promise<void> };

const MeContext = createContext<MeContextValue | null>(null);

export function MeProvider({ children }: { children: ReactNode }) {
  const router = useRouter();
  const [me, setMe] = useState<Me | null>(null);
  const [error, setError] = useState<unknown>(null);

  const refresh = useCallback(async () => {
    try {
      setMe(await api<Me>("/v1/auth/me"));
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        router.replace("/connexion");
        return;
      }
      setError(err);
    }
  }, [router]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  if (error) return <main className="centered"><ErrorMessage error={error} /></main>;
  if (!me) return <main className="centered"><Loading /></main>;
  return <MeContext.Provider value={{ me, refresh }}>{children}</MeContext.Provider>;
}

export function useMe(): MeContextValue {
  const value = useContext(MeContext);
  if (!value) throw new Error("useMe outside MeProvider");
  return value;
}

export function useMembership(orgId: string): MembershipSummary | undefined {
  return useMe().me.memberships.find((m) => m.organization.id === orgId);
}

export function can(membership: MembershipSummary | undefined, permission: string): boolean {
  return Boolean(membership?.permissions.includes(permission));
}
