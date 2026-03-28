"""Proposal Generation Service — creates the $20 structured proposal.

Takes a session_id, parses intake and extended_intake data, calls the
orchestrating services, and produces a structured proposal dict.
Saves to the database and returns the dict.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models import GreenhouseSession, Proposal
from app.services.design_service import recommend_design
from app.services.cost_service import estimate_costs
from app.services.crop_service import get_crop_plan
from app.services.suitability_service import check_suitability
from app.services.local_routing_service import get_local_resources

import logging
logger = logging.getLogger(__name__)

PROPOSAL_STRUCTURE = {
    "meta": {
        "generated_at": "",
        "data_version": "NS-Q1-2026",
        "session_id": ""
    },
    "intake_summary": {
        "declared": {},
        "inferred": {}
    },
    "recommendation": {
        "archetype_id": "",
        "archetype_name": "",
        "tagline": "",
        "why_this": "",
        "why_not_others": "",
        "size_range": "",
        "specs": {}
    },
    "cost_breakdown": {
        "kit_price_range": "",
        "true_installed_cost_range": "",
        "line_items": [],
        "total_note": ""
    },
    "site_prep": {
        "steps": [],
        "total_estimate": ""
    },
    "crop_fit": {
        "validated_crops": [],
        "warnings": [],
        "mismatches": []
    },
    "confidence": {
        "climate": {"rating": "", "note": ""},
        "budget": {"rating": "", "note": ""},
        "site_fit": {"rating": "", "note": ""},
        "overall": "",
        "escalation_recommended": False,
        "escalation_reason": None
    },
    "next_step": {
        "recommendation": "",
        "reasoning": "",
        "actions": []
    },
    "evidence": {
        "climate_source": "Environment Canada 1991-2020 Climate Normals",
        "cost_basis": "NS supplier and contractor market rates, Q1 2026",
        "archetype_basis": "Manufacturer specs for galvanized steel polycarbonate greenhouse class",
        "disclaimer": "This proposal is a planning tool, not a structural engineering assessment. Validate all recommendations with local professionals before purchasing."
    }
}

CROP_CATEGORY_MAP = {
    "tomatoes": ["Tomatoes"],
    "peppers": ["Peppers"],
    "lettuce_greens": ["Lettuce", "Spinach", "Leafy greens", "Leaf lettuce", "Microgreens", "Kale", "Winter Greens Mix", "Swiss Chard"],
    "herbs": ["Herbs", "Basil"],
    "root_vegetables": ["Root vegetables", "Potatoes", "Carrots", "Radishes", "Garlic"],
    "berries": ["Berries", "Strawberries"],
    "not_sure": []
}

HUMAN_READABLE_MAP = {
    "halifax": "Halifax / HRM",
    "annapolis_valley": "Annapolis Valley",
    "south_shore": "South Shore",
    "eastern_shore": "Eastern Shore",
    "cape_breton": "Cape Breton",
    "central_ns": "Central NS",
    "north_shore": "North Shore",
    
    "grow_food": "Grow my own food",
    "save_money": "Save money on groceries",
    "sustainability": "Sustainability & self-reliance",
    "mixed": "A mix of everything",
    
    "under_5k": "Under $5,000",
    "5k_10k": "$5,000 – $10,000",
    "over_10k": "$10,000+",
    
    "backyard": "Backyard",
    "rural": "Rural land",
    "small_lot": "Small lot",
    "not_sure": "Not sure",
    "unknown": "Unknown",
    "none": "None",

    "polycarbonate": "Backyard Greenhouse (Polycarbonate)",
    "passive_solar": "Passive Solar Greenhouse",
    
    "sheltered": "Sheltered",
    "moderate": "Moderate",
    "coastal_exposed": "Coastal / Exposed",
    
    "yes": "Yes",
    "no": "No",
    
    "first_time": "First-time grower",
    "some_experience": "Some experience",
    "experienced": "Experienced grower",
    
    "rooftop": "Rooftop panels",
    "ground": "Ground-mounted",

    "flat": "Flat",
    "slight": "Slight grade",
    "significant": "Significant slope",
    
    "good": "Good drainage",
    "poor": "Poor drainage",
    
    "fence": "Fence",
    "shed": "Shed",
    "garage": "Garage",
    "house_wall": "House wall",
    "multiple": "Multiple structures",
    
    "spring_to_fall": "Spring to Fall",
    "year_round_unheated": "Year-round (unheated)",
    "year_round_heated": "Year-round (heated)",
    
    "full_diy": "Full DIY",
    "partial_diy": "Partial DIY (hire for foundation)",
    "full_contractor": "Full Contractor"
}

def _hr(val):
    if isinstance(val, list):
        return [_hr(v) for v in val]
    return HUMAN_READABLE_MAP.get(val, val)

def generate_proposal(session_id: str, db: Session) -> dict:
    """Generate a structured proposal dict and save it."""
    
    # 1. Load Session
    gh_session = db.query(GreenhouseSession).filter_by(id=session_id).first()
    if not gh_session:
        raise ValueError(f"Session {session_id} not found")
        
    intake = json.loads(gh_session.intake_data) if gh_session.intake_data else {}
    
    try:
        ext_intake = json.loads(gh_session.extended_intake_data) if gh_session.extended_intake_data else {}
    except Exception:
        ext_intake = {}
        
    extended_provided = bool(ext_intake)
        
    # Apply defaults if missing extended intake
    slope = ext_intake.get("slope", "not_sure")
    drainage = ext_intake.get("drainage", "not_sure")
    nearby_structures = ext_intake.get("nearby_structures", "not_sure")
    desired_crops = ext_intake.get("desired_crops", ["not_sure"])
    seasonal_intent = ext_intake.get("seasonal_intent", "not_sure")
    diy_or_contractor = ext_intake.get("diy_or_contractor", "not_sure")
    
    # Initialize proposal dict
    # deep copy to avoid mutating constant
    proposal = json.loads(json.dumps(PROPOSAL_STRUCTURE))
    proposal["meta"]["generated_at"] = datetime.now(timezone.utc).isoformat()
    proposal["meta"]["session_id"] = session_id
    if not extended_provided:
        proposal["meta"]["extended_intake_provided"] = False
        
    # --- Block 1: Intake Summary ---
    declared = {}
    inferred = {}
    
    # helper for tracking
    def process_field(store_key, val, default_reason=None):
        if val in [None, "not_sure", "unknown", "none"]:
            inferred[store_key] = f"Not specified → {default_reason}" if default_reason else "Not specified"
        elif isinstance(val, list) and len(val) == 1 and val[0] in [None, "not_sure", "unknown", "none"]:
            inferred[store_key] = f"Not specified → {default_reason}" if default_reason else "Not specified"
        else:
            declared[store_key] = _hr(val)

    # Standard intake
    process_field("location", intake.get("location"), "Assumed Halifax/HRM climate profile")
    process_field("goal", intake.get("goal"), "Assumed generic food production")
    process_field("budget", intake.get("budget"), "Assumed standard entry-level pricing band")
    process_field("property_type", intake.get("property_type"), "Assumed standard backyard dimensions")
    process_field("greenhouse_preference", intake.get("greenhouse_type", intake.get("greenhouse_preference")), "System selected archetype based on wind and budget")
    process_field("wind_exposure", intake.get("wind_exposure"), "Assumed moderate exposure")
    process_field("has_south_wall", intake.get("has_south_wall"), "Passive solar lean-to deprioritized")
    process_field("experience_level", intake.get("experience_level"), "Safety-first crop plan provided")
    process_field("solar_existing", intake.get("solar_existing"), "No solar assumed")
    
    # Extended intake
    if extended_provided:
        process_field("slope", slope, "Assumed flat graded site")
        process_field("drainage", drainage, "Assumed standard drainage, no remediation required")
        process_field("nearby_structures", nearby_structures, "Assumed open site, no wind shelter from structures")
        process_field("desired_crops", desired_crops, "Standard archetype crops recommended")
        process_field("seasonal_intent", seasonal_intent, "Assumed spring-to-fall seasonal use")
        process_field("diy_or_contractor", diy_or_contractor, "Costing includes both DIY and Contractor options")
    else:
        inferred["extended_property_details"] = "Extended property details not provided. Using default assumptions for all."
        
    proposal["intake_summary"]["declared"] = declared
    proposal["intake_summary"]["inferred"] = inferred

    # --- Block 2: Recommendation Recap ---
    suitability = check_suitability(intake)
    archetype = recommend_design(intake, suitability)
    
    rec = proposal["recommendation"]
    rec["archetype_id"] = archetype.get("id", "")
    rec["archetype_name"] = archetype.get("name", "")
    rec["tagline"] = archetype.get("tagline", "")
    rec["why_this"] = archetype.get("why_this", "")
    rec["why_not_others"] = archetype.get("why_not_others", "")
    rec["size_range"] = archetype.get("size_range", "")
    rec["specs"] = archetype
    
    # --- Block 3: Installed Cost Breakdown ---
    costs = estimate_costs("", "", suitability["climate"], archetype_id=rec["archetype_id"])
    
    cb = proposal["cost_breakdown"]
    cb["kit_price_range"] = costs.get("kit_price_range", "")
    cb["true_installed_cost_range"] = costs.get("true_installed_cost_range", "")
    cb["line_items"] = costs.get("line_items", [])
    cb["total_note"] = costs.get("total_note", "")

    # Adjustments based on extended intake
    for item in cb["line_items"]:
        if "Labor" in item["category"]:
            if diy_or_contractor == "full_diy":
                item["note"] = f"{item['note']}. DIY assembly — labor cost assumes 0 if you do it yourself. Budget $0–$500 for tools/rental."
        if "Foundation" in item["category"] or "Site Prep" in item["category"]:
            if slope == "significant":
                item["note"] = f"{item['note']}. Significant slope detected. Site prep costs may be at the higher end of this range or require professional grading ($500–$1,500 additional)."
            
    # Add disclaimer
    cb["total_note"] = f"{cb['total_note']} Directional estimate. Validate with local quotes."

    # --- Block 4: Site Prep Checklist ---
    sp = proposal["site_prep"]
    steps = []
    
    steps.append({"step": 1, "action": "Choose and mark your site", "cost_estimate": "$0", "note": "Select a location with maximum southern exposure. Mark the footprint with stakes and string."})
    steps.append({"step": 2, "action": "Check for underground utilities", "cost_estimate": "$0", "note": "Call Nova Scotia Power / municipal utility locator before digging."})
    
    found_type = archetype.get("foundation_type", "").lower()
    
    if "gravel" in found_type or "timber" in found_type:
        lev_cost = "$100–$200"
        if slope == "slight": lev_cost = "$200–$500"
        elif slope == "significant": lev_cost = "$500–$1,500 — may need professional grading"
        steps.append({"step": 3, "action": "Clear and level the ground", "cost_estimate": lev_cost, "note": ""})
        steps.append({"step": 4, "action": "Lay gravel base (4–6 inches)", "cost_estimate": "$200–$400", "note": ""})
        steps.append({"step": 5, "action": "Build treated timber perimeter frame", "cost_estimate": "$150–$300", "note": ""})
    elif "pler" in found_type or "pier" in found_type or "concrete" in found_type:
        lev_cost = "$100–$200"
        if slope == "slight": lev_cost = "$200–$500"
        elif slope == "significant": lev_cost = "$500–$1,500 — may need professional grading"
        steps.append({"step": 3, "action": "Clear and level the ground", "cost_estimate": lev_cost, "note": ""})
        steps.append({"step": 4, "action": "Dig and pour concrete piers (4–6 piers)", "cost_estimate": "$400–$800", "note": ""})
        steps.append({"step": 5, "action": "Install anchor bolts and framing", "cost_estimate": "$200–$400", "note": ""})
    elif "cold_frame_bridge" in rec["archetype_id"]:
        steps.append({"step": 3, "action": "Level the bed area", "cost_estimate": "$0–$100", "note": "Cold frames sit directly on prepared soil or raised beds."})

    if drainage == "poor":
        steps.append({"step": len(steps)+1, "action": "Install French drain or redirect surface water", "cost_estimate": "$300–$800", "note": "Poor drainage can undermine foundations and flood growing beds."})
    elif drainage in ["not_sure", "unknown", None]:
        steps.append({"step": len(steps)+1, "action": "Test drainage", "cost_estimate": "$0", "note": "Pour a bucket of water, observe. If water pools for more than 30 minutes, you may need drainage work."})

    sp["steps"] = steps
    
    def extract_avg(cost_str):
        import re
        nums = [int(n.replace(',', '')) for n in re.findall(r'\d+,\d+|\d+', cost_str)]
        if not nums: return 0
        return sum(nums) / len(nums)

    total_low = sum([min([int(n.replace(',','')) for n in __import__('re').findall(r'\d+,\d+|\d+', s["cost_estimate"])] + [0]) for s in steps if __import__('re').findall(r'\d+,\d+|\d+', s["cost_estimate"])])
    total_high = sum([max([int(n.replace(',','')) for n in __import__('re').findall(r'\d+,\d+|\d+', s["cost_estimate"])] + [0]) for s in steps if __import__('re').findall(r'\d+,\d+|\d+', s["cost_estimate"])])
    
    sp["total_estimate"] = f"${total_low:,}–${total_high:,}. Directional estimate. Validate with local quotes."

    # --- Block 5: Crop-Fit Validation ---
    cf = proposal["crop_fit"]
    
    # We fetch crops but ignore the strict archetype validation output there
    # since we want to manually validate against desired_crops.
    crop_plan = get_crop_plan("", intake.get("goal",""), intake.get("location",""), archetype_id=rec["archetype_id"])
    supported_names_in_arch = [c["name"].lower() for c in crop_plan.get("crops", [])]
    
    if not extended_provided or desired_crops == ["not_sure"] or not desired_crops:
        cf["validated_crops"] = []
        cf["note"] = "No specific crops selected. See the full crop plan in your recommendation for suggestions."
    else:
        for cat in desired_crops:
            if cat in ["not_sure", "none"]:
                continue
                
            mapped = CROP_CATEGORY_MAP.get(cat, [])
            mapped_lower = [m.lower() for m in mapped]
            
            # Check for matches
            matched_spec = None
            for m in mapped_lower:
                for a_crop in supported_names_in_arch:
                    if m in a_crop or a_crop in m:
                        matched_spec = a_crop.title()
                        break
                if matched_spec: break
                
            hr_cat = _hr(cat)
                
            # Special Tomato Rule
            if cat == "tomatoes" and rec["archetype_id"] == "cold_frame_bridge":
                cf["mismatches"].append({
                    "crop": hr_cat,
                    "issue": f"{hr_cat} requires consistent warmth that the Cold Frame Bridge cannot provide. Consider upgrading to the Maritime Standard, or plant cold-hardy alternatives."
                })
                continue
                
            if matched_spec:
                cf["validated_crops"].append({
                    "name": hr_cat,
                    "status": "supported",
                    "note": f"Your archetype supports {matched_spec}."
                })
            else:
                if rec["archetype_id"] in ["maritime_standard", "serious_grower"]:
                    cf["validated_crops"].append({
                        "name": hr_cat,
                        "status": "partial",
                        "note": "Not in the standard crop plan for your archetype, but may be possible with modifications."
                    })
                else:
                    cf["mismatches"].append({
                        "crop": hr_cat,
                        "issue": f"{hr_cat} requires consistent warmth that the {rec['archetype_name']} cannot provide. Consider upgrading to the Maritime Standard, or plant cold-hardy alternatives."
                    })
    
    # --- Block 6: Confidence Assessment ---
    conf = proposal["confidence"]
    
    # Climate
    location = intake.get("location", "halifax")
    if location in ["halifax", "annapolis_valley", "south_shore", "cape_breton", "central_ns", "north_shore", "eastern_shore"]:
        conf["climate"]["rating"] = "high"
    else:
        conf["climate"]["rating"] = "medium"
    conf["climate"]["note"] = f"Climate data for {_hr(location)} is based on Environment Canada 1991-2020 normals."
    
    # Budget
    budget_raw = intake.get("budget", "under_5k")
    b_high = 5000 if budget_raw == "under_5k" else 10000 if budget_raw == "5k_10k" else 999999
    
    import re
    # Extract high end of true installed cost
    tic_str = cb["true_installed_cost_range"]
    nums = [int(n.replace(',', '')) for n in re.findall(r'\d+,\d+|\d+', tic_str)]
    t_high = max(nums) if nums else 0
    t_low = min(nums) if nums else 0
    
    if b_high >= t_high:
        conf["budget"]["rating"] = "high"
        conf["budget"]["note"] = f"Your budget of {_hr(budget_raw)} covers the estimated True Installed Cost range fully."
    elif b_high >= t_low:
        conf["budget"]["rating"] = "medium"
        conf["budget"]["note"] = f"Your budget of {_hr(budget_raw)} covers the low end of the True Installed Cost range."
    else:
        conf["budget"]["rating"] = "low"
        conf["budget"]["note"] = f"Your budget of {_hr(budget_raw)} does not cover the estimated True Installed Cost."
        
    # Site Fit
    conf["site_fit"]["rating"] = "high"
    conf["site_fit"]["note"] = "Standard site conditions assumed."
    
    if slope == "significant":
        conf["site_fit"]["rating"] = "medium"
        conf["site_fit"]["note"] = "Significant slope increases site prep complexity and cost."
    if drainage == "poor":
        if slope == "significant":
            conf["site_fit"]["rating"] = "low"
            conf["site_fit"]["note"] = "Significant slope combined with poor drainage creates meaningful site risk. Professional site assessment recommended."
        else:
            conf["site_fit"]["rating"] = "medium"
            conf["site_fit"]["note"] = "Poor drainage may require remediation before construction."
    
    wind = intake.get("wind_exposure", "moderate")
    if wind == "coastal_exposed" and rec["archetype_id"] not in ["maritime_standard", "serious_grower"]:
        conf["site_fit"]["rating"] = "low"
        conf["site_fit"]["note"] = "Your wind exposure exceeds the structural rating of the recommended archetype."
        
    if not extended_provided:
        if conf["site_fit"]["rating"] == "high":
            conf["site_fit"]["rating"] = "medium"
            conf["site_fit"]["note"] = "Site details not provided. Defaulting to medium confidence."
    elif slope in ["not_sure", "unknown", None] or drainage in ["not_sure", "unknown", None]:
        if conf["site_fit"]["rating"] == "high":
            conf["site_fit"]["rating"] = "medium"
            conf["site_fit"]["note"] = "Some site details are unknown. Defaulting to medium confidence."
            
    # Overall
    def rank(r): return {"low": 1, "medium": 2, "high": 3}.get(r, 0)
    
    min_rank = min(rank(conf["climate"]["rating"]), rank(conf["budget"]["rating"]), rank(conf["site_fit"]["rating"]))
    overall_rating = "high" if min_rank == 3 else "medium" if min_rank == 2 else "low"
    
    conf["overall"] = overall_rating
    if overall_rating == "low":
        conf["escalation_recommended"] = True
        conf["escalation_reason"] = "One or more confidence dimensions is LOW. A Site Feasibility Review ($79) would help validate whether this project is viable for your specific property."
        
    # --- Block 7: Next Step Recommendation ---
    ns = proposal["next_step"]
    
    if conf["escalation_recommended"]:
        ns["actions"].append({"type": "consultation", "label": "⚠ Recommended: Site Feasibility Review ($79)", "url": "/action/consultation"})
        
    if diy_or_contractor == "full_diy":
        ns["recommendation"] = "Source your materials"
        ns["reasoning"] = (
            "You indicated full DIY. Your next step is to source the kit and materials. "
            "Start with the structure — check availability at Kent Building Supplies or order "
            "directly from a greenhouse kit supplier (see local resources below). "
            "Budget 1-2 weekends for foundation prep and 1-2 weekends for assembly."
        )
        ns["actions"].extend([
            {"type": "resources", "label": "View Local Suppliers", "url": "#local-resources"},
            {"type": "consultation", "label": "Book a Quick Check ($49)", "url": "/action/consultation"}
        ])
    elif diy_or_contractor == "full_contractor":
        ns["recommendation"] = "Request a builder quote"
        ns["reasoning"] = (
            "You indicated full contractor. Your next step is to get quotes from local builders "
            "who work with this type of greenhouse structure. We can route your archetype specs "
            "and budget to builders in your area so you enter the conversation informed."
        )
        ns["actions"].extend([
            {"type": "quote", "label": "Request Builder Quote", "url": "/action/quote"},
            {"type": "consultation", "label": "Book Site Feasibility Review ($79)", "url": "/action/consultation"}
        ])
    elif diy_or_contractor == "partial_diy":
        ns["recommendation"] = "Buy the kit, hire for foundation and assembly"
        ns["reasoning"] = (
            "You indicated partial DIY. A practical split: order the kit yourself (saves markup), "
            "then hire a local contractor for foundation prep and structure assembly. "
            "Get a builder quote for the labor portion only."
        )
        ns["actions"].extend([
            {"type": "quote", "label": "Request Builder Quote (Labor Only)", "url": "/action/quote"},
            {"type": "resources", "label": "View Kit Suppliers", "url": "#local-resources"}
        ])
    else:  # not_sure
        ns["recommendation"] = "Start with a builder quote to understand your options"
        ns["reasoning"] = (
            "Not sure whether to DIY or hire? Start by getting a builder quote. "
            "This gives you a real number for the full-service option. "
            "You can always decide to DIY after seeing the quote."
        )
        ns["actions"].extend([
            {"type": "quote", "label": "Request Builder Quote", "url": "/action/quote"},
            {"type": "resources", "label": "View Local Suppliers", "url": "#local-resources"},
            {"type": "consultation", "label": "Book a Consultation", "url": "/action/consultation"}
        ])
        
    # Idempotent DB save
    existing_proposal = db.query(Proposal).filter_by(session_id=session_id).first()
    if existing_proposal:
        existing_proposal.proposal_data = json.dumps(proposal)
        existing_proposal.status = "draft"
        existing_proposal.generated_at = datetime.now(timezone.utc)
        logger.info(f"Updated existing proposal for session {session_id}")
    else:
        new_proposal = Proposal(
            id=str(import_uuid().uuid4()),
            session_id=session_id,
            proposal_data=json.dumps(proposal),
            status="draft",
        )
        db.add(new_proposal)
        logger.info(f"Created new proposal for session {session_id}")
        
    db.commit()
    
    return proposal

def import_uuid():
    import uuid
    return uuid

