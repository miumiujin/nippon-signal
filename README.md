# Nippon Signal 🇯🇵→🇹🇼

**Detect emerging Japanese technology signals that may become opportunities in Taiwan.**

Nippon Signal is a lightweight technology-intelligence pipeline.

v0.1:

**Japanese tech RSS → normalization → deduplication → category tagging → Signal Score → dashboard**

The first version deliberately starts without an LLM. This gives us a measurable baseline before adding embeddings, clustering, Taiwan-gap analysis, and AI-generated opportunity cards.

## What v0.1 does

- Collects articles from Japanese technology RSS feeds
- Normalizes title, URL, summary, source and publish time
- Deduplicates by canonical URL / stable fingerprint
- Tags articles into AI, Robotics, Semiconductor, Energy, Mobility, XR, Consumer Tech, Gov/DX, Other
- Calculates a transparent **Signal Score (0–100)**
- Stores results in SQLite
- Shows ranked signals in a Streamlit dashboard

## Architecture

```text
Japanese RSS Sources
        │
        ▼
   Feed Collector
        │
        ▼
  Normalize / Clean
        │
        ▼
     Deduplicate
        │
        ▼
 Keyword Classifier
        │
        ▼
    Signal Scorer
        │
        ▼
      SQLite
        │
        ▼
 Streamlit Dashboard
```

## Quick start

Python 3.11+.

```bash
python -m venv .venv
```

macOS / Linux:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install:

```bash
pip install -e ".[dev]"
```

Initialize and fetch:

```bash
nippon-signal init-db
nippon-signal ingest
nippon-signal top --limit 20
```

Dashboard:

```bash
streamlit run app.py
```

## Signal Score v0.1

```text
Signal Score =
  Recency            max 35
+ Opportunity terms  max 30
+ Category relevance max 20
+ Source quality     max 15
```

This is deliberately **not** the Taiwan Opportunity Score yet.

Later versions will separate:

```text
Signal Strength
Japan Traction
Taiwan Presence
Novelty
Solo-builder Feasibility
Commercial Potential
```

## Data model

```text
source
title
url
summary
published_at
category
signal_score
fingerprint
created_at
```

Only metadata / short feed summaries are stored. Do not mirror full copyrighted articles.

## Seed sources

- ITmedia AI+
- ITmedia NEWS — Science / Technology
- MONOist — Robotics
- Smart Japan — Energy / industrial technology
- Mogura VR — XR / metaverse

Edit `config/sources.yaml` to add or disable sources.

## Roadmap

### v0.1 — Baseline
- [x] RSS ingestion
- [x] SQLite
- [x] Deduplication
- [x] Rule-based categories
- [x] Signal Score
- [x] Streamlit dashboard

### v0.2 — Semantic intelligence
- [ ] Japanese sentence embeddings
- [ ] Cross-source story clustering
- [ ] Entity extraction
- [ ] Topic trend velocity

### v0.3 — Taiwan Gap
- [ ] Taiwan-side source collector
- [ ] Japan vs Taiwan topic coverage
- [ ] Taiwan Presence Score
- [ ] Gap Score

### v0.4 — Opportunity Cards
- [ ] Structured LLM analysis
- [ ] Why now?
- [ ] Taiwan gap hypothesis
- [ ] Solo-builder MVP suggestion
- [ ] Evidence / citations

### v0.5 — Proprietary feedback loop
- [ ] Save / Ignore
- [ ] Ignore reason
- [ ] Human override
- [ ] Historical prediction evaluation

## Portfolio strategy

Keep GitHub issues / releases showing the reasoning:

- baseline assumptions
- scoring revisions
- evaluation datasets
- failed experiments
- ranking improvements
- human feedback

That makes this an AI/data-product engineering case study rather than a generic news app.

## License

MIT for project code. Source-site content remains subject to each publisher's terms.


## v0.1.1 UI refresh

This version upgrades the dashboard with:

- Japanese-inspired visual styling
- Better signal cards
- Traditional Chinese translation support
- Sidebar browsing controls

To use translation:

```bash
pip install -e ".[dev]"
```

Then run:

```bash
streamlit run app.py
```

If the translator service is temporarily unavailable, the app will still show the original Japanese title and summary.


## v0.1.2 — Deploy-ready UI

Changes:

- Fixed raw HTML accidentally appearing in the Streamlit page
- Source-aware primary category
- Multi-category tags
- Explainable Signal Score breakdown
- Free Japanese → Traditional Chinese best-effort translation
- Translation provider errors are hidden from end users
- Automatic database bootstrap when deployed without a local SQLite file
- Manual **Refresh 最新資料** button
- `requirements.txt` and `.streamlit/config.toml` for Streamlit Community Cloud

### Streamlit Community Cloud

Deploy settings:

```text
Repository: your-user/nippon-signal
Branch: main
Main file path: app.py
```

The SQLite database is intentionally not committed. On a fresh deployment,
the app attempts to ingest feeds and build the database at runtime.
