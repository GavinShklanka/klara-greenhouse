"""
Routing service — orchestrates Steps 1-6 from Prompt 4 Section 2.
Takes intake data, queries all data layers, produces scored recommendation.
"""
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from . import regional_service
from . import component_service
from . import scoring_service

BLUEPRINT_PATH = Path(__file__).resolve().parent.parent.parent / "config" / "biological_blueprint.json"

_blueprint_cache = None


def _load_blueprint() -> dict:
    global _blueprint_cache
    if _blueprint_cache is None:
        try:
            _blueprint_cache = json.loads(BLUEPRINT_PATH.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logging.getLogger(__name__).warning(f"Failed to load biological blueprint: {e}")
            _blueprint_cache = {"species": [], "seasonal_calendar_summary": {}, "yield_summary": {}}
    return _blueprint_cache

logger = logging.getLogger(__name__)

# Disqualification conditions from Prompt 4 Section 4
BUDGET_MINIMUM = 2000
FOOTPRINT_MINIMUM_SQFT = 80

BUDGET_RANGES = {
    "under_3k": (0, 3000),
    "3k_5k": (3000, 5000),
    "5k_8k": (5000, 8000),
    "8k_plus": (8000, 25000),
}

FOOTPRINT_SQFT = {
    "small_under_80": 60,
    "medium_80_150": 120,
    "large_150_plus": 200,
}


class DisqualificationResult:
    def __init__(self, code: str, reason: str, suggestion: str):
        self.code = code
        self.reason = reason
        self.suggestion = suggestion

    def to_dict(self) -> dict:
        return {"code": self.code, "reason": self.reason, "suggestion": self.suggestion}


class RoutingResult:
    """Complete result of the routing decision pipeline."""

    def __init__(self):
        self.region = None
        self.components: dict = {}
        self.component_gaps: list = []
        self.system_cost: float = 0.0
        self.scores: dict = {}
        self.confidence: str = "low"
        self.disqualifications: list = []
        self.assumptions: list = []
        self.route_decision: str = "proceed"  # proceed | consult | disqualified
        self.action_text: str = ""
        self.species_matrix: list = []
        self.seasonal_calendar: dict = {}
        self.yield_summary: dict = {}
        self.intake: dict = {}

    def to_dict(self) -> dict:
        return {
            "region": self.region.to_dict() if self.region else None,
            "components": {k: v for k, v in self.components.items() if v is not None},
            "component_gaps": self.component_gaps,
            "system_cost": self.system_cost,
            "scores": self.scores,
            "confidence": self.confidence,
            "disqualifications": [d.to_dict() for d in self.disqualifications],
            "assumptions": self.assumptions,
            "route_decision": self.route_decision,
            "action_text": self.action_text,
            "species_matrix": self.species_matrix,
            "seasonal_calendar": self.seasonal_calendar,
            "yield_summary": self.yield_summary,
            "intake": self.intake,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }


def run_routing(intake: dict) -> RoutingResult:
    """Execute full routing pipeline: Steps 1-6.

    Args:
        intake: dict with keys:
            postal_code, budget_range, available_footprint_sqft,
            primary_use, diy_capacity, timeline,
            lot_orientation (optional), existing_infrastructure (optional)
    """
    result = RoutingResult()

    # --- STEP 1: Regional lookup ---
    postal_code = intake.get("postal_code", "")
    region, error = regional_service.get_region(postal_code)

    if error:
        if "outside NS/PEI" in error:
            result.disqualifications.append(DisqualificationResult(
                "OUTSIDE_SERVICE_AREA",
                "Klara currently serves Nova Scotia and Prince Edward Island only.",
                "Our recommendations are calibrated to Atlantic Canadian climate data."
            ))
            result.route_decision = "disqualified"
            result.action_text = error
            return result
        else:
            result.assumptions.append(f"Regional lookup failed: {error}. Using HRM defaults.")
            region, _ = regional_service.get_region("B3H")  # Halifax fallback

    result.region = region

    # --- PRE-CHECK: Disqualification checks ---
    budget_range = intake.get("budget_range", "3k_5k")
    budget_bounds = BUDGET_RANGES.get(budget_range, (3000, 5000))
    budget_ceiling = budget_bounds[1]

    if budget_ceiling < BUDGET_MINIMUM:
        result.disqualifications.append(DisqualificationResult(
            "BUDGET_BELOW_MINIMUM",
            f"The minimum Klara system costs ~$3,000. Your stated budget of under ${budget_ceiling} does not cover the base configuration.",
            "Consider starting with cold frames ($200-$800) to validate your interest."
        ))
        result.route_decision = "disqualified"
        return result

    footprint = FOOTPRINT_SQFT.get(intake.get("available_footprint_sqft", "medium_80_150"), 120)
    if footprint < FOOTPRINT_MINIMUM_SQFT:
        result.disqualifications.append(DisqualificationResult(
            "FOOTPRINT_TOO_SMALL",
            "The minimum Klara system requires ~100 sq ft. Your available space is below this threshold.",
            "Consider lean-to or cold frame configurations."
        ))
        result.route_decision = "disqualified"
        return result

    # --- STEP 2: System configuration ---
    # Determine structure size from footprint
    if footprint >= 150:
        target_area = "large"
    elif footprint >= 80:
        target_area = "medium"
    else:
        target_area = "small"

    # Determine renewable sizing from Persephone
    persephone = region.persephone_days if region else 94
    solar_panels_needed = 2 if persephone > 100 else 1

    # Foundation type from frost depth
    frost_depth = region.frost_depth_in if region else 48
    foundation = "concrete_piers" if frost_depth > 48 else "gravel_pad"

    result.assumptions.append(f"Foundation: {foundation} (frost depth {frost_depth}in)")
    result.assumptions.append(f"Solar panels: {solar_panels_needed} (Persephone {persephone} days)")

    # --- STEP 3: Component sourcing ---
    snow_load_req = region.snow_load_psf if region else 46
    remaining_budget = float(budget_ceiling)

    # Source each subsystem
    categories = [
        ("structures", {"min_snow_load_psf": snow_load_req, "system_fit": "core"}),
        ("lighting", {}),
        ("renewable", {}),
        ("sensors", {}),
        ("hydroponic", {}),
        ("biological", {}),
    ]

    for category, kwargs in categories:
        comp, gap_reason = component_service.find_best_component(
            category, region, remaining_budget, **kwargs
        )

        if comp:
            result.components[category] = comp
            price = comp.get("price_cad", 0) or 0
            remaining_budget -= price
        else:
            result.components[category] = None
            result.component_gaps.append({
                "category": category,
                "reason": gap_reason,
            })

    # Check for NO_RATED_STRUCTURE disqualification
    if result.components.get("structures") is None:
        structure_gap = next((g for g in result.component_gaps if g["category"] == "structures"), None)
        if structure_gap and "snow load" in (structure_gap.get("reason") or "").lower():
            result.disqualifications.append(DisqualificationResult(
                "NO_RATED_STRUCTURE",
                f"No greenhouse structure rated for the snow loads at your location ({snow_load_req} PSF).",
                "Contact Atlantic Greenhouse Supplies (902-968-1082) for a custom structural assessment."
            ))

    # Calculate system cost from sourced components
    result.system_cost = sum(
        (c.get("price_cad", 0) or 0)
        for c in result.components.values()
        if c is not None
    )

    # Add estimated costs for subsystems not yet in component DB
    thermal_estimate = 250  # Water drums + insulation
    water_estimate = 100  # Rainwater barrel + basic plumbing
    foundation_estimate = 300  # Gravel pad or pier materials

    non_scraped = thermal_estimate + water_estimate + foundation_estimate
    result.system_cost += non_scraped
    result.assumptions.append(
        f"Estimated costs for non-sourced subsystems: "
        f"thermal=${thermal_estimate}, water=${water_estimate}, "
        f"foundation=${foundation_estimate}"
    )

    # --- BIOLOGICAL BLUEPRINT ---
    blueprint = _load_blueprint()
    result.species_matrix = blueprint.get("species", [])
    result.seasonal_calendar = blueprint.get("seasonal_calendar_summary", {})
    result.yield_summary = blueprint.get("yield_summary", {})

    # Store intake for proposal rendering
    result.intake = intake

    # --- STEP 4: Feasibility validation (disqualification checks) ---
    if result.disqualifications:
        result.route_decision = "disqualified"
        return result

    # --- STEP 5: Scoring ---
    diy_capacity = intake.get("diy_capacity", "partial_diy")
    assembly = "moderate"
    structure = result.components.get("structures")
    if structure:
        assembly = structure.get("assembly_complexity", "moderate")

    result.scores = scoring_service.compute_all_scores(
        system_cost=result.system_cost,
        budget_range=budget_range,
        region=region,
        components=result.components,
        diy_capacity=diy_capacity,
        assembly_complexity=assembly,
    )

    # --- STEP 6: Route decision ---
    total = result.scores.get("weighted_total", 0)

    # Determine confidence level
    data_conf = result.scores.get("data_confidence", 0)
    has_gaps = len(result.component_gaps) > 0
    support_desert = region.support_desert if region else True

    # Apply intake "not_sure" penalties
    not_sure_count = sum(1 for v in intake.values() if v == "not_sure")
    if not_sure_count > 0:
        result.assumptions.append(f"{not_sure_count} intake field(s) answered 'not_sure'")

    if data_conf >= 70 and not has_gaps and not_sure_count == 0:
        result.confidence = "high"
    elif data_conf >= 40 or (has_gaps and len(result.component_gaps) <= 1):
        result.confidence = "medium"
    else:
        result.confidence = "low"

    # Force confidence downgrades
    if support_desert and diy_capacity == "need_install":
        result.confidence = "low"
        result.assumptions.append("Support desert + need_install → confidence downgraded to low")

    # Route decision
    if total >= 70:
        result.route_decision = "proceed"
        result.action_text = "Your property is well-suited for the Klara greenhouse ecosystem."
    elif total >= 50:
        result.route_decision = "consult"
        result.action_text = "Your property appears suitable with some considerations. We recommend a consultation to address specific factors."
    else:
        result.route_decision = "consult"
        result.confidence = "low"
        result.action_text = "We recommend a personalized consultation before proceeding. Several factors require professional assessment."

    return result
