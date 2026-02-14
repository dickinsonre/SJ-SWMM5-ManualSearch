import re
from urllib.parse import urljoin, urlparse, urldefrag

SAME_HOST = "swmm-manual.netlify.app"

def normalize_url(base: str, href: str) -> str | None:
    if not href:
        return None
    # remove in-page fragments
    href, _ = urldefrag(href)
    if not href:
        return None
    # no javascript/mailto/tel
    if href.startswith(("javascript:", "mailto:", "tel:")):
        return None
    url = urljoin(base, href)
    parsed = urlparse(url)
    if parsed.netloc != SAME_HOST:
        return None
    # stay on https
    if parsed.scheme not in ("http", "https"):
        return None
    return parsed.geturl()

def textify(s) -> str:
    # Normalize whitespace and collapse spaces
    s = re.sub(r"\s+", " ", (s or "")).strip()
    return s

MAIN_SELECTORS = [
    "main",
    "article",
    "#content",
    ".content",
    "#app main",
    "body"  # fallback
]

def pick_best_container(soup):
    for sel in MAIN_SELECTORS:
        el = soup.select_one(sel)
        if el and text_len(el) > 200:
            return el
    return soup  # fallback

def text_len(el) -> int:
    return len(el.get_text(" ", strip=True)) if el else 0