import type { Metadata } from "next";
import { getTranslations } from "next-intl/server";
import { AccountView } from "@/components/views/AccountView";

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations();
  return { title: t("account.pageTitle") };
}

export default function AccountPage() {
  return <AccountView />;
}
