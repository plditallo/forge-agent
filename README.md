# FORGE Agent
### AI-Powered Data Product Discovery, Assessment, and Monetization Platform

**Live Demo:** https://forge-agent-app.azurewebsites.net
**Demo Start Page:** https://forge-agent-app.azurewebsites.net/static/login.html

---

## The Problem

Most companies have no idea what data assets they possess, which assets have market value, what legal restrictions exist, or how to price access. Without a framework to assess, classify, and prepare data for commercial use, it stays buried generating cost instead of revenue.

This is not a technology problem. It is a methodology problem.

---

## The FORGE Framework

FORGE is a data readiness methodology: a structured, repeatable process for transforming raw organizational data into certified, commercially viable data products.

Think of it as Six Sigma for data monetization. Like Six Sigma, FORGE defines quality levels, certification tiers, and a progression path. Like TOEFL, it provides a recognized, verifiable credential that signals readiness to external parties. An organization does not simply "have good data." Under FORGE, they can prove it.

The framework is built around a mining metaphor that maps directly to data maturity:

| Level | Description |
|-------|-------------|
| Coal | Exists, but little value without extensive work |
| Iron | Useful operationally, but difficult to monetize |
| Bronze | Structured and partially governed |
| Silver | Trusted business asset |
| Gold | Product-ready data |
| Platinum | Strategic enterprise asset |
| Diamond | Unique, defensible, highly monetizable |

Every level has a roadmap, not just a score.

---

## The FORGE Data Assay: Eight Dimensions

Every dataset entering the FORGE process receives a Data Assay across eight weighted dimensions:

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

Four additional monetization metrics assess market value independent of quality: Uniqueness, Coverage, Historical Depth, and Enrichment Potential.

---

## FORGE Agent: The Full Ecosystem

FORGE Agent is the operational implementation of the FORGE framework. It is a complete data commercialization ecosystem with role-based access, live blockchain anchoring, and x402 micropayments.

### Assessment Engine

Upload a CSV or Excel file (up to 50MB), complete a 13-question intake form, and receive a complete FORGE Data Assay Report in under 60 seconds. The AI scoring engine (Claude, Anthropic) evaluates each dimension and returns scores with full defensible reasoning, not opaque outputs. Every upload is validated for content appropriateness before scoring begins. Datasets with PII are rejected before scoring.

### Certification Registry

Every assessment generates a SHA-256 hash anchored to the Casper Network testnet. That hash is an immutable, timestamped proof that the assessment occurred. The registry tracks a dataset's full certification history: every assessment run, every score change. Each Casper hash represents a point on the progression timeline from Coal toward Diamond.

### Data Marketplace

Certified data products are listed with per-call, monthly, and annual pricing in CSPR. Live CSPR/fiat conversion across six currencies (USD, EUR, GBP, CAD, AUD, JPY) makes pricing accessible to any buyer. A built-in price calculator shows cost breakdowns and recommends the most economical pricing tier based on expected usage volume.

