"""AliExpress storefronts: site host, language, currency and region sent as the standard preference cookie."""

import os

from pydantic import BaseModel


class Locale(BaseModel):
    site: str
    lang: str
    currency: str
    region: str
    site_code: str  # AliExpress internal code for the storefront ("ita", "deu", "glo")

    @property
    def base_url(self) -> str:
        return f"https://{self.site}"

    @property
    def cookie(self) -> str:
        return f"aep_usuc_f=site={self.site_code}&c_tp={self.currency}&region={self.region}&b_locale={self.lang}"

    @property
    def accept_language(self) -> str:
        return self.lang.replace("_", "-")


LOCALES = {
    "it": Locale(site="it.aliexpress.com", lang="it_IT", currency="EUR", region="IT", site_code="ita"),
    "de": Locale(site="de.aliexpress.com", lang="de_DE", currency="EUR", region="DE", site_code="deu"),
    "us": Locale(site="www.aliexpress.com", lang="en_US", currency="USD", region="US", site_code="glo"),
}
DEFAULT_LOCALE = "it"


def get(name: str | None = None) -> Locale:
    """Locale by name, falling back to the ALI_SCOUT_LOCALE environment variable, then to Italy."""
    key = name or os.environ.get("ALI_SCOUT_LOCALE", DEFAULT_LOCALE)
    if key not in LOCALES:
        raise ValueError(f"unknown locale '{key}', available: {', '.join(LOCALES)}")
    return LOCALES[key]
