import os
import sys
import json
import shutil
import uuid
import hashlib
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

sys.path.append(str(Path(__file__).parent.parent))

from database.connection import get_db, engine
from database.models import Base, Assessment, AssessmentFile
from database.models import MarketplaceListing, MarketplaceTransaction, MarketplaceBuyer
from ai.profiler import profile_file
from ai.scorer import run_scoring
from casper.recorder import record_assessment_on_chain

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


class ListingCreate(BaseModel):
    assessment_id: int
    dataset_name: str
    description: Optional[str] = None
    price_per_call: float
    price_monthly: Optional[float] = None
    price_annual: Optional[float] = None
    currency: str = "CSPR"
    data_file_path: Optional[str] = None
    tags: Optional[str] = None


class BuyerRegister(BaseModel):
    buyer_name: str
    organization: Optional[str] = None
    email: Optional[str] = None
    cspr_wallet: Optional[str] = None


# --- Core Endpoints ---

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
        dataset_name             = intake.dataset_name,
        data_owner               = intake.data_owner,
        business_steward         = intake.business_steward,
        source_system            = intake.source_system,
        industry_segment         = intake.industry_segment,
        file_name                = request.file_profile.get("file_name"),
        file_type                = request.file_profile.get("file_type"),
        ownership_level          = intake.ownership_level,
        documentation_level      = intake.documentation_level,
        refresh_frequency        = intake.refresh_frequency,
        refresh_reliability      = intake.refresh_reliability,
        sensitive_data_types     = intake.sensitive_data_types,
        compliance_controls      = intake.compliance_controls,
        continuity_risk          = intake.continuity_risk,
        backup_process           = intake.backup_process,
        primary_use              = intake.primary_use,
        business_value_driver    = intake.business_value_driver,
        competitor_availability  = intake.competitor_availability,
        historical_depth         = intake.historical_depth,
        enrichment_potential     = intake.enrichment_potential,
        score_data_quality       = scores["data_quality"],
        score_reliability        = scores["reliability"],
        score_refresh            = scores["refresh"],
        score_compliance         = scores["compliance"],
        score_governance         = scores["governance"],
        score_accessibility      = scores["accessibility"],
        score_business_relevance = scores["business_relevance"],
        score_sustainability     = scores["sustainability"],
        score_uniqueness         = scores["uniqueness"],
        score_coverage           = scores["coverage"],
        score_historical_depth   = scores["historical_depth"],
        score_enrichment         = scores["enrichment"],
        weighted_score           = result["weighted_score"],
        metal_rating             = result["metal_rating"],
        monetization_potential   = json.dumps(result["monetization_potential"]),
        recommended_actions      = json.dumps(result["recommended_actions"]),
        full_report              = json.dumps(result)
    )

    db.add(assessment)
    db.commit()
    db.refresh(assessment)

    # Record assessment hash on Casper testnet
    casper_result = record_assessment_on_chain(
        assessment_id=assessment.id,
        dataset_name=assessment.dataset_name,
        weighted_score=float(assessment.weighted_score),
        metal_rating=assessment.metal_rating,
        scores=scores
    )

    if casper_result["success"]:
        assessment.casper_tx_hash = casper_result["assessment_hash"]
        assessment.casper_recorded_at = datetime.utcnow()
        db.commit()

    return {
        "assessment_id":          assessment.id,
        "dataset_name":           assessment.dataset_name,
        "weighted_score":         float(assessment.weighted_score),
        "metal_rating":           assessment.metal_rating,
        "scores":                 scores,
        "score_reasoning":        result["score_reasoning"],
        "recommended_actions":    result["recommended_actions"],
        "monetization_potential": result["monetization_potential"],
        "casper_hash":            casper_result.get("assessment_hash"),
        "casper_chain":           casper_result.get("chain")
    }


@app.get("/assessments/{assessment_id}")
def get_assessment(assessment_id: int, db: Session = Depends(get_db)):
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    return {
        "assessment_id":          assessment.id,
        "created_at":             assessment.created_at,
        "dataset_name":           assessment.dataset_name,
        "weighted_score":         float(assessment.weighted_score) if assessment.weighted_score else None,
        "metal_rating":           assessment.metal_rating,
        "casper_tx_hash":         assessment.casper_tx_hash,
        "casper_recorded_at":     assessment.casper_recorded_at,
        "monetization_potential": json.loads(assessment.monetization_potential) if assessment.monetization_potential else None,
        "recommended_actions":    json.loads(assessment.recommended_actions) if assessment.recommended_actions else None
    }


