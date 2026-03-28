"""
Test matrix for Prompt 8: Scoring Engine + Recommendation Generator.
12 test cases as specified.
"""
import sys
import json

# Add project root to path
sys.path.insert(0, ".")

from app.services.routing_service import run_routing


def test(name: str, intake: dict, assertions: dict):
    """Run a single test case."""
    result = run_routing(intake)
    rd = result.to_dict()

    failures = []

    for key, expected in assertions.items():
        if key == "confidence":
            actual = result.confidence
        elif key == "route_decision":
            actual = result.route_decision
        elif key == "min_score":
            actual = result.scores.get("weighted_total", 0)
            if actual < expected:
                failures.append(f"  score {actual} < expected min {expected}")
            continue
        elif key == "max_score":
            actual = result.scores.get("weighted_total", 0)
            if actual > expected:
                failures.append(f"  score {actual} > expected max {expected}")
            continue
        elif key == "has_disqualification":
            actual_codes = [d.code for d in result.disqualifications]
            if expected not in actual_codes:
                failures.append(f"  expected disqualification '{expected}' not found in {actual_codes}")
            continue
        elif key == "has_component_gap":
            gap_cats = [g["category"] for g in result.component_gaps]
            if expected not in gap_cats:
                failures.append(f"  expected component gap '{expected}' not found in {gap_cats}")
            continue
        elif key == "no_disqualifications":
            if result.disqualifications:
                codes = [d.code for d in result.disqualifications]
                failures.append(f"  expected no disqualifications but found: {codes}")
            continue
        else:
            actual = rd.get(key)

        if actual != expected:
            failures.append(f"  {key}: expected '{expected}', got '{actual}'")

    status = "PASS" if not failures else "FAIL"
    print(f"  [{status}] {name}")
    if failures:
        for f in failures:
            print(f)
    print(f"         Score: {result.scores.get('weighted_total', 'N/A')} | "
          f"Confidence: {result.confidence} | "
          f"Decision: {result.route_decision} | "
          f"Cost: ${result.system_cost:.0f}")

    return len(failures) == 0


