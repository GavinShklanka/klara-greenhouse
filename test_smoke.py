"""
Smoke test script — verifies the full Klara Greenhouse user journey.
Run: python test_smoke.py [base_url]
Default: http://127.0.0.1:8000
"""
import json
import sys
import requests

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
PASS = 0
FAIL = 0


def test(name: str, condition: bool, detail: str = ""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name} — {detail}")


def section(title: str):
    print(f"\n{'='*50}")
    print(f"  {title}")
    print(f"{'='*50}")


# ═══════════════════════════════════════════════
section("1. INTAKE FORM")
# ═══════════════════════════════════════════════

r = requests.get(f"{BASE}/greenhouse/intake")
test("Intake form renders (200)", r.status_code == 200)
test("Contains postal code field", 'name="postal_code"' in r.text)
test("Contains submit button", "Get My Free Assessment" in r.text)


# ═══════════════════════════════════════════════
section("2. SUBMIT INTAKE — Halifax B3H 1A1, $5-8k, Full DIY")
# ═══════════════════════════════════════════════

s = requests.Session()
r = s.post(f"{BASE}/greenhouse/intake", data={
    "postal_code": "B3H 1A1",
    "budget_range": "5k_8k",
    "available_footprint_sqft": "medium_80_150",
    "primary_use": "year_round_food",
    "diy_capacity": "full_diy",
    "timeline": "this_spring",
}, allow_redirects=True)
test("Redirect to preview (200)", r.status_code == 200)
test("Preview page rendered", "Feasibility Assessment" in r.text)

# Extract session ID from URL
session_id = r.url.split("/")[-1]
test("Session ID extracted", len(session_id) == 36, f"Got: {session_id[:20]}...")

# ═══════════════════════════════════════════════
section("3. PREVIEW")
# ═══════════════════════════════════════════════

r = s.get(f"{BASE}/greenhouse/preview/{session_id}")
test("Preview renders (200)", r.status_code == 200)
test("Shows 'suitable' feasibility", "suitable" in r.text.lower() or "SUITABLE" in r.text)
test("Shows budget fit", "budget" in r.text.lower())
test("Shows $49 CTA", "$49" in r.text)
test("Shows system recommendation", "Greenhouse" in r.text)

# ═══════════════════════════════════════════════
section("4. CHECKOUT (dev fallback)")
# ═══════════════════════════════════════════════

r = s.post(f"{BASE}/greenhouse/checkout/{session_id}", allow_redirects=True)
test("Checkout redirects (200)", r.status_code == 200)
test("Reaches extend intake", "lot_orientation" in r.text.lower() or "Lot Orientation" in r.text)

# ═══════════════════════════════════════════════
section("5. EXTENDED INTAKE")
# ═══════════════════════════════════════════════

r = s.post(f"{BASE}/greenhouse/extend/{session_id}", data={
    "lot_orientation": "south_facing",
    "existing_infrastructure": "has_both",
}, allow_redirects=True)
test("Extended intake redirects to proposal (200)", r.status_code == 200)
test("Proposal page rendered", "Your Greenhouse Proposal" in r.text or "Property Summary" in r.text)

# ═══════════════════════════════════════════════
section("6. FULL PROPOSAL")
# ═══════════════════════════════════════════════

r = s.get(f"{BASE}/greenhouse/proposal/{session_id}")
test("Proposal renders (200)", r.status_code == 200)
test("Section 1: Property Summary", "Property Summary" in r.text)
test("Section 2: Recommended System", "Recommended System" in r.text)
test("Section 3: Biological Blueprint", "Biological Blueprint" in r.text)
test("Section 4: Cost Breakdown", "Cost Breakdown" in r.text)
test("Section 8: Confidence", "Confidence" in r.text)
test("Contains vendor URLs", "https://" in r.text)
test("Contains verification date", "Verified" in r.text or "2026" in r.text)

# ═══════════════════════════════════════════════
section("7. ADMIN DASHBOARD")
# ═══════════════════════════════════════════════

# Login first
r = s.post(f"{BASE}/admin/login", data={"password": "klara-admin-2026"}, allow_redirects=True)
test("Admin login succeeds (200)", r.status_code == 200)
test("Dashboard renders", "Proposals Dashboard" in r.text)
test("Shows our session", session_id[:8] in r.text)