@app.get("/assessments")
def list_assessments(db: Session = Depends(get_db)):
    assessments = db.query(Assessment).order_by(Assessment.created_at.desc()).limit(20).all()
    return [
        {
            "assessment_id":  a.id,
            "created_at":     a.created_at,
            "dataset_name":   a.dataset_name,
            "weighted_score": float(a.weighted_score) if a.weighted_score else None,
            "metal_rating":   a.metal_rating,
            "casper_tx_hash": a.casper_tx_hash
        }
        for a in assessments
    ]


@app.get("/registry")
def get_registry(db: Session = Depends(get_db)):
    assessments = db.query(Assessment).order_by(Assessment.created_at.desc()).all()
    return [
        {
            "assessment_id":    a.id,
            "created_at":       a.created_at,
            "dataset_name":     a.dataset_name,
            "weighted_score":   float(a.weighted_score) if a.weighted_score else None,
            "metal_rating":     a.metal_rating,
            "casper_tx_hash":   a.casper_tx_hash,
            "casper_recorded_at": a.casper_recorded_at,
            "scores": {
                "data_quality":       float(a.score_data_quality) if a.score_data_quality else None,
                "reliability":        float(a.score_reliability) if a.score_reliability else None,
                "refresh":            float(a.score_refresh) if a.score_refresh else None,
                "compliance":         float(a.score_compliance) if a.score_compliance else None,
                "governance":         float(a.score_governance) if a.score_governance else None,
                "accessibility":      float(a.score_accessibility) if a.score_accessibility else None,
                "business_relevance": float(a.score_business_relevance) if a.score_business_relevance else None,
                "sustainability":     float(a.score_sustainability) if a.score_sustainability else None,
            },
            "industry_segment": a.industry_segment,
            "source_system":    a.source_system,
            "data_owner":       a.data_owner,
        }
        for a in assessments
    ]


@app.get("/registry/{dataset_name}")
def get_dataset_history(dataset_name: str, db: Session = Depends(get_db)):
    assessments = db.query(Assessment)\
        .filter(Assessment.dataset_name.ilike(f"%{dataset_name}%"))\
        .order_by(Assessment.created_at.asc())\
        .all()

    if not assessments:
        raise HTTPException(status_code=404, detail="No assessments found for this dataset")

    return {
        "dataset_name":     dataset_name,
        "assessment_count": len(assessments),
        "current_rating":   assessments[-1].metal_rating,
        "current_score":    float(assessments[-1].weighted_score) if assessments[-1].weighted_score else None,
        "first_assessed":   assessments[0].created_at,
        "last_assessed":    assessments[-1].created_at,
        "history": [
            {
                "assessment_id":  a.id,
                "created_at":     a.created_at,
                "weighted_score": float(a.weighted_score) if a.weighted_score else None,
                "metal_rating":   a.metal_rating,
                "casper_tx_hash": a.casper_tx_hash,
            }
            for a in assessments
        ]
    }


# --- Marketplace Endpoints ---

@app.post("/marketplace/listings")
def create_listing(request: ListingCreate, db: Session = Depends(get_db)):
    listing = MarketplaceListing(
        assessment_id  = request.assessment_id,
        dataset_name   = request.dataset_name,
        description    = request.description,
        price_per_call = request.price_per_call,
        price_monthly  = request.price_monthly,
        price_annual   = request.price_annual,
        currency       = request.currency,
        data_file_path = request.data_file_path,
        tags           = request.tags
    )
    db.add(listing)
    db.commit()
    db.refresh(listing)
    return {"listing_id": listing.id, "dataset_name": listing.dataset_name, "status": "listed"}


@app.get("/marketplace/listings")
def get_listings(db: Session = Depends(get_db)):
    listings = db.query(MarketplaceListing)\
        .filter(MarketplaceListing.is_active == 1)\
        .order_by(MarketplaceListing.listed_at.desc())\
        .all()
    return [
        {
            "listing_id":     l.id,
            "dataset_name":   l.dataset_name,
            "description":    l.description,
            "price_per_call": float(l.price_per_call),
            "price_monthly":  float(l.price_monthly) if l.price_monthly else None,
            "currency":       l.currency,
            "total_calls":    l.total_calls,
            "tags":           l.tags,
            "listed_at":      l.listed_at,
            "assessment_id":  l.assessment_id
        }
        for l in listings
    ]


