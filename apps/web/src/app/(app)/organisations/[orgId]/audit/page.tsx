import type { Metadata } from "next";
import { getTranslations } from "next-intl/server";
import { AuditView } from "@/components/views/AuditView";

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations();
  return { title: t("audit.pageTitle") };
}

export default async function AuditPage({ params }: { params: Promise<{ orgId: string }> }) {
  const { orgId } = await params;
  return <AuditView orgId={orgId} />;
}
