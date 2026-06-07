# FORGE Agent
### AI-Powered Data Product Discovery, Assessment, and Monetization Platform

**Built by Paula Ditallo**
Founder & Innovator, Bauhaus Technology and Graphic Holdings LLC

---

## The Problem

Most small to mid-size organizations are sitting on data they cannot describe, cannot govern, and cannot sell. They know it exists. They suspect it has value. But without a framework to assess it, classify it, and prepare it for commercial use, it stays buried generating cost instead of revenue.

---

## The FORGE Framework

FORGE is a data readiness methodology. The methodology is a structured, repeatable process for transforming raw organizational data into certified, commercially viable data products.

Think of FORGE as Six Sigma for data monetization. Like Six Sigma, FORGE defines quality levels, certification tiers, and a progression path. Like TOEFL, the intent of FORGE is to provide a recognized, verifiable credential that signals readiness to external parties. An organization does not simply "have good data." Under FORGE, they can prove it.

The framework is built around a mining metaphor that maps directly to data maturity:

| Level | Score | Description |
|-------|-------|-------------|
| Coal | 0–49 | Exists, but little value without extensive work |
| Iron | 50–59 | Useful operationally, but difficult to monetize |
| Bronze | 60–69 | Structured and partially governed |
| Silver | 70–79 | Trusted business asset |
| Gold | 80–89 | Product-ready data |
| Platinum | 90–95 | Strategic enterprise asset |
| Diamond | 96–100 | Unique, defensible, highly monetizable |

The metaphor is not decorative. It defines the journey. A Bronze-rated dataset needs governance and documentation. A Silver dataset needs packaging and exposure. A Gold dataset is ready to monetize. Every level has a roadmap, not just a score.

---

## The FORGE Assay: Eight Dimensions of Readiness

Every dataset entering the FORGE process receives a Data Assay. The assay a structured evaluation across eight weighted dimensions:

| Dimension | Weight | What It Measures |
|-----------|--------|-----------------|
| Data Quality | 20% | Completeness, accuracy, null rates, validation |
| Compliance & Regulatory | 15% | HIPAA, GDPR, PII exposure, audit controls |
| Reliability & Consistency | 15% | Stability, reconciliation success, monitoring |
| Refresh Frequency | 10% | Timeliness, update cadence, SLA adherence |
| Governance & Lineage | 10% | Ownership, stewardship, provenance |
| Accessibility & Usability | 10% | Documentation, metadata, API readiness |
| Business Relevance | 10% | Revenue potential, strategic alignment |
| Sustainability & Risk | 10% | Key-person dependency, backup processes |

Four additional monetization metrics: Uniqueness, Coverage, Historical Depth, and Enrichment Potential assess market value independent of quality.

---

## FORGE Agent: The Certification Engine

FORGE Agent is the operational implementation of the FORGE framework. It is the mechanism by which organizations begin their certification journey.

Where the FORGE framework defines the standard, FORGE Agent applies it. An organization uploads a data asset, answers a structured intake questionnaire, and receives a FORGE Data Assay Report: a scored, reasoned, actionable assessment of that asset's readiness and monetization potential.

Like Six Sigma belt certifications, FORGE levels are not binary. A dataset does not pass or fail. It receives a rating, Coal through Diamond, along with a specific roadmap for advancing to the next level. An organization can track their entire data portfolio across the certification spectrum, prioritize remediation efforts, and ultimately register certified assets for commercial availability.

The blockchain layer makes this verifiable. Every assessment generates a cryptographic hash anchored to the Casper Network testnet. That hash is an immutable, timestamped proof that the assessment occurred. FORGE agent acts as the foundation of a trustworthy certification registry.

---

## What This Submission Demonstrates

This qualification round submission is a working prototype of the FORGE Agent certification engine. It demonstrates:

**End-to-end assessment workflow**
Upload a CSV or Excel file, complete a 13-question intake form covering governance, compliance, sustainability, and monetization context, and receive a complete FORGE Data Assay Report in under 30 seconds.

