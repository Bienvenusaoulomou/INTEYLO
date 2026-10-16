import type { Metadata } from "next";
import { getTranslations } from "next-intl/server";
import { PlatformView } from "@/components/views/PlatformView";

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations();
  return { title: t("platform.pageTitle") };
}

export default function PlatformPage() {
  return <PlatformView />;
}
