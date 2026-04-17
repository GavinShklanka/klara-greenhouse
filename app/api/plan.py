"""Plan API — orchestrates the full pipeline: suitability → design → cost → solar → crops."""

import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession

from app.core.database import get_db
from app.core.dependencies import get_session, get_session_intake, get_session_context
from app.models import GreenhouseSession
from app.services.suitability_service import check_suitability
from app.services.design_service import recommend_design
from app.services.cost_service import estimate_costs
from app.services.solar_service import get_solar_context
from app.services.crop_service import get_crop_plan
from app.services.local_routing_service import get_local_resources

router = APIRouter()


@router.get("/plan/{session_id}")
def get_plan(session_id: str, db: DBSession = Depends(get_db)):
    """Run full pipeline, return complete build plan."""
    gh_session = get_session(session_id, db)
    intake = json.loads(gh_session.intake_data)
    location = intake.get("location", "halifax")

    # Pipeline
    suitability = check_suitability(intake)
    design = recommend_design(intake, suitability)
    costs = estimate_costs(
        design["greenhouse"]["type_id"],
        design["size"]["tier_id"],
        suitability["climate"],
    )
    solar = get_solar_context(location)
    crops = get_crop_plan(design["greenhouse"]["type_id"], intake.get("goal", "grow_food"), location)
    local = get_local_resources(location)

    plan = {
        "suitability": {
            "suitable": suitability["suitable"],
            "warnings": suitability["warnings"],
        },
        "design": design,
        "impact": design.get("impact", {}),
        "costs": costs,
        "solar": solar,
        "crops": crops,
        "local_resources": local,
    }

    # Persist
    gh_session.plan_data = json.dumps(plan)
    gh_session.status = "plan"
    db.commit()

    return {"success": True, "plan": plan}


@router.get("/solar-context/{session_id}")
def solar_context(session_id: str, db: DBSession = Depends(get_db)):
    """Solar viability for a session's location."""
    _session, intake = get_session_intake(session_id, db)
    return get_solar_context(intake.get("location", "halifax"))


@router.get("/greenhouse-model/{session_id}")
def greenhouse_model(session_id: str, db: DBSession = Depends(get_db)):
    """Greenhouse type + size recommendation for a session."""
    _session, intake, suitability, design = get_session_context(session_id, db)
    return design


@router.get("/crop-plan/{session_id}")
def crop_plan(session_id: str, db: DBSession = Depends(get_db)):
    """Crop recommendations for a session."""
    _session, intake, suitability, design = get_session_context(session_id, db)
    return get_crop_plan(
        design["greenhouse"]["type_id"],
        intake.get("goal", "grow_food"),
        intake.get("location", "halifax"),
    )


@router.get("/cost-estimate/{session_id}")
def cost_estimate(session_id: str, db: DBSession = Depends(get_db)):
    """Cost estimate for a session."""
    _session, intake, suitability, design = get_session_context(session_id, db)
    return estimate_costs(
        design["greenhouse"]["type_id"],
        design["size"]["tier_id"],
        suitability["climate"],
    )


@router.get("/local-routing/{session_id}")
def local_routing(session_id: str, db: DBSession = Depends(get_db)):
    """Local resources for a session's location."""
    _session, intake = get_session_intake(session_id, db)
    return get_local_resources(intake.get("location", "halifax"))
