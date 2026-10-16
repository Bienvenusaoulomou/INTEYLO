import { getRequestConfig } from "next-intl/server";
import messages from "@messages/fr.json";
import { DEFAULT_TIME_ZONE, LOCALE, onIntlError, intlFallback } from "@/i18n/config";

// Français uniquement au lancement (prompt maître, section 13).
// L'ajout d'une langue consistera à fournir un nouveau catalogue, sans toucher aux composants.
export default getRequestConfig(async () => ({
  locale: LOCALE,
  messages,
  timeZone: DEFAULT_TIME_ZONE,
  onError: onIntlError,
  getMessageFallback: intlFallback,
}));