# ═══════════════════════════════════════════════
section("8. AUDIT TRAIL")
# ═══════════════════════════════════════════════

r = s.get(f"{BASE}/admin/proposal/{session_id}/audit")
test("Audit page renders (200)", r.status_code == 200)
test("Shows session ID", session_id[:8] in r.text)

# ═══════════════════════════════════════════════
section("9. PAYMENT GATE")
# ═══════════════════════════════════════════════

# Create unpaid session
r2 = s.post(f"{BASE}/greenhouse/intake", data={
    "postal_code": "B3A 1A1",
    "budget_range": "3k_5k",
    "available_footprint_sqft": "small_under_80",
    "primary_use": "seasonal_extension",
    "diy_capacity": "partial_diy",
    "timeline": "this_year",
}, allow_redirects=True)
unpaid_id = r2.url.split("/")[-1]

r3 = requests.get(f"{BASE}/greenhouse/proposal/{unpaid_id}", allow_redirects=False)
test("Unpaid session redirected from proposal", r3.status_code in (302, 303, 307))

# ═══════════════════════════════════════════════
section("10. ANALYTICS & CHECKPOINT")
# ═══════════════════════════════════════════════

r = s.get(f"{BASE}/admin/analytics")
test("Analytics page renders (200)", r.status_code == 200)
test("Shows funnel data", "Funnel" in r.text or "funnel" in r.text.lower())

r = s.get(f"{BASE}/admin/checkpoint")
test("Checkpoint page renders (200)", r.status_code == 200)
test("Shows signal indicators", "CONTINUE" in r.text or "continue" in r.text.lower())

# ═══════════════════════════════════════════════
section("11. HEALTH CHECK")
# ═══════════════════════════════════════════════

r = requests.get(f"{BASE}/greenhouse/health")
test("Health check (200)", r.status_code == 200)
health = r.json()
test("Status healthy", health.get("status") == "healthy")

# ═══════════════════════════════════════════════
section("12. FRICTION EVENTS")
# ═══════════════════════════════════════════════

r = requests.post(f"{BASE}/greenhouse/events", json={
    "session_id": session_id,
    "event_type": "proposal_download",
    "page": "/greenhouse/proposal",
    "time_on_page_seconds": 42.5,
})
test("Event recording (200)", r.status_code == 200)

# ═══════════════════════════════════════════════
section("13. BETA CODE FLOW")
# ═══════════════════════════════════════════════

r = s.post(f"{BASE}/admin/beta/generate", data={"count": "2"})
test("Beta code generation (200)", r.status_code == 200)
codes = r.json().get("codes", [])
test("Got 2 codes", len(codes) == 2, f"Got {len(codes)}")

if codes:
    code = codes[0]
    r = requests.get(f"{BASE}/greenhouse/beta/{code}")
    test("Beta entry page renders (200)", r.status_code == 200)
    test("Shows beta code applied", code in r.text)

    # Submit beta intake
    r = requests.post(f"{BASE}/greenhouse/beta/{code}/intake", data={
        "postal_code": "B3H 1A1",
        "budget_range": "5k_8k",
        "available_footprint_sqft": "medium_80_150",
        "primary_use": "year_round_food",
        "diy_capacity": "full_diy",
        "timeline": "this_spring",
    }, allow_redirects=True)
    test("Beta intake succeeds (200)", r.status_code == 200)
    test("Reaches extend intake (free)", "lot_orientation" in r.text.lower() or "Lot Orientation" in r.text)

    # Try reusing same code
    r = requests.get(f"{BASE}/greenhouse/beta/{code}")
    test("Reused code rejected (410)", r.status_code == 410)

# ═══════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════

print(f"\n{'='*50}")
print(f"  RESULTS: {PASS} passed / {FAIL} failed / {PASS + FAIL} total")
print(f"{'='*50}")

if FAIL > 0:
    print("\n⚠️  Some tests failed — review above for details.")
    sys.exit(1)
else:
    print("\n✅ All smoke tests passed!")
    sys.exit(0)