**AI-powered scoring with reasoning**
The scoring engine uses Claude (Anthropic) to evaluate each dimension against the FORGE rubric and return not just scores but the reasoning behind each one. The assessment is defensible, not opaque.

**On-chain provenance via Casper Network**
Every completed assessment is hashed and anchored to the Casper testnet. The hash is stored alongside the assessment record and displayed in the report. This is the seed of the FORGE certification registry. The registry provides a verifiable, decentralized ledger of data asset assessments.

**Monetization potential analysis**
Beyond readiness scoring, the agent evaluates each asset across five monetization vectors: internal reporting, analytics products, API products, marketplace listings, and licensing. This directly supports the commercial intent of the FORGE framework.

---

## Technical Stack

| Layer | Technology |
|-------|------------|
| Agent / Scoring | Anthropic Claude API |
| Backend API | Python, FastAPI |
| Data Ingestion | Pandas, openpyxl |
| Database | SQL Server, SQLAlchemy |
| Blockchain | Casper Network (pycspr), testnet hash anchoring |
| Frontend | HTML, CSS, JavaScript |
| Environment | Python 3.10, virtualenv |

---

## Project Structure

```
forge-agent/
├── ai/
│   ├── profiler.py       # File ingestion and column profiling
│   └── scorer.py         # FORGE scoring agent (Claude API)
├── api/
│   └── main.py           # FastAPI endpoints
├── casper/
│   └── recorder.py       # Casper testnet hash anchoring
├── database/
│   ├── connection.py     # SQL Server connection
│   ├── models.py         # SQLAlchemy ORM models
│   └── schema.sql        # Database schema
├── frontend/
│   └── index.html        # Single-page assessment UI
├── tests/
├── requirements.txt
└── README.md
```

---

## Running the Project

**Prerequisites**
- Python 3.10+
- SQL Server (Express or higher)
- ODBC Driver 17 for SQL Server
- Anthropic API key

**Setup**

```bash
git clone https://github.com/plditallo/forge-agent.git
cd forge-agent
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```
ANTHROPIC_API_KEY=your-key-here
DB_SERVER=your-server\SQLEXPRESS
DB_NAME=forge_agent
DB_USER=forge_user
DB_PASSWORD=your-password
CASPER_TESTNET_RPC=https://node.testnet.casper.network/rpc
```

Create the database in SQL Server and run `database/schema.sql`.

**Start the server**

```bash
uvicorn api.main:app --reload
```

Open `http://127.0.0.1:8000/static/index.html`

---

## The Broader Vision

FORGE Agent is the first component of a larger ecosystem:

**FORGE Framework** — The methodology and scoring standard. The equivalent of the Six Sigma body of knowledge.

**FORGE Certification** — A formal credentialing process by which organizations achieve recognized certification levels for individual data assets or their entire data portfolio.

**FORGE Registry** — A decentralized, on-chain registry of certified data products. Buyers can verify certification. Sellers can prove provenance. The Casper Network is the natural home for this registry given its focus on real-world assets and verifiable identity.

**FORGE Marketplace** — The commercial endpoint. Certified data products, discoverable and transactable, with x402 micropayment support for per-call API access.

The hackathon submission is the entry point. The certification engine. The piece that begins the journey from Coal to Diamond.

---

## About the Builder

**Paula Ditallo** is the Founder and Innovator at Bauhaus Technology and Graphic Holdings LLC, a consulting and product development firm focused on data strategy, monetization, and enterprise data management. Paula is the author of *Security Without Accountability: The LAG Framework for Web 3.0 Governance*, *Algorithmic Infrastructures and the Temporal Reconfiguration of Accountability in Digital Governance*, and *Forging Data into Value: The FORGE Model for Data Productization in Mid-Market Firms* . Paula DiTallo brings deep expertise in data governance, product design, and enterprise architecture to the FORGE project.

---

## Links

- GitHub: https://github.com/plditallo/forge-agent
- Casper Network Testnet: https://testnet.cspr.live
- Casper AI Toolkit: https://www.casper.network/ai

---

*Submitted to the Casper Agentic Buildathon 2026 — Qualification Round*
*June 2026*
