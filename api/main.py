import os
import sys
import json
import shutil
import uuid
import hashlib
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Request
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
from database.models import BuyerApiImport, BuyerApiImportData
from ai.profiler import profile_file, validate_content
from ai.scorer import run_scoring
from casper.recorder import record_assessment_on_chain

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

# --- Rate Limiting ---
upload_counts = defaultdict(list)
MAX_UPLOADS_PER_HOUR = 5


def check_rate_limit(client_ip: str) -> bool:
    now = datetime.utcnow()
    hour_ago = now.timestamp() - 3600
    upload_counts[client_ip] = [t for t in upload_counts[client_ip] if t > hour_ago]
    if len(upload_counts[client_ip]) >= MAX_UPLOADS_PER_HOUR:
        return False
    upload_counts[client_ip].append(now.timestamp())
    return True


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
    user_id: Optional[str] = None


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
    row_count: Optional[int] = None
    file_size_mb: Optional[float] = None
    seller_user_id: Optional[str] = None
    seller_name: Optional[str] = None


class BuyerRegister(BaseModel):
    buyer_name: str
    organization: Optional[str] = None
    email: Optional[str] = None
    cspr_wallet: Optional[str] = None
    user_id: Optional[str] = None


# --- Core Endpoints ---

@app.get("/")
def root():
    return {"message": "FORGE Agent API is running."}


@app.post("/upload")
async def upload_file(request: Request, file: UploadFile = File(...)):
    client_ip = request.client.host
    if not check_rate_limit(client_ip):
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Maximum {MAX_UPLOADS_PER_HOUR} uploads per hour per IP address."
        )

    ext = Path(file.filename).suffix.lower()
    if ext not in {".csv", ".xlsx", ".xls"}:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

    contents = await file.read()
    file_size_mb = len(contents) / 1024 / 1024
    if file_size_mb > 50:
        raise HTTPException(
            status_code=413,
            detail=f"File size {file_size_mb:.1f}MB exceeds the 50MB maximum."
        )

    tmp_path = UPLOAD_DIR / file.filename
    with open(tmp_path, "wb") as buffer:
        buffer.write(contents)

    try:
        profile = profile_file(str(tmp_path))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Profiling failed: {str(e)}")

    try:
        validation = validate_content(profile)
        if not validation.get("approved", True):
            tmp_path.unlink(missing_ok=True)
            # detail must be a plain string for clean display in the frontend's
            # error message. Structured fields (reason, flags) are still
            # included as a separate, parseable block for any UI that wants
            # to render them individually, but the top-level detail itself
            # is always a string so a naive "Upload failed: " + detail
            # concatenation never produces "[object Object]".
            reason = validation.get("reason") or "This file did not pass our content review."
            raise HTTPException(
                status_code=422,
                detail=(
                    f"This dataset could not be accepted: {reason} "
                    f"FORGE Agent's content policy — agreed to at registration — "
                    f"prohibits sensitive personal identifiers (such as Social Security "
                    f"or account numbers), offensive content, and content not suited to "
                    f"a professional data marketplace. Please remove or anonymize the "
                    f"flagged fields and try again."
                )
            )
    except HTTPException:
        raise
    except Exception:
        pass

    profile["file_size_mb"] = round(file_size_mb, 2)

    return {
        "file_name": file.filename,
        "file_size_mb": round(file_size_mb, 2),
        "profile": profile,
        "content_approved": True
    }


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
        full_report              = json.dumps(result),
        uploaded_by_user_id      = request.user_id
    )

    db.add(assessment)
    db.commit()
    db.refresh(assessment)

    casper_result = record_assessment_on_chain(
        assessment_id=assessment.id,
        dataset_name=assessment.dataset_name,
        weighted_score=float(assessment.weighted_score),
        metal_rating=assessment.metal_rating,
        scores=scores
    )

    if casper_result["success"]:
        # Store the REAL Casper testnet transaction hash from record_certification,
        # not the local-only assessment hash. assessment_hash (local SHA-256) is
        # still available in casper_result for reference/audit but is not what
        # gets persisted as casper_tx_hash going forward.
        assessment.casper_tx_hash = casper_result["casper_tx_hash"]
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
        "casper_tx_hash":         casper_result.get("casper_tx_hash"),
        "casper_explorer_url":    casper_result.get("explorer_url"),
        "casper_success":         casper_result["success"],
        "casper_error":           casper_result.get("friendly_message") if not casper_result["success"] else None,
        "casper_error_category":  casper_result.get("error_category") if not casper_result["success"] else None,
        "offered_for_sale":       assessment.offered_for_sale
    }


