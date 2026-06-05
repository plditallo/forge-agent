from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Assessment(Base):
    __tablename__ = "assessments"

    id                      = Column(Integer, primary_key=True, index=True)
    created_at              = Column(DateTime, default=datetime.utcnow)
    dataset_name            = Column(String(255), nullable=False)
    data_owner              = Column(String(255))
    business_steward        = Column(String(255))
    source_system           = Column(String(255))
    industry_segment        = Column(String(255))
    file_name               = Column(String(255))
    file_type               = Column(String(50))

    # Intake questionnaire
    ownership_level         = Column(String(50))
    documentation_level     = Column(String(50))
    refresh_frequency       = Column(String(50))
    refresh_reliability     = Column(String(50))
    sensitive_data_types    = Column(String(255))
    compliance_controls     = Column(String(50))
    continuity_risk         = Column(String(50))
    backup_process          = Column(String(50))
    primary_use             = Column(String(100))
    business_value_driver   = Column(String(50))
    competitor_availability = Column(String(50))
    historical_depth        = Column(String(50))
    enrichment_potential    = Column(String(50))

    # Dimension scores
    score_data_quality      = Column(Numeric(3, 1))
    score_reliability       = Column(Numeric(3, 1))
    score_refresh           = Column(Numeric(3, 1))
    score_compliance        = Column(Numeric(3, 1))
    score_governance        = Column(Numeric(3, 1))
    score_accessibility     = Column(Numeric(3, 1))
    score_business_relevance = Column(Numeric(3, 1))
    score_sustainability    = Column(Numeric(3, 1))

    # Monetization metrics
    score_uniqueness        = Column(Numeric(3, 1))
    score_coverage          = Column(Numeric(3, 1))
    score_historical_depth  = Column(Numeric(3, 1))
    score_enrichment        = Column(Numeric(3, 1))

    # Results
    weighted_score          = Column(Numeric(5, 2))
    metal_rating            = Column(String(20))
    monetization_potential  = Column(Text)
    recommended_actions     = Column(Text)
    full_report             = Column(Text)

    # Casper
    casper_tx_hash          = Column(String(255))
    casper_recorded_at      = Column(DateTime)

    files = relationship("AssessmentFile", back_populates="assessment")


class AssessmentFile(Base):
    __tablename__ = "assessment_files"

    id              = Column(Integer, primary_key=True, index=True)
    assessment_id   = Column(Integer, ForeignKey("assessments.id"))
    file_name       = Column(String(255))
    file_type       = Column(String(50))
    row_count       = Column(Integer)
    column_count    = Column(Integer)
    file_metadata   = Column(Text)
    uploaded_at     = Column(DateTime, default=datetime.utcnow)

    assessment = relationship("Assessment", back_populates="files")