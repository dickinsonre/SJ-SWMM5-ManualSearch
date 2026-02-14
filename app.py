from fastapi import FastAPI, Query, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import httpx
from whoosh import index
from whoosh.qparser import MultifieldParser, OrGroup
from whoosh.highlight import ContextFragmenter, UppercaseFormatter
from whoosh.query import Every

from pathlib import Path
import subprocess
import asyncio
import json
import time
import queue
import threading
import re
import hashlib
from datetime import date
from collections import defaultdict, Counter
from inp_reference import find_matching_inp_sections

INDEX_DIR = Path("index")
DOCS_PATH = Path("data/docs.jsonl")

FEATURED_SEARCHES = [
    "LID controls",
    "dynamic wave routing",
    "infiltration",
    "Manning roughness",
    "subcatchment",
    "Green-Ampt",
    "runoff coefficient",
    "Horton equation",
    "storm sewer",
    "rainfall hyetograph",
    "detention pond",
    "water quality",
    "pollutant buildup",
    "groundwater",
    "snowmelt",
    "pump station",
    "flow routing",
    "Curve Number",
    "hydraulic grade line",
    "bioretention",
]

CONCEPT_MAP = {
    "infiltration": ["percolation", "groundwater", "soil moisture", "losses", "Green-Ampt", "Horton", "Curve Number"],
    "runoff": ["rainfall", "impervious", "subcatchment", "overland flow", "hydrograph", "peak flow"],
    "routing": ["dynamic wave", "kinematic wave", "conduit", "flow", "Saint-Venant", "hydraulic"],
    "LID": ["bioretention", "rain garden", "permeable pavement", "green roof", "swale", "low impact"],
    "conduit": ["pipe", "Manning", "roughness", "cross section", "diameter", "slope"],
    "pump": ["pump curve", "pump station", "wet well", "force main", "lift station"],
    "pollutant": ["buildup", "washoff", "water quality", "concentration", "treatment", "EMC"],
    "groundwater": ["aquifer", "infiltration", "percolation", "water table", "baseflow", "lateral flow"],
    "subcatchment": ["area", "width", "slope", "impervious", "pervious", "runoff", "outlet"],
    "flooding": ["surcharge", "ponding", "overflow", "depth", "volume", "node"],
    "rainfall": ["hyetograph", "rain gage", "time series", "intensity", "duration", "frequency"],
    "snowmelt": ["snow pack", "cold content", "melt coefficient", "temperature", "plowing"],
    "detention": ["storage", "pond", "outflow", "stage", "volume", "weir", "orifice"],
    "calibration": ["validation", "sensitivity", "parameters", "observed", "simulated", "error"],
    "weir": ["orifice", "outlet", "transverse", "side flow", "V-notch", "trapezoidal"],
    "junction": ["node", "manhole", "invert", "surcharge", "inflow", "depth"],
    "treatment": ["removal", "pollutant", "BMP", "concentration", "effluent"],
    "hydraulic": ["head", "pressure", "velocity", "energy", "friction", "losses"],
}

def get_todays_search():
    day_index = date.today().toordinal() % len(FEATURED_SEARCHES)
    return FEATURED_SEARCHES[day_index]

# Global queue for streaming indexing progress
progress_queue = queue.Queue()

app = FastAPI(title="SWMM5 Manual Search - Local search for swmm-manual.netlify.app")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def have_index() -> bool:
    try:
        return index.exists_in(INDEX_DIR)
    except Exception:
        return False

import re as _re

_SENT_END_RE = _re.compile(r'[.!?](?:\s|\n|$)')
_SENT_BOUNDARY_RE = _re.compile(r'[.!?](?:\s+|\n+)')


def _snap_to_sentence(snippet: str) -> str:
    snippet = snippet.strip()
    if not snippet:
        return snippet

    needs_left_ellipsis = False
    if snippet and snippet[0].islower():
        first_space = snippet.find(' ')
        if 0 < first_space < 30:
            snippet = snippet[first_space:].lstrip()
            needs_left_ellipsis = True

    m_end = None
    for m in _SENT_END_RE.finditer(snippet):
        if m.start() > len(snippet) * 0.4:
            m_end = m
    if m_end:
        snippet = snippet[:m_end.end()].rstrip()
    else:
        last_space = snippet.rfind(' ')
        if last_space > len(snippet) * 0.7:
            snippet = snippet[:last_space] + '...'
        elif not snippet.endswith(('.', '!', '?')):
            snippet = snippet.rstrip() + '...'

    if needs_left_ellipsis and not snippet.startswith('...'):
        snippet = '...' + snippet

    return snippet


