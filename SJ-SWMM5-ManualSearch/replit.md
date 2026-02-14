# Overview

SWMM5 Manual Search - A fast, local search engine for the SWMM (Storm Water Management Model) 5.2 Manual documentation. The application crawls the SWMM Manual website, builds a full-text search index, and provides an instant search interface with dual-pane INP file cross-referencing, interactive table of contents, auto-extracted glossary, related concept discovery, featured daily searches, dark mode with water-themed styling, chapter-filtered searching, and cross-app deep linking support.

# Recent Changes

- **Feb 14, 2026**: Added in-app presentation viewer (/presentation) with 12 slides converted from PPTX, keyboard/swipe navigation, progress bar, download option. Added PowerPoint presentation download to intro page, SearchEnhancer class with combined history+autocomplete suggestions, results summary bar with sort/export/share, improved highlightMatches with phrase/AND/OR support, extractSmartSnippet with sentence-aware context, XSS fixes (DOM-based rendering, no inline handlers), handleUrlParams race condition fix
- **Feb 14, 2026**: Complete UI redesign — search moved into gradient header, chapter filtering via dynamic chips instead of dropdown, result cards with rounded corners/chapter labels/meta rows, simplified footer with stats, cleaner color scheme (#2563eb primary), result limit selector in filter bar
- **Feb 14, 2026**: Added autocomplete suggestions for 80+ SWMM terms, export results to CSV/PDF, advanced search options panel (scope filter, result type checkboxes, alphabetical sort), SWMM version selector (5.2/5.1/5.0), INP syntax blocks with copy buttons, improved TOC/Glossary loading states, clarified source link attribution
- **Feb 14, 2026**: Welcome popup restorable via "Welcome" button + interactive 6-step guided tutorial with spotlight highlighting, step-by-step navigation, keyboard/click controls
- **Feb 8, 2026**: Animated intro walkthrough (/intro) — 8-slide auto-playing captioned presentation with water-themed dark styling, INP cross-reference demo, typing animation, touch/keyboard navigation, and "Skip to App" option
- **Feb 8, 2026**: Public API v1 (/api/v1/) for programmatic access - search, lookup, chapters, stats, INP reference, health endpoints with pagination, field selection, and self-documenting overview
- **Feb 8, 2026**: UX enhancements - search syntax help tooltip, recent searches (localStorage), graceful empty states, breadcrumb paths in results, "Showing X of Y" result count, grouped chapter filter (optgroups), search term highlighting, keyboard shortcuts (/ and Ctrl+K), mobile responsive layout
- **Feb 8, 2026**: Major frontend rebuild - search-first layout with stats bar, example query chips, chapter filter dropdown, dual-pane INP reference panel, "View in manual" deep links, "Copy passage" buttons, source preview on demand, Scott Jeffers citation in footer, URL query parameter support for cross-app linking
- **Feb 8, 2026**: Added backend endpoints: /stats, /chapters, chapter-filtered search, search timing, total result count
- **Feb 7, 2026**: Added INP reference database (inp_reference.py), related concepts, featured search, TOC, glossary, dark mode

# User Preferences

- Preferred communication style: Simple, everyday language
- Attribution: Robert Dickinson (App creator) - LinkedIn: https://www.linkedin.com/in/robertdickinson/
- Attribution: Scott Jeffers, PE, PhD - LinkedIn: https://www.linkedin.com/in/scott-jeffers-pe-phd-a7638717/
- Domain: SJ_SWMM5_ManualSearch

# System Architecture

## Application Structure
The system follows a three-stage pipeline architecture:
1. **Crawling** - Web scraping with httpx for markdown files from SWMM Manual Collection
2. **Indexing** - Full-text search index creation using Whoosh with stemming analysis
3. **Serving** - FastAPI web application with search API, INP cross-references, and rich UI

## Key Files
- **app.py** - FastAPI application with all API endpoints
- **main.py** - Uvicorn server entry point (port 5000)
- **crawler.py** - HTTP-based crawler for swmm-manual.netlify.app
- **indexer.py** - Whoosh index builder from JSONL docs
- **inp_reference.py** - Complete INP file section database with field specs
- **templates/index.html** - Main Jinja2 template with CSS variables for dark/light themes
- **static/app.js** - Frontend JavaScript for search, TOC, glossary, INP panel, deep linking
- **data/docs.jsonl** - 631 document sections from 53 documents (251K+ words)

## Internal Endpoints (Frontend)
- `GET /` - Main page (accepts ?q=&results=&chapter= for deep linking)
- `GET /search?q=&limit=&chapter=` - Search with chapter filter, returns results + related + INP refs + timing
- `GET /stats` - Index statistics (chapters, sections, words, version)
- `GET /chapters` - Chapter list for filter dropdown
- `GET /featured-search` - Daily rotating featured search (20 curated queries)
- `GET /toc` - Interactive table of contents
- `GET /glossary` - Auto-extracted glossary from bold terms and section headings
- `POST /reindex` - Trigger re-crawl and re-index
- `GET /indexing-progress` - SSE stream for indexing progress
- `GET /live-screenshot` - Live screenshot of source website
- `GET /source` - View application source code
- `GET /healthz` - Health check

## Public API (v1) — for other SWMM tools
- `GET /api/v1` - Self-documenting API overview with examples
- `GET /api/v1/search?q=&limit=&chapter=&offset=&fields=` - Full-text search with pagination, field selection (all/minimal/urls)
- `GET /api/v1/lookup?title=&section=` - Retrieve specific section content by title/section name
- `GET /api/v1/chapters` - List all chapters with sections and word counts
- `GET /api/v1/stats` - Index statistics
- `GET /api/v1/inp?q=` - INP file reference lookup
- `GET /api/v1/health` - Health check
- All responses include `"ok": true/false` top-level field
- Supports pagination via offset/limit, field selection via fields param

## Frontend Features
- Search-first layout with prominent search box
- Stats bar showing 53 chapters, 631 sections, 251K+ words
- 6 clickable example query chips
- Chapter filter dropdown for scoped searching
- Comma-separated AND logic for multi-term search
- Configurable result limits (20/50/100/200)
- Dual-pane INP file cross-reference panel (appears when INP sections match query)
- "View in manual" deep links on each result
- "Copy passage" clipboard functionality
- Related concepts discovery via concept map
- Featured search of the day (rotating through 20 curated queries)
- Interactive Table of Contents (53 docs, 631 sections)
- Auto-extracted glossary browser
- Dark/light mode with water-themed CSS variables
- URL query parameter support (?q=&results=&chapter=) for cross-app linking
- Source website preview on demand
- Scott Jeffers attribution in footer

## Cross-App Linking
URL pattern: `/?q=CONDUITS` or `/?q=surcharge+junction&chapter=...&results=50`
Other apps can deep-link to manual search for contextual knowledge.

## Data Storage
- **JSONL format** stores crawled documents as line-delimited JSON
- **Whoosh index** provides fast search with stemming analysis
- File-based storage, no database dependency

# External Dependencies

## Core Web Framework
- **FastAPI 0.115.0** - Web framework with automatic API docs
- **Uvicorn 0.30.6** - ASGI server

## Search Engine
- **Whoosh 2.7.4** - Full-text search with stemming and highlighting

## Web Scraping
- **httpx 0.27.2** - HTTP client with HTTP/2 support
- **BeautifulSoup4 4.12.3** - HTML parsing

## Templating
- **Jinja2 3.1.4** - Template engine

## Target Website
- **SWMM Manual** (https://swmm-manual.netlify.app/) - Source documentation site