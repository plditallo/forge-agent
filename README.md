# FORGE Agent
### AI-Powered Data Product Discovery, Assessment, and Monetization Platform

**Live Demo:** https://forge-agent-app.azurewebsites.net

---

## The Problem

Most companies have no idea what data assets they possess, which assets have market value, what legal restrictions exist, or how to price access. Without a framework to assess, classify, and prepare data for commercial use, it stays buried generating cost instead of revenue.

This is not a technology problem. It is a methodology problem.

---

## The FORGE Framework

FORGE is a data readiness methodology utilizing a structured, repeatable process for transforming raw organizational data into certified, commercially viable data products.

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

Four additional monetization metrics: Uniqueness, Coverage, Historical Depth, and Enrichment Potential assess market value independent of quality.

---

## FORGE Agent: The Full Ecosystem

FORGE Agent is the operational implementation of the FORGE framework. It is a complete data commercialization ecosystem with role-based access, live blockchain anchoring, and x402 micropayments.

### Assessment Engine
Upload a CSV or Excel file (up to 50MB), complete a 13-question intake form, and receive a complete FORGE Data Assay Report in under 60 seconds. The AI scoring engine (Claude, Anthropic) evaluates each dimension and returns scores with full defensible reasoning, not opaque. Every upload is validated for content appropriateness before scoring begins.

### Certification Registry
Every assessment generates a SHA-256 hash anchored to the Casper Network testnet. That hash is an immutable, timestamped proof that the assessment occurred. The registry tracks a dataset's full certification history, every assessment run, every score change, and every Casper hash represents a progression timeline from Coal toward Diamond.

### Data Marketplace
Certified data products are listed in the FORGE Marketplace with per-call, monthly, and annual pricing in CSPR. Live CSPR/fiat conversion across six currencies (USD, EUR, GBP, CAD, AUD, JPY) makes pricing accessible to any buyer. A built-in price calculator shows cost breakdowns and recommends the most economical pricing tier based on expected usage volume.

Buyers access data through an x402-compliant payment flow:
1. Buyer calls the data endpoint
2. Server responds with HTTP 402 and payment terms
3. Buyer provides payment authorization
4. Casper records the transaction on-chain
5. Data is delivered with a Casper transaction hash

### Role-Based Access Control
Three distinct roles with appropriate visibility at every level:

- **Seller** — registers, uploads datasets, receives FORGE certification, lists in marketplace, sees only their own revenue and buyers
- **Buyer** — registers, browses certified datasets, purchases via x402 flow, sees only their own import history and costs
- **Admin** — full platform visibility, user management, data browser, cannot purchase

Users can hold multiple roles simultaneously. A seller can also be a buyer. Role badges appear in the header on every page.

### Buyer Dashboard
Registered buyers see their complete import history — every dataset purchased, records delivered, cost per record, total spend, and the Casper hash for each transaction. Imported data is browsable record by record.

### Seller Dashboard
Data sellers see revenue by dataset, revenue by buyer, total records delivered, and a complete filterable, paginated transaction ledger with Casper hashes. Non-admin sellers see only data related to their own listings.

### Admin Dashboard
Platform administrators have full visibility: user management with API key tracking and activation/deactivation controls, error log, and a filtered SQL data browser across all tables.

### Security
- Claude-powered content validation on every upload — rejects inappropriate, offensive, or PII-heavy content before scoring
- 50MB file size limit enforced at upload
- Rate limiting: 5 uploads per hour per IP
- API key authentication with attestation-gated registration
- Three-checkbox attestation required at registration (data ownership, no PII, appropriate content)

---

## Live Demo Datasets

| Dataset | Rating | Score | Records | Description |
|---------|--------|-------|---------|-------------|
| EPA Air Quality Monitor — Oklahoma & Kansas 2025-2026 | Gold | 88 | 25,296 | Daily air quality across 6 pollutants, 8 EPA stations, Oklahoma City / Tulsa / Wichita / Topeka |
| EPA Air Quality Monitor — Oklahoma City May 2026 | Gold | 84 | 186 | Daily air quality sample, OKC, May 2026 |
| MidAmerica Regional Respiratory Admissions 2025-2026 | Gold | 88 | 3,648 | Weekly aggregated hospital admissions by zip code, HIPAA compliant |
| Heartland Commercial Building Permits 2025-2026 | Gold | 81 | 500 | Commercial permit activity across OKC / Tulsa / Wichita corridor |
| Heartland Ag Supply Order History 2025-2026 | Gold | 82 | 200 | Agricultural supply orders across Kansas, Missouri, and Iowa |
| Arctic Express Refrigerated Delivery Records 2025-2026 | Coal | 39 | 120 | Refrigerated logistics — demonstrates low-scoring dataset path to improvement |

---

## Demo Personas

**Dr. Sarah Chen** — MidAmerica Health Analytics LLC
Purchases EPA air quality data and respiratory admissions data to correlate air quality events with hospital ER visits. Public health use case.

**Marcus Webb** — Heartland Site Solutions Inc.
Purchases EPA air quality data and commercial permit data to score development sites for industrial and medical facility suitability.

---

## Technical Stack

| Layer | Technology |
|-------|------------|
| Agent / Scoring | Anthropic Claude API (claude-opus-4-6) |
| Backend API | Python, FastAPI |
| Data Ingestion | Pandas, openpyxl |
| Database | Azure SQL Database (Serverless), SQLAlchemy ORM |
| Blockchain | Casper Network testnet (pycspr), SHA-256 hash anchoring |
| Payment Protocol | x402 HTTP-native micropayment flow |
| Price Feed | CoinGecko API (live CSPR/fiat conversion) |
| Frontend | HTML, CSS, JavaScript (7 pages) |
| Deployment | Azure App Service (Linux, Python 3.10) |
| Security | Claude content validation, rate limiting, API key auth |

