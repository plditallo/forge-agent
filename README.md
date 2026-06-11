# FORGE Agent
### AI-Powered Data Product Discovery, Assessment, and Monetization Platform

**Built by Paula DiTallo**
Founder & Innovator, Bauhaus Technology and Graphic Holdings LLC

---

## The Problem

Most companies have no idea what data assets they possess, which assets have market value, what legal restrictions exist, or how to price access. Without a framework to assess, classify, and prepare data for commercial use, it stays buried — generating cost instead of revenue.

This is not a technology problem. It is a methodology problem.

---

## The FORGE Framework

FORGE is a data readiness methodology — a structured, repeatable process for transforming raw organizational data into certified, commercially viable data products.

Think of it as Six Sigma for data monetization. Like Six Sigma, FORGE defines quality levels, certification tiers, and a progression path. Like TOEFL, it provides a recognized, verifiable credential that signals readiness to external parties. An organization does not simply "have good data." Under FORGE, they can prove it.

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

Four additional monetization metrics — Uniqueness, Coverage, Historical Depth, and Enrichment Potential — assess market value independent of quality.

---

## FORGE Agent: The Full Ecosystem

FORGE Agent is the operational implementation of the FORGE framework. It is not just an assessment tool — it is a complete data commercialization ecosystem.

### Assessment Engine
Upload a CSV or Excel file, complete a 13-question intake form, and receive a complete FORGE Data Assay Report in under 30 seconds. The AI scoring engine (Claude, Anthropic) evaluates each dimension and returns scores with full reasoning — defensible, not opaque.

### Certification Registry
Every assessment generates a SHA-256 hash anchored to the Casper Network testnet. That hash is an immutable, timestamped proof that the assessment occurred. The registry page tracks a dataset's full certification history — every assessment run, every score change, every Casper hash — visualized as a progression timeline from Coal toward Diamond.

### Data Marketplace
Certified data products are listed in the FORGE Marketplace with per-call, monthly, and annual pricing in CSPR. Buyers register once and access data through an x402-compliant payment flow:

1. Buyer calls the data endpoint
2. Server responds with HTTP 402 and payment terms
3. Buyer provides payment authorization
4. Casper records the transaction on-chain
5. Data is delivered with a Casper transaction hash

Every transaction is recorded, every Casper hash is stored, and the full ledger is visible in real time.

### Buyer Dashboard
Registered buyers see their complete import history — every dataset purchased, records delivered, cost per record, total spend, and the Casper hash for each transaction. Imported data is browsable record by record. Cost trends are visualized over time.

### Seller Dashboard
Data sellers see revenue by dataset, revenue by buyer, total records delivered, and a complete transaction ledger with Casper hashes. The economic loop is fully closed and auditable.

---

## Live Demo Datasets

| Dataset | Rating | Score | Description |
|---------|--------|-------|-------------|
| EPA Air Quality Monitor — OKC June 2023 | Gold | 89.0 | Daily air quality across 6 pollutants, 6 EPA monitoring stations, Oklahoma City |
| Heartland Ag Supply Order History 2024 | Silver | 79.0 | Regional agricultural supply orders across Kansas, Missouri, and Iowa |
| Arctic Express Delivery Records 2024 | Iron | ~54 | Refrigerated transport deliveries serving the OKC/Tulsa/Wichita seafood industry |

---

## Technical Stack

| Layer | Technology |
|-------|------------|
| Agent / Scoring | Anthropic Claude API (claude-opus-4-6) |
| Backend API | Python, FastAPI |
| Data Ingestion | Pandas, openpyxl |
| Database | SQL Server, SQLAlchemy ORM |
| Blockchain | Casper Network testnet (pycspr), SHA-256 hash anchoring |
| Payment Protocol | x402 HTTP-native micropayment flow |
| Frontend | HTML, CSS, JavaScript (5 pages) |
| Environment | Python 3.10, virtualenv |

---

## Project Structure

