"""
Base scraper class for Klara Greenhouse component sourcing.
All vendor scrapers inherit from this class and implement fetch/normalize/validate.
"""
import hashlib
import json
import logging
import time
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "greenhouse_components"
META_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "_meta"


class EvidenceMetadata:
    """Provenance metadata for every data point."""

    def __init__(self, source_url: str, extraction_method: str = "scraped",
                 data_confidence: str = "confirmed", notes: str | None = None):
        self.source_url = source_url
        self.fetch_date = datetime.now(timezone.utc).isoformat()
        self.extraction_method = extraction_method  # 'scraped' | 'manual' | 'api'
        self.data_confidence = data_confidence  # 'confirmed' | 'assumed' | 'unknown'
        self.verified_by = "automated" if extraction_method == "scraped" else None
        self.notes = notes

    def to_dict(self) -> dict:
        return {
            "source_url": self.source_url,
            "fetch_date": self.fetch_date,
            "extraction_method": self.extraction_method,
            "data_confidence": self.data_confidence,
            "verified_by": self.verified_by,
            "notes": self.notes,
        }


class ValidationReport:
    """Report from validation pass on scraped products."""

    def __init__(self):
        self.valid: list[dict] = []
        self.warnings: list[dict] = []
        self.errors: list[dict] = []

    def add_valid(self, product_id: str, message: str = ""):
        self.valid.append({"product_id": product_id, "message": message})

    def add_warning(self, product_id: str, field: str, message: str):
        self.warnings.append({"product_id": product_id, "field": field, "message": message})

    def add_error(self, product_id: str, field: str, message: str):
        self.errors.append({"product_id": product_id, "field": field, "message": message})

    def to_dict(self) -> dict:
        return {
            "valid_count": len(self.valid),
            "warning_count": len(self.warnings),
            "error_count": len(self.errors),
            "valid": self.valid,
            "warnings": self.warnings,
            "errors": self.errors,
        }


def compute_spec_completeness(product: dict, required_fields: list[str], optional_fields: list[str]) -> int:
    """Score 0-100 based on how many fields are populated and non-null."""
    total = len(required_fields) + len(optional_fields)
    if total == 0:
        return 100
    filled = 0
    for f in required_fields:
        val = product.get(f)
        if val is not None and val != "" and val != []:
            filled += 1
    for f in optional_fields:
        val = product.get(f)
        if val is not None and val != "" and val != []:
            filled += 1
    return int((filled / total) * 100)


def product_hash(product: dict) -> str:
    """Deterministic hash of product data for delta detection.
    Excludes volatile fields (fetch_date, stale)."""
    stable = {k: v for k, v in product.items()
              if k not in ("evidence", "last_verified", "stale", "spec_completeness_score")}
    return hashlib.sha256(json.dumps(stable, sort_keys=True, default=str).encode()).hexdigest()


