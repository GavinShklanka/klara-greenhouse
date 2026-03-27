"""Cost Service — dual-price output (kit price vs true installed cost) per archetype.

Each archetype produces 5 line items: Kit/Structure, Foundation & Site Prep,
Growing Setup, Assembly Labor, Contingency (10%). All ranges are directional
estimates labeled as such.
"""

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


# ── Per-archetype cost breakdowns ────────────────────────────────────────

_COST_DATA: dict[str, dict] = {
    "cold_frame_bridge": {
        "kit_price_range": "$200–$800",
        "true_installed_cost_range": "$300–$1,200",
        "line_items": [
            {"category": "Kit / Structure",
             "range": "$150–$600",
             "note": "Treated lumber or cedar frame, polycarbonate lid or storm window"},
            {"category": "Foundation & Site Prep",
             "range": "$0–$100",
             "note": "Minimal — level ground, optional landscape fabric"},
            {"category": "Growing Setup",
             "range": "$50–$200",
             "note": "Soil amendment, compost, optional soil thermometer"},
            {"category": "Assembly Labor",
             "range": "$0–$200",
             "note": "DIY project — 2–4 hours. No specialized tools needed"},
            {"category": "Contingency (10%)",
             "range": "$20–$100",
             "note": "Budget buffer for hardware, screws, hinges"},
        ],
        "timeline": "1 weekend",
        "total_note": (
            "True Installed Cost reflects what you will actually spend to have "
            "functioning cold frames on your property. This is the most affordable "
            "entry point for Nova Scotia growing season extension."
        ),
    },

    "starter_kit": {
        "kit_price_range": "$1,500–$3,500",
        "true_installed_cost_range": "$2,500–$5,500",
        "line_items": [
            {"category": "Kit / Structure",
             "range": "$1,200–$3,000",
             "note": "Aluminum frame, 6mm twin-wall polycarbonate panels, vents, door hardware"},
            {"category": "Foundation & Site Prep",
             "range": "$300–$700",
             "note": "Gravel pad (6\" crushed stone), leveling, treated 4×4 timber base frame"},
            {"category": "Growing Setup",
             "range": "$200–$500",
             "note": "2 raised beds (cedar 2×10), soil, basic drip irrigation"},
            {"category": "Assembly Labor",
             "range": "$0–$800",
             "note": "DIY: 2–3 weekends. Contractor: 1–2 days, 2-person crew"},
            {"category": "Contingency (10%)",
             "range": "$200–$500",
             "note": "Budget buffer for site surprises, material waste, delivery fees"},
        ],
        "timeline": "1–2 weekends (DIY) or 1–2 days (contractor)",
        "total_note": (
            "True Installed Cost reflects what you will actually spend to have a "
            "functioning greenhouse on your property, not just the kit sticker price. "
            "Includes site prep, foundation, growing infrastructure, and a 10% buffer."
        ),
    },

    "maritime_standard": {
        "kit_price_range": "$4,000–$8,000",
        "true_installed_cost_range": "$6,000–$12,000",
        "line_items": [
            {"category": "Kit / Structure",
             "range": "$3,500–$7,000",
             "note": "Galvanized steel frame (14-gauge), 8mm polycarbonate, ridge vent, louvers, insulated door"},
            {"category": "Foundation & Site Prep",
             "range": "$800–$1,800",
             "note": "Sono tubes or concrete piers to frost depth (42–54\"), treated 6×6 sill, gravel base, leveling"},
            {"category": "Growing Setup",
             "range": "$400–$900",
             "note": "3–4 raised beds (cedar 2×12), compost/soil blend, drip irrigation rough-in"},
            {"category": "Assembly Labor",
             "range": "$800–$2,500",
             "note": "DIY: 2–4 weeks (weekends). Contractor: 3–5 days, 2-person crew at $35–$50/hr"},
            {"category": "Contingency (10%)",
             "range": "$500–$1,200",
             "note": "Budget buffer for site surprises, delivery, hardware, and material waste"},
        ],
        "timeline": "2–4 weeks (DIY weekends) or 3–5 days (contractor)",
        "total_note": (
            "True Installed Cost reflects what you will actually spend to have a "
            "functioning, Fiona-rated greenhouse on your property. Kit price is what "
            "the manufacturer charges. The gap — foundation, site prep, beds, labor — "
            "is where most first-time buyers get surprised."
        ),
    },

    "passive_solar_leanto": {
        "kit_price_range": "$6,000–$10,000",
        "true_installed_cost_range": "$9,000–$16,000",
        "line_items": [
            {"category": "Kit / Structure",
             "range": "$5,000–$8,500",
             "note": "Timber frame, insulated wall panels (R-20), south-face polycarbonate or glass, door, ridge vent"},
            {"category": "Foundation & Site Prep",
             "range": "$1,200–$2,500",
             "note": "Continuous footing or pier connection to host building, ledger board, flashing, gravel base"},
            {"category": "Growing Setup",
             "range": "$600–$1,200",
             "note": "Raised beds with thermal base, 4–8 water barrels (thermal mass), soil/compost blend"},
            {"category": "Assembly Labor",
             "range": "$1,500–$3,500",
             "note": "Higher complexity build. DIY: 4–6 weeks. Contractor: 1–2 weeks, skilled crew required"},
            {"category": "Contingency (10%)",
             "range": "$800–$1,600",
             "note": "Budget buffer — lean-to builds have more attachment variables than standalone structures"},
        ],
        "timeline": "4–6 weeks (DIY) or 1–2 weeks (contractor)",
        "total_note": (
            "True Installed Cost reflects the full build including thermal mass, "
            "insulated walls, and structural connection to your existing building. "
            "This is a higher-complexity build than a standalone greenhouse, but the "
            "payoff is near-zero heating cost through Maritime winters."
        ),
    },

    "serious_grower": {
        "kit_price_range": "$8,000–$15,000",
        "true_installed_cost_range": "$12,000–$22,000",
        "line_items": [
            {"category": "Kit / Structure",
             "range": "$7,000–$13,000",
             "note": "Commercial steel frame (12-gauge), polycarbonate or reinforced poly, roll-up vents, exhaust fan, end walls"},
            {"category": "Foundation & Site Prep",
             "range": "$1,500–$3,000",
             "note": "Concrete piers with steel post anchors (8–12), gravel base, site grading, drainage"},
            {"category": "Growing Setup",
             "range": "$800–$1,800",
             "note": "6+ raised beds or in-ground prep, drip irrigation system, staging area"},
            {"category": "Assembly Labor",
             "range": "$2,000–$4,500",
             "note": "Professional assembly recommended. 1–2 weeks, experienced crew. Electrical for fan/thermostat"},
            {"category": "Contingency (10%)",
             "range": "$1,100–$2,200",
             "note": "Budget buffer for site complexity, electrical hookup, delivery logistics"},
        ],
        "timeline": "3–6 weeks (DIY) or 1–2 weeks (professional crew)",
        "total_note": (
            "True Installed Cost reflects a production-grade installation including "
            "commercial foundation, ventilation, irrigation rough-in, and professional "
            "assembly. This is not a weekend kit — it is a serious growing facility "
            "built to commercial structural standards."
        ),
    },
}


