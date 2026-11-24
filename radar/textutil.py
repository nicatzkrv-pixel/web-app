"""Small text helpers: HTML stripping, title normalising, URL canonicalising."""
from __future__ import annotations

import hashlib
import html
import re
import unicodedata
from html.parser import HTMLParser
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

_TRACKING_PARAMS = re.compile(r"^(utm_|fbclid$|gclid$|mc_|ref$|ref_src$|oc$|cmpid$|ito$)")
_WS = re.compile(r"\s+")


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript", "nav", "footer", "header", "aside", "form"):
            self._skip += 1
        elif tag in ("p", "br", "li", "h1", "h2", "h3", "div"):
            self.parts.append(" ")

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript", "nav", "footer", "header", "aside", "form") and self._skip:
            self._skip -= 1

    def handle_data(self, data):
        if not self._skip:
            self.parts.append(data)


def strip_html(text: str | None) -> str:
    if not text:
        return ""
    parser = _TextExtractor()
    try:
        parser.feed(text)
        parser.close()
        out = "".join(parser.parts)
    except Exception:  # malformed markup: fall back to a crude strip
        out = re.sub(r"<[^>]+>", " ", text)
    return _WS.sub(" ", html.unescape(out)).strip()


class _ParagraphExtractor(HTMLParser):
    """Collects text inside <p> tags, skipping page chrome. Good enough for news articles."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.paragraphs: list[str] = []
        self._in_p = 0
        self._skip = 0
        self._buf: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript", "nav", "footer", "header", "aside", "form", "figcaption"):
            self._skip += 1
        elif tag == "p":
            self._in_p += 1
            self._buf = []

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript", "nav", "footer", "header", "aside", "form", "figcaption"):
            if self._skip:
                self._skip -= 1
        elif tag == "p" and self._in_p:
            self._in_p -= 1
            text = _WS.sub(" ", "".join(self._buf)).strip()
            if len(text) > 60:
                self.paragraphs.append(text)
            self._buf = []

    def handle_data(self, data):
        if self._in_p and not self._skip:
            self._buf.append(data)


def article_text(page_html: str, limit: int) -> str:
    parser = _ParagraphExtractor()
    try:
        parser.feed(page_html)
        parser.close()
    except Exception:
        return ""
    text = " ".join(parser.paragraphs)
    return text[:limit]


def normalize_title(title: str) -> str:
    """Lowercase, strip accents and punctuation, drop a trailing ' - Publisher'."""
    t = title or ""
    t = re.sub(r"\s+[-–—|]\s+[^-–—|]{2,60}$", "", t)  # " - Finextra Research"
    t = unicodedata.normalize("NFKD", t)
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = t.lower()
    t = re.sub(r"[^\w\s]", " ", t)
    return _WS.sub(" ", t).strip()


def canonical_url(url: str) -> str:
    """Scheme-less, www-less, tracking-free URL used for dedupe."""
    if not url:
        return ""
    parts = urlsplit(url.strip())
    host = parts.netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    query = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=False) if not _TRACKING_PARAMS.match(k)]
    path = parts.path.rstrip("/") or "/"
    return urlunsplit(("", host, path, urlencode(sorted(query)), "")).lstrip("/")


def item_id(url: str, title: str = "") -> str:
    key = canonical_url(url) or normalize_title(title)
    return hashlib.sha1(key.encode("utf-8")).hexdigest()[:12]


def first_sentences(text: str, n: int = 2, max_chars: int = 320) -> str:
    text = (text or "").strip()
    if not text:
        return ""
    sentences = re.split(r"(?<=[.!?])\s+", text)
    out = " ".join(sentences[:n]).strip()
    if len(out) > max_chars:
        out = out[: max_chars - 1].rsplit(" ", 1)[0] + "…"
    return out
