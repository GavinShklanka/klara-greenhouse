"""Quick verification of the archetype selection logic."""

from app.services.design_service import recommend_design
from app.services.suitability_service import check_suitability

tests = [
    # (description, intake_overrides, expected_archetype_id)
    ("under_5k + sheltered backyard → starter_kit",
     {"budget": "under_5k", "property_type": "backyard", "goal": "grow_food",
      "greenhouse_type": "not_sure", "location": "halifax", "wind_exposure": "sheltered"},
     "starter_kit"),

    ("under_5k + coastal_exposed → cold_frame_bridge",
     {"budget": "under_5k", "property_type": "backyard", "goal": "grow_food",
      "greenhouse_type": "not_sure", "location": "cape_breton", "wind_exposure": "coastal_exposed"},
     "cold_frame_bridge"),

    ("5k_10k + backyard + polycarbonate → maritime_standard",
     {"budget": "5k_10k", "property_type": "backyard", "goal": "grow_food",
      "greenhouse_type": "polycarbonate", "location": "halifax", "wind_exposure": "moderate"},
     "maritime_standard"),

    ("over_10k + rural + experienced → serious_grower",
     {"budget": "over_10k", "property_type": "rural", "goal": "grow_food",
      "greenhouse_type": "not_sure", "location": "halifax", "wind_exposure": "moderate",
      "experience_level": "experienced"},
     "serious_grower"),

    ("over_10k + passive_solar + south wall yes → passive_solar_leanto",
     {"budget": "over_10k", "property_type": "backyard", "goal": "sustainability",
      "greenhouse_type": "passive_solar", "location": "halifax", "has_south_wall": "yes"},
     "passive_solar_leanto"),

    ("over_10k + passive_solar + south wall NO → maritime_standard (downgraded)",
     {"budget": "over_10k", "property_type": "backyard", "goal": "sustainability",
      "greenhouse_type": "passive_solar", "location": "halifax", "has_south_wall": "no"},
     "maritime_standard"),

    ("over_10k + rural + first_time → maritime_standard (not serious_grower)",
     {"budget": "over_10k", "property_type": "rural", "goal": "grow_food",
      "greenhouse_type": "not_sure", "location": "halifax", "experience_level": "first_time"},
     "maritime_standard"),

    ("coastal_exposed + starter budget → maritime_standard (upgraded from starter_kit)",
     {"budget": "5k_10k", "property_type": "backyard", "goal": "grow_food",
      "greenhouse_type": "not_sure", "location": "halifax", "wind_exposure": "coastal_exposed"},
     "maritime_standard"),
]

passed = 0
failed = 0

for desc, intake, expected in tests:
    suit = check_suitability(intake)
    result = recommend_design(intake, suit)
    actual = result["id"]
    status = "PASS" if actual == expected else "FAIL"
    if status == "PASS":
        passed += 1
    else:
        failed += 1
    print(f"  [{status}] {desc}")
    if actual != expected:
        print(f"         Expected: {expected}, Got: {actual}")

print(f"\n{passed}/{passed+failed} tests passed.")

# Also verify full response shape
print("\n--- Full Maritime Standard response keys ---")
sample = recommend_design(
    {"budget": "5k_10k", "property_type": "backyard", "goal": "grow_food",
     "greenhouse_type": "polycarbonate", "location": "halifax"},
    check_suitability({"budget": "5k_10k", "property_type": "backyard",
                        "goal": "grow_food", "location": "halifax"})
)
for key in sorted(sample.keys()):
    val = sample[key]
    if isinstance(val, str) and len(val) > 60:
        val = val[:60] + "..."
    print(f"  {key}: {val}")
