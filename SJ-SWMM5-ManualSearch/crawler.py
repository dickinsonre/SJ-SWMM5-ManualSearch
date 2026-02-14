import asyncio
import json
import os
from pathlib import Path
from typing import Iterable, Dict
from urllib.parse import urlparse, urljoin

import httpx
from bs4 import BeautifulSoup
from urllib.robotparser import RobotFileParser

from utils import normalize_url, pick_best_container, textify, SAME_HOST

BASE_URL = "https://swmm-manual.netlify.app/"
OUT_PATH = Path("data/docs.jsonl")
MAX_PAGES = int(os.getenv("MAX_PAGES", "250"))

# Global progress reporting
progress_callback = None

def set_progress_callback(callback):
    global progress_callback
    progress_callback = callback

def report_progress(message):
    if progress_callback:
        progress_callback(message)
    else:
        print(message)

def ensure_dirs():
    Path("data").mkdir(exist_ok=True)
    Path("index").mkdir(exist_ok=True)

async def fetch_robots_allowed(client: httpx.AsyncClient) -> RobotFileParser:
    rp = RobotFileParser()
    robots_url = "https://swmm-manual.netlify.app/robots.txt"
    try:
        r = await client.get(robots_url, timeout=20)
        rp.parse(r.text.splitlines())
    except Exception:
        rp.parse(["User-agent: *", "Allow: /"])
    return rp

def split_into_sections(url: str, title: str, container) -> Iterable[Dict]:
    """
    Split page into sub-docs by H2/H3 where possible.
    """
    # Collect sections
    docs = []
    current_title = title or ""
    current_parts = []

    def flush():
        text = textify(" ".join(current_parts))
        if text:
            docs.append({
                "url": url,
                "title": title or "",
                "section": current_title,
                "content": text
            })

    # If there are headers, split; else treat as one blob
    headers = container.select("h2, h3")
    if not headers:
        text = textify(container.get_text(" ", strip=True))
        if text:
            docs.append({"url": url, "title": title or "", "section": "", "content": text})
        return docs

    # Walk through elements
    for h in headers:
        if current_parts:
            flush()
            current_parts = []
        current_title = textify(h.get_text(" ", strip=True))
        # gather siblings until next header
        for sib in h.next_siblings:
            # Stop if next header
            if getattr(sib, "name", None) in {"h2", "h3"}:
                break
            if hasattr(sib, "get_text"):
                current_parts.append(sib.get_text(" ", strip=True))
    # flush tail
    if current_parts:
        flush()
    return docs

async def discover_markdown_files(client: httpx.AsyncClient) -> list:
    """Automatically discover markdown files from the main page"""
    try:
        response = await client.get(BASE_URL)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Find all elements with data-src attributes pointing to .md files
        md_files = []
        for element in soup.find_all(attrs={"data-src": True}):
            data_src = element.get("data-src")
            if data_src and data_src.endswith(".md"):
                md_files.append(data_src)
        
        if md_files:
            report_progress(f"STATUS: Discovered {len(md_files)} markdown files automatically")
            return md_files
        else:
            # Fallback to known files if discovery fails
            fallback_files = [
                "Manual/manual/Intro.md",
                "Manual/manual/Chapter1.md",
                "Manual/manual/Chapter2.md", 
                "Manual/manual/Chapter3.md",
                "Manual/manual/Chapter4.md",
                "Manual/manual/Chapter5.md",
                "Manual/manual/Chapter6.md",
                "Manual/manual/Chapter7.md",
                "Manual/manual/Chapter8.md",
                "Manual/manual/Chapter9.md",
                "Manual/manual/Chapter10.md",
                "Manual/manual/Chapter11.md",
                "Manual/manual/Chapter12.md",
                "Manual/manual/AppendixA.md",
                "Manual/manual/AppendixB.md",
                "Manual/manual/AppendixC.md",
                "Manual/manual/AppendixD.md",
                "Manual/manual/AppendixE.md",
                "VolumeI/sections/Disclaimer.md"
            ]
            report_progress("STATUS: Using fallback file list")
            return fallback_files
    except Exception as e:
        report_progress(f"FAILED: Could not discover files - {e}")
        return []

def slugify(text: str) -> str:
    """Convert text to URL-friendly slug like the SWMM site does"""
    import re
    # Remove special characters, convert to lowercase, replace spaces with hyphens
    slug = re.sub(r'[^\w\s-]', '', text).strip().lower()
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug

def process_markdown_content(markdown_text: str, title: str, base_url: str) -> list:
    """Process markdown content and split into sections"""
    docs = []
    lines = markdown_text.split('\n')
    current_section = ""
    current_content = []
    
    def flush_section():
        if current_content:
            content_text = textify('\n'.join(current_content))
            if content_text.strip():
                # Create proper URL with slugified anchor
                section_url = base_url
                if current_section:
                    section_url += "#" + slugify(current_section)
                
                docs.append({
                    "url": section_url,
                    "title": title,
                    "section": current_section,
                    "content": content_text
                })
    
    for line in lines:
        line = line.strip()
        # Check if this is a heading (markdown style)
        if line.startswith('#'):
            # Flush previous section
            flush_section()
            current_content = []
            # Extract heading text
            current_section = line.lstrip('#').strip()
        else:
            current_content.append(line)
    
    # Flush final section
    flush_section()
    return docs

async def crawl():
    ensure_dirs()
    docs = []
    
    report_progress("STATUS: Starting to crawl SWMM manual markdown files...")
    
    async with httpx.AsyncClient(
        follow_redirects=True, 
        headers={"User-Agent": "SWMM-SearchBot/1.0"},
        timeout=30.0
    ) as client:
        
        # Automatically discover markdown files
        md_files = await discover_markdown_files(client)
        if not md_files:
            report_progress("ERROR: No markdown files found")
            return 0

        for md_file in md_files:
            url = urljoin(BASE_URL, md_file)
            
            report_progress(f"CRAWLING: {url}")
            try:
                response = await client.get(url)
                response.raise_for_status()
                markdown_content = response.text
            except Exception as e:
                report_progress(f"FAILED: {url} - {str(e)}")
                continue

            # Extract title from filename
            filename = md_file.split('/')[-1].replace('.md', '')
            if filename.startswith('Chapter'):
                title = f"SWMM Manual {filename}"
            elif filename.startswith('Appendix'):
                title = f"SWMM Manual {filename}"
            else:
                title = f"SWMM Manual {filename}"

            # Process markdown content
            page_docs = process_markdown_content(markdown_content, title, url)
            docs.extend(page_docs)
            
            report_progress(f"INDEXED: {title} ({len(page_docs)} sections)")

    # write docs
    with OUT_PATH.open("w", encoding="utf-8") as f:
        for d in docs:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")
    
    report_progress(f"STATUS: Completed! Wrote {len(docs)} docs to {OUT_PATH}")
    return len(docs)

if __name__ == "__main__":
    result = asyncio.run(crawl())
    print(f"Crawling completed with {result} documents")