"""Crop Plan Service — archetype-aware crop recommendations.

Each archetype has a curated crop set. Experience level filters difficulty.
Every crop includes archetype_fit and first_harvest_weeks.
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


# ── Archetype-specific crop sets ─────────────────────────────────────────
# Keyed by archetype_id. Each crop has: name, season, difficulty, reason,
# first_harvest_weeks, archetype_fit.

_CROP_MATRIX: dict[str, list[dict]] = {
    "cold_frame_bridge": [
        {"name": "Kale", "season": "March–May start, harvest May–Nov", "difficulty": "easy",
         "reason": "NS cold-hardy champion. Sweetens after frost — perfect for cold frame growing.",
         "first_harvest_weeks": 8, "archetype_fit": "Thrives at cold frame temperatures. No heat needed."},
        {"name": "Lettuce & Salad Greens", "season": "March–May start, harvest April–Nov", "difficulty": "easy",
         "reason": "Fast-growing and cold-tolerant. Succession sow every 2 weeks for continuous harvest.",
         "first_harvest_weeks": 4, "archetype_fit": "Perfect cold frame crop — low light and cool temps are fine."},
        {"name": "Spinach", "season": "March start, harvest April–Nov", "difficulty": "easy",
         "reason": "Grows in temperatures as low as -5°C. One of the best cold frame crops for NS.",
         "first_harvest_weeks": 5, "archetype_fit": "Cold-hardy down to light frost. Ideal cold frame use."},
        {"name": "Radishes", "season": "March start, direct sow, harvest April–Oct", "difficulty": "easy",
         "reason": "30-day crop. Quick wins build confidence between longer-cycle plantings.",
         "first_harvest_weeks": 4, "archetype_fit": "Fast turnaround crop perfect for cold frame beginners."},
        {"name": "Carrots (short varieties)", "season": "April start, harvest June–Oct", "difficulty": "easy",
         "reason": "Short-root varieties like Nantes or Chantenay work well in cold frame depth.",
         "first_harvest_weeks": 10, "archetype_fit": "Deeper cold frames (12\"+) support root crops well."},
        {"name": "Arugula", "season": "March start, harvest April–Oct", "difficulty": "easy",
         "reason": "Bolt-resistant in cool temps. High-value salad green that grows fast.",
         "first_harvest_weeks": 3, "archetype_fit": "Cool-season crop that thrives in cold frame conditions."},
    ],

    "starter_kit": [
        {"name": "Tomatoes", "season": "Start indoor March, transplant May, harvest Jul–Oct", "difficulty": "easy",
         "reason": "The #1 greenhouse crop. Greenhouse protection extends the NS tomato season by 8+ weeks.",
         "first_harvest_weeks": 12, "archetype_fit": "The Starter Kit provides enough warmth and space for 4–6 indeterminate plants."},
        {"name": "Lettuce & Salad Greens", "season": "March–May start, harvest March–Nov", "difficulty": "easy",
         "reason": "Succession plant every 2 weeks. You'll never buy bagged salad again.",
         "first_harvest_weeks": 4, "archetype_fit": "Low-light tolerant. Fills bed edges and gaps between larger plants."},
        {"name": "Kale", "season": "March start, harvest May–Nov", "difficulty": "easy",
         "reason": "NS-proven, extremely productive. One kale plant yields 2–3 lbs over a season.",
         "first_harvest_weeks": 8, "archetype_fit": "Hardy enough to tolerate the Starter Kit's unheated overnight temps."},
        {"name": "Cucumbers", "season": "Start indoor April, transplant May, harvest Jul–Sep", "difficulty": "easy",
         "reason": "Train vertically to maximize limited Starter Kit floor space.",
         "first_harvest_weeks": 9, "archetype_fit": "English greenhouse varieties thrive in the Starter Kit's protected environment."},
        {"name": "Basil & Herbs", "season": "March start, harvest May–Oct", "difficulty": "easy",
         "reason": "Basil, cilantro, parsley, dill — high grocery value per square foot.",
         "first_harvest_weeks": 6, "archetype_fit": "Herbs love the warmth of an enclosed polycarbonate space."},
        {"name": "Peas (snap/snow)", "season": "March start, harvest June–Jul", "difficulty": "easy",
         "reason": "Quick spring crop. Train up the greenhouse frame for vertical growing.",
         "first_harvest_weeks": 8, "archetype_fit": "Good early-season crop before warm-season plants take over the space."},
        {"name": "Spinach", "season": "March start, harvest April–Nov", "difficulty": "easy",
         "reason": "Cold-hardy guaranteed crop. Good for shoulder season when other crops taper off.",
         "first_harvest_weeks": 5, "archetype_fit": "Fills the spring and fall gaps in the Starter Kit growing calendar."},
    ],

    "maritime_standard": [
        {"name": "Tomatoes", "season": "Start indoor March, transplant May, harvest Jul–Oct", "difficulty": "easy",
         "reason": "The Maritime Standard's wind-rated structure means reliable warmth for full-season tomato production.",
         "first_harvest_weeks": 12, "archetype_fit": "Thrives in the Maritime Standard's consistent ventilation and 10×16 space."},
        {"name": "Cucumbers", "season": "Start indoor April, transplant May, harvest Jul–Sep", "difficulty": "easy",
         "reason": "Train vertically on greenhouse frame. English greenhouse varieties produce heavily.",
         "first_harvest_weeks": 9, "archetype_fit": "The steel frame provides strong trellising support for vertical cucumber growth."},
        {"name": "Peppers", "season": "Start indoor Feb, transplant May, harvest Jul–Oct", "difficulty": "moderate",
         "reason": "A greenhouse is the ONLY reliable way to grow peppers in NS. High grocery savings.",
         "first_harvest_weeks": 14, "archetype_fit": "The Maritime Standard holds heat well enough for pepper production without supplemental heating."},
        {"name": "Lettuce & Salad Greens", "season": "March–Nov continuous", "difficulty": "easy",
         "reason": "Succession plant every 2 weeks. The Maritime Standard's 3–4 beds support year-round greens rotation.",
         "first_harvest_weeks": 4, "archetype_fit": "Low-light tolerant. Perfect for bed edges and inter-planting."},
        {"name": "Kale", "season": "March start, harvest May–Nov", "difficulty": "easy",
         "reason": "NS cold-hardy champion. Sweetens after frost. Produces heavily in the Maritime Standard's full beds.",
         "first_harvest_weeks": 8, "archetype_fit": "Hardy enough for unheated Maritime Standard shoulder-season temps."},
        {"name": "Basil & Herbs", "season": "March start, harvest May–Oct", "difficulty": "easy",
         "reason": "High grocery value per square foot. Basil, cilantro, parsley, dill — all thrive in greenhouse warmth.",
         "first_harvest_weeks": 6, "archetype_fit": "Herbs maximize the value of the Maritime Standard's protected growing environment."},
        {"name": "Spinach", "season": "March start, harvest April–Nov", "difficulty": "easy",
         "reason": "Cold-tolerant. Fills calendar gaps. One of the most reliable shoulder-season crops.",
         "first_harvest_weeks": 5, "archetype_fit": "Extends the Maritime Standard's productive months into early spring and late fall."},
        {"name": "Beans (bush)", "season": "May start, harvest Jul–Sep", "difficulty": "easy",
         "reason": "Quick summer crop. Fixes nitrogen for following plantings.",
         "first_harvest_weeks": 7, "archetype_fit": "Compact enough for Maritime Standard beds. Improves soil for next rotation."},
        {"name": "Swiss Chard", "season": "March start, harvest May–Nov", "difficulty": "easy",
         "reason": "Cut-and-come-again greens. Beautiful and productive for 6+ months.",
         "first_harvest_weeks": 7, "archetype_fit": "Tolerates wide temperature swings typical of Maritime greenhouse growing."},
        {"name": "Microgreens", "season": "Year-round", "difficulty": "easy",
         "reason": "7–14 day crop. No supplemental light needed. Highest nutrition per square foot.",
         "first_harvest_weeks": 2, "archetype_fit": "Can be grown on shelves — doesn't compete with bed space."},
    ],

    "passive_solar_leanto": [
        {"name": "Winter Lettuce", "season": "Sep start, harvest Oct–Mar", "difficulty": "moderate",
         "reason": "Grows slowly but steadily through NS winter using stored solar heat.",
         "first_harvest_weeks": 6, "archetype_fit": "The thermal mass in the Passive Solar Lean-To sustains winter lettuce without supplemental heat."},
        {"name": "Kale", "season": "March start, harvest year-round", "difficulty": "easy",
         "reason": "Survives near-freezing temps. The lean-to's thermal mass keeps it productive through winter.",
         "first_harvest_weeks": 8, "archetype_fit": "Year-round production in the lean-to's moderated temperature environment."},
        {"name": "Spinach", "season": "March start, harvest year-round in lean-to", "difficulty": "easy",
         "reason": "Cold-hardy to -5°C. The lean-to extends this into true year-round production.",
         "first_harvest_weeks": 5, "archetype_fit": "Thrives in the Passive Solar Lean-To's cool but frost-free winter conditions."},
        {"name": "Tomatoes", "season": "Start indoor March, transplant May, harvest Jul–Oct", "difficulty": "easy",
         "reason": "Full summer production, with extended shoulder season thanks to thermal mass.",
         "first_harvest_weeks": 12, "archetype_fit": "The lean-to's south-facing glazing maximizes solar gain for warm-season crops."},
        {"name": "Garlic (overwintered)", "season": "Plant Oct, harvest July", "difficulty": "easy",
         "reason": "Plant in fall, harvest mid-summer. NS garlic is premium quality. Perfect lean-to crop.",
         "first_harvest_weeks": 36, "archetype_fit": "Overwintering garlic thrives in the lean-to's frost-protected but cool environment."},
        {"name": "Microgreens", "season": "Year-round", "difficulty": "easy",
         "reason": "7–14 day crop. The lean-to's stable temps make winter microgreen production reliable.",
         "first_harvest_weeks": 2, "archetype_fit": "Shelf-grown. Benefits from the lean-to's consistent winter temperatures."},
        {"name": "Peppers", "season": "Start Feb, transplant May, harvest Jul–Oct", "difficulty": "moderate",
         "reason": "The lean-to's heat retention gives peppers the warm nights they need to set fruit.",
         "first_harvest_weeks": 14, "archetype_fit": "South-facing glazing plus thermal mass creates ideal pepper growing conditions."},
        {"name": "Swiss Chard", "season": "March start, harvest May–Dec in lean-to", "difficulty": "easy",
         "reason": "Cut-and-come-again greens. Extended harvest season in the lean-to environment.",
         "first_harvest_weeks": 7, "archetype_fit": "Tolerates the lean-to's wide seasonal temperature range."},
        {"name": "Herbs (cold-hardy)", "season": "March start, some year-round", "difficulty": "easy",
         "reason": "Rosemary, thyme, oregano, sage — perennial herbs that overwinter in the lean-to.",
         "first_harvest_weeks": 8, "archetype_fit": "Mediterranean herbs that would die outside in NS winter survive in the lean-to."},
    ],

    "serious_grower": [
        {"name": "Tomatoes (succession)", "season": "Stagger Feb–Apr starts, harvest Jun–Nov", "difficulty": "easy",
         "reason": "Succession planting 3 waves ensures continuous harvest from June through November.",
         "first_harvest_weeks": 12, "archetype_fit": "The Serious Grower's 12×20+ footprint supports 12–20 indeterminate tomato plants."},
        {"name": "Cucumbers (succession)", "season": "Stagger Apr–Jun, harvest Jul–Oct", "difficulty": "easy",
         "reason": "2 waves ensures no cucumber gap. English greenhouse varieties produce 20+ lbs per plant.",
         "first_harvest_weeks": 9, "archetype_fit": "Commercial ventilation prevents the mildew that kills cucumbers in smaller structures."},
        {"name": "Peppers (mixed varieties)", "season": "Start Feb, transplant May, harvest Jul–Nov", "difficulty": "moderate",
         "reason": "Sweet and hot varieties. Plant 20+ for meaningful production volume.",
         "first_harvest_weeks": 14, "archetype_fit": "The Serious Grower's heat retention and space supports pepper diversity."},
        {"name": "Lettuce & Salad Greens", "season": "Year-round succession", "difficulty": "easy",
         "reason": "Market-rate salad greens. Succession plant weekly for continuous harvest and potential sales.",
         "first_harvest_weeks": 4, "archetype_fit": "Dedicated salad beds with weekly succession planting maximize the Serious Grower format."},
        {"name": "Kale", "season": "March start, year-round with succession", "difficulty": "easy",
         "reason": "Market crop. 30+ plants produce enough for personal use AND market sales.",
         "first_harvest_weeks": 8, "archetype_fit": "Cold-hardy enough for early spring and late fall production in the unheated Serious Grower."},
        {"name": "Basil (production scale)", "season": "March start, harvest May–Oct", "difficulty": "easy",
         "reason": "High-value market crop. 50+ basil plants produce meaningful revenue.",
         "first_harvest_weeks": 6, "archetype_fit": "Scale basil production using the Serious Grower's large bed count."},
        {"name": "Beans (bush, succession)", "season": "May–Jul staggered, harvest Jun–Sep", "difficulty": "easy",
         "reason": "3 succession plantings ensure continuous yield. Fixes nitrogen for following crops.",
         "first_harvest_weeks": 7, "archetype_fit": "Quick turnover crop that maximizes Serious Grower bed utilization."},
        {"name": "Spinach (market scale)", "season": "March start, succession through Nov", "difficulty": "easy",
         "reason": "Baby spinach at market scale. Harvest at 3 weeks for premium baby leaf.",
         "first_harvest_weeks": 3, "archetype_fit": "High-density planting in dedicated beds for market-quality baby spinach."},
        {"name": "Swiss Chard", "season": "March start, harvest May–Nov", "difficulty": "easy",
         "reason": "Rainbow chard is market-attractive and long-producing. Plant once, harvest for 6 months.",
         "first_harvest_weeks": 7, "archetype_fit": "Low-maintenance production crop for the Serious Grower's extended rotation."},
        {"name": "Eggplant", "season": "Start Feb, transplant May, harvest Aug–Oct", "difficulty": "moderate",
         "reason": "High-value crop impossible to grow outdoors in NS. Greenhouse-only in Maritime climate.",
         "first_harvest_weeks": 16, "archetype_fit": "Needs the Serious Grower's sustained daytime heat plus nighttime heat retention."},
        {"name": "Melons", "season": "Start Mar, transplant May, harvest Aug–Sep", "difficulty": "advanced",
         "reason": "Cantaloupe and specialty melons — impossible outdoors in NS. Premium market value.",
         "first_harvest_weeks": 14, "archetype_fit": "Only viable in the Serious Grower's large footprint with full solar exposure."},
        {"name": "Microgreens (commercial)", "season": "Year-round, 7–14 day cycle", "difficulty": "easy",
         "reason": "Highest revenue per square foot. Restaurant and market demand in HRM is strong.",
         "first_harvest_weeks": 2, "archetype_fit": "Shelving system in the Serious Grower supports commercial microgreen production."},
        {"name": "Garlic (overwintered)", "season": "Plant Oct, harvest July", "difficulty": "easy",
         "reason": "NS garlic is premium. 200+ cloves planted in fall produce meaningful harvest.",
         "first_harvest_weeks": 36, "archetype_fit": "The Serious Grower's large bed count allows garlic to occupy beds over winter."},
        {"name": "Winter Greens Mix", "season": "Sep start, harvest Nov–Mar", "difficulty": "moderate",
         "reason": "Mâche, claytonia, winter purslane — cold-hardy greens for shoulder-season market sales.",
         "first_harvest_weeks": 6, "archetype_fit": "Extends the Serious Grower's revenue season into winter months."},
    ],
}


def get_crop_plan(
    greenhouse_type: str,
    goal: str,
    location: str,
    archetype_id: str = "",
    experience_level: str = "first_time",
) -> dict:
    """
    Recommend crops based on archetype, goal, and experience level.

    If archetype_id is provided, use the archetype-specific crop set.
    Falls back to legacy behavior if archetype_id is empty.
    """
    data = _load_data()
    climate = data["climate_zones"].get(location, data["climate_zones"]["halifax"])

    # Determine which crop set to use
    if archetype_id and archetype_id in _CROP_MATRIX:
        all_crops = list(_CROP_MATRIX[archetype_id])
    else:
        # Legacy fallback: use maritime_standard as default
        all_crops = list(_CROP_MATRIX.get("maritime_standard", []))

    # Filter by experience level
    if experience_level == "first_time":
        crops = [c for c in all_crops if c["difficulty"] != "advanced"]
    elif experience_level == "some_experience":
        # Include all, but flag advanced ones
        crops = []
        for c in all_crops:
            entry = dict(c)
            if entry["difficulty"] == "advanced":
                entry["experience_note"] = "Advanced crop — suitable for growers with prior greenhouse experience."
            crops.append(entry)
    else:
        # Experienced: include everything
        crops = all_crops

    # Goal-based prioritization (move goal-relevant crops to top)
    goal_priority = {
        "grow_food": ["Tomatoes", "Cucumbers", "Kale", "Lettuce"],
        "save_money": ["Peppers", "Basil", "Tomatoes", "Herbs"],
        "sustainability": ["Kale", "Garlic", "Winter", "Spinach"],
        "mixed": ["Tomatoes", "Lettuce", "Kale", "Cucumbers"],
    }
    priority_names = goal_priority.get(goal, [])

    def sort_key(crop):
        name = crop["name"]
        for i, pn in enumerate(priority_names):
            if pn in name:
                return i
        return 100

    crops.sort(key=sort_key)

    # Build seasonal timeline
    seasons = {
        "spring": [c["name"] for c in crops if "March" in c.get("season", "") or "April" in c.get("season", "")],
        "summer": [c["name"] for c in crops if any(m in c.get("season", "") for m in ["Jul", "Aug", "Jun"])],
        "fall": [c["name"] for c in crops if any(m in c.get("season", "") for m in ["Sep", "Oct", "Nov"])],
        "winter": [c["name"] for c in crops if any(m in c.get("season", "") for m in ["Dec", "Jan", "Feb", "Year-round"])],
    }

    archetype_label = archetype_id.replace("_", " ").title() if archetype_id else greenhouse_type

    return {
        "recommendation": f"{len(crops)} crops selected for your {archetype_label}",
        "why": (
            f"These crops are curated for the {archetype_label} in "
            f"{climate['label']} (Zone {climate['zone']}, "
            f"{climate['growing_season_days']}-day outdoor season). "
            f"Your greenhouse extends this dramatically."
        ),
        "assumptions": (
            f"Based on a {archetype_label} in {climate['label']}. "
            f"Experience level: {experience_level.replace('_', ' ')}. "
            f"Crops filtered accordingly."
        ),
        "next_step": "Your full plan includes planting schedules and spacing guides for each crop.",
        "crops": [
            {
                "name": c["name"],
                "season": c["season"],
                "difficulty": c["difficulty"],
                "reason": c["reason"],
                "first_harvest_weeks": c["first_harvest_weeks"],
                "archetype_fit": c["archetype_fit"],
                **({"experience_note": c["experience_note"]} if "experience_note" in c else {}),
            }
            for c in crops
        ],
        "seasonal_timeline": seasons,
    }