class BaseScraper(ABC):
    """Abstract base scraper. All vendor scrapers inherit from this."""

    vendor_name: str = ""
    vendor_url: str = ""
    category: str = ""  # structures | hydroponic | lighting | sensors | renewable | biological
    requires_manual: bool = False
    rate_limit_seconds: float = 2.0

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "KlaraDataCollector/1.0 (+https://blackpointanalytics.ca/klara)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-CA,en;q=0.9",
        })
        self._last_request_time = 0.0

    def _rate_limited_get(self, url: str, **kwargs) -> requests.Response | None:
        """GET with rate limiting and error handling."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.rate_limit_seconds:
            time.sleep(self.rate_limit_seconds - elapsed)

        try:
            resp = self.session.get(url, timeout=15, **kwargs)
            self._last_request_time = time.time()

            if resp.status_code == 403:
                logger.warning(f"[{self.vendor_name}] 403 Forbidden at {url} — marking as requires_manual")
                self.requires_manual = True
                return None
            if resp.status_code == 429:
                logger.warning(f"[{self.vendor_name}] 429 Rate Limited at {url}")
                time.sleep(10)
                return None
            resp.raise_for_status()
            return resp
        except requests.RequestException as e:
            logger.error(f"[{self.vendor_name}] Request failed for {url}: {e}")
            return None

    def _make_product_id(self, model: str) -> str:
        """Generate a slug-style product_id."""
        vendor_slug = self.vendor_name.lower().replace(" ", "_").replace("'", "")
        model_slug = model.lower().replace(" ", "_").replace("'", "").replace("/", "_")
        return f"{vendor_slug}_{model_slug}"

    def _base_product(self, product_name: str, product_url: str,
                      price_cad: float | None = None,
                      price_source: str = "unknown") -> dict:
        """Create base product dict with common fields."""
        return {
            "product_id": self._make_product_id(product_name),
            "product_name": product_name,
            "vendor_name": self.vendor_name,
            "vendor_url": self.vendor_url,
            "product_url": product_url,
            "price_cad": price_cad,
            "price_source": price_source,
            "ships_to_ns": None,
            "ships_to_pei": None,
            "delivery_cost_estimate_cad": None,
            "delivery_source": "unknown",
            "klara_system_fit": "standard",
            "meets_minimum_spec": True,
            "spec_gap_notes": None,
            "evidence": EvidenceMetadata(
                source_url=product_url,
                extraction_method="scraped",
            ).to_dict(),
            "spec_completeness_score": 0,
            "last_verified": datetime.now(timezone.utc).isoformat(),
            "stale": False,
        }

    @abstractmethod
    def fetch(self) -> list[dict]:
        """Retrieve raw product data from vendor source."""
        ...

    @abstractmethod
    def normalize(self, raw: list[dict]) -> list[dict]:
        """Map raw data to canonical schema. Fill evidence metadata."""
        ...

    @abstractmethod
    def validate(self, products: list[dict]) -> ValidationReport:
        """Check against minimum specs. Flag suspicious data."""
        ...

    def run(self) -> dict:
        """Execute full scrape pipeline: fetch → normalize → validate → save."""
        result = {
            "vendor": self.vendor_name,
            "category": self.category,
            "requires_manual": self.requires_manual,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "products_found": 0,
            "products_valid": 0,
            "warnings": 0,
            "errors": 0,
            "validation_report": {},
        }

        if self.requires_manual:
            logger.info(f"[{self.vendor_name}] Marked as requires_manual — skipping automated scrape")
            result["completed_at"] = datetime.now(timezone.utc).isoformat()
            return result

        try:
            raw = self.fetch()
            if not raw:
                logger.warning(f"[{self.vendor_name}] No raw data fetched")
                result["completed_at"] = datetime.now(timezone.utc).isoformat()
                return result

            products = self.normalize(raw)
            report = self.validate(products)

            result["products_found"] = len(products)
            result["products_valid"] = len(report.valid)
            result["warnings"] = len(report.warnings)
            result["errors"] = len(report.errors)
            result["validation_report"] = report.to_dict()

            # Save to data directory
            self._save_products(products)

        except Exception as e:
            logger.error(f"[{self.vendor_name}] Scrape failed: {e}", exc_info=True)
            result["errors"] = 1
            result["validation_report"] = {"fatal_error": str(e)}

        result["completed_at"] = datetime.now(timezone.utc).isoformat()
        return result

    def _save_products(self, products: list[dict]):
        """Save products to data/greenhouse_components/{category}/{vendor}.json"""
        out_dir = DATA_DIR / self.category
        out_dir.mkdir(parents=True, exist_ok=True)

        vendor_slug = self.vendor_name.lower().replace(" ", "_").replace("'", "")
        out_file = out_dir / f"{vendor_slug}.json"

        # Delta detection
        previous = []
        if out_file.exists():
            try:
                previous = json.loads(out_file.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                previous = []

        prev_hashes = {p.get("product_id"): product_hash(p) for p in previous}
        changes = []
        for p in products:
            pid = p.get("product_id")
            new_hash = product_hash(p)
            if pid in prev_hashes and prev_hashes[pid] != new_hash:
                changes.append({
                    "product_id": pid,
                    "detected_at": datetime.now(timezone.utc).isoformat(),
                    "action": "updated",
                })
            elif pid not in prev_hashes:
                changes.append({
                    "product_id": pid,
                    "detected_at": datetime.now(timezone.utc).isoformat(),
                    "action": "new",
                })

        if changes:
            self._log_deltas(changes)

        out_file.write_text(json.dumps(products, indent=2, default=str), encoding="utf-8")
        logger.info(f"[{self.vendor_name}] Saved {len(products)} products to {out_file}")

    def _log_deltas(self, changes: list[dict]):
        """Append changes to delta changelog."""
        META_DIR.mkdir(parents=True, exist_ok=True)
        changelog_file = META_DIR / "delta_changelog.json"

        existing = []
        if changelog_file.exists():
            try:
                existing = json.loads(changelog_file.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                existing = []

        existing.extend(changes)
        changelog_file.write_text(json.dumps(existing, indent=2, default=str), encoding="utf-8")
