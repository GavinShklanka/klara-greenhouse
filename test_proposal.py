import json
import uuid
import os
import sys

# Add app to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models import GreenhouseSession, Proposal
from app.services.proposal_service import generate_proposal

def test_proposal_generation():
    db = SessionLocal()
    
    # helper
    def create_session(intake_opts, ext_opts=None, omit_ext=False):
        s_id = str(uuid.uuid4())
        intake_data = json.dumps(intake_opts)
        
        gh = GreenhouseSession(
            id=s_id,
            intake_data=intake_data,
        )
        if not omit_ext:
            gh.extended_intake_data = json.dumps(ext_opts or {})
        
        db.add(gh)
        db.commit()
        return s_id

    print("Running Tests...\n")
    
    # 1. Maritime Standard + tomatoes
    print("Test 1: Maritime Standard + tomatoes -> supported")
    s1 = create_session(
        {"budget": "5k_10k", "wind_exposure": "moderate"},
        {"desired_crops": ["tomatoes"], "slope": "flat", "diy_or_contractor": "full_contractor"}
    )
    p1 = generate_proposal(s1, db)
    # verify keys populated
    assert all(k in p1 for k in ["meta", "intake_summary", "recommendation", "cost_breakdown", "site_prep", "crop_fit", "confidence", "next_step"])
    found_supported = any(c["name"] == "tomatoes" and c["status"] == "supported" for c in p1["crop_fit"]["validated_crops"])
    assert found_supported, "Tomatoes should be supported"
    print("✓ Passed")
    
    # 2. Cold Frame Bridge + tomatoes -> mismatch
    print("Test 2: CFB + tomatoes -> mismatch")
    s2 = create_session(
        {"budget": "under_5k", "wind_exposure": "coastal_exposed"},
        {"desired_crops": ["tomatoes"], "slope": "flat"}
    )
    p2 = generate_proposal(s2, db)
    assert any("tomatoes" in c["crop"] for c in p2["crop_fit"]["mismatches"]), "Tomatoes should mismatch CFB"
    print("✓ Passed")
    
    # 3. Slope + Drainage -> Low confidence + escalation
    print("Test 3: slope=significant, drainage=poor -> site_fit low, escalate")
    s3 = create_session(
        {"budget": "5k_10k"},
        {"slope": "significant", "drainage": "poor"}
    )
    p3 = generate_proposal(s3, db)
    assert p3["confidence"]["site_fit"]["rating"] == "low"
    assert p3["confidence"]["escalation_recommended"] == True
    print("✓ Passed")
    
    # 4. All "not_sure" extended -> degrades gracefully
    print("Test 4: All not_sure -> degrades gracefully")
    s4 = create_session(
        {"budget": "5k_10k"},
        {"slope": "not_sure", "drainage": "not_sure", "nearby_structures": "not_sure", "desired_crops": ["not_sure"], "seasonal_intent": "not_sure", "diy_or_contractor": "not_sure"}
    )
    p4 = generate_proposal(s4, db)
    assert p4["confidence"]["site_fit"]["rating"] == "medium"
    assert "medium" in str(p4["confidence"])
    print("✓ Passed")

    # 5. Missing extended_intake_data -> degrades gracefully
    print("Test 5: Missing extended entirely -> degrades gracefully")
    s5 = create_session(
        {"budget": "5k_10k"},
        None,
        omit_ext=True
    )
    p5 = generate_proposal(s5, db)
    assert p5["confidence"]["site_fit"]["rating"] == "medium"
    assert len(p5["crop_fit"]["validated_crops"]) == 0
    print("✓ Passed")

    # 6. Next step DIY Check
    print("Test 6: DIY Next steps")
    s6 = create_session({"budget": "5k_10k"}, {"diy_or_contractor": "full_diy"})
    p6 = generate_proposal(s6, db)
    assert "Source your materials" in p6["next_step"]["recommendation"]
    print("✓ Passed")
    
    # 7. Next step Contractor Check
    print("Test 7: Contractor Next steps")
    assert "Request a builder quote" in p1["next_step"]["recommendation"]
    print("✓ Passed")
    
    # 8. Idempotency Check
    print("Test 8: Double invoke -> updates don't duplicate")
    c_before = db.query(Proposal).filter_by(session_id=s1).count()
    generate_proposal(s1, db)
    c_after = db.query(Proposal).filter_by(session_id=s1).count()
    assert c_before == 1 and c_after == 1, "Should remain 1"
    print("✓ Passed")

    print("\nAll 9 requirements verified.")


if __name__ == "__main__":
    test_proposal_generation()
