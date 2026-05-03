#!/usr/bin/env python3
"""Generate sitemap.xml for a static HTML site.

Walks a directory, collects indexable HTML pages, emits a canonical sitemap
with optional hreflang alternates for localized versions.

Usage:
    # Minimum: just a base URL
    python3 generate_sitemap.py --base-url https://example.com

    # With a config file (recommended for repeated runs)
    python3 generate_sitemap.py --config sitemap.config.json

Config file format (sitemap.config.json):
    {
      "base_url": "https://example.com",
      "root": ".",
      "output": "sitemap.xml",
      "locales": ["es", "fr"],
      "exclude_dirs": ["node_modules", ".git", "scripts", "backup"],
      "exclude_files": ["404.html", "401.html", "temp.html"],
      "exclude_patterns": ["^draft-.*\\.html$"],
      "priority_overrides": {
        "index.html": 1.0,
        "about.html": 0.8
      },
      "default_priority": 0.6,
      "default_changefreq": "monthly",
      "changefreq_overrides": {
        "index.html": "weekly"
      }
    }

Excluded automatically (regardless of config):
    - any file with <meta name="robots" content="noindex">
    - any directory whose name matches a configured locale (those are siblings,
      not separate pages — picked up as hreflang alternates of their English
      counterpart)

Adapt the config file per project. Run before every deploy.
"""
from __future__ import annotations
import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape

DEFAULT_EXCLUDE_DIRS = {
    ".git", "node_modules", ".github", "scripts", "backup",
    ".claude", ".uisnap", "__pycache__", "dist", ".next", ".vercel",
}
DEFAULT_EXCLUDE_FILES = {
    "404.html", "401.html", "500.html", "temp.html",
}


def load_config(path: Path) -> dict:
    if not path.exists():
        sys.exit(f"Config file not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def page_has_noindex(path: Path) -> bool:
    try:
        head = path.read_text(encoding="utf-8", errors="ignore")[:8000]
    except OSError:
        return False
    for m in re.finditer(r"<meta\b[^>]*>", head, re.I):
        tag = m.group(0)
        if not re.search(r'name\s*=\s*["\']robots["\']', tag, re.I):
            continue
        if re.search(r'content\s*=\s*["\'][^"\']*noindex', tag, re.I):
            return True
    return False


def url_from_path(path: Path, root: Path, base_url: str) -> str:
    rel = path.relative_to(root).as_posix()
    if rel.endswith("/index.html"):
        rel = rel[: -len("index.html")]
    elif rel == "index.html":
        rel = ""
    return f"{base_url}/{rel}" if rel else f"{base_url}/"


def locale_url_for(english_path: Path, root: Path, base_url: str, locale: str) -> str | None:
    rel = english_path.relative_to(root)
    localized = root / locale / rel
    if not localized.exists():
        return None
    rel_str = rel.as_posix()
    if rel_str.endswith("/index.html"):
        rel_str = rel_str[: -len("index.html")]
    elif rel_str == "index.html":
        rel_str = ""
    return f"{base_url}/{locale}/{rel_str}" if rel_str else f"{base_url}/{locale}/"


def collect_pages(
    root: Path,
    locales: set[str],
    exclude_dirs: set[str],
    exclude_files: set[str],
    exclude_patterns: list[re.Pattern],
) -> list[Path]:
    pages = []
    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = Path(dirpath).relative_to(root)
        parts = rel_dir.parts
        if parts and (parts[0] in exclude_dirs or parts[0] in locales):
            dirnames[:] = []
            continue
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs and d not in locales]
        for fn in filenames:
            if not fn.endswith(".html"):
                continue
            if fn in exclude_files:
                continue
            if any(p.match(fn) for p in exclude_patterns):
                continue
            p = Path(dirpath) / fn
            if page_has_noindex(p):
                continue
            pages.append(p)
    return sorted(pages)


def build_sitemap(
    pages: list[Path],
    root: Path,
    base_url: str,
    locales: list[str],
    priority_overrides: dict[str, float],
    default_priority: float,
    changefreq_overrides: dict[str, str],
    default_changefreq: str,
) -> str:
    out = ['<?xml version="1.0" encoding="UTF-8"?>']
    out.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"')
    out.append('        xmlns:xhtml="http://www.w3.org/1999/xhtml">')
    for p in pages:
        rel = p.relative_to(root).as_posix()
        en_url = url_from_path(p, root, base_url)
        priority = priority_overrides.get(rel, default_priority)
        changefreq = changefreq_overrides.get(rel, default_changefreq)
        ts = p.stat().st_mtime
        lastmod = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")

        alternates: list[tuple[str, str]] = []
        if locales:
            alternates.append(("en", en_url))
            for loc in locales:
                lu = locale_url_for(p, root, base_url, loc)
                if lu:
                    alternates.append((loc, lu))
            alternates.append(("x-default", en_url))

        out.append("  <url>")
        out.append(f"    <loc>{escape(en_url)}</loc>")
        out.append(f"    <lastmod>{lastmod}</lastmod>")
        out.append(f"    <changefreq>{changefreq}</changefreq>")
        out.append(f"    <priority>{priority:.2f}</priority>")
        for hreflang, url in alternates:
            out.append(
                f'    <xhtml:link rel="alternate" hreflang="{hreflang}" href="{escape(url)}"/>'
            )
        out.append("  </url>")
    out.append("</urlset>")
    return "\n".join(out) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate sitemap.xml for a static HTML site")
    ap.add_argument("--config", type=Path, help="Path to sitemap.config.json")
    ap.add_argument("--base-url", help="Site base URL (e.g. https://example.com). Required if --config is not given.")
    ap.add_argument("--root", type=Path, default=Path("."), help="Repo root (default: cwd)")
    ap.add_argument("--output", type=Path, default=Path("sitemap.xml"), help="Output file (default: sitemap.xml)")
    args = ap.parse_args()

    cfg: dict = {}
    if args.config:
        cfg = load_config(args.config)
    if args.base_url:
        cfg["base_url"] = args.base_url
    if "base_url" not in cfg:
        sys.exit("--base-url or --config with base_url is required")

    root = (args.root or Path(cfg.get("root", "."))).resolve()
    output = args.output if args.output != Path("sitemap.xml") else Path(cfg.get("output", "sitemap.xml"))
    base_url = cfg["base_url"].rstrip("/")
    locales = cfg.get("locales", [])
    exclude_dirs = DEFAULT_EXCLUDE_DIRS | set(cfg.get("exclude_dirs", []))
    exclude_files = DEFAULT_EXCLUDE_FILES | set(cfg.get("exclude_files", []))
    exclude_patterns = [re.compile(p) for p in cfg.get("exclude_patterns", [])]
    priority_overrides = cfg.get("priority_overrides", {})
    default_priority = cfg.get("default_priority", 0.6)
    changefreq_overrides = cfg.get("changefreq_overrides", {})
    default_changefreq = cfg.get("default_changefreq", "monthly")

    pages = collect_pages(root, set(locales), exclude_dirs, exclude_files, exclude_patterns)
    xml = build_sitemap(
        pages, root, base_url, locales,
        priority_overrides, default_priority,
        changefreq_overrides, default_changefreq,
    )
    output.write_text(xml, encoding="utf-8")
    print(f"Wrote {output} with {len(pages)} English URLs")
    if locales:
        print(f"Locale alternates checked: {', '.join(locales)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
