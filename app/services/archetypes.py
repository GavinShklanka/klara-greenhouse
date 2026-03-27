"""Greenhouse Archetypes — 5 named models replacing binary selection logic.

Each archetype is a complete, self-contained recommendation object with
trust-building fields: why_this, why_not_others, assumptions, confidence
scores, and dual pricing (kit price vs true installed cost).
"""

from __future__ import annotations

from typing import Optional


ARCHETYPES: dict[str, dict] = {

    # ──────────────────────────────────────────────────────────────────────
    # 1. THE COLD FRAME BRIDGE
    # ──────────────────────────────────────────────────────────────────────
    "cold_frame_bridge": {
        "id": "cold_frame_bridge",
        "name": "The Cold Frame Bridge",
        "tagline": "Not ready for a greenhouse? Start here — and do it right.",
        "size_range": "4×4 to 4×8 ft per unit (stackable)",
        "budget_range": "$200–$800 materials / $300–$1,200 installed",
        "frame_material": "Treated lumber or cedar frame",
        "glazing": "Polycarbonate lid or old storm window",
        "wind_rating": "Ground-level — inherently wind-resistant",
        "snow_load": "Handles full snow cover (manual clearing recommended)",
        "foundation_type": "Sits directly on soil or raised bed",
        "best_for": [
            "Budgets under $1,000",
            "First-time growers testing commitment",
            "Properties where a full greenhouse is impractical",
            "Season extension without a permanent structure",
        ],
        "not_suitable_for": [
            "Year-round growing",
            "Warm-season crops (tomatoes, peppers)",
            "Anyone needing stand-up workspace",
            "Overwintering tender plants",
        ],
        "materials_list_summary": [
            "Treated 2×6 or 2×8 lumber (frame)",
            "Polycarbonate sheet or salvaged storm window (lid)",
            "Galvanized hinges and prop arm",
            "Landscape fabric (base)",
            "Optional: soil thermometer",
        ],
        "kit_price_only": "$200–$800",
        "true_installed_cost": "$300–$1,200",
        "why_this": (
            "Your budget or property constraints mean a full greenhouse would be "
            "either financially stressful or physically impractical right now. A cold "
            "frame setup lets you extend your season by 6–10 weeks, learn what grows "
            "in your microclimate, and build confidence before committing to a larger "
            "structure. This is not a consolation prize — it is the honest recommendation."
        ),
        "why_not_others": (
            "A full greenhouse at this budget would mean cutting corners on structure "
            "or glazing. In Nova Scotia, a cheap greenhouse is worse than no greenhouse "
            "— it fails in the first nor'easter and costs you money twice. A cold frame "
            "gives you real growing results without structural risk."
        ),
        "assumptions": [
            "Budget is under $1,000, OR property constraints prevent a full structure",
            "You have access to basic hand tools",
            "Ground is accessible and roughly level",
            "You are open to starting small and upgrading later",
        ],
        "climate_confidence": "high",
        "budget_confidence": "high",
        "site_fit_confidence": "high",
        # Internal mapping to legacy config keys for cost/crop services
        "_legacy_type_id": "polytunnel",
        "_legacy_tier_id": "starter",
    },

    # ──────────────────────────────────────────────────────────────────────
    # 2. THE STARTER KIT
    # ──────────────────────────────────────────────────────────────────────
    "starter_kit": {
        "id": "starter_kit",
        "name": "The Starter Kit",
        "tagline": "Your first real greenhouse — sized right, built to last.",
        "size_range": "8×10 to 8×12 ft",
        "budget_range": "$1,500–$3,500 kit / $2,500–$5,500 installed",
        "frame_material": "Aluminum frame with steel base",
        "glazing": "6mm twin-wall polycarbonate",
        "wind_rating": "Rated for 60–75 km/h gusts (sheltered sites)",
        "snow_load": "Handles moderate NS snow loads (35–40 PSF)",
        "foundation_type": "Gravel pad with treated timber frame",
        "best_for": [
            "First-time greenhouse owners",
            "Suburban backyards with some wind shelter",
            "Budgets of $1,500–$5,500",
            "Season extension and starter food production",
        ],
        "not_suitable_for": [
            "Coastal or hilltop sites with direct wind exposure",
            "Heavy snow zones (Cape Breton, Central NS) without reinforcement",
            "Year-round heated growing",
            "Anyone planning to scale to market production",
        ],
        "materials_list_summary": [
            "Aluminum frame kit with polycarbonate panels",
            "Treated 4×4 timber base frame",
            "Crushed gravel (6\" base, leveled)",
            "Ridge vent and louvre vent",
            "Door with auto-closer",
            "Galvanized ground anchors (4–6)",
            "Basic raised bed lumber (2×10 cedar)",
        ],
        "kit_price_only": "$1,500–$3,500",
        "true_installed_cost": "$2,500–$5,500",
        "why_this": (
            "This is the right entry point for a first greenhouse on a sheltered "
            "backyard lot. The 8×10 to 8×12 footprint gives you enough space for "
            "two raised beds and a potting area without overwhelming your yard or "
            "your budget. The aluminum frame is lighter than steel but adequate for "
            "sites with trees or buildings blocking the worst Maritime winds."
        ),
        "why_not_others": (
            "We did not recommend the Maritime Standard because your budget or site "
            "does not require that level of structural reinforcement. A polytunnel "
            "would be cheaper but the poly film needs replacing every 4–5 years and "
            "struggles in heavy snow. The Starter Kit gives you a permanent structure "
            "at the lowest credible price point."
        ),
        "assumptions": [
            "Site has partial wind shelter (trees, buildings, fence line)",
            "Ground is roughly level or can be leveled with gravel",
            "Budget of $1,500–$5,500 including site prep",
            "No requirement for year-round heated growing",
            "Standard residential property (no unusual zoning)",
        ],
        "climate_confidence": "high",
        "budget_confidence": "high",
        "site_fit_confidence": "medium",
        "_legacy_type_id": "polycarbonate",
        "_legacy_tier_id": "starter",
    },

    # ──────────────────────────────────────────────────────────────────────
    # 3. THE MARITIME STANDARD
    # ──────────────────────────────────────────────────────────────────────
    "maritime_standard": {
        "id": "maritime_standard",
        "name": "The Maritime Standard",
        "tagline": "The greenhouse that survives hurricane season.",
        "size_range": "10×12 to 10×16 ft",
        "budget_range": "$4,000–$8,000 kit / $6,000–$12,000 installed",
        "frame_material": "Galvanized steel frame (14-gauge or heavier)",
        "glazing": "8mm twin-wall polycarbonate (UV-stabilized)",
        "wind_rating": "Rated for 90+ km/h gusts — Fiona-rated",
        "snow_load": "Handles 2+ ft wet Maritime snow (45–55 PSF)",
        "foundation_type": "Concrete piers to frost depth or sono tubes with treated timber sill",
        "best_for": [
            "Most Nova Scotia homeowners",
            "Sites with moderate to high wind exposure",
            "Year-round growing with optional heating",
            "Anyone who wants a structure that lasts 15+ years",
        ],
        "not_suitable_for": [
            "Budgets under $4,000",
            "Very small lots where 10×12 is too large",
            "Users who want passive solar performance without supplemental heating",
        ],
        "materials_list_summary": [
            "Galvanized steel frame kit (14-gauge)",
            "8mm twin-wall polycarbonate panels",
            "Sono tubes or concrete piers (4–6, to frost depth)",
            "Treated 6×6 sill plate",
            "Ridge vent + automatic side louvers (2)",
            "Insulated door with weather stripping",
            "Galvanized anchor bolts",
            "Raised beds (cedar 2×12, 3–4 beds)",
        ],
        "kit_price_only": "$4,000–$8,000",
        "true_installed_cost": "$6,000–$12,000",
        "why_this": (
            "This is the default recommendation for most Nova Scotia properties. "
            "The galvanized steel frame and 8mm polycarbonate are rated for the wind "
            "loads and snow loads that destroy lighter structures every winter. The "
            "10×12 to 10×16 footprint gives you 3–4 raised beds with a proper "
            "working aisle — enough space for a family's year-round vegetable production. "
            "This is the structure that was still standing after Fiona."
        ),
        "why_not_others": (
            "Aluminum-frame kits and polytunnels are not rated for the sustained "
            "gusts your area experiences. Given your location and wind exposure, "
            "we ruled out lighter structures. The Passive Solar Lean-To requires "
            "a south-facing wall attachment — if you have one, it may be worth "
            "considering, but the Maritime Standard is the safer standalone choice."
        ),
        "assumptions": [
            "Site can accommodate a 10×12 to 10×16 footprint",
            "Ground can be leveled and piers dug to frost depth (42–54\")",
            "Budget of $4,000–$12,000 including foundation and assembly",
            "Moderate to high wind exposure typical of Maritime NS",
            "Snow loads of 40–55 PSF expected",
        ],
        "climate_confidence": "high",
        "budget_confidence": "medium",
        "site_fit_confidence": "high",
        "_legacy_type_id": "polycarbonate",
        "_legacy_tier_id": "family",
    },

    # ──────────────────────────────────────────────────────────────────────
    # 4. THE PASSIVE SOLAR LEAN-TO
    # ──────────────────────────────────────────────────────────────────────
    "passive_solar_leanto": {
        "id": "passive_solar_leanto",
        "name": "The Passive Solar Lean-To",
        "tagline": "Harvest heat from your own south wall — grow through a Nova Scotia winter.",
        "size_range": "8×12 to 10×16 ft (attached to existing structure)",
        "budget_range": "$6,000–$10,000 kit / $9,000–$16,000 installed",
        "frame_material": "Timber frame with insulated north/east/west walls",
        "glazing": "Twin-wall polycarbonate or double-pane glass (south face only)",
        "wind_rating": "High — attached structure with insulated mass walls",
        "snow_load": "Handles full Maritime snow (shed roof pitch assists clearing)",
        "foundation_type": "Continuous footing or concrete piers tied to existing structure foundation",
        "best_for": [
            "Homeowners with a south-facing wall on their house, garage, or barn",
            "Year-round growing with minimal energy input",
            "Sustainability-focused growers",
            "Budgets above $8,000 who want performance over size",
        ],
        "not_suitable_for": [
            "Properties without a suitable south-facing wall",
            "Renters or those who cannot modify an existing structure",
            "Users who want a large standalone footprint",
            "Budgets under $6,000",
        ],
        "materials_list_summary": [
            "Timber frame (2×6 or 4×4 posts, engineered connections)",
            "Insulated wall panels (north/east/west — R-20 minimum)",
            "South-face twin-wall polycarbonate or tempered glass",
            "Thermal mass (55-gallon water barrels, 4–8 units)",
            "Continuous footing or pier connection to host building",
            "Insulated door (exterior-grade)",
            "Automatic ridge vent",
            "Ground-level raised beds with thermal base",
        ],
        "kit_price_only": "$6,000–$10,000",
        "true_installed_cost": "$9,000–$16,000",
        "why_this": (
            "You have a south-facing wall and the budget for a high-performance "
            "structure. The Passive Solar Lean-To captures and stores daytime solar "
            "heat using thermal mass, releasing it overnight. In a well-built lean-to, "
            "temperatures stay above freezing through most Maritime winters without "
            "any supplemental heating. This is the most energy-efficient greenhouse "
            "option for Nova Scotia — but it requires the right wall orientation "
            "and a willingness to invest in the build."
        ),
        "why_not_others": (
            "A standalone Maritime Standard would work, but you would need supplemental "
            "heating to grow through winter. The lean-to design eliminates that cost "
            "by using your existing structure as a heat battery. We did not recommend "
            "a Starter Kit because your budget and goals exceed what a basic kit delivers."
        ),
        "assumptions": [
            "You have a south-facing wall (within 30° of true south)",
            "The host wall is structurally sound and you have permission to attach",
            "Budget of $9,000–$16,000 including foundation and thermal mass",
            "You are comfortable with a higher-complexity build (or hiring a builder)",
            "Goal includes winter growing or maximum season extension",
        ],
        "climate_confidence": "high",
        "budget_confidence": "medium",
        "site_fit_confidence": "medium",
        "_legacy_type_id": "passive_solar",
        "_legacy_tier_id": "family",
    },

    # ──────────────────────────────────────────────────────────────────────
    # 5. THE SERIOUS GROWER
    # ──────────────────────────────────────────────────────────────────────
    "serious_grower": {
        "id": "serious_grower",
        "name": "The Serious Grower",
        "tagline": "Built for yield — when season extension is not enough.",
        "size_range": "12×20 to 14×24 ft (or equivalent high tunnel)",
        "budget_range": "$8,000–$15,000 kit / $12,000–$22,000 installed",
        "frame_material": "Commercial-grade galvanized steel (12-gauge) or gothic-arch tubing",
        "glazing": "8mm twin-wall polycarbonate or reinforced greenhouse poly (commercial grade)",
        "wind_rating": "Rated for 100+ km/h — commercial structural spec",
        "snow_load": "Engineered for 55+ PSF (gothic arch sheds snow naturally)",
        "foundation_type": "Concrete piers with steel post anchors, or continuous concrete footing",
        "best_for": [
            "Hobby growers scaling toward market production",
            "Community gardens and food security projects",
            "Grant-funded installations needing defensible specs",
            "Experienced growers who have outgrown smaller structures",
        ],
        "not_suitable_for": [
            "Suburban backyards with limited space",
            "First-time growers (the complexity and cost are premature)",
            "Budgets under $8,000",
            "Properties without vehicle access for material delivery",
        ],
        "materials_list_summary": [
            "Commercial steel frame kit (12-gauge, gothic arch or gable)",
            "8mm polycarbonate or commercial-grade poly with inflation kit",
            "Concrete piers with post anchors (8–12 units)",
            "Roll-up side vents (manual or motorized)",
            "Exhaust fan with thermostat",
            "End-wall with commercial door (sliding or roll-up)",
            "In-ground or raised bed system (6+ beds)",
            "Drip irrigation rough-in",
        ],
        "kit_price_only": "$8,000–$15,000",
        "true_installed_cost": "$12,000–$22,000",
        "why_this": (
            "You are past the hobby stage. Your goals — whether market production, "
            "community food supply, or serious self-sufficiency — require a footprint "
            "and structural rating that smaller greenhouses cannot provide. The 12×20+ "
            "format gives you the bed count for succession planting, the headroom for "
            "vertical crops, and the ventilation capacity for dense planting. This is "
            "the structure you build when growing is not a hobby — it is a commitment."
        ),
        "why_not_others": (
            "The Maritime Standard maxes out at 10×16. For your production goals, "
            "you need more square footage, better ventilation, and commercial-grade "
            "structural integrity. A Passive Solar Lean-To would give you winter "
            "performance but not the footprint. The Serious Grower is a standalone "
            "production facility."
        ),
        "assumptions": [
            "Property has space for a 12×20+ footprint with vehicle access",
            "Budget of $12,000–$22,000 including foundation and professional assembly",
            "Owner has growing experience or is working with experienced partners",
            "Site allows for concrete pier or continuous footing foundation",
            "Electrical access available for ventilation fans",
        ],
        "climate_confidence": "high",
        "budget_confidence": "medium",
        "site_fit_confidence": "medium",
        "_legacy_type_id": "polycarbonate",
        "_legacy_tier_id": "serious",
    },
}


def get_archetype(archetype_id: str) -> Optional[dict]:
    """Return a single archetype by slug, or None if not found."""
    return ARCHETYPES.get(archetype_id)


def get_all_archetypes() -> dict[str, dict]:
    """Return all archetypes."""
    return ARCHETYPES
