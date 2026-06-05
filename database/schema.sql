-- FORGE Agent Database Schema
USE forge_agent;
GO

CREATE TABLE assessments (
    id              INT IDENTITY(1,1) PRIMARY KEY,
    created_at      DATETIME2 DEFAULT GETDATE(),
    dataset_name    NVARCHAR(255) NOT NULL,
    data_owner      NVARCHAR(255),
    business_steward NVARCHAR(255),
    source_system   NVARCHAR(255),
    industry_segment NVARCHAR(255),
    file_name       NVARCHAR(255),
    file_type       NVARCHAR(50),

    -- Intake questionnaire responses
    ownership_level         NVARCHAR(50),
    documentation_level     NVARCHAR(50),
    refresh_frequency       NVARCHAR(50),
    refresh_reliability     NVARCHAR(50),
    sensitive_data_types    NVARCHAR(255),
    compliance_controls     NVARCHAR(50),
    continuity_risk         NVARCHAR(50),
    backup_process          NVARCHAR(50),
    primary_use             NVARCHAR(100),
    business_value_driver   NVARCHAR(50),
    competitor_availability NVARCHAR(50),
    historical_depth        NVARCHAR(50),
    enrichment_potential    NVARCHAR(50),

    -- FORGE dimension scores (0-5)
    score_data_quality      DECIMAL(3,1),
    score_reliability       DECIMAL(3,1),
    score_refresh           DECIMAL(3,1),
    score_compliance        DECIMAL(3,1),
    score_governance        DECIMAL(3,1),
    score_accessibility     DECIMAL(3,1),
    score_business_relevance DECIMAL(3,1),
    score_sustainability    DECIMAL(3,1),

    -- Monetization metrics (0-5)
    score_uniqueness        DECIMAL(3,1),
    score_coverage          DECIMAL(3,1),
    score_historical_depth  DECIMAL(3,1),
    score_enrichment        DECIMAL(3,1),

    -- Composite results
    weighted_score          DECIMAL(5,2),
    metal_rating            NVARCHAR(20),
    monetization_potential  NVARCHAR(MAX),
    recommended_actions     NVARCHAR(MAX),
    full_report             NVARCHAR(MAX),

    -- Casper blockchain
    casper_tx_hash          NVARCHAR(255),
    casper_recorded_at      DATETIME2
);

CREATE TABLE assessment_files (
    id              INT IDENTITY(1,1) PRIMARY KEY,
    assessment_id   INT FOREIGN KEY REFERENCES assessments(id),
    file_name       NVARCHAR(255),
    file_type       NVARCHAR(50),
    row_count       INT,
    column_count    INT,
    file_metadata   NVARCHAR(MAX),
    uploaded_at     DATETIME2 DEFAULT GETDATE()
);