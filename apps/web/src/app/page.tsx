import Link from "next/link";
import { getTranslations } from "next-intl/server";

export default async function HomePage() {
  const t = await getTranslations();
  return (
    <main className="landing">
      <div className="landing-inner">
        <p className="landing-brand">
          <span className="brand-mark" aria-hidden="true" />
          {t("brand.name")}
        </p>
        <h1>{t("home.title")}</h1>
        <p className="landing-lead">{t("brand.tagline")}</p>
        <ul className="landing-pillars">
          <li>
            <strong>{t("home.pillars.intelligence.title")}</strong>
            <span>{t("home.pillars.intelligence.text")}</span>
          </li>
          <li>
            <strong>{t("home.pillars.actions.title")}</strong>
            <span>{t("home.pillars.actions.text")}</span>
          </li>
          <li>
            <strong>{t("home.pillars.memory.title")}</strong>
            <span>{t("home.pillars.memory.text")}</span>
          </li>
        </ul>
        <div className="landing-actions">
          <Link className="btn btn-primary" href="/inscription">
            {t("home.cta.signup")}
          </Link>
          <Link className="btn btn-secondary" href="/connexion">
            {t("home.cta.login")}
          </Link>
        </div>
      </div>
    </main>
  );
}
