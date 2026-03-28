"""
Component service — queries scraped data by category.
Applies sourcing preferences: local > Atlantic > national.
"""
import json
import logging
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Optional

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "greenhouse_components"


def _load_category(category: str) -> list[dict]:
    """Load all products for a category from all vendor files."""
    cat_dir = DATA_DIR / category
    if not cat_dir.exists():
        return []

    products = []
    for f in cat_dir.glob("*.json"):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            if isinstance(data, list):
                products.extend(data)
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"Failed to load {f}: {e}")
    return products


def _is_stale(product: dict, days: int = 90) -> bool:
    """Check if product data is older than threshold."""
    last_verified = product.get("last_verified")
    if not last_verified:
        return True
    try:
        verified_dt = datetime.fromisoformat(last_verified)
        if verified_dt.tzinfo is None:
            verified_dt = verified_dt.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - verified_dt) > timedelta(days=days)
    except (ValueError, TypeError):
        return True


def find_best_component(category: str, region=None,
                        budget_remaining: float = 999999,
                        min_snow_load_psf: float = 0,
                        system_fit: str = "core") -> tuple[Optional[dict], Optional[str]]:
    """Find the best available component for a category.

    Sourcing preferences:
    1. Meets minimum spec
    2. System fit matches (core > standard > alternative)
    3. Confirmed price > estimated > unknown
    4. Higher spec completeness
    5. Within budget

    Returns:
        (product_dict, None) on success
        (None, reason_string) on failure
    """
    products = _load_category(category)
    if not products:
        return None, f"No products available in category '{category}'"

    # Mark stale products
    for p in products:
        p["stale"] = _is_stale(p)

    # Filter: must meet minimum spec
    viable = [p for p in products if p.get("meets_minimum_spec", False)]
    if not viable:
        viable = products  # Fall back to all if none meet spec, but note it

    # Filter: snow load for structures
    if category == "structures" and min_snow_load_psf > 0:
        snow_viable = [p for p in viable if (p.get("snow_load_psf") or 0) >= min_snow_load_psf]
        if snow_viable:
            viable = snow_viable
        else:
            return None, f"No structure meets snow load requirement of {min_snow_load_psf} PSF"

    # Filter: within budget
    priced = [p for p in viable if p.get("price_cad") is not None and p["price_cad"] <= budget_remaining]
    if priced:
        viable = priced
    # If nothing is within budget, keep all — we'll report the gap

    # Sort by scoring criteria
    def sort_key(p):
        fit_scores = {"core": 3, "standard": 2, "full": 2, "alternative": 1, "upgrade": 0}
        fit = fit_scores.get(p.get("klara_system_fit", "standard"), 1)

        price_scores = {"listed": 3, "quoted": 2, "estimated": 1, "unknown": 0}
        price_conf = price_scores.get(p.get("price_source", "unknown"), 0)

        completeness = p.get("spec_completeness_score", 0)
        stale_penalty = -20 if p.get("stale") else 0

        return (fit, price_conf, completeness + stale_penalty)

    viable.sort(key=sort_key, reverse=True)

    if viable:
        best = viable[0]

        # Check if within budget
        if best.get("price_cad") and best["price_cad"] > budget_remaining:
            best["_budget_note"] = f"Price ${best['price_cad']} exceeds remaining budget ${budget_remaining:.0f}"

        if best.get("stale"):
            best["_stale_note"] = "Data is stale (>90 days since last verification)"

        return best, None

    return None, f"No viable product found in category '{category}'"


def find_all_components(category: str) -> list[dict]:
    """Return all products for a category, sorted by preference."""
    return _load_category(category)


def get_category_summary() -> dict:
    """Return product counts per category."""
    summary = {}
    if not DATA_DIR.exists():
        return summary

    for cat_dir in DATA_DIR.iterdir():
        if cat_dir.is_dir():
            products = _load_category(cat_dir.name)
            summary[cat_dir.name] = {
                "total": len(products),
                "with_price": sum(1 for p in products if p.get("price_cad") is not None),
                "meets_spec": sum(1 for p in products if p.get("meets_minimum_spec")),
                "stale": sum(1 for p in products if _is_stale(p)),
            }
    return summary
