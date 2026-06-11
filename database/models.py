from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Assessment(Base):
    __tablename__ = "assessments"

    id                       = Column(Integer, primary_key=True, index=True)
    created_at               = Column(DateTime, default=datetime.utcnow)
    dataset_name             = Column(String(255), nullable=False)
    data_owner               = Column(String(255))
    business_steward         = Column(String(255))
    source_system            = Column(String(255))
    industry_segment         = Column(String(255))
    file_name                = Column(String(255))
    file_type                = Column(String(50))

    # Intake questionnaire
    ownership_level          = Column(String(50))
    documentation_level      = Column(String(50))
    refresh_frequency        = Column(String(50))
    refresh_reliability      = Column(String(50))
    sensitive_data_types     = Column(String(255))
    compliance_controls      = Column(String(50))
    continuity_risk          = Column(String(50))
    backup_process           = Column(String(50))
    primary_use              = Column(String(100))
    business_value_driver    = Column(String(50))
    competitor_availability  = Column(String(50))
    historical_depth         = Column(String(50))
    enrichment_potential     = Column(String(50))

    # Dimension scores
    score_data_quality       = Column(Numeric(3, 1))
    score_reliability        = Column(Numeric(3, 1))
    score_refresh            = Column(Numeric(3, 1))
    score_compliance         = Column(Numeric(3, 1))
    score_governance         = Column(Numeric(3, 1))
    score_accessibility      = Column(Numeric(3, 1))
    score_business_relevance = Column(Numeric(3, 1))
    score_sustainability     = Column(Numeric(3, 1))

    # Monetization metrics
    score_uniqueness         = Column(Numeric(3, 1))
    score_coverage           = Column(Numeric(3, 1))
    score_historical_depth   = Column(Numeric(3, 1))
    score_enrichment         = Column(Numeric(3, 1))

    # Results
    weighted_score           = Column(Numeric(5, 2))
    metal_rating             = Column(String(20))
    monetization_potential   = Column(Text)
    recommended_actions      = Column(Text)
    full_report              = Column(Text)

    # Casper
    casper_tx_hash           = Column(String(255))
    casper_recorded_at       = Column(DateTime)

    files = relationship("AssessmentFile", back_populates="assessment")


class AssessmentFile(Base):
    __tablename__ = "assessment_files"

    id            = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"))
    file_name     = Column(String(255))
    file_type     = Column(String(50))
    row_count     = Column(Integer)
    column_count  = Column(Integer)
    file_metadata = Column(Text)
    uploaded_at   = Column(DateTime, default=datetime.utcnow)

    assessment = relationship("Assessment", back_populates="files")


class MarketplaceListing(Base):
    __tablename__ = "marketplace_listings"

    id              = Column(Integer, primary_key=True, index=True)
    assessment_id   = Column(Integer, ForeignKey("assessments.id"))
    dataset_name    = Column(String(255), nullable=False)
    description     = Column(Text)
    price_per_call  = Column(Numeric(10, 4), nullable=False)
    price_monthly   = Column(Numeric(10, 2))
    price_annual    = Column(Numeric(10, 2))
    currency        = Column(String(10), default="CSPR")
    listed_at       = Column(DateTime, default=datetime.utcnow)
    is_active       = Column(Integer, default=1)
    total_calls     = Column(Integer, default=0)
    total_revenue   = Column(Numeric(12, 4), default=0)
    data_file_path  = Column(String(500))
    tags            = Column(String(255))

    transactions = relationship("MarketplaceTransaction", back_populates="listing")


class MarketplaceTransaction(Base):
    __tablename__ = "marketplace_transactions"

    id                = Column(Integer, primary_key=True, index=True)
    listing_id        = Column(Integer, ForeignKey("marketplace_listings.id"))
    buyer_id          = Column(String(100), nullable=False)
    buyer_name        = Column(String(255))
    transaction_type  = Column(String(50))
    amount            = Column(Numeric(10, 4))
    currency          = Column(String(10), default="CSPR")
    transacted_at     = Column(DateTime, default=datetime.utcnow)
    casper_tx_hash    = Column(String(255))
    api_endpoint      = Column(String(255))
    records_delivered = Column(Integer)
    status            = Column(String(20), default="completed")

    listing = relationship("MarketplaceListing", back_populates="transactions")


class MarketplaceBuyer(Base):
    __tablename__ = "marketplace_buyers"

    id            = Column(Integer, primary_key=True, index=True)
    buyer_id      = Column(String(100), unique=True, nullable=False)
    buyer_name    = Column(String(255))
    organization  = Column(String(255))
    email         = Column(String(255))
    registered_at = Column(DateTime, default=datetime.utcnow)
    cspr_wallet   = Column(String(255))
    total_spent   = Column(Numeric(12, 4), default=0)
    total_calls   = Column(Integer, default=0)
    is_active     = Column(Integer, default=1)


class BuyerApiImport(Base):
    __tablename__ = "buyer_api_imports"

    import_id         = Column(Integer, primary_key=True, index=True)
    api_import_id     = Column(String(50), unique=True, nullable=False)
    listing_id        = Column(Integer, ForeignKey("marketplace_listings.id"))
    buyer_id          = Column(String(100), nullable=False)
    buyer_name        = Column(String(255))
    dataset_name      = Column(String(255))
    imported_at       = Column(DateTime, default=datetime.utcnow)
    casper_tx_hash    = Column(String(255))
    records_delivered = Column(Integer, default=0)
    cost_per_record   = Column(Numeric(10, 6))
    total_cost        = Column(Numeric(10, 4))
    currency          = Column(String(10), default="CSPR")
    status            = Column(String(20), default="completed")

    records = relationship("BuyerApiImportData", back_populates="import_batch")


class BuyerApiImportData(Base):
    __tablename__ = "buyer_api_import_data"

    id              = Column(Integer, primary_key=True, index=True)
    api_import_id   = Column(String(50), nullable=False)
    import_id       = Column(Integer, ForeignKey("buyer_api_imports.import_id"))
    record_sequence = Column(Integer)
    record_data     = Column(Text)
    imported_at     = Column(DateTime, default=datetime.utcnow)

    import_batch = relationship("BuyerApiImport", back_populates="records")