class MarketplaceDecision(BaseModel):
    offer_for_sale: bool
    seller_user_id: str
    seller_name: str
    description: Optional[str] = None
    price_per_call: Optional[float] = 0.001
    price_monthly: Optional[float] = None
    price_annual: Optional[float] = None
    currency: Optional[str] = "CSPR"
    data_file_path: Optional[str] = None
    tags: Optional[str] = None
    row_count: Optional[int] = None
    file_size_mb: Optional[float] = None


@app.post("/assessments/{assessment_id}/marketplace-decision")
def set_marketplace_decision(assessment_id: int, decision: MarketplaceDecision, db: Session = Depends(get_db)):
    """
    Records a seller's explicit decision on whether a certified assessment
    is offered for sale in the public marketplace/registry.

    The certification itself (score, Casper hash) always exists and is
    always visible to the seller and admin -- this decision only controls
    whether it becomes a public, sellable marketplace listing.
    """
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    assessment.offered_for_sale = decision.offer_for_sale
    db.commit()

    if not decision.offer_for_sale:
        return {
            "assessment_id": assessment_id,
            "offered_for_sale": False,
            "status": "kept_private"
        }

    # Yes -- create the real marketplace listing, same shape as create_listing()
    existing = db.query(MarketplaceListing).filter(MarketplaceListing.assessment_id == assessment_id).first()
    if existing:
        return {
            "assessment_id": assessment_id,
            "offered_for_sale": True,
            "listing_id": existing.id,
            "status": "already_listed"
        }

    listing = MarketplaceListing(
        assessment_id  = assessment_id,
        dataset_name   = assessment.dataset_name,
        description    = decision.description,
        price_per_call = decision.price_per_call,
        price_monthly  = decision.price_monthly,
        price_annual   = decision.price_annual,
        currency       = decision.currency,
        data_file_path = decision.data_file_path,
        tags           = decision.tags,
        row_count      = decision.row_count,
        file_size_mb   = decision.file_size_mb,
        seller_user_id = decision.seller_user_id,
        seller_name    = decision.seller_name
    )
    db.add(listing)
    db.commit()
    db.refresh(listing)

    return {
        "assessment_id": assessment_id,
        "offered_for_sale": True,
        "listing_id": listing.id,
        "status": "listed"
    }


