import type { Metadata } from "next";
import { getTranslations } from "next-intl/server";
import { InvitationAccept } from "@/components/auth/InvitationAccept";

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations();
  return { title: t("invitation.pageTitle") };
}

export default function InvitationPage() {
  return <InvitationAccept />;
}
