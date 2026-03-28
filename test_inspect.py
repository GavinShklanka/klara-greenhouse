import sys, json
sys.path.insert(0, ".")
from app.services.routing_service import run_routing

r = run_routing({
    "postal_code": "B3H 1A1",
    "budget_range": "5k_8k",
    "available_footprint_sqft": "medium_80_150",
    "primary_use": "year_round_food",
    "diy_capacity": "full_diy",
    "timeline": "this_spring",
})

out = {
    "score": r.scores.get("weighted_total"),
    "confidence": r.confidence,
    "decision": r.route_decision,
    "cost": r.system_cost,
    "components_found": [k for k, v in r.components.items() if v is not None],
    "component_gaps": [g["category"] for g in r.component_gaps],
    "species_count": len(r.species_matrix),
    "seasonal_months": len(r.seasonal_calendar),
    "component_details": {cat: {"name": c.get("product_name"), "price": c.get("price_cad")} for cat, c in r.components.items() if c},
}

with open("test_verify.json", "w") as f:
    json.dump(out, f, indent=2)

print("Written to test_verify.json")
