import type { Metadata } from "next";
import { getTranslations } from "next-intl/server";
import { MembersView } from "@/components/views/MembersView";

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations();
  return { title: t("members.pageTitle") };
}

export default async function MembersPage({ params }: { params: Promise<{ orgId: string }> }) {
  const { orgId } = await params;
  return <MembersView orgId={orgId} />;
}