@app.get("/assessments/{assessment_id}")
def get_assessment(assessment_id: int, db: Session = Depends(get_db)):
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    full_report_data = json.loads(assessment.full_report) if assessment.full_report else {}

    return {
        "assessment_id":          assessment.id,
        "created_at":             assessment.created_at,
        "dataset_name":           assessment.dataset_name,
        "weighted_score":         float(assessment.weighted_score) if assessment.weighted_score else None,
        "metal_rating":           assessment.metal_rating,
        "casper_tx_hash":         assessment.casper_tx_hash,
        "casper_recorded_at":     assessment.casper_recorded_at,
        "monetization_potential": json.loads(assessment.monetization_potential) if assessment.monetization_potential else None,
        "recommended_actions":    json.loads(assessment.recommended_actions) if assessment.recommended_actions else None,
        "score_reasoning":        full_report_data.get("score_reasoning")
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
def get_registry(viewer_user_id: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Public registry visibility rule:
      - Anyone sees assessments where offered_for_sale == True (the seller has
        explicitly agreed to make this certification public by listing it for sale).
      - If viewer_user_id is provided and belongs to an admin, all assessments
        are visible regardless of offered_for_sale.
      - If viewer_user_id is provided and matches the assessment's own seller
        (via a marketplace_listings row, or simply being the one who ran it --
        tracked here by checking existing listings for that seller), their own
        not-yet-decided or private assessments are also visible to them.

    The certification itself (score, Casper hash) is never hidden from the
    seller or admin -- this filter only controls what becomes part of the
    public registry that other buyers and visitors can browse.
    """
    is_viewer_admin = False
    if viewer_user_id:
        from database.models import ForgeApiUser
        viewer = db.query(ForgeApiUser).filter(ForgeApiUser.user_id == viewer_user_id).first()
        if viewer and viewer.is_admin:
            is_viewer_admin = True

    query = db.query(Assessment)

    if not is_viewer_admin:
        if viewer_user_id:
            # Public listings OR assessments this viewer owns themselves.
            # Ownership for a not-yet-listed assessment is inferred from any
            # existing listing under their user_id; for assessments with no
            # listing at all yet (offered_for_sale IS NULL), the original
            # assess-time user_id is used (see /assess's stored uploader).
            query = query.filter(
                (Assessment.offered_for_sale == True) |
                (Assessment.id.in_(
                    db.query(MarketplaceListing.assessment_id)
                      .filter(MarketplaceListing.seller_user_id == viewer_user_id)
                )) |
                (Assessment.uploaded_by_user_id == viewer_user_id)
            )
        else:
            query = query.filter(Assessment.offered_for_sale == True)

    assessments = query.order_by(Assessment.created_at.desc()).all()
    return [
        {
            "assessment_id":      a.id,
            "created_at":         a.created_at,
            "dataset_name":       a.dataset_name,
            "weighted_score":     float(a.weighted_score) if a.weighted_score else None,
            "metal_rating":       a.metal_rating,
            "casper_tx_hash":     a.casper_tx_hash,
            "casper_recorded_at": a.casper_recorded_at,
            "offered_for_sale":   a.offered_for_sale,
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
        tags           = request.tags,
        row_count      = request.row_count,
        file_size_mb   = request.file_size_mb,
        seller_user_id = request.seller_user_id if hasattr(request, 'seller_user_id') else None,
        seller_name    = request.seller_name if hasattr(request, 'seller_name') else None
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
            "price_annual":   float(l.price_annual) if l.price_annual else None,
            "currency":       l.currency,
            "total_calls":    l.total_calls,
            "tags":           l.tags,
            "listed_at":      l.listed_at,
            "assessment_id":  l.assessment_id,
            "row_count":      l.row_count,
            "file_size_mb":   float(l.file_size_mb) if l.file_size_mb else None,
            "seller_user_id": l.seller_user_id,
            "seller_name":    l.seller_name
        }
        for l in listings
    ]


@app.post("/marketplace/buyers/register")
def register_buyer(request: BuyerRegister, db: Session = Depends(get_db)):
    from database.models import ForgeApiUser
    buyer_id = "BUYER-" + str(uuid.uuid4())[:8].upper()
    buyer = MarketplaceBuyer(
        buyer_id     = buyer_id,
        buyer_name   = request.buyer_name,
        organization = request.organization,
        email        = request.email,
        cspr_wallet  = request.cspr_wallet,
        user_id      = request.user_id if hasattr(request, 'user_id') else None
    )
    db.add(buyer)

    # If user_id provided, update their is_buyer flag
    if hasattr(request, 'user_id') and request.user_id:
        user = db.query(ForgeApiUser).filter(ForgeApiUser.user_id == request.user_id).first()
        if user:
            user.is_buyer = 1

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

    tx_hash = hashlib.sha256(
        f"{buyer_id}:{listing_id}:{payment_proof}:{datetime.utcnow().isoformat()}".encode()
    ).hexdigest()

    api_import_id = "IMP-" + str(uuid.uuid4())[:8].upper()

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

    cost_per_record = float(listing.price_per_call) / record_count if record_count > 0 else 0
    import_batch = BuyerApiImport(
        api_import_id     = api_import_id,
        listing_id        = listing_id,
        buyer_id          = buyer_id,
        buyer_name        = buyer.buyer_name,
        dataset_name      = listing.dataset_name,
        casper_tx_hash    = tx_hash,
        records_delivered = record_count,
        cost_per_record   = cost_per_record,
        total_cost        = float(listing.price_per_call),
        currency          = listing.currency,
        status            = "completed"
    )
    db.add(import_batch)
    db.flush()

    for seq, record in enumerate(records):
        import_data = BuyerApiImportData(
            api_import_id   = api_import_id,
            import_id       = import_batch.import_id,
            record_sequence = seq + 1,
            record_data     = json.dumps(record)
        )
        db.add(import_data)

    listing.total_calls   += 1
    listing.total_revenue  = float(listing.total_revenue or 0) + float(listing.price_per_call)
    buyer.total_calls     += 1
    buyer.total_spent      = float(buyer.total_spent or 0) + float(listing.price_per_call)

    db.commit()

    return {
        "status":            "success",
        "api_import_id":     api_import_id,
        "listing_id":        listing_id,
        "dataset_name":      listing.dataset_name,
        "records_delivered": record_count,
        "cost_per_record":   cost_per_record,
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


@app.get("/marketplace/buyer/imports/{buyer_id}")
def get_buyer_imports(buyer_id: str, db: Session = Depends(get_db)):
    imports = db.query(BuyerApiImport)\
        .filter(BuyerApiImport.buyer_id == buyer_id)\
        .order_by(BuyerApiImport.imported_at.desc())\
        .all()
    return [
        {
            "api_import_id":     i.api_import_id,
            "import_id":         i.import_id,
            "dataset_name":      i.dataset_name,
            "imported_at":       i.imported_at,
            "records_delivered": i.records_delivered,
            "cost_per_record":   float(i.cost_per_record) if i.cost_per_record else 0,
            "total_cost":        float(i.total_cost) if i.total_cost else 0,
            "currency":          i.currency,
            "casper_tx_hash":    i.casper_tx_hash,
            "status":            i.status
        }
        for i in imports
    ]


@app.get("/marketplace/buyer/imports/{buyer_id}/{api_import_id}/data")
def get_import_data(buyer_id: str, api_import_id: str, db: Session = Depends(get_db)):
    import_batch = db.query(BuyerApiImport).filter(
        BuyerApiImport.api_import_id == api_import_id,
        BuyerApiImport.buyer_id == buyer_id
    ).first()

    if not import_batch:
        raise HTTPException(status_code=404, detail="Import not found")

    records = db.query(BuyerApiImportData)\
        .filter(BuyerApiImportData.api_import_id == api_import_id)\
        .order_by(BuyerApiImportData.record_sequence)\
        .all()

    return {
        "api_import_id":     api_import_id,
        "dataset_name":      import_batch.dataset_name,
        "imported_at":       import_batch.imported_at,
        "records_delivered": import_batch.records_delivered,
        "total_cost":        float(import_batch.total_cost) if import_batch.total_cost else 0,
        "cost_per_record":   float(import_batch.cost_per_record) if import_batch.cost_per_record else 0,
        "currency":          import_batch.currency,
        "casper_tx_hash":    import_batch.casper_tx_hash,
        "records":           [json.loads(r.record_data) for r in records]
    }


@app.get("/marketplace/seller/revenue")
def get_seller_revenue(db: Session = Depends(get_db)):
    imports = db.query(BuyerApiImport).all()

    buyer_revenue = {}
    for i in imports:
        key = i.buyer_id
        if key not in buyer_revenue:
            buyer_revenue[key] = {
                "buyer_id":      i.buyer_id,
                "buyer_name":    i.buyer_name,
                "total_spent":   0,
                "total_records": 0,
                "import_count":  0,
                "last_import":   None
            }
        buyer_revenue[key]["total_spent"]   += float(i.total_cost or 0)
        buyer_revenue[key]["total_records"] += i.records_delivered or 0
        buyer_revenue[key]["import_count"]  += 1
        buyer_revenue[key]["last_import"]    = i.imported_at

    dataset_revenue = {}
    for i in imports:
        key = i.dataset_name
        if key not in dataset_revenue:
            dataset_revenue[key] = {
                "dataset_name":  i.dataset_name,
                "total_revenue": 0,
                "total_records": 0,
                "import_count":  0
            }
        dataset_revenue[key]["total_revenue"] += float(i.total_cost or 0)
        dataset_revenue[key]["total_records"] += i.records_delivered or 0
        dataset_revenue[key]["import_count"]  += 1

    total_revenue = sum(float(i.total_cost or 0) for i in imports)
    total_records = sum(i.records_delivered or 0 for i in imports)

    return {
        "total_revenue":  total_revenue,
        "total_records":  total_records,
        "total_imports":  len(imports),
        "by_buyer":       list(buyer_revenue.values()),
        "by_dataset":     list(dataset_revenue.values())
    }


# --- CSPR Price Endpoint ---

@app.get("/market/cspr-price")
async def get_cspr_price():
    import httpx
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(
                "https://api.coingecko.com/api/v3/simple/price",
                params={"ids": "casper-network", "vs_currencies": "usd,eur,gbp,cad,aud,jpy"},
                timeout=5.0
            )
            data = r.json()
            prices = data.get("casper-network", {})
            return {
                "cspr_usd": prices.get("usd", 0),
                "cspr_eur": prices.get("eur", 0),
                "cspr_gbp": prices.get("gbp", 0),
                "cspr_cad": prices.get("cad", 0),
                "cspr_aud": prices.get("aud", 0),
                "cspr_jpy": prices.get("jpy", 0),
                "source":   "CoinGecko",
                "cached_at": datetime.utcnow().isoformat()
            }
    except Exception as e:
        return {
            "cspr_usd": 0.23,
            "cspr_eur": 0.21,
            "cspr_gbp": 0.18,
            "cspr_cad": 0.31,
            "cspr_aud": 0.35,
            "cspr_jpy": 34.5,
            "source":   "fallback",
            "cached_at": datetime.utcnow().isoformat()
        }


# --- Auth Request Models ---

class UserRegister(BaseModel):
    full_name: str
    email: str
    phone: Optional[str] = None
    organization: Optional[str] = None
    use_case: Optional[str] = None
    attest_owner: bool = False
    attest_no_pii: bool = False
    attest_appropriate: bool = False


class UserLogin(BaseModel):
    api_key: str


# --- Auth Endpoints ---

@app.post("/auth/register")
def register_user(request: UserRegister, db: Session = Depends(get_db)):
    from database.models import ForgeApiUser

    if not request.attest_owner or not request.attest_no_pii or not request.attest_appropriate:
        raise HTTPException(status_code=400, detail="All three attestations are required.")

    existing = db.query(ForgeApiUser).filter(ForgeApiUser.email == request.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="An account with this email already exists.")

    user_id = "USR-" + str(uuid.uuid4())[:8].upper()
    api_key = "FORGE-" + str(uuid.uuid4()).upper()

    user = ForgeApiUser(
        user_id            = user_id,
        api_key            = api_key,
        full_name          = request.full_name,
        email              = request.email,
        phone              = request.phone,
        organization       = request.organization,
        use_case           = request.use_case,
        attest_owner       = 1 if request.attest_owner else 0,
        attest_no_pii      = 1 if request.attest_no_pii else 0,
        attest_appropriate = 1 if request.attest_appropriate else 0
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "user_id":       user.user_id,
        "api_key":       user.api_key,
        "full_name":     user.full_name,
        "email":         user.email,
        "registered_at": user.registered_at,
        "is_admin":      bool(user.is_admin),
        "is_seller":     bool(user.is_seller),
        "is_buyer":      bool(user.is_buyer),
        "status":        "registered"
    }


@app.post("/auth/login")
def login_user(request: UserLogin, db: Session = Depends(get_db)):
    from database.models import ForgeApiUser

    user = db.query(ForgeApiUser).filter(
        ForgeApiUser.api_key == request.api_key,
        ForgeApiUser.is_active == 1
    ).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key.")

    user.last_login = datetime.utcnow()
    db.commit()

    return {
        "user_id":      user.user_id,
        "full_name":    user.full_name,
        "email":        user.email,
        "organization": user.organization,
        "last_login":   user.last_login,
        "is_admin":     bool(user.is_admin),
        "is_seller":    bool(user.is_seller),
        "is_buyer":     bool(user.is_buyer),
        "status":       "authenticated"
    }


@app.get("/auth/verify")
def verify_key(api_key: str, db: Session = Depends(get_db)):
    from database.models import ForgeApiUser

    user = db.query(ForgeApiUser).filter(
        ForgeApiUser.api_key == api_key,
        ForgeApiUser.is_active == 1
    ).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid or inactive API key.")

    return {
        "valid":        True,
        "user_id":      user.user_id,
        "full_name":    user.full_name,
        "organization": user.organization
    }


# --- Role Management Endpoints ---

@app.post("/auth/become-seller")
def become_seller(user_id: str, db: Session = Depends(get_db)):
    from database.models import ForgeApiUser
    user = db.query(ForgeApiUser).filter(
        ForgeApiUser.user_id == user_id,
        ForgeApiUser.is_active == 1
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    user.is_seller = 1
    db.commit()
    return {"status": "seller_enabled", "user_id": user_id, "is_seller": True}


@app.get("/auth/me")
def get_me(api_key: str, db: Session = Depends(get_db)):
    from database.models import ForgeApiUser
    user = db.query(ForgeApiUser).filter(
        ForgeApiUser.api_key == api_key,
        ForgeApiUser.is_active == 1
    ).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key.")
    return {
        "user_id":      user.user_id,
        "full_name":    user.full_name,
        "email":        user.email,
        "organization": user.organization,
        "is_admin":     bool(user.is_admin),
        "is_seller":    bool(user.is_seller),
        "is_buyer":     bool(user.is_buyer),
        "registered_at": user.registered_at,
        "last_login":   user.last_login
    }


# --- Admin Endpoints ---

ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "ForgeAdmin2026!")


def verify_admin(admin_key: str):
    if admin_key != ADMIN_PASSWORD:
        raise HTTPException(status_code=403, detail="Invalid admin credentials.")


@app.get("/admin/users")
def admin_get_users(admin_key: str, db: Session = Depends(get_db)):
    from database.models import ForgeApiUser
    verify_admin(admin_key)
    users = db.query(ForgeApiUser).order_by(ForgeApiUser.registered_at.desc()).all()
    return [
        {
            "user_id":           u.user_id,
            "full_name":         u.full_name,
            "email":             u.email,
            "phone":             u.phone,
            "organization":      u.organization,
            "use_case":          u.use_case,
            "registered_at":     u.registered_at,
            "last_login":        u.last_login,
            "is_active":         u.is_active,
            "api_key_prefix":    u.api_key[:16] + "..." if u.api_key else None,
            "attest_owner":      u.attest_owner,
            "attest_no_pii":     u.attest_no_pii,
            "attest_appropriate": u.attest_appropriate
        }
        for u in users
    ]


@app.post("/admin/users/{user_id}/deactivate")
def admin_deactivate_user(user_id: str, admin_key: str, db: Session = Depends(get_db)):
    from database.models import ForgeApiUser
    verify_admin(admin_key)
    user = db.query(ForgeApiUser).filter(ForgeApiUser.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    user.is_active = 0
    db.commit()
    return {"status": "deactivated", "user_id": user_id}


@app.post("/admin/users/{user_id}/activate")
def admin_activate_user(user_id: str, admin_key: str, db: Session = Depends(get_db)):
    from database.models import ForgeApiUser
    verify_admin(admin_key)
    user = db.query(ForgeApiUser).filter(ForgeApiUser.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    user.is_active = 1
    db.commit()
    return {"status": "activated", "user_id": user_id}


@app.get("/admin/errors")
def admin_get_errors(admin_key: str, db: Session = Depends(get_db)):
    from database.models import ForgeApiError
    verify_admin(admin_key)
    errors = db.query(ForgeApiError).order_by(ForgeApiError.logged_at.desc()).limit(100).all()
    return [
        {
            "id":             e.id,
            "logged_at":      e.logged_at,
            "user_id":        e.user_id,
            "api_key_prefix": e.api_key_prefix,
            "endpoint":       e.endpoint,
            "error_type":     e.error_type,
            "error_detail":   e.error_detail,
            "client_ip":      e.client_ip,
            "http_status":    e.http_status
        }
        for e in errors
    ]


@app.get("/admin/data/{table_name}")
def admin_get_table(
    table_name: str,
    admin_key: str,
    page: int = 1,
    page_size: int = 50,
    request: Request = None,
    db: Session = Depends(get_db)
):
    from sqlalchemy import text
    verify_admin(admin_key)

    allowed_tables = [
        "assessments", "marketplace_listings", "marketplace_transactions",
        "marketplace_buyers", "buyer_api_imports", "buyer_api_import_data",
        "forge_api_users", "forge_api_errors"
    ]

    if table_name not in allowed_tables:
        raise HTTPException(status_code=400, detail=f"Table not allowed. Allowed: {allowed_tables}")

    # Extract filter params (filter_fieldname=value)
    filters = {}
    if request:
        for key, value in request.query_params.items():
            if key.startswith("filter_") and value:
                field = key[7:]  # strip "filter_"
                filters[field] = value

    # Build WHERE clause safely using LIKE for text fields
    where_clauses = []
    for field, value in filters.items():
        # Only allow alphanumeric/underscore field names to prevent injection
        if field.replace("_","").isalnum():
            where_clauses.append(f"CAST({field} AS NVARCHAR(MAX)) LIKE '%{value}%'")

    where_sql = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""

    offset = (page - 1) * page_size

    count_result = db.execute(text(f"SELECT COUNT(*) FROM {table_name}{where_sql}")).scalar()
    rows = db.execute(text(f"SELECT * FROM {table_name}{where_sql} ORDER BY 1 DESC OFFSET {offset} ROWS FETCH NEXT {page_size} ROWS ONLY")).fetchall()

    if count_result > 0:
        col_result = db.execute(text(f"SELECT * FROM {table_name} ORDER BY 1 DESC OFFSET 0 ROWS FETCH NEXT 1 ROWS ONLY"))
        col_names = list(col_result.keys())
    else:
        col_result = db.execute(text(f"SELECT * FROM {table_name} ORDER BY 1 DESC OFFSET 0 ROWS FETCH NEXT 1 ROWS ONLY"))
        col_names = list(col_result.keys())

    data = [dict(zip(col_names, row)) for row in rows]

    for row in data:
        for k, v in row.items():
            if hasattr(v, 'isoformat'):
                row[k] = v.isoformat()
            elif v is None:
                row[k] = None
            else:
                row[k] = str(v) if not isinstance(v, (int, float, bool, str)) else v

    return {
        "table":      table_name,
        "total_rows": count_result,
        "page":       page,
        "page_size":  page_size,
        "columns":    col_names,
        "filters":    filters,
        "data":       data
    }


@app.get("/admin/summary")
def admin_summary(admin_key: str, db: Session = Depends(get_db)):
    from database.models import ForgeApiUser, ForgeApiError
    verify_admin(admin_key)

    total_users    = db.query(ForgeApiUser).count()
    active_users   = db.query(ForgeApiUser).filter(ForgeApiUser.is_active == 1).count()
    total_errors   = db.query(ForgeApiError).count()
    total_assess   = db.query(Assessment).count()
    total_listings = db.query(MarketplaceListing).count()
    total_buyers   = db.query(MarketplaceBuyer).count()
    total_txs      = db.query(MarketplaceTransaction).count()
    total_imports  = db.query(BuyerApiImport).count()

    revenue = db.query(BuyerApiImport).all()
    total_revenue = sum(float(i.total_cost or 0) for i in revenue)

    return {
        "users":          {"total": total_users, "active": active_users},
        "errors":         total_errors,
        "assessments":    total_assess,
        "listings":       total_listings,
        "buyers":         total_buyers,
        "transactions":   total_txs,
        "imports":        total_imports,
        "total_revenue":  total_revenue
    }
