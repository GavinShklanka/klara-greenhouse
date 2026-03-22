"""Local Routing Service — connects users to NS resources (not a marketplace)."""

from __future__ import annotations

import json
from pathlib import Path

_DATA: dict = {}


def _load_data():
    global _DATA
    if not _DATA:
        path = Path(__file__).resolve().parents[2] / "config" / "greenhouse_data.json"
        with open(path, "r", encoding="utf-8") as f:
            _DATA = json.load(f)
    return _DATA


def get_local_resources(location: str) -> dict:
    """
    Return local seeds, materials, builders, and ag extensions for a NS region.
    This is guidance, NOT a marketplace.
    """
    data = _load_data()
    resources = data.get("local_resources", {})
    contractors = data.get("contractors", [])
    climate = data["climate_zones"].get(location, data["climate_zones"]["halifax"])

    # Match contractors by region
    region_label = climate.get("label", "").lower()
    matched_contractors = []
    for c in contractors:
        if any(r.strip().lower() in c["region"].lower()
               for r in [location.replace("_", " "), region_label]):
            matched_contractors.append(c)
    if not matched_contractors:
        matched_contractors = contractors  # Return all if no match

    return {
        "recommendation": "Local resources for your greenhouse project",
        "why": f"These suppliers and organizations serve {climate['label']} and surrounding areas.",
        "assumptions": "Links and availability may change. Verify before purchasing.",
        "next_step": "Your full build plan includes a complete materials list with quantities.",
        "seeds": resources.get("seed_suppliers", []),
        "materials": resources.get("material_suppliers", []),
        "builders": [
            {"name": c["name"], "phone": c["phone"], "email": c["email"], "region": c["region"]}
            for c in matched_contractors
        ],
        "agricultural_support": resources.get("agricultural_extensions", []),
        "co_ops": resources.get("co_ops", []),
    }
