import os
import sys
import json
import shutil
import tempfile
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

sys.path.append(str(Path(__file__).parent.parent))

from database.connection import get_db, engine
from database.models import Base, Assessment, AssessmentFile
from ai.profiler import profile_file
from ai.scorer import run_scoring

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FORGE Agent API",
    description="AI-Powered Data Product Discovery and Monetization Platform",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# --- Request Models ---

class IntakeAnswers(BaseModel):
    dataset_name: str
    data_owner: Optional[str] = None
    business_steward: Optional[str] = None
    source_system: Optional[str] = None
    industry_segment: Optional[str] = None
    ownership_level: str
    documentation_level: str
    refresh_frequency: str
    refresh_reliability: str
    sensitive_data_types: str
    compliance_controls: str
    continuity_risk: str
    backup_process: str
    primary_use: str
    business_value_driver: str
    competitor_availability: str
    historical_depth: str
    enrichment_potential: str


class AssessRequest(BaseModel):
    file_profile: dict
    intake_answers: IntakeAnswers


# --- Endpoints ---

@app.get("/")
def root():
    return {"message": "FORGE Agent API is running."}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    ext = Path(file.filename).suffix.lower()
    if ext not in {".csv", ".xlsx", ".xls"}:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

    tmp_path = UPLOAD_DIR / file.filename
    with open(tmp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        profile = profile_file(str(tmp_path))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Profiling failed: {str(e)}")

    return {"file_name": file.filename, "profile": profile}


@app.post("/assess")
async def assess(request: AssessRequest, db: Session = Depends(get_db)):
    intake = request.intake_answers

    try:
        result = run_scoring(request.file_profile, intake.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scoring failed: {str(e)}")

    scores = result["scores"]

    assessment = Assessment(
        dataset_name            = intake.dataset_name,
        data_owner              = intake.data_owner,
        business_steward        = intake.business_steward,
        source_system           = intake.source_system,
        industry_segment        = intake.industry_segment,
        file_name               = request.file_profile.get("file_name"),
        file_type               = request.file_profile.get("file_type"),
        ownership_level         = intake.ownership_level,
        documentation_level     = intake.documentation_level,
        refresh_frequency       = intake.refresh_frequency,
        refresh_reliability     = intake.refresh_reliability,
        sensitive_data_types    = intake.sensitive_data_types,
        compliance_controls     = intake.compliance_controls,
        continuity_risk         = intake.continuity_risk,
        backup_process          = intake.backup_process,
        primary_use             = intake.primary_use,
        business_value_driver   = intake.business_value_driver,
        competitor_availability = intake.competitor_availability,
        historical_depth        = intake.historical_depth,
        enrichment_potential    = intake.enrichment_potential,
        score_data_quality      = scores["data_quality"],
        score_reliability       = scores["reliability"],
        score_refresh           = scores["refresh"],
        score_compliance        = scores["compliance"],
        score_governance        = scores["governance"],
        score_accessibility     = scores["accessibility"],
        score_business_relevance = scores["business_relevance"],
        score_sustainability    = scores["sustainability"],
        score_uniqueness        = scores["uniqueness"],
        score_coverage          = scores["coverage"],
        score_historical_depth  = scores["historical_depth"],
        score_enrichment        = scores["enrichment"],
        weighted_score          = result["weighted_score"],
        metal_rating            = result["metal_rating"],
        monetization_potential  = json.dumps(result["monetization_potential"]),
        recommended_actions     = json.dumps(result["recommended_actions"]),
        full_report             = json.dumps(result)
    )

    db.add(assessment)
    db.commit()
    db.refresh(assessment)

    return {
        "assessment_id": assessment.id,
        "dataset_name": assessment.dataset_name,
        "weighted_score": float(assessment.weighted_score),
        "metal_rating": assessment.metal_rating,
        "scores": scores,
        "score_reasoning": result["score_reasoning"],
        "recommended_actions": result["recommended_actions"],
        "monetization_potential": result["monetization_potential"]
    }


@app.get("/assessments/{assessment_id}")
def get_assessment(assessment_id: int, db: Session = Depends(get_db)):
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    return {
        "assessment_id": assessment.id,
        "created_at": assessment.created_at,
        "dataset_name": assessment.dataset_name,
        "weighted_score": float(assessment.weighted_score) if assessment.weighted_score else None,
        "metal_rating": assessment.metal_rating,
        "monetization_potential": json.loads(assessment.monetization_potential) if assessment.monetization_potential else None,
        "recommended_actions": json.loads(assessment.recommended_actions) if assessment.recommended_actions else None
    }


@app.get("/assessments")
def list_assessments(db: Session = Depends(get_db)):
    assessments = db.query(Assessment).order_by(Assessment.created_at.desc()).limit(20).all()
    return [
        {
            "assessment_id": a.id,
            "created_at": a.created_at,
            "dataset_name": a.dataset_name,
            "weighted_score": float(a.weighted_score) if a.weighted_score else None,
            "metal_rating": a.metal_rating
        }
        for a in assessments
    ]