@app.post("/marketplace/buyers/register")
def register_buyer(request: BuyerRegister, db: Session = Depends(get_db)):
    buyer_id = "BUYER-" + str(uuid.uuid4())[:8].upper()
    buyer = MarketplaceBuyer(
        buyer_id     = buyer_id,
        buyer_name   = request.buyer_name,
        organization = request.organization,
        email        = request.email,
        cspr_wallet  = request.cspr_wallet
    )
    db.add(buyer)
    db.commit()
    db.refresh(buyer)
    return {
        "buyer_id":      buyer.buyer_id,
        "buyer_name":    buyer.buyer_name,
        "organization":  buyer.organization,
        "registered_at": buyer.registered_at,
        "status":        "registered"
    }


@app.get("/marketplace/data/{listing_id}")
async def access_data(
    listing_id: int,
    buyer_id: str,
    payment_proof: Optional[str] = None,
    db: Session = Depends(get_db)
):
    import pandas as pd

    listing = db.query(MarketplaceListing).filter(
        MarketplaceListing.id == listing_id,
        MarketplaceListing.is_active == 1
    ).first()

    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    buyer = db.query(MarketplaceBuyer).filter(
        MarketplaceBuyer.buyer_id == buyer_id
    ).first()

    if not buyer:
        raise HTTPException(status_code=403, detail="Buyer not registered")

    # x402 payment check
    if not payment_proof:
        return JSONResponse(
            status_code=402,
            content={
                "error": "Payment required",
                "x402": {
                    "price_per_call": float(listing.price_per_call),
                    "currency":       listing.currency,
                    "network":        "casper:casper-test",
                    "payee":          "forge-agent-marketplace",
                    "dataset":        listing.dataset_name,
                    "instructions":   "Include X-Payment header with signed CSPR authorization"
                }
            },
            headers={
                "X-Payment-Price":    str(listing.price_per_call),
                "X-Payment-Network":  "casper:casper-test",
                "X-Payment-Currency": listing.currency
            }
        )

    # Payment proof provided — record transaction
    tx_hash = hashlib.sha256(
        f"{buyer_id}:{listing_id}:{payment_proof}:{datetime.utcnow().isoformat()}".encode()
    ).hexdigest()

    # Load the data
    try:
        if listing.data_file_path and os.path.exists(listing.data_file_path):
            df = pd.read_csv(listing.data_file_path)
            records = df.head(100).to_dict(orient="records")
            record_count = len(records)
        else:
            records = []
            record_count = 0
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data load failed: {str(e)}")

    # Record transaction
    tx = MarketplaceTransaction(
        listing_id        = listing_id,
        buyer_id          = buyer_id,
        buyer_name        = buyer.buyer_name,
        transaction_type  = "api_call",
        amount            = listing.price_per_call,
        currency          = listing.currency,
        casper_tx_hash    = tx_hash,
        api_endpoint      = f"/marketplace/data/{listing_id}",
        records_delivered = record_count,
        status            = "completed"
    )
    db.add(tx)

    # Update counters
    listing.total_calls   += 1
    listing.total_revenue  = float(listing.total_revenue or 0) + float(listing.price_per_call)
    buyer.total_calls     += 1
    buyer.total_spent      = float(buyer.total_spent or 0) + float(listing.price_per_call)

    db.commit()

    return {
        "status":            "success",
        "listing_id":        listing_id,
        "dataset_name":      listing.dataset_name,
        "records_delivered": record_count,
        "amount_charged":    float(listing.price_per_call),
        "currency":          listing.currency,
        "casper_tx_hash":    tx_hash,
        "data":              records
    }


@app.get("/marketplace/transactions")
def get_transactions(db: Session = Depends(get_db)):
    txs = db.query(MarketplaceTransaction)\
        .order_by(MarketplaceTransaction.transacted_at.desc())\
        .limit(50).all()
    return [
        {
            "id":                t.id,
            "listing_id":        t.listing_id,
            "buyer_id":          t.buyer_id,
            "buyer_name":        t.buyer_name,
            "amount":            float(t.amount) if t.amount else None,
            "currency":          t.currency,
            "transacted_at":     t.transacted_at,
            "casper_tx_hash":    t.casper_tx_hash,
            "records_delivered": t.records_delivered,
            "status":            t.status
        }
        for t in txs
    ]