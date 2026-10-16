"use client";

import { NextIntlClientProvider } from "next-intl";
import type { ReactNode } from "react";
import messages from "@messages/fr.json";
import { DEFAULT_TIME_ZONE, LOCALE, intlFallback, onIntlError } from "@/i18n/config";

export function IntlProvider({ children }: { children: ReactNode }) {
  return (
    <NextIntlClientProvider
      locale={LOCALE}
      messages={messages}
      timeZone={DEFAULT_TIME_ZONE}
      onError={onIntlError}
      getMessageFallback={intlFallback}
    >
      {children}
    </NextIntlClientProvider>
  );
}
