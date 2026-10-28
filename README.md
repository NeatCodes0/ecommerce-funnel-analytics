# E-Commerce Funnel & Cart Abandonment Analytics Engine

**High-Throughput Vectorized Clickstream Analytics, Funnel Sessionization & Statistical Inference**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ecommerce-funnel-analytics.streamlit.app/)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![DuckDB](https://img.shields.io/badge/DuckDB-1.0%2B-FEE000?style=for-the-badge&logo=duckdb&logoColor=black)
![Pandas](https://img.shields.io/badge/Pandas-2.2%2B-150458?style=for-the-badge&logo=pandas&logoColor=white)
![SciPy](https://img.shields.io/badge/SciPy-1.13%2B-8CAAE6?style=for-the-badge&logo=scipy&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)

A production-grade, serverless analytical pipeline diagnosing checkout drop-offs, session-level friction, and visitor conversion behavior across **4.1M+ raw clickstream events**.

[Live Application](https://ecommerce-funnel-analytics.streamlit.app/) • [Key Findings](#-executive-summary--critical-business-findings) • [Architecture & ADRs](#%EF%B8%8F-system-architecture--technical-decisions) • [Statistical Rigor](#-statistical-hypothesis-testing--validation) • [Interactive Dashboard](#-interactive-web-app--visualizations) • [Quickstart](#-reproduction--quickstart)

---

## Executive Summary & Critical Business Findings

Across **873,960 unique browsing sessions** and **399,664 individual users** in October 2019:

```text
[1,862,164 Views]
       │
       ▼  (27.69% View-to-Cart Conversion)
[1,232,385 Carts]
       │
       ▼  (12.86% Cart-to-Purchase Conversion) ──► 89.40% Cart Abandonment Cliff
[  245,624 Purchases] (3.36% Overall Session CVR)
```

### Core Business Takeaways
1. **The Cart Functions as a Wishlist:** Unlike traditional e-commerce platforms where cart-add rates hover around 5–10%, users exhibit a **27.69% view-to-cart rate** alongside an **89.40% cart abandonment rate**. The shopping cart functions primarily as a temporary holding bin during window shopping.
2. **Quantified Revenue Opportunity:** **203,891 sessions** abandoned carts without completing a purchase, leaving **$5,512,701.50** in unrecovered merchandise value. Reducing abandonment by just 200 basis points (down to 87.40%) unlocks ~$120,000+ in monthly gross sales.
3. **Session Duration as an Intent Filter:** Sessions under 60 seconds bounce with virtually zero purchase conversion (<0.5%), while sessions crossing 5 minutes yield conversion rates above 8.5%.

---

## System Architecture & Technical Decisions

```text
┌────────────────────────────────┐
│   Raw Clickstream (4.1M CSV)   │
└───────────────┬────────────────┘
                │ Stream Ingestion (DECIMAL types, TIMESTAMPTZ)
                ▼
┌────────────────────────────────┐
│     DuckDB OLAP Engine         │
│  (Vectorized Columnar Storage) │
└───────┬────────────────┬───────┘
        │                │
        │ Single-pass    │ Aggregations
        ▼                ▼
┌──────────────────┐  ┌───────────────────────────┐
│ Cleaned Events   │  │ Dimensional Marts (11.7KB)│
│ & Session Models │  │ (Daily, Brand, Duration)  │
└───────┬──────────┘  └─────────────┬─────────────┘
        │                           │
        ▼                           ▼
┌──────────────────────────┐  ┌───────────────────────────┐
│ Statistical Testing      │  │ Presentation Layer        │
│ (SciPy Z-Test / Chi-Sq)  │  │ (Streamlit Web Dashboard) │
└──────────────────────────┘  └───────────────────────────┘
```

### Architectural Decision Records (ADRs)

| Component        | Choice                             | Alternatives Rejected     | Rationale                                                                                                  |
| :--------------- | :--------------------------------- | :------------------------ | :--------------------------------------------------------------------------------------------------------- |
| **Engine**       | **DuckDB**                         | PostgreSQL, SQLite        | Columnar, vectorized execution processed 4.1M rows in **3.98s** locally without background server daemons. |
| **Currency**     | **DECIMAL(10,2)**                  | FLOAT, DOUBLE             | Eliminates IEEE 754 floating-point drift across millions of price additions.                               |
| **Funnel Logic** | **Conditional Aggregation (CTEs)** | Self-Joins (`JOIN ON`)    | Reduced multi-stage funnel calculation from an $O(N^2)$ join into a single linear sequential scan.         |
| **Presentation** | **Streamlit + Code**               | Power BI, Tableau Desktop | Full Python reproducibility, git-versioned code, zero vendor lock-in, and instant cloud deployability.     |

---

## Statistical Hypothesis Testing & Validation

### 1. Two-Proportion $Z$-Test: Visitor Loyalty
* **Hypothesis:** Does cart-to-purchase conversion differ significantly between first-time visitors and returning users?
  * $H_0: p_{\text{returning}} = p_{\text{new}}$
  * $H_1: p_{\text{returning}} \neq p_{\text{new}}$
* **Output:**
  * Returning Visitor CVR: **13.52%** (vs. New Visitor: **12.31%**)
  * $Z\text{-Statistic} = 31.42$, $p\text{-value} = 3.24 \times 10^{-216}$
* **Conclusion:** Reject $H_0$. Returning visitors demonstrate statistically higher checkout commitment, validating dedicated retargeting workflows.

### 2. Chi-Square ($\chi^2$) Test: Session Duration vs. Conversion
* **Hypothesis:** Is purchase completion independent of browsing duration?
  * $H_0: \text{Duration Bracket and Purchase are independent}$
  * $H_1: \text{Duration Bracket and Purchase are dependent}$
* **Output:**
  * $\chi^2 = 80,635.69$, $\text{Degrees of Freedom} = 3$, $p\text{-value} < 10^{-15}$
* **Conclusion:** Reject $H_0$. Engagement time strongly dictates checkout likelihood, identifying users browsing 3–5 minutes as prime candidates for exit-intent prompts.

---

## Interactive Web App & Visualizations

The interactive Streamlit interface provides real-time cohort filtering, KPI cards, and brand opportunity drill-downs:

* **Live Demo:** [ecommerce-funnel-analytics.streamlit.app](https://ecommerce-funnel-analytics.streamlit.app/)
* **Local Launch:** `streamlit run src/app.py`
* **Static Assets:** Run `python src/generate_visuals.py` to regenerate static assets:
  - `dashboards/assets/funnel_waterfall.png`
  - `dashboards/assets/duration_conversion_curve.png`
  - `dashboards/assets/daily_revenue_vs_abandoned.png`

---

## Project Structure

```text
ecommerce-funnel-analytics/
├── data/
│   ├── raw/                  # Source CSVs (ignored by .gitignore)
│   └── processed/            # Exported dimensional marts (fact_daily_funnel, etc.)
├── database/
│   └── analytics.duckdb      # DuckDB persistent OLAP store
├── sql/
│   ├── 03_funnel_staging.sql # Sessionization & conditional aggregation logic
│   └── 04_funnel_segmentation.sql # Loyalty & duration bracket segmentation
├── notebooks/
│   └── funnel_analytics_walkthrough.ipynb # Step-by-step interactive workflow
├── src/
│   ├── ingest.py             # Vectorized ingestion & data hygiene checks
│   ├── hypothesis_testing.py # Z-Test & Chi-Square test execution
│   ├── export_bi_layers.py   # Dimensional mart materialization
│   ├── generate_visuals.py   # Publication-grade chart generation
│   └── app.py                # Interactive Streamlit dashboard
├── dashboards/
│   └── assets/               # Exported visual artifacts
├── docs/                     # Architecture logs, data dictionary, metrics
├── requirements.txt
└── README.md
```

---

## Reproduction & Quickstart

1. **Clone the repository:**
   ```bash
   git clone https://github.com/NeatCodes0/ecommerce-funnel-analytics.git
   cd ecommerce-funnel-analytics
   ```

2. **Activate Virtual Environment & Install Dependencies:**
   ```bash
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

3. **Execute Pipeline:**
   ```bash
   python src/ingest.py
   python src/run_transformations.py
   python src/hypothesis_testing.py
   python src/export_bi_layers.py
   python src/generate_visuals.py
   ```

4. **Launch Dashboard Locally:**
   ```bash
   streamlit run src/app.py
   ```