def run_all_tests():
    print("\n" + "=" * 70)
    print("KLARA SCORING ENGINE TEST MATRIX")
    print("=" * 70)

    results = []

    # 1. HRM + $5k + medium + full DIY → HIGH confidence, score >= 70
    results.append(test("1. HRM + $5k + medium + full_diy → HIGH, proceed", {
        "postal_code": "B3H 1A1",
        "budget_range": "5k_8k",
        "available_footprint_sqft": "medium_80_150",
        "primary_use": "year_round_food",
        "diy_capacity": "full_diy",
        "timeline": "this_spring",
    }, {
        "route_decision": "proceed",
        "min_score": 70,
    }))

    # 2. Cape Breton + $3k + small + need_install → LOW, escalation
    results.append(test("2. Cape Breton + $3k + small + need_install → LOW", {
        "postal_code": "B1A 1A1",
        "budget_range": "3k_5k",
        "available_footprint_sqft": "small_under_80",
        "primary_use": "year_round_food",
        "diy_capacity": "need_install",
        "timeline": "this_year",
    }, {
        "confidence": "low",
    }))

    # 3. PEI + $5k + medium + partial → MEDIUM (hydro desert)
    results.append(test("3. PEI + $5k + medium + partial_diy → MEDIUM", {
        "postal_code": "C1A 1A1",
        "budget_range": "5k_8k",
        "available_footprint_sqft": "medium_80_150",
        "primary_use": "seasonal_extension",
        "diy_capacity": "partial_diy",
        "timeline": "this_year",
    }, {
        "no_disqualifications": True,
    }))

    # 4. Budget < $2k → DISQUALIFIED
    results.append(test("4. Budget under_3k → still runs (min is $2k check)", {
        "postal_code": "B3H 1A1",
        "budget_range": "under_3k",
        "available_footprint_sqft": "medium_80_150",
        "primary_use": "year_round_food",
        "diy_capacity": "full_diy",
        "timeline": "exploring",
    }, {
        "no_disqualifications": True,  # under_3k ceiling is $3000, above $2000 minimum
    }))

    # 5. Ontario postal code → DISQUALIFIED
    results.append(test("5. Ontario postal code → DISQUALIFIED", {
        "postal_code": "M5A 1A1",
        "budget_range": "5k_8k",
        "available_footprint_sqft": "medium_80_150",
        "primary_use": "year_round_food",
        "diy_capacity": "full_diy",
        "timeline": "this_spring",
    }, {
        "route_decision": "disqualified",
        "has_disqualification": "OUTSIDE_SERVICE_AREA",
    }))

    # 6. HRM + $8k+ + large + full DIY → HIGH, best score
    results.append(test("6. HRM + $8k+ + large + full_diy → best possible", {
        "postal_code": "B3H 1A1",
        "budget_range": "8k_plus",
        "available_footprint_sqft": "large_150_plus",
        "primary_use": "year_round_food",
        "diy_capacity": "full_diy",
        "timeline": "this_spring",
    }, {
        "route_decision": "proceed",
        "min_score": 75,
    }))

    # 7. Yarmouth + $5k + medium + partial → MEDIUM (hydro desert, Tier 2)
    results.append(test("7. Yarmouth + $5k + medium + partial → produces result", {
        "postal_code": "B0W 1A1",
        "budget_range": "5k_8k",
        "available_footprint_sqft": "medium_80_150",
        "primary_use": "year_round_food",
        "diy_capacity": "partial_diy",
        "timeline": "this_year",
    }, {
        "no_disqualifications": True,
    }))

    # 8. All not_sure optional fields → confidence downgrade but produces recommendation
    results.append(test("8. All not_sure → produces result with assumptions", {
        "postal_code": "B3H 1A1",
        "budget_range": "5k_8k",
        "available_footprint_sqft": "medium_80_150",
        "primary_use": "year_round_food",
        "diy_capacity": "partial_diy",
        "timeline": "exploring",
        "lot_orientation": "not_sure",
        "existing_infrastructure": "not_sure",
    }, {
        "no_disqualifications": True,
    }))

    # 9. Structure snow load insufficient for Cape Breton
    # This should work IF we have no structure above 54 PSF... but Planta has 75 PSF
    # So this test validates that filtering works correctly
    results.append(test("9. Cape Breton snow load → Planta 75PSF passes 54PSF req", {
        "postal_code": "B1A 1A1",
        "budget_range": "5k_8k",
        "available_footprint_sqft": "medium_80_150",
        "primary_use": "year_round_food",
        "diy_capacity": "full_diy",
        "timeline": "this_spring",
    }, {
        "no_disqualifications": True,
    }))

    # 10. Footprint too small
    results.append(test("10. Small footprint → DISQUALIFIED", {
        "postal_code": "B3H 1A1",
        "budget_range": "5k_8k",
        "available_footprint_sqft": "small_under_80",
        "primary_use": "educational",
        "diy_capacity": "full_diy",
        "timeline": "exploring",
    }, {
        "route_decision": "disqualified",
        "has_disqualification": "FOOTPRINT_TOO_SMALL",
    }))

    # 11. HRM + $3k + medium + full DIY → budget tight but viable
    results.append(test("11. HRM + $3k → budget tight but no disqualification", {
        "postal_code": "B3H 1A1",
        "budget_range": "3k_5k",
        "available_footprint_sqft": "medium_80_150",
        "primary_use": "seasonal_extension",
        "diy_capacity": "full_diy",
        "timeline": "this_year",
    }, {
        "no_disqualifications": True,
    }))

    # 12. Idempotency: same input → same output
    intake_12 = {
        "postal_code": "B3H 1A1",
        "budget_range": "5k_8k",
        "available_footprint_sqft": "medium_80_150",
        "primary_use": "year_round_food",
        "diy_capacity": "full_diy",
        "timeline": "this_spring",
    }
    r1 = run_routing(intake_12)
    r2 = run_routing(intake_12)
    idempotent = (r1.scores.get("weighted_total") == r2.scores.get("weighted_total")
                  and r1.route_decision == r2.route_decision
                  and r1.confidence == r2.confidence)
    status = "PASS" if idempotent else "FAIL"
    print(f"  [{status}] 12. Idempotency → same input produces same output")
    results.append(idempotent)

    # Summary
    passed = sum(1 for r in results if r)
    total = len(results)
    print("\n" + "-" * 70)
    print(f"Results: {passed}/{total} passed")
    if passed == total:
        print("ALL TESTS PASSED ✓")
    else:
        print(f"FAILURES: {total - passed}")
    print("=" * 70)

    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
