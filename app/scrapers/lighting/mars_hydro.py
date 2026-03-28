"""
Mars Hydro scraper — marshydro.ca
Budget-tier LED grow lights for Persephone supplementation.
"""
import re
import json
import logging

from bs4 import BeautifulSoup

from ..base import BaseScraper, ValidationReport, compute_spec_completeness
from ..validator import validate_product

logger = logging.getLogger(__name__)

LIGHTING_REQUIRED = ["product_name", "vendor_name", "product_url", "price_cad", "wattage"]
LIGHTING_OPTIONAL = [
    "ppf_umol_s", "ppfd_umol_m2_s_at_18in", "efficacy_umol_j",
    "spectrum", "color_temp_k", "coverage_sqft", "diode_type",
    "dimmable", "lifespan_hours", "driver_type", "light_type",
]


class MarsHydroScraper(BaseScraper):
    vendor_name = "Mars Hydro"
    vendor_url = "https://www.marshydro.ca"
    category = "lighting"
    requires_manual = False

    # Target: bar-style LEDs suitable for greenhouse supplemental lighting, 100-200W range
    PRODUCT_URLS = [
        ("SP 150", "/products/mars-hydro-sp-150-led-grow-light"),
        ("SP 3000", "/products/mars-hydro-sp-3000-led-grow-light"),
        ("TS 1000", "/products/mars-hydro-ts-1000-led-grow-light"),
        ("TS 600", "/products/mars-hydro-ts-600-led-grow-light"),
    ]

    def fetch(self) -> list[dict]:
        raw = []
        for name, path in self.PRODUCT_URLS:
            url = self.vendor_url + path
            resp = self._rate_limited_get(url)
            if resp is None:
                continue
            raw.append({"name": name, "url": url, "html": resp.text})
            logger.info(f"Fetched {name}: {resp.status_code}")
        return raw

    def normalize(self, raw: list[dict]) -> list[dict]:
        products = []
        for item in raw:
            soup = BeautifulSoup(item["html"], "html.parser")
            product = self._base_product(item["name"], item["url"])
            product["light_type"] = "led_bar"
            product["spectrum"] = "full_spectrum"

            # Extract price
            price = self._extract_price(soup)
            if price:
                product["price_cad"] = price
                product["price_source"] = "listed"

            # Extract specs from page text
            page_text = soup.get_text(" ", strip=True)

            # Wattage
            watt_match = re.search(r'(\d+)\s*[Ww](?:att)?(?:\s|,|\.|\b)', page_text)
            if watt_match:
                product["wattage"] = int(watt_match.group(1))

            # PPF
            ppf_match = re.search(r'PPF[:\s]*(\d+)\s*µmol', page_text)
            if ppf_match:
                product["ppf_umol_s"] = int(ppf_match.group(1))

            # Efficacy
            eff_match = re.search(r'(\d+\.?\d*)\s*µmol/[Jj]', page_text)
            if eff_match:
                product["efficacy_umol_j"] = float(eff_match.group(1))

            # Coverage
            cov_match = re.search(r'(\d+)\s*[x×]\s*(\d+)', page_text)
            if cov_match:
                # Often given in inches or cm — convert to sqft estimate
                pass

            # Diode type
            if "lm301" in page_text.lower():
                product["diode_type"] = "Samsung LM301B"
            elif "osram" in page_text.lower():
                product["diode_type"] = "Osram"

            # Dimmable
            product["dimmable"] = "dimmable" in page_text.lower() or "dimmer" in page_text.lower()

            # Lifespan
            life_match = re.search(r'(\d{2,6})\s*hours?\s*(?:lifespan|life)', page_text, re.IGNORECASE)
            if life_match:
                product["lifespan_hours"] = int(life_match.group(1))

            product["ships_to_ns"] = True
            product["ships_to_pei"] = True

            product["spec_completeness_score"] = compute_spec_completeness(
                product, LIGHTING_REQUIRED, LIGHTING_OPTIONAL
            )

            products.append(product)

        return products

    def validate(self, products: list[dict]) -> ValidationReport:
        report = ValidationReport()
        for p in products:
            validate_product(p, self.category, report)
        return report

    def _extract_price(self, soup: BeautifulSoup) -> float | None:
        meta = soup.find("meta", {"property": "og:price:amount"})
        if meta:
            try:
                return float(meta["content"])
            except (ValueError, KeyError):
                pass

        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and "offers" in data:
                    offers = data["offers"]
                    if isinstance(offers, dict):
                        return float(offers.get("price", 0))
                    if isinstance(offers, list) and offers:
                        return float(offers[0].get("price", 0))
            except (json.JSONDecodeError, ValueError, TypeError):
                continue

        for cls in ["product-price", "price__regular", "price--regular"]:
            el = soup.find(class_=re.compile(cls, re.IGNORECASE))
            if el:
                match = re.search(r'\$?([\d,]+\.?\d*)', el.get_text(strip=True))
                if match:
                    try:
                        return float(match.group(1).replace(",", ""))
                    except ValueError:
                        continue
        return None