def _extract_sentence_snippet(content: str, match_pos: int, max_chars: int = 350) -> str:
    search_start = max(0, match_pos - 120)
    best_start = search_start
    for m in _SENT_BOUNDARY_RE.finditer(content[search_start:match_pos]):
        candidate = search_start + m.end()
        if candidate <= match_pos:
            best_start = candidate

    newline_pos = content.rfind('\n', search_start, match_pos)
    if newline_pos >= 0 and newline_pos + 1 > best_start:
        best_start = newline_pos + 1

    raw = content[best_start:best_start + max_chars]

    last_sent_end = None
    for m in _SENT_BOUNDARY_RE.finditer(raw):
        if m.start() > len(raw) * 0.4:
            last_sent_end = m

    if last_sent_end:
        raw = raw[:last_sent_end.end()].rstrip()
    else:
        newline_end = raw.rfind('\n')
        if newline_end > len(raw) * 0.5:
            raw = raw[:newline_end].rstrip()
        else:
            last_space = raw.rfind(' ')
            if last_space > len(raw) * 0.7:
                raw = raw[:last_space] + '...'

    if best_start > 0:
        raw = '...' + raw.lstrip()

    return raw

def search_whoosh(q: str, limit: int = 20, chapter: str = ""):
    from whoosh.query import And, Term
    ix = index.open_dir(INDEX_DIR)
    with ix.searcher() as s:
        if not q.strip():
            query = Every()
        else:
            terms = [term.strip() for term in q.split(',') if term.strip()]
            
            if len(terms) == 1:
                parser = MultifieldParser(["title","section","content"], schema=ix.schema, group=OrGroup)
                query = parser.parse(terms[0])
            else:
                queries = []
                parser = MultifieldParser(["title","section","content"], schema=ix.schema, group=OrGroup)
                
                for term in terms:
                    try:
                        parsed_query = parser.parse(term)
                        queries.append(parsed_query)
                    except:
                        continue
                
                if queries:
                    query = And(queries)
                else:
                    query = Every()
        
        if chapter and chapter.strip():
            from whoosh.qparser import QueryParser
            from whoosh.query import Or
            ch_parts = [c.strip() for c in chapter.split('|') if c.strip()]
            if len(ch_parts) == 1:
                ch_parser = QueryParser("title", schema=ix.schema)
                ch_query = ch_parser.parse(f'"{ch_parts[0]}"')
                query = And([query, ch_query])
            elif len(ch_parts) > 1:
                ch_parser = QueryParser("title", schema=ix.schema)
                ch_queries = []
                for cp in ch_parts:
                    try:
                        ch_queries.append(ch_parser.parse(f'"{cp}"'))
                    except:
                        continue
                if ch_queries:
                    query = And([query, Or(ch_queries)])
        
        results = s.search(query, limit=limit)
        total = results.estimated_length()
        results.fragmenter = ContextFragmenter(maxchars=350, surround=100)
        results.formatter = UppercaseFormatter()

        payload = []
        for hit in results:
            content = hit.get("content", "")
            snippet = hit.highlights("content") or hit.highlights("title") or hit.highlights("section") or ""
            if snippet:
                snippet = _snap_to_sentence(snippet)
            if not snippet and content:
                q_terms = [t.strip().lower() for t in q.split(',') if t.strip()]
                all_words = []
                for t in q_terms:
                    all_words.extend(t.split())
                best_pos = -1
                for w in all_words:
                    pos = content.lower().find(w)
                    if pos >= 0:
                        best_pos = pos
                        break
                if best_pos >= 0:
                    snippet = _extract_sentence_snippet(content, best_pos, max_chars=350)
                else:
                    snippet = _extract_sentence_snippet(content, 0, max_chars=300)
            payload.append({
                "url": hit["url"],
                "title": hit.get("title", ""),
                "section": hit.get("section", ""),
                "snippet": snippet,
                "chapter_order": hit.docnum
            })
        return payload, total

@app.get("/intro")
async def intro(request: Request):
    return templates.TemplateResponse("intro.html", {"request": request})

