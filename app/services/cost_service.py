"""Cost Service — cost breakdown + timeline for a greenhouse type + size."""

from __future__ import annotations

from app.core.data_loader import get_greenhouse_data


def estimate_costs(greenhouse_type: str, tier_id: str, climate: dict) -> dict:
    """
    Produce cost breakdown + timeline for a given greenhouse type + size.
    """
    data = get_greenhouse_data()
    type_costs = data["cost_matrix"].get(greenhouse_type, data["cost_matrix"]["polycarbonate"])
    costs = type_costs.get(tier_id, type_costs["starter"])
    type_timeline = data["timeline"].get(greenhouse_type, data["timeline"]["polycarbonate"])
    timeline = type_timeline.get(tier_id, type_timeline["starter"])

    diy_low = costs["total_diy_low"]
    diy_high = costs["total_diy_high"]
    con_low = costs["total_contractor_low"]
    con_high = costs["total_contractor_high"]

    return {
        "recommendation": f"${diy_low:,}–${diy_high:,} (DIY) or ${con_low:,}–${con_high:,} (contractor)",
        "why": (
            f"Costs are based on current Nova Scotia material pricing for a {greenhouse_type} "
            f"greenhouse. Foundation depth accounts for {climate.get('frost_depth_inches', 48)}\" "
            f"frost line in {climate.get('label', 'your region')}."
        ),
        "assumptions": (
            f"Material prices as of 2024–2025 NS market. "
            f"Labor rate ~$35–$50/hr for contractor. "
            f"Foundation: sono tubes to frost depth."
        ),
        "next_step": "Choose your path: get the full build plan, request a builder quote, or book a consultation.",
        "breakdown": {
            "materials_low": costs["materials_low"],
            "materials_high": costs["materials_high"],
            "foundation": costs["foundation"],
            "extras": costs["extras"],
        },
        "labor": {
            "diy_hours": costs["labor_diy_hours"],
            "contractor_cost": costs["labor_contractor"],
        },
        "totals": {
            "diy_low": diy_low,
            "diy_high": diy_high,
            "contractor_low": con_low,
            "contractor_high": con_high,
        },
        "timeline": {
            "diy_weeks": timeline["diy_weeks"],
            "contractor_weeks": timeline["contractor_weeks"],
        },
        "seasonal_note": (
            f"In {climate.get('label', 'your region')}, start after "
            f"{climate.get('avg_last_frost', 'last frost')}. "
            f"Finish glazing before {climate.get('avg_first_frost', 'first frost')}."
        ),
    }
