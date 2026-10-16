import type { Metadata } from "next";
import { getTranslations } from "next-intl/server";
import { WorkspaceView } from "@/components/views/WorkspaceView";

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations();
  return { title: t("workspace.pageTitle") };
}

export default function WorkspacePage() {
  return <WorkspaceView />;
}