@app.get("/presentation")
async def presentation(request: Request):
    import glob
    slide_count = len(glob.glob("static/slides/slide-*.png"))
    return templates.TemplateResponse("presentation.html", {"request": request, "slide_count": slide_count})

@app.get("/")
async def home(request: Request, q: str = "", results: int = 20, chapter: str = ""):
    accept_header = request.headers.get("accept", "")
    user_agent = request.headers.get("user-agent", "")
    
    if ("application/json" in accept_header or 
        "health" in user_agent.lower() or
        "probe" in user_agent.lower() or
        "monitor" in user_agent.lower() or
        "check" in user_agent.lower()):
        return {"status": "ok", "service": "SWMM Search", "index": have_index()}
    
    return templates.TemplateResponse("index.html", {"request": request, "ready": have_index()})

@app.get("/search")
async def search(q: str = Query("", min_length=0, max_length=200), limit: int = 20, chapter: str = Query("", max_length=200)):
    if not have_index():
        return JSONResponse({"error": "index_missing"})
    t0 = time.time()
    results, total = search_whoosh(q, limit, chapter)
    elapsed = round(time.time() - t0, 3)
    related = get_related_concepts(q)
    inp_refs = find_matching_inp_sections(q)
    return {"results": results, "total": total, "related": related, "inp_references": inp_refs, "elapsed": elapsed}

