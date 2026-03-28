"""
Scoring service — implements 6-dimension scoring rubric from Prompt 4 Section 3.
Each dimension scores 0-100. Weights are configurable.
"""
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Default weights from Prompt 4 Section 3
DEFAULT_WEIGHTS = {
    "budget_fit": 0.25,
    "regional_viability": 0.20,
    "data_confidence": 0.15,
    "installation_feasibility": 0.15,
    "biological_viability": 0.15,
    "local_support": 0.10,
}

BUDGET_RANGES = {
    "under_3k": (0, 3000),
    "3k_5k": (3000, 5000),
    "5k_8k": (5000, 8000),
    "8k_plus": (8000, 25000),
}


def score_budget_fit(system_cost: float, budget_range: str) -> int:
    """Score 0-100 based on how well system cost fits stated budget."""
    bounds = BUDGET_RANGES.get(budget_range)
    if not bounds:
        return 50  # Unknown range

    _, ceiling = bounds

    if system_cost <= ceiling:
        return 100
    elif system_cost <= ceiling * 1.15:
        return 75
    elif system_cost <= ceiling * 1.30:
        return 50
    elif system_cost <= ceiling * 1.50:
        return 25
    else:
        return 0


def score_regional_viability(region) -> int:
    """Score 0-100 based on snow/wind compliance, delivery tier, season length."""
    score = 100

    # Snow load compliance (structure must meet regional requirement)
    snow_conf = getattr(region, "snow_load_confidence", "unknown")
    if snow_conf == "unknown":
        score -= 30
    elif snow_conf == "estimated":
        score -= 15

    # Delivery tier penalty
    tier = getattr(region, "delivery_tier", 4)
    if tier == 1:
        pass  # No penalty
    elif tier == 2:
        score -= 5
    elif tier == 3:
        score -= 15
    elif tier == 4:
        score -= 25

    # Growing season
    season = getattr(region, "growing_season_days", 0)
    if season >= 150:
        pass
    elif season >= 120:
        score -= 10
    elif season >= 100:
        score -= 20
    else:
        score -= 35

    return max(0, min(100, score))


def score_data_confidence(region, components: dict) -> int:
    """Score 0-100 based on how much data is confirmed vs estimated."""
    confirmed = 0
    total = 0

    # Regional data confidence
    if getattr(region, "snow_load_confidence", "unknown") == "confirmed":
        confirmed += 2
    elif getattr(region, "snow_load_confidence", "unknown") == "corroborated":
        confirmed += 1.5
    total += 2

    # Component data confidence
    for cat, comp in components.items():
        if comp is None:
            total += 1
            continue
        total += 1
        price_source = comp.get("price_source", "unknown")
        if price_source == "listed":
            confirmed += 1
        elif price_source in ("quoted", "estimated"):
            confirmed += 0.5

        completeness = comp.get("spec_completeness_score", 0)
        if completeness >= 80:
            confirmed += 0.5
        total += 0.5

    if total == 0:
        return 50

    return max(0, min(100, int((confirmed / total) * 100)))


def score_installation_feasibility(diy_capacity: str, region, assembly_complexity: str = "moderate") -> int:
    """Score 0-100 based on DIY capacity vs installation complexity."""
    base_scores = {
        ("full_diy", "easy"): 100,
        ("full_diy", "moderate"): 85,
        ("full_diy", "hard"): 60,
        ("full_diy", "professional_required"): 30,
        ("partial_diy", "easy"): 90,
        ("partial_diy", "moderate"): 75,
        ("partial_diy", "hard"): 50,
        ("partial_diy", "professional_required"): 25,
        ("need_install", "easy"): 70,
        ("need_install", "moderate"): 50,
        ("need_install", "hard"): 30,
        ("need_install", "professional_required"): 15,
    }

    score = base_scores.get((diy_capacity, assembly_complexity), 50)

    # Support desert penalty for need_install
    if diy_capacity == "need_install":
        support = getattr(region, "support_density", {})
        if not support.get("installer_within_50km", False):
            score -= 25

    return max(0, min(100, score))


def score_biological_viability(region) -> int:
    """Score 0-100 based on growing conditions for the biological species matrix."""
    score = 100

    # Persephone period
    persephone = getattr(region, "persephone_days", 0)
    if persephone < 95:
        pass  # Ideal
    elif persephone <= 100:
        score -= 10
    elif persephone <= 105:
        score -= 20
    else:
        score -= 35

    # Winter solar resource
    solar = getattr(region, "winter_solar_kwh", 0)
    if solar >= 2.5:
        pass
    elif solar >= 2.2:
        score -= 5
    elif solar >= 2.0:
        score -= 10
    else:
        score -= 20

    # Growing season
    season = getattr(region, "growing_season_days", 0)
    if season >= 150:
        pass
    elif season >= 130:
        score -= 10
    else:
        score -= 20

    return max(0, min(100, score))


def score_local_support(region) -> int:
    """Score 0-100 based on proximity to suppliers, retailers, installers."""
    support = getattr(region, "support_density", {})

    categories = [
        "structure_supplier_within_50km",
        "hydro_retailer_within_50km",
        "installer_within_50km",
        "seed_supplier_within_50km",
    ]

    available = sum(1 for c in categories if support.get(c, False))

    if available == 4:
        return 100
    elif available == 3:
        return 75
    elif available == 2:
        return 50
    elif available == 1:
        return 25
    else:
        return 0


def compute_weighted_total(scores: dict, weights: dict | None = None) -> float:
    """Compute weighted total score from dimension scores."""
    w = weights or DEFAULT_WEIGHTS
    total = 0.0
    for dim, weight in w.items():
        total += scores.get(dim, 0) * weight
    return round(total, 1)


def compute_all_scores(system_cost: float, budget_range: str, region,
                       components: dict, diy_capacity: str,
                       assembly_complexity: str = "moderate",
                       weights: dict | None = None) -> dict:
    """Compute all 6 dimension scores and weighted total."""
    scores = {
        "budget_fit": score_budget_fit(system_cost, budget_range),
        "regional_viability": score_regional_viability(region),
        "data_confidence": score_data_confidence(region, components),
        "installation_feasibility": score_installation_feasibility(diy_capacity, region, assembly_complexity),
        "biological_viability": score_biological_viability(region),
        "local_support": score_local_support(region),
    }

    scores["weighted_total"] = compute_weighted_total(scores, weights)

    return scores
