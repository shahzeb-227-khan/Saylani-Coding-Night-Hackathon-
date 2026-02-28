# Real-Time Crypto Analytics Platform

**ETL + API + PostgreSQL + Live Dashboard**

> Built by **Shahzeb Alam** during **Coding Night** organized by **Saylani Mass IT Training Program** — March 1, 2026

[![Live Dashboard](https://img.shields.io/badge/Live%20Demo-Streamlit-E1BB80?style=for-the-badge&logo=streamlit&logoColor=white)](https://crypto-analytics-ai.streamlit.app/)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-352208?style=for-the-badge&logo=github&logoColor=white)](https://github.com/shahzeb-227-khan)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Shahzeb%20Alam-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/shahzeb-alam-759b992a4/)

---

## Live Demo

**https://crypto-analytics-ai.streamlit.app/**

---

## Project Overview

A full-stack real-time cryptocurrency analytics platform that pulls live market data from the CoinGecko API, transforms and stores it in a PostgreSQL database (Supabase), runs scheduled ETL pipelines, performs SQL-based data analysis, and displays everything on a dynamic Streamlit dashboard.

### What It Covers

- Complete **ETL architecture** (Extract → Transform → Load)
- **API consumption** from CoinGecko (no key required)
- **PostgreSQL** database integration with Supabase
- **Data analysis** using SQL aggregations, window functions, and feature engineering
- **Interactive dashboard** that auto-refreshes when new data arrives

---

## System Architecture

```
[ CoinGecko API ]
        |
   Extract Layer       →  extract.py (API calls, validation, raw JSON logging)
        |
  Transform Layer      →  transform.py (cleaning, type conversion, feature engineering)
        |
   Load Layer          →  load.py (batch UPSERT into PostgreSQL)
        |
   PostgreSQL DB       →  database.py (connection pooling, schema, indexes)
        |
  Analysis Layer       →  analysis.py (SQL aggregations, rankings, sentiment)
        |
 Streamlit Dashboard   →  dashboard.py (live KPIs, charts, ticker, watchlist)
```

---

## Database Schema

**Table: `crypto_market`**

| Column | Type |
|---|---|
| id | SERIAL PRIMARY KEY |
| coin_id | TEXT |
| symbol | TEXT |
| name | TEXT |
| current_price | FLOAT |
| market_cap | BIGINT |
| total_volume | BIGINT |
| price_change_24h | FLOAT |
| market_cap_rank | INTEGER |
| volatility_score | FLOAT |
| extracted_at | TIMESTAMP |

**Indexes:** `coin_id`, `extracted_at`, `market_cap_rank`

**Constraint:** `UNIQUE(coin_id, extracted_at)` — enables UPSERT

---

## Task Breakdown

### Task 1 — Database Setup (`database.py`)
- PostgreSQL connection via `psycopg2` with **connection pooling** (ThreadedConnectionPool)
- Table creation with `CREATE TABLE IF NOT EXISTS`
- Index creation for query performance
- Transaction handling with commit/rollback

### Task 2 — Extract Layer (`extract.py`)
- Pulls top 20 cryptocurrencies from **CoinGecko API**
- Validates API response structure
- Saves raw JSON locally to `raw_data/` for logging
- Handles timeouts, rate limiting (429), and network errors

### Task 3 — Transform Layer (`transform.py`)
- Cleans null/None values with typed defaults
- Converts numeric fields to proper types
- **Feature engineering:** `volatility_score = abs(price_change_24h) * total_volume`
- Adds `extracted_at` timestamp
- Selects required fields for DB schema

### Task 4 — Load Layer (`load.py`)
- **UPSERT** using `ON CONFLICT (coin_id, extracted_at) DO UPDATE`
- Batch inserts with configurable batch size
- Parameterized queries for security
- Transaction management per batch

### Task 5 — ETL Orchestrator (`etl_pipeline.py`)
- Orchestrates extract → transform → load
- **Scheduled execution** every 5 minutes using APScheduler
- File + console logging to `logs/`
- Supports `--once` and `--schedule` CLI modes

### Task 6 — Data Analysis (`analysis.py`)
- Top 5 gainers/losers by 24h price change
- Top coins by market cap
- Average market cap and total market value
- Volatility ranking with `RANK() OVER()` **window function**
- Market dominance percentages
- Price tier categorization (CASE + GROUP BY)
- Volume-to-market-cap liquidity ratio
- Market sentiment (FILTER, STDDEV aggregations)
- Top coins by trading volume

### Task 7 — Live Dashboard (`dashboard.py`)
- **KPI Cards:** Total Market Cap, Average Price, Top Gainer, Most Volatile
- **Charts:** Market Cap Bar, Price Change, Volatility Ranking, Volume Donut, Market Dominance, Liquidity Ranking, Price Tiers
- **Animated ticker** strip with live prices
- **Watchlist** — select coins to highlight across all charts
- **Market sentiment** panel in sidebar
- **Auto-refresh** every 60 seconds — reflects ETL changes immediately
- Modern typography: Poppins + Inter + JetBrains Mono
- Dark coffee/olive color palette

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3 |
| Database | PostgreSQL (Supabase) |
| API | CoinGecko REST API |
| ETL Scheduling | APScheduler |
| Dashboard | Streamlit |
| Charts | Plotly |
| Data | pandas |
| HTTP | requests |
| DB Driver | psycopg2 |

---

## Project Structure

```
crypto-analytics/
├── config.py            # Configuration (DB creds, API settings, ETL interval)
├── database.py          # Database connection, pooling, schema setup
├── extract.py           # API extraction with validation and logging
├── transform.py         # Data cleaning, type conversion, feature engineering
├── load.py              # Batch UPSERT into PostgreSQL
├── etl_pipeline.py      # ETL orchestrator with APScheduler
├── analysis.py          # SQL-based analytics and aggregations
├── dashboard.py         # Streamlit live dashboard
├── requirements.txt     # Python dependencies
├── README.md            # This file
├── .gitignore           # Ignores venv, logs, raw_data, editor files
├── logs/                # ETL log files
└── raw_data/            # Raw JSON snapshots from API
```

---

## How to Run

### 1. Clone the repo

```bash
git clone https://github.com/shahzeb-227-khan/crypto-analytics.git
cd crypto-analytics
```

### 2. Create virtual environment

```bash
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # macOS/Linux
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run ETL once

```bash
python etl_pipeline.py --once
```

### 5. Run ETL on schedule (every 5 min)

```bash
python etl_pipeline.py --schedule
```

### 6. Launch dashboard

```bash
streamlit run dashboard.py
```

---

## Connect

- **LinkedIn:** [Shahzeb Alam](https://www.linkedin.com/in/shahzeb-alam-759b992a4/)
- **GitHub:** [shahzeb-227-khan](https://github.com/shahzeb-227-khan)

---

*Built during Coding Night — Saylani Mass IT Training Program — March 1, 2026*
