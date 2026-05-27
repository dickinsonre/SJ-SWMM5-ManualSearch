 
# SJ SWMM5 Manual Search

**A fast, local search engine for the EPA Storm Water Management Model (SWMM) 5.2 Manual documentation.**

Built by [Robert Dickinson](https://www.linkedin.com/in/robertdickinson/) — Data source: [Scott Jeffers' SWMM Manual Collection](https://swmm-manual.netlify.app/)

---

## What It Does

This app crawls the entire SWMM 5.2 Manual Collection — **5 separate manuals**, **53 chapters**, **621 sections**, and **248,000+ words** — and combines them into a single, instant-search interface. Instead of clicking through 5 different manual sidebars, engineers type a term and get results from everywhere in under a second.

---

## At a Glance

| Metric | Value |
|--------|-------|
| Chapters indexed | 53 |
| Sections indexed | 621 |
| Words indexed | 248,407 |
| INP file sections mapped | 43 |
| ICM field mappings | 294 across 10 groups |
| Version history entries | 41 versions (v5.0.001 – v5.2.4) |
| Engine updates tracked | 537 |
| GUI updates tracked | 246 |
| Glossary terms | 773 curated (705 core + 68 parameter) |
| Interactive diagrams | 31 |
| Calculators | 9 (with US/SI toggle) |
| INP templates | 18 hand-crafted + generic skeleton for all 621 sections |
| Engine integration | EPA SWMM 5.2.4 via `pyswmm` 2.1.0 (validate + run) |
| Total source code | ~9,800 lines |

---

## Source Manual Structure

The SWMM Manual Collection consists of 5 separate manuals published by the EPA. This app crawls all 5 and unifies them into one searchable index.

![Source Manual TOC Structure](static/toc-structure.png)

| Source Manual | App Chapters |
|---|---|
| **Users Manual** | Chapters 1–12, Appendices A–E, Glossary, Intro |
| **Ref Vol I — Hydrology** | Ch1-Overview, Ch2-Meteorology, Ch3-SurfaceRunoff, Ch4-Infiltration, Ch5-Groundwater, Ch6-Snowmelt, Ch7-RDII |
| **Ref Vol II — Hydraulics** | Ch1-PreissmannSlot, Ch2-HydraulicModel, Ch3-DynamicWave, Ch4-KinematicWave, Ch5-CrossSection, Ch6-PumpsRegulators, Ch7-AdvancedFeatures |
| **Ref Vol II Addendum** | Ch2-StreetCrossSections, Ch3-StorageUnitGeometry, Ch4-Pumps, Ch5-StormDrainInlets |
| **Ref Vol III — Water Quality/LID** | Ch2-UrbanRunoffQuality, Ch3-PollutantBuildup, Ch4-SurfaceWashoff, Ch5-TransportAndTreatment, Ch6-LowImpactDevelopmentControls |

---

## Features

### 1. Full-Text Search with Instant Results

- Type any SWMM topic — results appear instantly with highlighted snippets
- Comma-separated AND logic for multi-term searches (e.g., `infiltration, groundwater`)
- Chapter filter chips to scope searches to specific manuals
- Fuzzy/synonym matching with 70+ SWMM synonym mappings and typo tolerance
- Configurable result limits (20/50/100/200)
- Sort by relevance, chapter order, or alphabetical
- Export results to CSV
- Shareable URL links (`?q=conduits&chapter=...&results=50`)

### 2. INP File Reference Browser

A dedicated 1,157-line database (`inp_reference.py`) mapping every INP section, every field, every unit. When you search for a term that matches an INP section, a dual-pane view appears with the INP field specifications alongside the manual content.

**What's mapped:**
- All INP file sections (JUNCTIONS, CONDUITS, SUBCATCHMENTS, etc.)
- Field names, data types, units, and default values
- ICM InfoWorks Network equivalents for each section
- Import status badges (Full Import / Partial / Manual Transfer)

### 3. ICM Variable Mapping Cross-Reference

A complete SWMM5 ↔ ICM cross-reference system with Ruby scripting variables. Built from `icm_variable_mapping.py` (736 lines).

| Metric | Count |
|--------|-------|
| INP sections covered | 43 |
| Field mappings | 294 |
| Groups | 10 (Nodes, Links, Subcatchments, Climatology, Controls, LID, Map, System, Time-Dependent, Water Quality) |

**Each mapping shows:**
- SWMM field name
- InfoWorks ICM HW (Hydraulic Works) table and Ruby variable
- InfoWorks ICM SW (Stormwater) table and Ruby variable
- Conversion notes
- Import status (Full / Partial / Manual)

**5-color legend system** distinguishes SWMM fields, HW tables, HW Ruby variables, SW tables, and SW Ruby variables.

Features: bidirectional search (SWMM fields ↔ Ruby variables), group filter chips, CSV export, cross-linked from INP Reference.

### 4. Version History (EPA Updates)

Complete SWMM5 update history parsed from the official EPA `epaswmm5_updates.txt` file.

- **41 versions** from v5.0.001 to v5.2.4
- **537 engine updates** + **246 GUI updates**
- Collapsible version cards with Engine/GUI sections
- Version filter chips (5.2.x / 5.1.x / 5.0.x)
- Full-text search across all updates
- Color-coded major version badges (green = 5.2, blue = 5.1, yellow = 5.0)
- **Glossary term highlighting** — recognized SWMM terms are highlighted in yellow and clickable to search
- **Integrated with main search** — when you search for a term, matching version history entries appear below the manual results

### 5. AI-Powered SWMM Assistant (Chat)

A floating chat assistant powered by Claude (Anthropic) via Replit AI Integrations.

![Chat Feature Overview](static/chat-features.png)

- RAG (Retrieval-Augmented Generation) — searches the top 8 manual sections for each question
- Streaming responses (word-by-word)
- Markdown rendering (bold, code, lists)
- 19-language support with auto-detection
- Suggestion chips for common questions
- Session memory — AI remembers conversation context
- Full dark/light mode support
- Mobile responsive (full-screen on mobile)

### 6. Table of Contents

Interactive browsable TOC covering all 53 documents and 621 sections. Click any section to search for it.

### 7. Glossary

Auto-extracted from bold terms in the manual content:

- **705 core concept** terms (highlighted blue)
- **68 parameter** terms (highlighted purple)
- Tier filter buttons (Curated / Core Concepts / All)
- Click any term to instantly search for it
- Alphabetical index with letter navigation

### 8. Equation Rendering

14 SWMM equations rendered as formatted math (KaTeX) when search queries match equation keywords:
Manning, Green-Ampt, Horton, Saint-Venant, and more.

### 9. Dark / Light Mode

Water-themed CSS variables for both themes. Toggle with the theme button. All components — search, INP browser, ICM mapping, version history, chat — fully support both modes.

### 10. Cross-App Deep Linking

Other SWMM tools can deep-link directly to manual search results:

```
https://your-domain/?q=CONDUITS
https://your-domain/?q=surcharge+junction&chapter=Chapter3&results=50
```

### 11. INP Model Builder + Live Simulation

Pick any of the 621 manual sections from the **INP Models** tab and the app auto-generates a runnable `.inp` file (18 hand-crafted templates for common section types; generic skeleton otherwise). Three toolbar actions:

- **✓ Validate** — opens the INP through the real EPA SWMM 5.2.4 engine via `pyswmm` (parse-only, no run). Reports "Valid INP (engine X ms)" or the engine's exact error string.
- **▶ Run Simulation** — runs the INP server-side, streams back the `.rpt` report.
- **.rpt analysis panel** — color-coded continuity verdict (ok ≤1%, fair ≤5%, poor ≤10%, bad >10%) plus parsed warnings/engine errors and guidance text.

Both endpoints are protected by 60 s/15 s timeouts, 500 KB / 500k-step caps, and a 2-concurrent-request semaphore with 429 backpressure.

### 12. INP Data Quality Checker

A dedicated tab for static analysis of any pasted INP. Backend `/api/inp-quality` flags:

- Duplicate IDs (junctions, conduits, subcatchments, etc.)
- Zero-length conduits, adverse slopes, Manning n out of range (0.001–0.5)
- Missing-node references on links
- Orphan junctions (not referenced by any link or subcatchment outlet)
- Missing TIMESERIES / CURVES / PATTERNS references (raingage, XSECTIONS CUSTOM, DWF, INFLOWS)
- Missing `[OPTIONS]`, no-outfall, area sanity

Issues are returned with severity (error / warning / info), code, message, and section name; the UI renders them as severity-color-coded cards with summary pills and per-section element counts.

### 13. Parameter Calculator Suite with SI Toggle

9 live calculators (Manning circular pipe, Rational Method, Green-Ampt, SCS CN, RTK RDII peak, Orifice, Weir, Normal Depth, Critical Depth) with US/SI toggle at the top. SI mode appends italic metric conversions (m, m², m³/s, mm/hr, ha, etc.) next to each US value. Preference persists in localStorage.

### 14. Result Quality-of-Life Upgrades

- **Source-manual color coding** — each result card carries a 4 px left border and pill tag colored by source manual (Users blue, Hydrology green, Hydraulics orange, Quality purple, Applications pink, Glossary gray) so you can tell at a glance which manual a hit came from.
- **Per-chapter result counts** — chapter filter chips show "<N> hits / <total>" in primary color when the current query matches that chapter; no need to click in to find out which chapters are relevant.
- **Search-within-results** — a filter input below the summary bar narrows currently-shown cards via client-side text match with live "X/Y shown" count. No new request, no flicker.
- **Field-range tooltips** — 33 SWMM field range hints (Manning 0.011–0.035, Horton f0 1–10 in/hr, CN 30–98, Green-Ampt Ksat tiers, orifice Cd 0.6–0.65, etc.) appear on hover over any field name in the INP Reference panel.
- **INP syntax highlighting** — all read-only `.inp` example blocks are tokenized: `[SECTION]` headers in blue, `;comments` in gray italic, numbers in green, reserved keywords (DYNWAVE/HORTON/CIRCULAR/…) in purple.

---

## Architecture

### Three-Stage Pipeline

```
┌──────────────┐     ┌──────────────┐     ┌──────────────────┐
│   CRAWLING   │────▶│   INDEXING   │────▶│     SERVING      │
│  httpx +     │     │  Whoosh      │     │  FastAPI +       │
│  BeautifulSoup│     │  full-text   │     │  Jinja2 +        │
│              │     │  stemming    │     │  vanilla JS       │
└──────────────┘     └──────────────┘     └──────────────────┘
```

1. **Crawling** — `crawler.py` (244 lines) uses httpx to scrape markdown files from swmm-manual.netlify.app
2. **Indexing** — `indexer.py` (45 lines) builds a Whoosh full-text search index with stemming analysis
3. **Serving** — `app.py` (1,476 lines) is a FastAPI application with all API endpoints

### Key Files

| File | Lines | Purpose |
|------|-------|---------|
| `app.py` | 1,476 | FastAPI application — all API endpoints |
| `static/app.js` | 2,347 | Frontend JavaScript — search, tabs, all interactive features |
| `templates/index.html` | 3,103 | Main Jinja2 template with CSS variables for theming |
| `inp_reference.py` | 1,157 | Complete INP file section database with field specs |
| `icm_variable_mapping.py` | 736 | SWMM ↔ ICM cross-reference with Ruby variables |
| `crawler.py` | 244 | HTTP-based crawler for the SWMM Manual Collection |
| `indexer.py` | 45 | Whoosh index builder from JSONL documents |
| `main.py` | 6 | Uvicorn server entry point (port 5000) |
| `data/docs.jsonl` | — | 621 document sections from 53 documents (248K+ words) |
| `data/swmm_version_history.json` | — | 41 versions parsed from EPA epaswmm5_updates.txt |

### Data Storage

- **JSONL format** — crawled documents stored as line-delimited JSON
- **Whoosh index** — fast search with stemming analysis
- **File-based** — no database dependency

---

## API Endpoints

### Internal (Frontend)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main page (accepts `?q=`, `?results=`, `?chapter=`) |
| `/search` | GET | Search with chapter filter, returns results + related + INP refs |
| `/stats` | GET | Index statistics |
| `/chapters` | GET | Chapter list for filter dropdown |
| `/featured-search` | GET | Daily rotating featured search (20 curated queries) |
| `/toc` | GET | Interactive table of contents |
| `/glossary` | GET | Auto-extracted glossary with tier system |
| `/glossary-terms` | GET | Glossary term names for highlighting |
| `/swmm-updates` | GET | Version history (filterable by version and search) |
| `/icm-mapping` | GET | ICM variable mapping cross-reference |
| `/chat` | POST | AI assistant (Claude via RAG) |
| `/api/validate-inp` | POST | Parse INP through SWMM5 engine (open-only, 15 s timeout, 2-concurrent) |
| `/api/run-inp` | POST | Run full simulation, return `.rpt` + continuity analysis (60 s timeout) |
| `/api/inp-quality` | POST | Static INP analyzer — duplicate IDs, orphan refs, missing patterns/timeseries |
| `/reindex` | POST | Trigger re-crawl and re-index |

### Public API v1 (for other SWMM tools)

| Endpoint | Description |
|----------|-------------|
| `GET /api/v1` | Self-documenting overview with examples |
| `GET /api/v1/search?q=&limit=&offset=&fields=` | Full-text search with pagination |
| `GET /api/v1/lookup?title=&section=` | Retrieve specific section by title |
| `GET /api/v1/chapters` | List all chapters with section/word counts |
| `GET /api/v1/stats` | Index statistics |
| `GET /api/v1/inp?q=` | INP file reference lookup |
| `GET /api/v1/health` | Health check |

All API responses include `"ok": true/false`. Supports pagination via `offset`/`limit` and field selection via `fields` parameter.

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Web framework | FastAPI 0.115.0 |
| Server | Uvicorn 0.30.6 |
| Search engine | Whoosh 2.7.4 (full-text with stemming) |
| HTTP client | httpx 0.27.2 (HTTP/2) |
| HTML parsing | BeautifulSoup4 4.12.3 |
| Templating | Jinja2 3.1.4 |
| AI | Claude (Anthropic) via Replit AI Integrations |
| Math rendering | KaTeX (CDN) |
| Frontend | Vanilla JavaScript, CSS custom properties |
| Offline support | Service Worker with app shell caching |

---

## Offline Support

A service worker caches the app shell and search data for offline use. When the network is unavailable, the app falls back to cached search results with an "offline" badge.

---

## Getting Started

The app auto-builds its search index on first launch by crawling the SWMM Manual Collection. After that, searches are instant against the local Whoosh index.

1. Start the server: `python main.py`
2. Open the app at `http://localhost:5000`
3. Type any SWMM topic in the search bar
4. Use tabs to explore: Table of Contents, INP Reference, Glossary, ICM Mapping, Version History

To rebuild the index from scratch, click the refresh button or call `POST /reindex`.

---

## Credits

- **App created by:** [Robert Dickinson](https://www.linkedin.com/in/robertdickinson/)
- **SWMM Manual Collection by:** [Scott Jeffers, PE, PhD](https://www.linkedin.com/in/scott-jeffers-pe-phd-a7638717/)
- **SWMM developed by:** U.S. Environmental Protection Agency (EPA)