---

## Project Structure

```
forge-agent/
├── ai/
│   ├── profiler.py           # File ingestion, column profiling, Claude content validation
│   └── scorer.py             # FORGE scoring agent (Claude API)
├── api/
│   └── main.py               # FastAPI — all endpoints
├── casper/
│   └── recorder.py           # Casper testnet hash anchoring
├── database/
│   ├── connection.py         # Azure SQL / local SQL Server connection
│   ├── models.py             # SQLAlchemy ORM models
│   └── schema.sql            # Database schema reference
├── frontend/
│   ├── index.html            # Assessment workflow
│   ├── registry.html         # Certification registry
│   ├── marketplace.html      # Data product marketplace with price calculator
│   ├── buyer_dashboard.html  # Buyer import & cost tracking
│   ├── seller_dashboard.html # Seller revenue analytics
│   ├── register.html         # User registration with role selection
│   ├── login.html            # API key login
│   ├── admin.html            # Admin dashboard
│   └── shared_header.js     # Role-aware session manager (injected on every page)
├── data/
│   ├── epa_air_quality_ok_ks_2025_2026.csv
│   ├── epa_air_quality_okc_sample.csv
│   ├── midamerica_respiratory_admissions.csv
│   ├── heartland_commercial_permits.csv
│   ├── heartland_ag_orders.csv
│   └── arctic_express_deliveries.csv
├── requirements.txt
└── README.md
```

---

## Running Locally

**Prerequisites**
- Python 3.10+
- SQL Server Express (or Azure SQL)
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

```env
ANTHROPIC_API_KEY=your-key-here
DB_SERVER=your-server
DB_NAME=forge_agent
DB_USER=forge_user
DB_PASSWORD=your-password
DB_ENCRYPT=False
ADMIN_PASSWORD=your-forge-agent-admin-password
CASPER_TESTNET_RPC=https://node.testnet.casper.network/rpc
```

Create the database tables:

```python
python -c "from database.connection import engine; from database.models import Base; Base.metadata.create_all(bind=engine)"
```

**Start the server**

```bash
uvicorn api.main:app --reload
```

**Pages**
- Assessment: `/static/index.html`
- Registry: `/static/registry.html`
- Marketplace: `/static/marketplace.html`
- Buyer Dashboard: `/static/buyer_dashboard.html`
- Seller Dashboard: `/static/seller_dashboard.html`
- Register: `/static/register.html`
- Login: `/static/login.html`
- Admin: `/static/admin.html`
- API Docs: `/docs`

---

## Live Deployment

**URL:** https://forge-agent-app.azurewebsites.net

Deployed on Azure App Service (Linux, Python 3.10, Free tier) backed by Azure SQL Database (Serverless, General Purpose).

---

## The Broader Vision

FORGE Agent is the entry point to a larger ecosystem:

**FORGE Framework** — The methodology and scoring standard. The body of knowledge that defines what certified data looks like at every level from Coal to Diamond.

**FORGE Certification** — A formal credentialing process. Organizations achieve recognized certification levels for individual data assets or their entire portfolio.

**FORGE Registry** — A decentralized, on-chain registry of certified data products on the Casper Network. Buyers verify certification. Sellers prove provenance. Trust is built in.

**FORGE Marketplace** — Certified data products, discoverable and transactable. x402 micropayment support enables per-call API access, machine-to-machine commerce for data at the speed agents operate.

---

## Why Casper

The FORGE Registry requires a trust layer that is immutable, verifiable, and independent of any single organization. Casper's focus on real-world assets, its x402 micropayment protocol, and its enterprise-grade architecture make it the natural home for FORGE certification records and data product transactions.

Every assessment hash recorded on Casper testnet in this submission is a proof of concept for what becomes a production registry where any buyer can verify that a dataset is genuinely FORGE-certified, and any seller can prove provenance without relying on a centralized authority.

Steel is forged in fire. So is trusted data.

---

## About the Builder

**Paula DiTallo** is the Founder and Innovator at Bauhaus Technology and Graphic Holdings LLC, a consulting and product development firm focused on data strategy, monetization, and enterprise data management. Paula is the author of [*Security Without Accountability: The LAG Framework for Web 3.0 Governance*](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6232958), [*Algorithmic Infrastructures and the Temporal Reconfiguration of Accountability in Digital Governance*](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6253460), [*Forging Data into Value: The FORGE Model for Data Productization in Mid-Market Firms*](https://www.researchgate.net/publication/404151942_Forging_Data_into_Value_The_FORGE_Model_for_Data_Productization_in_Mid-Market_Firms), and [*The Future of IT Leadership: The Rise of the Fractional CXO*](https://www.amazon.com/Future-Leadership-Rise-Fractional-CXO-ebook/dp/B0GX3F7NY3/ref=sr_1_1?). Paula DiTallo brings deep expertise in data governance, product design, and enterprise architecture to the FORGE project.

---

## Links

- GitHub: https://github.com/plditallo/forge-agent
- Live Demo: https://forge-agent-app.azurewebsites.net
- Casper Network Testnet: https://testnet.cspr.live

---

*Submitted to the Casper Agentic Buildathon 2026*
*June 2026*
