"use client";

import { useCallback, useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { Organization } from "@/lib/types";

export function useOrganization(orgId: string) {
  const [org, setOrg] = useState<Organization | null>(null);
  const [error, setError] = useState<unknown>(null);

  const reload = useCallback(async () => {
    try {
      setOrg(await api<Organization>(`/v1/orgs/${orgId}`));
      setError(null);
    } catch (err) {
      setError(err);
    }
  }, [orgId]);

  useEffect(() => {
    void reload();
  }, [reload]);

  return { org, setOrg, error, reload };
}