def estimate_costs(
    greenhouse_type: str,
    tier_id: str,
    climate: dict,
    archetype_id: str = "",
) -> dict:
    """
    Produce cost breakdown with kit price vs true installed cost.

    If archetype_id is provided, use the archetype-specific cost data.
    Falls back to legacy calculation if no archetype_id.
    """
    data = _load_data()

    # Use archetype-specific cost data if available
    if archetype_id and archetype_id in _COST_DATA:
        cost_data = _COST_DATA[archetype_id]
        return {
            "kit_price_range": cost_data["kit_price_range"],
            "true_installed_cost_range": cost_data["true_installed_cost_range"],
            "line_items": cost_data["line_items"],
            "timeline": cost_data["timeline"],
            "total_note": cost_data["total_note"],
            "estimate_disclaimer": (
                "These are directional ranges based on Nova Scotia market conditions "
                "as of spring 2026. Validate with a local quote before committing."
            ),
            "seasonal_note": (
                f"In {climate.get('label', 'your region')}, start foundation work after "
                f"{climate.get('avg_last_frost', 'last frost')}. "
                f"Finish glazing before {climate.get('avg_first_frost', 'first frost')}."
            ),
        }

    # Legacy fallback using cost_matrix from greenhouse_data.json
    type_costs = data["cost_matrix"].get(greenhouse_type, data["cost_matrix"]["polycarbonate"])
    costs = type_costs.get(tier_id, type_costs["starter"])
    type_timeline = data["timeline"].get(greenhouse_type, data["timeline"]["polycarbonate"])
    timeline = type_timeline.get(tier_id, type_timeline["starter"])

    diy_low = costs["total_diy_low"]
    diy_high = costs["total_diy_high"]
    con_low = costs["total_contractor_low"]
    con_high = costs["total_contractor_high"]

    return {
        "kit_price_range": f"${costs['materials_low']:,}–${costs['materials_high']:,}",
        "true_installed_cost_range": f"${diy_low:,}–${con_high:,}",
        "line_items": [
            {"category": "Kit / Structure",
             "range": f"${costs['materials_low']:,}–${costs['materials_high']:,}",
             "note": "Frame, glazing, vents, door hardware"},
            {"category": "Foundation & Site Prep",
             "range": f"${costs['foundation']:,}",
             "note": f"Foundation to frost depth ({climate.get('frost_depth_inches', 48)}\" in {climate.get('label', 'your region')})"},
            {"category": "Growing Setup",
             "range": f"${costs['extras']:,}",
             "note": "Raised beds, soil, basic fittings"},
            {"category": "Assembly Labor",
             "range": f"${costs.get('labor_contractor', 0):,}",
             "note": f"DIY: {costs['labor_diy_hours']} hours. Contractor rate: ~$35–$50/hr"},
            {"category": "Contingency (10%)",
             "range": f"${int(diy_low * 0.1):,}–${int(con_high * 0.1):,}",
             "note": "Budget buffer for surprises"},
        ],
        "timeline": f"{timeline['diy_weeks']} weeks (DIY) or {timeline['contractor_weeks']} weeks (contractor)",
        "total_note": (
            "True Installed Cost reflects what you will actually spend to have a "
            "functioning greenhouse on your property, not just the kit sticker price."
        ),
        "estimate_disclaimer": (
            "These are directional ranges based on Nova Scotia market conditions "
            "as of spring 2026. Validate with a local quote before committing."
        ),
        "seasonal_note": (
            f"In {climate.get('label', 'your region')}, start after "
            f"{climate.get('avg_last_frost', 'last frost')}. "
            f"Finish glazing before {climate.get('avg_first_frost', 'first frost')}."
        ),
    }