```
forge-agent/
├── ai/
│   ├── profiler.py           # File ingestion and column profiling
│   └── scorer.py             # FORGE scoring agent (Claude API)
├── api/
│   └── main.py               # FastAPI — all endpoints
├── casper/
│   └── recorder.py           # Casper testnet hash anchoring
├── database/
│   ├── connection.py         # SQL Server connection
│   ├── models.py             # SQLAlchemy ORM models
│   └── schema.sql            # Database schema
├── frontend/
│   ├── index.html            # Assessment workflow
│   ├── registry.html         # Certification registry
│   ├── marketplace.html      # Data product marketplace
│   ├── buyer_dashboard.html  # Buyer import & cost tracking
│   └── seller_dashboard.html # Seller revenue analytics
├── data/
│   ├── epa_air_quality_okc_june2023_sample.csv
│   ├── epa_air_quality_ok_ks_2022_2023.csv
│   ├── heartland_ag_orders.csv
│   └── arctic_express_deliveries.csv
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
CASPER_PRIVATE_KEY=your-casper-private-key
CASPER_PUBLIC_KEY=your-casper-public-key
```

Create the database in SQL Server and run `database/schema.sql`.

**Start the server**

```bash
uvicorn api.main:app --reload
```

Open `http://127.0.0.1:8000/static/index.html`

**All pages:**
- Assessment: `/static/index.html`
- Registry: `/static/registry.html`
- Marketplace: `/static/marketplace.html`
- Buyer Dashboard: `/static/buyer_dashboard.html`
- Seller Dashboard: `/static/seller_dashboard.html`
- API Docs: `/docs`

---

## The Broader Vision

FORGE Agent is the entry point to a larger ecosystem:

**FORGE Framework** — The methodology and scoring standard. The body of knowledge that defines what certified data looks like at every level from Coal to Diamond.

**FORGE Certification** — A formal credentialing process. Organizations achieve recognized certification levels for individual data assets or their entire portfolio — like Six Sigma belt levels.

**FORGE Registry** — A decentralized, on-chain registry of certified data products on the Casper Network. Buyers verify certification. Sellers prove provenance. Trust is built in.

**FORGE Marketplace** — Certified data products, discoverable and transactable. x402 micropayment support enables per-call API access — machine-to-machine commerce for data at the speed agents operate.

The hackathon submission is the certification engine, the registry, and the marketplace — all working together, all anchored to Casper.

---

## Why Casper

The FORGE Registry requires a trust layer that is immutable, verifiable, and independent of any single organization. Casper's focus on real-world assets, its x402 micropayment protocol, and its enterprise-grade architecture make it the natural home for FORGE certification records and data product transactions.

Every assessment hash recorded on Casper testnet in this submission is a proof of concept for what becomes a production registry — where any buyer can verify that a dataset is genuinely FORGE-certified, and any seller can prove provenance without relying on a centralized authority.

---

## About the Builder


**Paula DiTallo** is the Founder and Innovator at Bauhaus Technology and Graphic Holdings LLC, a consulting and product development firm focused on data strategy, monetization, and enterprise data management. Paula is the author of [*Security Without Accountability: The LAG Framework for Web 3.0 Governance*](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6232958), [*Algorithmic Infrastructures and the Temporal Reconfiguration of Accountability in Digital Governance*](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6253460), [*Forging Data into Value: The FORGE Model for Data Productization in Mid-Market Firms*](https://www.researchgate.net/publication/404151942_Forging_Data_into_Value_The_FORGE_Model_for_Data_Productization_in_Mid-Market_Firms), and [*The Future of IT Leadership: The Rise of the Fractional CXO*](https://www.amazon.com/Future-Leadership-Rise-Fractional-CXO-ebook/dp/B0GX3F7NY3/ref=sr_1_1?). Paula DiTallo brings deep expertise in data governance, product design, and enterprise architecture to the FORGE project.

---

## Links

- GitHub: https://github.com/plditallo/forge-agent
- Casper Network Testnet: https://testnet.cspr.live
- Casper AI Toolkit: https://www.casper.network/ai

---

*Submitted to the Casper Agentic Buildathon 2026 — Qualification Round*
*June 2026*
