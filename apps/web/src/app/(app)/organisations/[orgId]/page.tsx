import type { Metadata } from "next";
import { getTranslations } from "next-intl/server";
import { OverviewView } from "@/components/views/OverviewView";

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations();
  return { title: t("organization.pageTitle") };
}

export default async function OverviewPage({ params }: { params: Promise<{ orgId: string }> }) {
  const { orgId } = await params;
  return <OverviewView orgId={orgId} />;
}
