"""Solar Context Service — simplified solar viability and orientation advice."""

from __future__ import annotations

from app.core.data_loader import get_greenhouse_data


def get_solar_context(location: str) -> dict:
    """
    Return solar viability and orientation guidance for a NS region.
    Rule-based — no simulation engine.
    """
    data = get_greenhouse_data()
    climate = data["climate_zones"].get(location, data["climate_zones"]["halifax"])

    summer_hours = climate.get("peak_sun_hours_summer", 5.0)
    winter_hours = climate.get("peak_sun_hours_winter", 2.5)
    annual_hours = climate.get("annual_sun_hours", 1800)

    # Viability assessment
    if annual_hours >= 1900:
        viability = "excellent"
        viability_note = "Your region receives above-average sunlight for Nova Scotia — ideal for greenhouse growing."
    elif annual_hours >= 1800:
        viability = "good"
        viability_note = "Your region receives solid sunlight — well-suited for a productive greenhouse."
    else:
        viability = "adequate"
        viability_note = "Your region gets less sun than southern NS, but a greenhouse still dramatically extends your season."

    return {
        "recommendation": f"South-facing orientation with long axis running East-West",
        "why": (
            "South-facing glazing captures maximum winter sun when the sun is low on the horizon. "
            "An East-West long axis gives the largest south-facing surface area. "
            "This is critical in NS where winter days are short."
        ),
        "assumptions": (
            f"Based on {climate['label']} receiving ~{summer_hours} peak sun hours/day in summer "
            f"and ~{winter_hours} hours/day in winter ({annual_hours} annual hours total)."
        ),
        "next_step": "Your greenhouse plan will be optimized for this solar profile.",
        "solar_data": {
            "peak_sun_hours_summer": summer_hours,
            "peak_sun_hours_winter": winter_hours,
            "annual_sun_hours": annual_hours,
            "viability": viability,
            "viability_note": viability_note,
        },
        "heat_retention": {
            "recommendation": "Add thermal mass (water barrels or stone) along the north wall",
            "why": (
                "Thermal mass absorbs solar heat during the day and releases it at night. "
                "Two to three 55-gallon water barrels per 100 sq ft can keep temps above freezing "
                "on most NS winter nights without supplemental heat."
            ),
        },
        "orientation": {
            "ideal": "South-facing (within 15° of true south)",
            "long_axis": "East-West",
            "avoid": "North-facing slopes or areas shaded by buildings/trees in winter",
        },
    }