The current marketplace operates on spot pricing: a buyer sees a certified dataset, pays the listed price, and receives the data immediately. Every transaction is anchored on Casper as a single event. The commercial version adds forward supply contracts as a third transaction type alongside spot purchases. See [Spot Pricing and the Road to Contract Pricing](#spot-pricing-and-the-road-to-contract-pricing) below.

Buyers access data through an x402-compliant payment flow:
1. Buyer calls the data endpoint
2. Server responds with HTTP 402 and payment terms
3. Buyer provides payment authorization
4. Casper records the transaction on-chain
5. Data is delivered with a Casper transaction hash

### Role-Based Access Control

Three distinct roles with appropriate visibility at every level:

- Seller: registers, uploads datasets, receives FORGE certification, lists in marketplace, sees only their own revenue and buyers
- Buyer: registers, browses certified datasets, purchases via x402 flow, sees only their own import history and costs
- Admin: full platform visibility, user management, data browser, cannot purchase

Users can hold multiple roles simultaneously. A seller can also be a buyer. Role badges appear in the header on every page.

### Buyer Dashboard

Registered buyers see their complete import history: every dataset purchased, records delivered, cost per record, total spend, and the Casper hash for each transaction. Imported data is browsable record by record.

### Seller Dashboard

Data sellers see revenue by dataset, revenue by buyer, total records delivered, and a complete filterable, paginated transaction ledger with Casper hashes. Non-admin sellers see only data related to their own listings.

### Admin Dashboard

Platform administrators have full visibility: user management with API key tracking and activation/deactivation controls, error log, and a filtered SQL data browser across all tables.

### Admin Invite-Mint

The admin console is gated by a shared password, intentionally separate from the buyer/seller registration flow. To grant admin access to a new person without sharing the password directly, an existing admin generates a single-use invite link from the admin header. The link is valid for 24 hours and can only be redeemed once. The recipient opens it, enters their name, and receives the admin password. The token is burned on redemption. The commercial version will use per-admin credentials with independent revocation.

### Security

Claude-powered content validation on every upload rejects inappropriate, offensive, or PII-heavy content before scoring begins. File size is capped at 50MB. Rate limiting is set at 5 uploads per hour per IP. API key authentication with attestation-gated registration requires a three-checkbox attestation at registration covering data ownership, no PII, and appropriate content.

---

## Live Demo

The platform is fully deployed on Azure with real on-chain transactions verifiable at [testnet.cspr.live](https://testnet.cspr.live).

**Demo accounts:**

| Role | Name | Organization |
|------|------|--------------|
| Seller | Malcolm Gladwell | Beacon Insights, LLC |
| Seller | Manuel Cabrera Kabana | Ifria Cold Chain Development Company |
| Buyer | Eustace Haney | Haney Cold Chain Logistics, LLC |

**Current marketplace state:**

Malcolm Gladwell has two certified datasets at Beacon Insights:

- **Southwestern Cities Refrigeration Transportation Data (sampling)**, Silver, 75.0. Listed for sale. Eustace Haney has purchased a copy; the on-chain purchase record is verifiable on testnet.cspr.live.
- **Dallas Independent Coffee Shops Features and Services (sampling)**, Silver, 72.0. Private (not yet listed). Real Casper certification hash on record.

Both datasets are synthesized samples created for demonstration purposes.

**Demo personas:**

Malcolm Gladwell at Beacon Insights, LLC assesses the Southwestern Cities Refrigeration Transportation Data (sampling) dataset, receives a Silver certification at 75.0, and lists it in the marketplace.

Eustace Haney at Haney Cold Chain Logistics, LLC purchases a copy of the Southwestern Cities Refrigeration Transportation Data (sampling) dataset. The on-chain purchase record is verifiable at testnet.cspr.live.

The Admin persona reviews platform activity across all datasets, users, and transactions in the admin console.

---

## Sample Datasets

The `data/` directory contains synthesized datasets for testing assessments locally. None contain real personal or proprietary data.

| File | Domain |
|------|--------|
| `arctic_express_deliveries.csv` | Cold chain logistics |
| `midwest_reefer_transport_market.csv` | Refrigerated transport |
| `southeast_reefer_transport_market.csv` | Refrigerated transport |
| `southwest_reefer_transport_market.csv` | Refrigerated transport |
| `oklahoma_city_independent_coffee_market.csv` | Specialty retail |
| `affluent_suburbs_pet_grooming_market_demographics.csv` | Consumer services |
| `heartland_ag_orders.csv` | Agricultural supply |
| `heartland_commercial_permits.csv` | Commercial real estate |
| `epa_air_quality_ok_ks_2025_2026.csv` | Environmental monitoring |
| `epa_air_quality_okc_sample.csv` | Environmental monitoring |
| `midamerica_respiratory_admissions.csv` | Healthcare |
| `costume_designer_fastener_firstlook_survey.csv` | Specialty manufacturing |
| `it_decision_maker_governance_appetite_survey.csv` | Enterprise IT |
| `synthesized_us_mid_size_city_transportation_marketing_data.csv` | Transportation |
| `pii_rejection_test_sample.csv` | PII rejection testing |

---

## Spot Pricing and the Road to Contract Pricing

The current marketplace is spot-based. A buyer sees a certified dataset, pays the listed price, and receives the data immediately. Every transaction is a single on-chain event.

The commercial version adds forward supply contracts as a third transaction type. A buyer and seller agree to a price band and delivery window before the data is delivered. The contract terms are anchored on Casper at negotiation time, before anyone knows what the delivery-time score will be. At delivery, FORGE re-certifies the dataset independently and settles the price based on where the score lands in the band. If the score misses the agreed tier floor, the contract has a defined remedy path rather than a renegotiation.

This is a direct application of the Dual-Commitment Architecture: the party with an incentive over the outcome (the seller) cannot be the sole author of the record determining that outcome (the settlement score). The terms hash anchored in February and the score hash anchored at delivery are linked on-chain and checkable by anyone, without trusting either party's account of what happened.

Casper's machine economy thesis fits here well. An agent buying data on behalf of an enterprise client needs to point at an immutable record of what was agreed to and what was delivered, without the human principals having to adjudicate it themselves. Pre-committed, independently-settled agreements are exactly the structure that makes agent-to-agent commerce auditable.

Dataset lifecycle management travels with this. A dataset entering a forward contract needs explicit states (Draft, Active, Superseded, Retired), versioning that links old and new certifications, and a retirement workflow that notifies existing buyers and anchors the end-of-life event on-chain.

---

## Technical Stack

| Layer | Technology |
|-------|------------|
| Agent / Scoring | Anthropic Claude API (claude-opus-4-6) |
| Backend API | Python, FastAPI |
| Data Ingestion | Pandas, openpyxl |
| Database | Azure SQL Database (Serverless), SQLAlchemy ORM |
| Blockchain | Casper Network testnet, ForgeRegistry Odra/Rust contract |
| Payment Protocol | x402 HTTP-native micropayment flow |
| Price Feed | CoinGecko API (live CSPR/fiat conversion) |
| Frontend | HTML, CSS, JavaScript (7 pages) |
| Deployment | Azure App Service (Linux, Python 3.10) + separate Node.js bridge service |
| Security | Claude content validation, rate limiting, API key auth |

---

## Architecture

The Casper bridge runs as a separate Azure App Service because `casper-types`, the Rust crate underlying the Python Casper SDK, calls Unix-only OS APIs that fail to compile on Windows. The Node.js `casper-js-sdk` has no native compilation step. The bridge isolates the signing key from the public-facing application and can be restarted or rekeyed without touching the main app.

```
Browser (Vanilla HTML/JS)
        |
        v
FastAPI backend (Azure App Service, Python)
        |                    |
        v                    v
Azure SQL              Anthropic Claude API
                             |
                             v
                    Casper Bridge Service
                    (Azure App Service, Node.js)
                             |
                             v
                    Casper Testnet (ForgeRegistry contract)
```

---

## Project Structure

```
forge-agent/
|-- ai/
|   |-- profiler.py           # File ingestion, column profiling, Claude content validation
|   `-- scorer.py             # FORGE scoring agent (Claude API)
|-- api/
|   `-- main.py               # FastAPI -- all endpoints
|-- casper/
|   `-- recorder.py           # Bridge HTTP client
|-- casper-bridge/
|   `-- server.js             # Node.js Casper signing bridge
|-- database/
|   |-- connection.py         # Azure SQL / local SQL Server connection
|   |-- models.py             # SQLAlchemy ORM models
|   `-- schema.sql            # Database schema reference
|-- frontend/
|   |-- index.html            # Assessment workflow
|   |-- registry.html         # Certification registry
|   |-- marketplace.html      # Data product marketplace with price calculator
|   |-- buyer_dashboard.html  # Buyer import & cost tracking
|   |-- seller_dashboard.html # Seller revenue analytics
|   |-- register.html         # User registration with role selection
|   |-- login.html            # API key login
|   |-- admin.html            # Admin dashboard
|   |-- admin-mint.html       # Token-gated admin invite flow
|   `-- shared_header.js      # Role-aware session manager (injected on every page)
|-- data/                     # Sample datasets for testing
|-- requirements.txt
`-- README.md
```

---

## Running Locally

**Prerequisites:** Python 3.10+, Node.js 22, SQL Server Express or Azure SQL, ODBC Driver 17 for SQL Server, Anthropic API key.

```bash
git clone https://github.com/plditallo/forge-agent.git
cd forge-agent
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

Create a `.env` file at the project root:

```
ANTHROPIC_API_KEY=your-key-here
DB_SERVER=your-server
DB_NAME=forge_agent
DB_USER=forge_user
DB_PASSWORD=your-password
DB_ENCRYPT=False
ADMIN_PASSWORD=your-admin-password
CASPER_BRIDGE_URL=http://localhost:3000
CASPER_BRIDGE_API_KEY=your-bridge-api-key
CASPER_TESTNET_RPC=https://node.testnet.casper.network/rpc
```

`ADMIN_PASSWORD` must be set before first run. There is no default shipped in the codebase.

If upgrading from an earlier version, run the migration for new columns:

```sql
ALTER TABLE assessments ADD casper_pending BIT NULL DEFAULT 0;
```

Create the database tables on first run:

```python
python -c "from database.connection import engine; from database.models import Base; Base.metadata.create_all(bind=engine)"
```

Start both services:

```bash
# Terminal 1: main app
uvicorn api.main:app --reload

# Terminal 2: Casper bridge
cd casper-bridge
node server.js
```

Pages available at `http://127.0.0.1:8000/static/`:

- `index.html` -- Assessment workflow
- `registry.html` -- Certification registry
- `marketplace.html` -- Data product marketplace
- `buyer_dashboard.html` -- Buyer import and cost tracking
- `seller_dashboard.html` -- Seller revenue analytics
- `register.html` -- User registration
- `login.html` -- API key login
- `admin.html` -- Admin dashboard
- `admin-mint.html` -- Token-gated admin invite redemption
- `/docs` -- FastAPI interactive API documentation

---

## Azure Deployment

The platform runs on two Azure App Services:

| Service | Runtime | Purpose |
|---------|---------|---------|
| `forge-agent-app` | Python 3.10 | Main application |
| `forge-casper-bridge` | Node 22 | Casper signing bridge |

After every deployment, confirm all required environment variables are present:

```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
.\forge_azure_verify.ps1
```

If any settings are missing, restore them:

```powershell
.\forge_azure_setup.ps1
```

Both scripts are in `.gitignore` and must not be committed to the repository. The Casper bridge's private key (`CASPER_SECRET_KEY_PEM_B64`) must be set by reading from the PEM file, not by pasting a value. Azure CLI silently truncates multi-line strings. The setup script contains the correct PowerShell method using `[System.IO.File]::ReadAllBytes()`.

---

## Casper Integration

FORGE uses Casper for two purposes:

Certification anchoring: each dataset assessment produces a hash of the scoring record (dataset name, weighted score, tier, timestamp). That hash is submitted as an argument to `record_certification` on the deployed ForgeRegistry contract. The resulting transaction hash is stored in Azure SQL and surfaced to sellers and buyers as a verifiable link to testnet.cspr.live.

Purchase attestation: each completed marketplace purchase is recorded as a second `record_certification` call with `tier: "TRANSACTION"` and `score: 0`, clearly distinguishing purchase events from certification events in the on-chain record.

If the bridge is unreachable, assessments complete and store normally with `casper_pending = true`. The seller can retry the anchor from their dashboard when the bridge recovers. Purchases are blocked entirely when the bridge is down, since the platform's value proposition requires an on-chain record for every completed transaction.

**ForgeRegistry contract:**
- Package hash: `160ad02bc56d6ec6b034139281bce4dee1757d69fdfdf69b81706fef66ccc260`
- Install transaction: `5ab2982e53b5c0054d2691dd8d499b2dc9e37cb3b4aeaac08aafdedbcf342ba2`

---

## The Broader Vision

FORGE Agent is the entry point to a larger ecosystem.

The FORGE Framework is the methodology and scoring standard: the body of knowledge that defines what certified data looks like at every level from Coal to Diamond.

FORGE Certification becomes a formal credentialing process. Organizations achieve recognized certification levels for individual data assets or their entire portfolio.

The FORGE Registry becomes a decentralized, on-chain registry of certified data products on Casper. Buyers verify certification. Sellers prove provenance. Trust is established without a centralized authority.

The FORGE Marketplace scales to certified data products that are discoverable and transactable, with x402 micropayment support enabling per-call API access and machine-to-machine commerce at the speed agents operate.

---

## Why Casper

The FORGE Registry requires a trust layer that is immutable, verifiable, and independent of any single organization. Casper's focus on real-world assets, its x402 micropayment protocol, and its enterprise architecture make it a natural fit for FORGE certification records and data product transactions.

Every assessment hash recorded on Casper testnet in this submission is a proof of concept for what becomes a production registry where any buyer can verify that a dataset is genuinely FORGE-certified, and any seller can prove provenance without relying on a centralized authority.

Steel is forged in fire. So is trusted data.

---

## About the Builder

**Paula DiTallo** is the Founder and Innovator at Bauhaus Technology and Graphic Holdings LLC, a consulting and product development firm focused on data strategy, monetization, and enterprise data management. Paula is the author of [*Security Without Accountability: The LAG Framework for Web 3.0 Governance*](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6232958), [*Algorithmic Infrastructures and the Temporal Reconfiguration of Accountability in Digital Governance*](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6253460), [*Forging Data into Value: The FORGE Model for Data Productization in Mid-Market Firms*](https://www.researchgate.net/publication/404151942_Forging_Data_into_Value_The_FORGE_Model_for_Data_Productization_in_Mid-Market_Firms), [*Disclosure Integrity in Autonomous Agent Brokering: A Dual-Commitment Verification Architecture*](https://www.researchgate.net/publication/408143880_Disclosure_Integrity_in_Autonomous_Agent_Brokering_A_Dual-Commitment_Verification_Architecture), and [*The Future of IT Leadership: The Rise of the Fractional CXO*](https://www.amazon.com/Future-Leadership-Rise-Fractional-CXO-ebook/dp/B0GX3F7NY3/ref=sr_1_1?). Paula DiTallo brings deep expertise in data governance, product design, and enterprise architecture to the FORGE project.

---

## Links

- GitHub: https://github.com/plditallo/forge-agent
- Live Demo: https://forge-agent-app.azurewebsites.net
- Demo Start Page: https://forge-agent-app.azurewebsites.net/static/login.html
- Casper Network Testnet: https://testnet.cspr.live

---

*Submitted to the Casper Agentic Buildathon 2026*
*July 2026*
