import type { ReactNode } from "react";
import { AppShell } from "@/components/AppShell";
import { MeProvider } from "@/components/MeProvider";

export default function AuthenticatedLayout({ children }: { children: ReactNode }) {
  return (
    <MeProvider>
      <AppShell>{children}</AppShell>
    </MeProvider>
  );
}
