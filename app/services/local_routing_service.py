"""Local Routing Service — real, categorized NS resources with archetype-aware filtering.

Resources are grouped by: education, seeds/supplies, builders/installers, consultation.
Builder resources only shown when archetype true installed cost exceeds $5,000.
Cold Frame Bridge users see education and seed sources only.
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


# ── Resource registry ────────────────────────────────────────────────────

LOCAL_RESOURCES: list[dict] = [
    # ── Education ─────────────────────────────────────────────────────
    {
        "name": "Perennia Food & Agriculture",
        "type": "education",
        "city_or_region": "Truro, NS",
        "url": "https://www.perennia.ca",
        "what_they_do": "Provincial agricultural extension — free greenhouse growing guides and climate-specific crop calendars.",
        "who_its_for": "Any NS grower, especially first-timers who want research-backed growing advice.",
        "why_klara_includes_them": "Perennia is the authoritative source for Maritime-specific growing data and best practices.",
        "disclosure": "Klara has no financial relationship with Perennia.",
    },
    {
        "name": "Dalhousie Faculty of Agriculture",
        "type": "education",
        "city_or_region": "Truro, NS",
        "url": "https://www.dal.ca/faculty/agriculture.html",
        "what_they_do": "Research-backed growing advice for Maritime conditions, including greenhouse management publications.",
        "who_its_for": "Growers who want peer-reviewed data on cold-climate greenhouse production.",
        "why_klara_includes_them": "Dalhousie Agriculture publishes the most reliable NS-specific greenhouse research.",
        "disclosure": "Klara has no financial relationship with Dalhousie University.",
    },
    {
        "name": "NS Association of Garden Clubs",
        "type": "education",
        "city_or_region": "Province-wide, NS",
        "url": "https://www.nsagc.com",
        "what_they_do": "Network of local garden clubs with hands-on workshops, plant swaps, and mentorship for new growers.",
        "who_its_for": "First-time growers who want community support and local growing knowledge.",
        "why_klara_includes_them": "Local clubs provide the peer mentorship that online guides cannot — real people growing in your microclimate.",
        "disclosure": "Klara has no financial relationship with NSAGC.",
    },

    # ── Seeds & Supplies ──────────────────────────────────────────────
    {
        "name": "Halifax Seed Company",
        "type": "seed",
        "city_or_region": "Halifax, NS",
        "url": "https://www.halifaxseed.ca",
        "what_they_do": "NS institution since 1866. Varieties specifically selected and tested for Maritime climates.",
        "who_its_for": "Any NS greenhouse grower — their Maritime-tested seed selection removes guesswork.",
        "why_klara_includes_them": "Halifax Seed stocks varieties proven in NS conditions. Their staff can advise on greenhouse-specific selections.",
        "disclosure": "Klara has no financial relationship with Halifax Seed Company.",
    },
    {
        "name": "Veseys Seeds",
        "type": "seed",
        "city_or_region": "PEI (ships to NS)",
        "url": "https://www.veseys.com",
        "what_they_do": "Atlantic Canada seed specialist. Cold-hardy, short-season varieties designed for Maritime growing.",
        "who_its_for": "Growers who want proven Atlantic Canada genetics and reliable shipping.",
        "why_klara_includes_them": "Veseys tests varieties in Maritime conditions — their catalog is pre-filtered for what works here.",
        "disclosure": "Klara has no financial relationship with Veseys Seeds.",
    },
    {
        "name": "Hope Seeds",
        "type": "seed",
        "city_or_region": "Annapolis Valley, NS",
        "url": "https://www.hopeseed.com",
        "what_they_do": "Organic, open-pollinated seeds actually grown in Nova Scotia. Adapted to local soil and climate.",
        "who_its_for": "Growers who prioritize organic, locally-adapted seed stock.",
        "why_klara_includes_them": "Seeds grown in NS are already adapted to NS conditions — the most locally-grounded option available.",
        "disclosure": "Klara has no financial relationship with Hope Seeds.",
    },
    {
        "name": "Kent Building Supplies",
        "type": "supply",
        "city_or_region": "Multiple NS locations",
        "url": "https://www.kent.ca",
        "what_they_do": "Lumber, foundation materials, hardware, concrete, gravel — everything for greenhouse construction.",
        "who_its_for": "DIY builders who need foundation materials, treated lumber, and hardware locally.",
        "why_klara_includes_them": "Kent is the most accessible building supply chain in NS — most materials can be sourced in one trip.",
        "disclosure": "Klara has no financial relationship with Kent Building Supplies.",
    },

    # ── Builders / Installers ─────────────────────────────────────────
    {
        "name": "Sun Valley Greenhouses",
        "type": "builder",
        "city_or_region": "Halifax Regional Municipality, NS",
        "url": "https://www.sunvalleygreenhouses.ca",
        "what_they_do": "Greenhouse design, supply, and installation for residential and commercial projects in the Halifax area.",
        "who_its_for": "Homeowners in HRM who want professional greenhouse installation with local expertise.",
        "why_klara_includes_them": "Local greenhouse specialist with direct experience in Maritime weather-rated structures.",
        "disclosure": "Klara has no financial relationship with this provider. Always get at least two quotes.",
    },
    {
        "name": "Atlantic Greenhouse Supplies",
        "type": "builder",
        "city_or_region": "Eastern Nova Scotia",
        "url": "https://www.atlanticgreenhouse.ca",
        "what_they_do": "Greenhouse kits, parts, and installation support for Eastern NS and Cape Breton.",
        "who_its_for": "Homeowners outside HRM who need local greenhouse supply and assembly support.",
        "why_klara_includes_them": "Covers regions where Halifax-based installers may not service — important for rural NS properties.",
        "disclosure": "Klara has no financial relationship with this provider. Always get at least two quotes.",
    },

    # ── Consultation ──────────────────────────────────────────────────
    {
        "name": "Klara Greenhouse Consultation",
        "type": "consultation",
        "city_or_region": "Province-wide (video call)",
        "url": "#consultation",
        "what_they_do": "45-minute video consultation covering complex yards, unusual zoning, or specific crop goals beyond the standard intake.",
        "who_its_for": "Users whose situation truly defies the standard intake form — sloped lots, unusual zoning, unique crop goals.",
        "why_klara_includes_them": "For edge cases that need human expert review beyond what the recommendation engine handles.",
        "disclosure": "This is a Klara service. Fee applies.",
    },
]

# ── Service routing explainer (included in every response) ───────────────

SERVICE_ROUTING_EXPLAINER = (
    "Klara provides the greenhouse recommendation and planning. "
    "Local resources help you execute. "
    "Builders listed here are included because they serve Nova Scotia "
    "and have relevant greenhouse experience — not because they pay us. "
    "Always get at least two quotes."
)

# Archetypes where builder resources are relevant (true installed cost > $5K)
_BUILDER_ELIGIBLE_ARCHETYPES = {
    "maritime_standard",
    "passive_solar_leanto",
    "serious_grower",
}


def get_local_resources(location: str, archetype_id: str = "") -> dict:
    """
    Return categorized local resources filtered by archetype relevance.

    Cold Frame Bridge: education + seeds only.
    Starter Kit: education + seeds + supplies only.
    Maritime Standard+: all categories including builders.
    """
    data = _load_data()
    climate = data["climate_zones"].get(location, data["climate_zones"]["halifax"])

    # Determine which resource types to include
    if archetype_id == "cold_frame_bridge":
        include_types = {"education", "seed"}
    elif archetype_id == "starter_kit":
        include_types = {"education", "seed", "supply"}
    elif archetype_id in _BUILDER_ELIGIBLE_ARCHETYPES:
        include_types = {"education", "seed", "supply", "builder", "consultation"}
    else:
        # Default: all types
        include_types = {"education", "seed", "supply", "builder", "consultation"}

    # Filter resources
    filtered = [r for r in LOCAL_RESOURCES if r["type"] in include_types]

    # Group by type
    grouped = {}
    for r in filtered:
        rtype = r["type"]
        if rtype not in grouped:
            grouped[rtype] = []
        grouped[rtype].append(r)

    return {
        "resources": filtered,
        "resources_by_type": grouped,
        "service_routing_explainer": SERVICE_ROUTING_EXPLAINER,
        "region": climate["label"],
        "archetype_filter_applied": archetype_id or "none",
        "note": (
            f"These resources serve {climate['label']} and surrounding areas. "
            "Links and availability may change — verify before purchasing or hiring."
        ),
    }
