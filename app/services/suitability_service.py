"""Suitability Service — climate zone lookup and feasibility check."""

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


def check_suitability(intake: dict) -> dict:
    """
    Cross-reference intake with NS climate data.
    Returns suitability verdict + warnings.
    """
    data = _load_data()
    location = intake.get("location", "halifax")
    budget = intake.get("budget", "under_5k")

    # Climate zone lookup
    climate = data["climate_zones"].get(location, data["climate_zones"]["halifax"])

    # Budget feasibility — cheapest option is polytunnel starter
    cost_matrix = data["cost_matrix"]
    min_cost = cost_matrix["polytunnel"]["starter"]["total_diy_low"]
    budget_map = {
        "under_5k": 5000,
        "5k_10k": 10000,
        "over_10k": 15000,
    }
    budget_ceiling = budget_map.get(budget, 5000)

    warnings = []
    suitable = True

    if budget_ceiling < min_cost:
        warnings.append(
            f"Your budget may be tight — the smallest greenhouse starts around ${min_cost:,} for DIY. "
            f"We'll find the best option within your range."
        )

    # Zone 5b gets extra snow/cold note
    if climate["zone"] == "5b":
        warnings.append(
            f"{climate['label']} is Zone 5b — colder with heavier snow loads "
            f"({climate['design_snow_load_psf']} PSF). We'll recommend a structure rated for this."
        )

    return {
        "suitable": suitable,
        "climate": climate,
        "warnings": warnings,
        "budget_ceiling": budget_ceiling,
    }