@app.get("/stats")
async def stats():
    if not have_index():
        return JSONResponse({"error": "index_missing"})
    ix = index.open_dir(INDEX_DIR)
    doc_count = ix.doc_count()
    chapters = set()
    total_words = 0
    if DOCS_PATH.exists():
        with open(DOCS_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                d = json.loads(line)
                chapters.add(d.get("title", ""))
                total_words += len(d.get("content", "").split())
    import os
    idx_time = None
    if DOCS_PATH.exists():
        idx_time = os.path.getmtime(DOCS_PATH)
    return {
        "chapters": len(chapters),
        "sections": doc_count,
        "words": total_words,
        "indexed_at": idx_time,
        "version": "5.2",
    }

@app.get("/chapters")
async def chapters():
    if not DOCS_PATH.exists():
        return JSONResponse({"error": "no_data"})
    ch = {}
    with open(DOCS_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            d = json.loads(line)
            title = d.get("title", "Unknown")
            if title not in ch:
                ch[title] = 0
            ch[title] += 1
    result = [{"title": t, "sections": c} for t, c in sorted(ch.items())]
    return {"chapters": result}

@app.get("/featured-search")
async def featured_search():
    if not have_index():
        return JSONResponse({"error": "index_missing"})
    query = get_todays_search()
    results, total = search_whoosh(query, 5)
    return {"query": query, "results": results, "total": total, "total_available": len(FEATURED_SEARCHES)}

@app.get("/toc")
async def table_of_contents():
    if not DOCS_PATH.exists():
        return JSONResponse({"error": "no_data"})
    toc: dict[str, dict] = {}
    with open(DOCS_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            d = json.loads(line)
            title = d.get("title", "Unknown")
            section = d.get("section", "")
            content = d.get("content", "")
            words = len(content.split())
            if title not in toc:
                toc[title] = {"sections": [], "word_count": 0}
            toc[title]["sections"].append(section)
            toc[title]["word_count"] += words
    result = []
    for title in sorted(toc.keys()):
        info = toc[title]
        sections_list = info["sections"]
        result.append({
            "title": title,
            "section_count": len(sections_list),
            "word_count": info["word_count"],
            "sections": sections_list
        })
    return {"toc": result, "total_documents": sum(t["section_count"] for t in result)}

@app.get("/glossary")
async def glossary():
    if not DOCS_PATH.exists():
        return JSONResponse({"error": "no_data"})
    term_locations = defaultdict(list)
    bold_pattern = re.compile(r'\*\*([A-Z][A-Za-z\s\-/()]{2,40})\*\*')
    with open(DOCS_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            d = json.loads(line)
            content = d.get("content", "")
            matches = bold_pattern.findall(content)
            for match in matches:
                term = match.strip()
                if len(term) > 2 and not term.isupper():
                    term_locations[term].append({
                        "title": d.get("title", ""),
                        "section": d.get("section", ""),
                    })
    heading_pattern = re.compile(r'^#{1,3}\s+(.+)', re.MULTILINE)
    with open(DOCS_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            d = json.loads(line)
            section = d.get("section", "")
            if section and len(section) > 2:
                clean = re.sub(r'^\d+[\.\d]*\s*', '', section).strip()
                if clean and not clean.startswith("CHAPTER"):
                    if clean not in term_locations:
                        term_locations[clean] = []
                    term_locations[clean].append({
                        "title": d.get("title", ""),
                        "section": section,
                    })
    glossary_by_letter = defaultdict(list)
    for term in sorted(term_locations.keys(), key=str.lower):
        first_letter = term[0].upper()
        if first_letter.isalpha():
            unique_locs = []
            seen = set()
            for loc in term_locations[term]:
                key = f"{loc['title']}|{loc['section']}"
                if key not in seen:
                    seen.add(key)
                    unique_locs.append(loc)
            glossary_by_letter[first_letter].append({
                "term": term,
                "count": len(unique_locs),
                "locations": unique_locs[:5]
            })
    return {
        "glossary": dict(sorted(glossary_by_letter.items())),
        "total_terms": sum(len(v) for v in glossary_by_letter.values())
    }

def get_related_concepts(query: str) -> list:
    if not query or not query.strip():
        return []
    q_lower = query.lower()
    related = []
    for concept, neighbors in CONCEPT_MAP.items():
        if concept.lower() in q_lower or q_lower in concept.lower():
            for neighbor in neighbors:
                if neighbor.lower() not in q_lower:
                    related.append(neighbor)
        else:
            for neighbor in neighbors:
                if neighbor.lower() in q_lower or q_lower in neighbor.lower():
                    related.append(concept)
                    for n2 in neighbors:
                        if n2.lower() not in q_lower and n2 != neighbor:
                            related.append(n2)
                    break
    seen = set()
    unique = []
    for r in related:
        if r.lower() not in seen:
            seen.add(r.lower())
            unique.append(r)
    return unique[:8]

def run_indexing_with_progress():
    """Run indexing and capture output for streaming"""
    try:
        # Clear the queue
        while not progress_queue.empty():
            progress_queue.get()
        
        progress_queue.put("STATUS: Starting crawling process...")
        
        # Run crawler and capture output
        crawler_process = subprocess.Popen(
            ["python", "crawler.py"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            text=True, 
            bufsize=1
        )
        
        if crawler_process.stdout:
            for line in crawler_process.stdout:
                line = line.strip()
                if line:
                    progress_queue.put(line)
        
        crawler_process.wait()
        
        progress_queue.put("STATUS: Crawling complete, building search index...")
        
        # Run indexer and capture output
        indexer_process = subprocess.Popen(
            ["python", "indexer.py"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            text=True, 
            bufsize=1
        )
        
        if indexer_process.stdout:
            for line in indexer_process.stdout:
                line = line.strip()
                if line:
                    progress_queue.put(line)
        
        indexer_process.wait()
        
        progress_queue.put("STATUS: Indexing complete!")
        
    except Exception as e:
        progress_queue.put(f"ERROR: {str(e)}")

@app.post("/reindex")
async def reindex():
    # Start indexing in background thread
    thread = threading.Thread(target=run_indexing_with_progress)
    thread.daemon = True
    thread.start()
    return {"status": "started"}

@app.get("/indexing-progress")
async def indexing_progress():
    """Stream indexing progress via Server-Sent Events"""
    def event_stream():
        while True:
            try:
                # Get message from queue with timeout
                message = progress_queue.get(timeout=1)
                yield f"data: {json.dumps({'message': message})}\n\n"
                
                # If this is the completion message, end the stream
                if message.startswith("STATUS: Indexing complete"):
                    break
                    
            except queue.Empty:
                # Send heartbeat to keep connection alive
                yield f"data: {json.dumps({'heartbeat': True})}\n\n"
            except Exception:
                break
    
    return StreamingResponse(
        event_stream(), 
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

@app.get("/live-screenshot")
async def live_screenshot():
    """Capture a live screenshot of the SWMM manual website"""
    try:
        # Using screenshotapi.net - free tier available
        screenshot_url = "https://shot.screenshotapi.net/screenshot"
        params = {
            "url": "https://swmm-manual.netlify.app/",
            "width": "1200",
            "height": "800",
            "output": "image",
            "file_type": "png",
            "wait_for_event": "load",
            "fresh": "true"  # Get a fresh screenshot, not cached
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(screenshot_url, params=params)
            
            if response.status_code == 200:
                return Response(
                    content=response.content,
                    media_type="image/png",
                    headers={
                        "Cache-Control": "public, max-age=300",  # Cache for 5 minutes
                        "Content-Type": "image/png"
                    }
                )
            else:
                # Fallback to static image if screenshot fails
                try:
                    with open("static/swmm-manual-collection.png", "rb") as f:
                        static_content = f.read()
                    return Response(
                        content=static_content,
                        media_type="image/png",
                        headers={"Content-Type": "image/png"}
                    )
                except:
                    return Response(
                        content=b"",
                        status_code=404
                    )
    except Exception:
        # Fallback to static image on any error
        try:
            with open("static/swmm-manual-collection.png", "rb") as f:
                static_content = f.read()
            return Response(
                content=static_content,
                media_type="image/png",
                headers={"Content-Type": "image/png"}
            )
        except:
            return Response(
                content=b"",
                status_code=404
            )

@app.get("/sw.js")
async def service_worker():
    sw_path = Path("static/sw.js")
    if sw_path.exists():
        return Response(
            content=sw_path.read_text(),
            media_type="application/javascript",
            headers={"Service-Worker-Allowed": "/", "Cache-Control": "no-cache"}
        )
    return Response(status_code=404)

@app.get("/offline-docs")
async def offline_docs():
    if not DOCS_PATH.exists():
        return JSONResponse({"error": "no_data"}, status_code=503)
    docs = []
    with open(DOCS_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            d = json.loads(line)
            docs.append({
                "t": d.get("title", ""),
                "s": d.get("section", ""),
                "u": d.get("url", ""),
                "c": d.get("content", "")[:500],
            })
    return JSONResponse(
        {"docs": docs, "count": len(docs)},
        headers={"Cache-Control": "public, max-age=86400"}
    )

@app.get("/healthz")
async def health():
    return {"status": "ok", "index": have_index()}

API_VERSION = "1.0"
API_BASE = "/api/v1"

@app.get(f"{API_BASE}")
async def api_docs(request: Request):
    host = request.headers.get("host", "localhost:5000")
    scheme = request.headers.get("x-forwarded-proto", "https")
    base = f"{scheme}://{host}{API_BASE}"
    return {
        "ok": True,
        "name": "SWMM5 Manual Search API",
        "version": API_VERSION,
        "description": "Programmatic access to the EPA SWMM 5.2 Manual full-text search index. "
                       "Built from Scott Jeffers' web-based SWMM Manual Collection (swmm-manual.netlify.app).",
        "endpoints": {
            "GET /api/v1": "This documentation page",
            "GET /api/v1/search": "Full-text search across all manual sections",
            "GET /api/v1/lookup": "Retrieve a specific section by title and section name",
            "GET /api/v1/chapters": "List all chapters with section counts",
            "GET /api/v1/stats": "Index statistics (chapter count, word count, etc.)",
            "GET /api/v1/inp": "INP file reference lookup for a keyword",
            "GET /api/v1/health": "Health check",
        },
        "examples": {
            "search": f"{base}/search?q=Manning+roughness",
            "search_with_chapter": f"{base}/search?q=infiltration&chapter=Chapter4&limit=50",
            "search_phrase": f"{base}/search?q=%22dynamic+wave%22",
            "search_multi": f"{base}/search?q=pump,curve&limit=10",
            "lookup": f"{base}/lookup?title=SWMM+Manual+Chapter5-Hydraulics&section=5.1",
            "inp": f"{base}/inp?q=conduits",
            "chapters": f"{base}/chapters",
            "stats": f"{base}/stats",
        },
        "notes": {
            "search_syntax": "Use commas for AND logic. Wrap phrases in quotes. Use * for wildcards.",
            "rate_limits": "No rate limits currently enforced.",
            "response_format": "All responses are JSON with a top-level 'ok' boolean.",
            "deep_link": "Link users to the UI: /?q=SEARCH_TERM&chapter=CHAPTER&results=LIMIT",
        },
        "attribution": {
            "manual_source": "Scott Jeffers, PE, PhD - SWMM Manual Collection (swmm-manual.netlify.app)",
            "app_creator": "Robert Dickinson",
            "data": "EPA SWMM 5.2 User's Manual",
        }
    }

@app.get(f"{API_BASE}/search")
async def api_search(
    q: str = Query(..., min_length=1, max_length=200, description="Search query"),
    limit: int = Query(20, ge=1, le=500, description="Max results to return"),
    chapter: str = Query("", max_length=200, description="Filter by chapter title (partial match)"),
    offset: int = Query(0, ge=0, description="Skip first N results for pagination"),
    fields: str = Query("all", description="Fields to return: all, minimal, urls"),
):
    if fields not in ("all", "minimal", "urls"):
        return JSONResponse({"ok": False, "error": "invalid_fields", "message": "fields must be one of: all, minimal, urls"}, status_code=400)
    if not have_index():
        return JSONResponse({"ok": False, "error": "index_not_built", "message": "Search index has not been built yet."}, status_code=503)
    t0 = time.time()
    fetch_limit = limit + offset
    raw_results, total = search_whoosh(q, fetch_limit, chapter)
    elapsed = round(time.time() - t0, 3)
    paginated = raw_results[offset:]
    related = get_related_concepts(q)
    inp_refs = find_matching_inp_sections(q)

    if fields == "minimal":
        results_out = [{"title": r["title"], "section": r.get("section", ""), "url": r["url"]} for r in paginated]
    elif fields == "urls":
        results_out = [r["url"] for r in paginated]
    else:
        results_out = paginated

    return {
        "ok": True,
        "query": q,
        "total": total,
        "returned": len(results_out),
        "offset": offset,
        "limit": limit,
        "elapsed_seconds": elapsed,
        "results": results_out,
        "related_concepts": related,
        "inp_references": [{
            "section": ref["section"],
            "description": ref.get("description", ""),
            "fields": ref.get("fields", []),
        } for ref in inp_refs],
    }

@app.get(f"{API_BASE}/lookup")
async def api_lookup(
    title: str = Query(..., description="Document title (e.g. 'SWMM Manual Chapter5-Hydraulics')"),
    section: str = Query("", description="Section name to match (partial match)"),
):
    if not DOCS_PATH.exists():
        return JSONResponse({"ok": False, "error": "no_data"}, status_code=503)
    matches = []
    with open(DOCS_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            d = json.loads(line)
            if title.lower() in d.get("title", "").lower():
                if not section or section.lower() in d.get("section", "").lower():
                    matches.append({
                        "title": d.get("title", ""),
                        "section": d.get("section", ""),
                        "url": d.get("url", ""),
                        "content": d.get("content", "")[:2000],
                        "word_count": len(d.get("content", "").split()),
                    })
    return {"ok": True, "query": {"title": title, "section": section}, "total": len(matches), "results": matches}

@app.get(f"{API_BASE}/chapters")
async def api_chapters():
    if not DOCS_PATH.exists():
        return JSONResponse({"ok": False, "error": "no_data"}, status_code=503)
    ch = {}
    with open(DOCS_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            d = json.loads(line)
            title = d.get("title", "Unknown")
            if title not in ch:
                ch[title] = {"sections": [], "word_count": 0}
            ch[title]["sections"].append(d.get("section", ""))
            ch[title]["word_count"] += len(d.get("content", "").split())
    result = []
    for t in sorted(ch.keys()):
        result.append({
            "title": t,
            "section_count": len(ch[t]["sections"]),
            "word_count": ch[t]["word_count"],
            "sections": ch[t]["sections"],
        })
    return {"ok": True, "total_chapters": len(result), "chapters": result}

@app.get(f"{API_BASE}/stats")
async def api_stats():
    if not have_index():
        return JSONResponse({"ok": False, "error": "index_not_built"}, status_code=503)
    ix = index.open_dir(INDEX_DIR)
    doc_count = ix.doc_count()
    chapters = set()
    total_words = 0
    if DOCS_PATH.exists():
        with open(DOCS_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                d = json.loads(line)
                chapters.add(d.get("title", ""))
                total_words += len(d.get("content", "").split())
    import os
    idx_time = None
    if DOCS_PATH.exists():
        idx_time = os.path.getmtime(DOCS_PATH)
    return {
        "ok": True,
        "swmm_version": "5.2",
        "chapters": len(chapters),
        "sections": doc_count,
        "total_words": total_words,
        "indexed_at": idx_time,
        "api_version": API_VERSION,
    }

@app.get(f"{API_BASE}/inp")
async def api_inp(q: str = Query(..., min_length=1, max_length=100, description="Keyword to look up INP file sections")):
    if not have_index():
        return JSONResponse({"ok": False, "error": "index_not_built"}, status_code=503)
    refs = find_matching_inp_sections(q)
    results = []
    for ref in refs:
        entry = {
            "section": ref["section"],
            "description": ref.get("description", ""),
            "fields": ref.get("fields", []),
        }
        if ref.get("example"):
            entry["example"] = ref["example"]
        if ref.get("methods"):
            entry["methods"] = ref["methods"]
        if ref.get("layers"):
            entry["layers"] = ref["layers"]
        results.append(entry)
    return {"ok": True, "query": q, "total": len(results), "inp_sections": results}

@app.get(f"{API_BASE}/health")
async def api_health():
    idx = have_index()
    doc_count = 0
    if idx:
        try:
            ix = index.open_dir(INDEX_DIR)
            doc_count = ix.doc_count()
        except Exception:
            pass
    return {"ok": True, "index_ready": idx, "sections_indexed": doc_count}

@app.get("/docs-files")
async def docs_files():
    import os
    FILE_GROUPS = [
        {
            "group": "Core Application",
            "icon": "&#9881;",
            "files": [
                {"path": "app.py", "desc": "FastAPI web server, all API endpoints, search logic"},
                {"path": "main.py", "desc": "Uvicorn entry point (port 5000)"},
            ]
        },
        {
            "group": "Data Pipeline",
            "icon": "&#128269;",
            "files": [
                {"path": "crawler.py", "desc": "HTTP crawler for swmm-manual.netlify.app"},
                {"path": "indexer.py", "desc": "Whoosh full-text index builder from JSONL"},
                {"path": "inp_reference.py", "desc": "INP file section database with field specs"},
            ]
        },
        {
            "group": "Frontend",
            "icon": "&#127912;",
            "files": [
                {"path": "templates/index.html", "desc": "Main Jinja2 template with CSS + layout"},
                {"path": "static/app.js", "desc": "Frontend JavaScript — search, TOC, glossary, INP panel"},
                {"path": "templates/intro.html", "desc": "Animated intro walkthrough page"},
                {"path": "templates/presentation.html", "desc": "Slide presentation viewer"},
            ]
        },
        {
            "group": "Configuration",
            "icon": "&#128221;",
            "files": [
                {"path": "requirements.txt", "desc": "Python dependencies"},
                {"path": "replit.md", "desc": "Project documentation and architecture notes"},
            ]
        },
    ]
    result = []
    for grp in FILE_GROUPS:
        files = []
        for f in grp["files"]:
            try:
                stat = os.stat(f["path"])
                size = stat.st_size
                with open(f["path"], "r", encoding="utf-8", errors="replace") as fh:
                    lines = fh.readlines()
                content = "".join(lines)
                ext = f["path"].rsplit(".", 1)[-1] if "." in f["path"] else ""
                files.append({
                    "path": f["path"],
                    "desc": f["desc"],
                    "size": size,
                    "lines": len(lines),
                    "ext": ext,
                    "content": content,
                })
            except Exception:
                files.append({"path": f["path"], "desc": f["desc"], "size": 0, "lines": 0, "ext": "", "content": "# File not found"})
        result.append({"group": grp["group"], "icon": grp["icon"], "files": files})
    return {"ok": True, "groups": result}


@app.get("/source", response_class=HTMLResponse)
async def view_source(request: Request):
    source_files = ["app.py", "main.py", "crawler.py", "indexer.py", "utils.py", "requirements.txt"]
    file_contents = {}
    for filename in source_files:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                file_contents[filename] = f.read()
        except FileNotFoundError:
            file_contents[filename] = f"# {filename} not found"
    try:
        with open("templates/index.html", 'r', encoding='utf-8') as f:
            file_contents["templates/index.html"] = f.read()
    except FileNotFoundError:
        pass
    try:
        with open("static/app.js", 'r', encoding='utf-8') as f:
            file_contents["static/app.js"] = f.read()
    except FileNotFoundError:
        pass
    return templates.TemplateResponse("source.html", {
        "request": request,
        "files": file_contents,
        "title": "Source Code - SWMM5 Manual Search"
    })
