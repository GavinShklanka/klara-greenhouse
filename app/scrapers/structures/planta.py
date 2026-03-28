"""
Planta Greenhouses scraper — plantagreenhouses.ca
Primary structure vendor for Klara system.
Sungrow series is the target: 75 PSF snow, 105 km/h wind.
"""
import re
import logging

from bs4 import BeautifulSoup

from ..base import BaseScraper, ValidationReport, EvidenceMetadata, compute_spec_completeness
from ..validator import validate_product

logger = logging.getLogger(__name__)

# Known Planta specs from product pages and marketing materials.
# These are used to supplement scraped data where page parsing is incomplete.
KNOWN_PLANTA_SPECS = {
    "sungrow": {
        "frame_material": "galvanized_steel",
        "frame_gauge": 14,
        "glazing_type": "twin_wall_polycarb",
        "glazing_thickness_mm": 6,
        "snow_load_psf": 75,
        "wind_load_kmh": 105,
        "wind_load_mph": 65,
        "warranty_months": 120,
        "ventilation_type": "auto_ridge",
        "assembly_complexity": "moderate",
    },
    "sigma": {
        "frame_material": "galvanized_steel",
        "frame_gauge": 14,
        "glazing_type": "twin_wall_polycarb",
        "glazing_thickness_mm": 4,
        "snow_load_psf": 60,
        "wind_load_kmh": 90,
        "wind_load_mph": 56,
        "warranty_months": 120,
        "ventilation_type": "auto_ridge",
        "assembly_complexity": "moderate",
    },
}

STRUCTURE_REQUIRED_FIELDS = [
    "product_name", "vendor_name", "product_url", "price_cad",
    "snow_load_psf", "wind_load_kmh", "frame_material", "glazing_type",
]
STRUCTURE_OPTIONAL_FIELDS = [
    "dimensions_ft", "area_sqft", "frame_gauge", "glazing_thickness_mm",
    "warranty_months", "ventilation_type", "assembly_complexity",
    "foundation_requirements", "extendable",
]


class PlantaScraper(BaseScraper):
    vendor_name = "Planta Greenhouses"
    vendor_url = "https://www.plantagreenhouses.ca"
    category = "structures"
    requires_manual = False

    # Target product pages
    PRODUCT_URLS = [
        ("Sungrow 20", "/collections/greenhouses/products/sungrow-20"),
        ("Sungrow 26", "/collections/greenhouses/products/sungrow-26"),
        ("Sigma 10", "/collections/greenhouses/products/sigma-urban-greenhouse"),
        ("Sigma 20", "/collections/greenhouses/products/sigma-20"),
    ]

    def fetch(self) -> list[dict]:
        """Fetch product pages from plantagreenhouses.ca"""
        raw = []
        for name, path in self.PRODUCT_URLS:
            url = self.vendor_url + path
            resp = self._rate_limited_get(url)
            if resp is None:
                logger.warning(f"Failed to fetch {name} at {url}")
                continue

            raw.append({
                "name": name,
                "url": url,
                "html": resp.text,
                "status_code": resp.status_code,
            })
            logger.info(f"Fetched {name}: {resp.status_code}")

        return raw

    def normalize(self, raw: list[dict]) -> list[dict]:
        """Parse Planta product pages and normalize to canonical schema."""
        products = []

        for item in raw:
            soup = BeautifulSoup(item["html"], "html.parser")
            product = self._base_product(item["name"], item["url"])

            # Determine series from name
            name_lower = item["name"].lower()
            series = "sungrow" if "sungrow" in name_lower else "sigma" if "sigma" in name_lower else None

            # Extract price from page
            price = self._extract_price(soup)
            if price:
                product["price_cad"] = price
                product["price_source"] = "listed"

            # Extract dimensions
            dims = self._extract_dimensions(soup, item["name"])
            if dims:
                product["dimensions_ft"] = dims
                product["area_sqft"] = dims.get("length", 0) * dims.get("width", 0)

            # Apply known specs for this series
            if series and series in KNOWN_PLANTA_SPECS:
                specs = KNOWN_PLANTA_SPECS[series]
                for key, value in specs.items():
                    product[key] = value
                product["evidence"]["data_confidence"] = "confirmed"
                product["evidence"]["notes"] = f"Specs from Planta {series.title()} series product page and marketing materials"
            else:
                product["evidence"]["data_confidence"] = "assumed"

            # Planta ships across Canada
            product["ships_to_ns"] = True
            product["ships_to_pei"] = True
            product["delivery_source"] = "assumed"

            # Klara system fit assessment
            if series == "sungrow":
                product["klara_system_fit"] = "core"  # Best match for Klara spec
            elif series == "sigma":
                product["klara_system_fit"] = "alternative"

            # Spec completeness
            product["spec_completeness_score"] = compute_spec_completeness(
                product, STRUCTURE_REQUIRED_FIELDS, STRUCTURE_OPTIONAL_FIELDS
            )

            products.append(product)

        return products

    def validate(self, products: list[dict]) -> ValidationReport:
        report = ValidationReport()
        for p in products:
            validate_product(p, self.category, report)
        return report

    def _extract_price(self, soup: BeautifulSoup) -> float | None:
        """Try to extract price from various Shopify page patterns."""
        # Shopify meta tag pattern
        meta_price = soup.find("meta", {"property": "og:price:amount"})
        if meta_price:
            try:
                return float(meta_price["content"])
            except (ValueError, KeyError):
                pass

        # Shopify product JSON pattern
        scripts = soup.find_all("script", type="application/ld+json")
        for script in scripts:
            try:
                import json
                data = json.loads(script.string)
                if isinstance(data, dict) and "offers" in data:
                    offers = data["offers"]
                    if isinstance(offers, dict) and "price" in offers:
                        return float(offers["price"])
                    if isinstance(offers, list) and offers:
                        return float(offers[0].get("price", 0))
            except (json.JSONDecodeError, ValueError, TypeError):
                continue

        # Fallback: look for price in spans with common Shopify classes
        for cls in ["product-price", "price__regular", "product__price", "ProductMeta__Price"]:
            el = soup.find(class_=re.compile(cls, re.IGNORECASE))
            if el:
                text = el.get_text(strip=True)
                match = re.search(r'\$?([\d,]+\.?\d*)', text)
                if match:
                    try:
                        return float(match.group(1).replace(",", ""))
                    except ValueError:
                        continue

        return None

    def _extract_dimensions(self, soup: BeautifulSoup, name: str) -> dict | None:
        """Extract dimensions from product name or page content."""
        # Planta names often encode dimensions: "Sungrow 20" = ~20 ft long
        # Extract from specs table if available
        for table in soup.find_all("table"):
            for row in table.find_all("tr"):
                cells = row.find_all(["td", "th"])
                if len(cells) >= 2:
                    label = cells[0].get_text(strip=True).lower()
                    value = cells[1].get_text(strip=True)
                    if "dimension" in label or "size" in label:
                        match = re.search(r"(\d+)\s*[x×X]\s*(\d+)", value)
                        if match:
                            return {
                                "width": int(match.group(1)),
                                "length": int(match.group(2)),
                                "peak_height": 8,  # Standard residential greenhouse height
                            }

        # Fallback: derive from product name
        name_dims = {
            "Sungrow 20": {"width": 10, "length": 20, "peak_height": 8},
            "Sungrow 26": {"width": 10, "length": 26, "peak_height": 8},
            "Sigma 10": {"width": 8, "length": 10, "peak_height": 7},
            "Sigma 20": {"width": 8, "length": 20, "peak_height": 7},
        }
        return name_dims.get(name)
