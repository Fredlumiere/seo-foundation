#!/usr/bin/env python3
"""Parse unlighthouse payload.js into a prioritized fix list (findings.json).

Usage:
    # Run from the {project}-audit/ directory after fetching payload.js
    python3 ../seo-foundation/scripts/extract.py

    # Or specify paths explicitly
    python3 extract.py --payload pdf-build/payload.js --output pdf-build/findings.json
"""
import argparse, json, re, sys
from collections import defaultdict
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--payload", type=Path, default=Path("pdf-build/payload.js"),
                help="Path to unlighthouse payload.js (default: pdf-build/payload.js)")
ap.add_argument("--output", type=Path, default=Path("pdf-build/findings.json"),
                help="Output JSON path (default: pdf-build/findings.json)")
args = ap.parse_args()

if not args.payload.exists():
    sys.exit(f"Payload not found: {args.payload}")

raw = args.payload.read_text(encoding="utf-8")
m = re.match(r'window\.__unlighthouse_payload\s*=\s*', raw)
if not m:
    sys.exit("Could not find 'window.__unlighthouse_payload =' prefix in payload")
data = json.loads(raw[m.end():].rstrip().rstrip(';'))

reports = data['reports']
print(f"Pages audited: {len(reports)}", file=sys.stderr)

# Aggregate failing audits across pages
audit_map = defaultdict(lambda: {'title': '', 'description': '', 'pages': [], 'savings_ms': 0, 'category': ''})

# Track per-page summary
page_summary = []
for r in reports:
    url = r['route']['$url']
    path = r['route']['path']
    seo = r.get('seo', {}) or {}
    cats = {c['id']: c.get('score') for c in r['report']['categories']}
    page_summary.append({
        'url': url,
        'path': path,
        'title': seo.get('title', ''),
        'description': seo.get('description', ''),
        'html_size': seo.get('htmlSize', 0),
        'performance': cats.get('performance'),
        'accessibility': cats.get('accessibility'),
        'best_practices': cats.get('best-practices'),
        'seo': cats.get('seo'),
    })
    audits = r['report'].get('audits', {})
    for aid, a in audits.items():
        score = a.get('score')
        if score is None or score == 1:
            continue
        # severe: score < 0.5; warning: 0.5-0.9
        display = a.get('displayValue', '')
        savings = (a.get('metricSavings') or {}).get('LCP', 0) or 0
        entry = audit_map[aid]
        entry['title'] = a.get('title', aid)
        entry['description'] = a.get('description', '')
        entry['pages'].append({'url': url, 'path': path, 'score': score, 'display': display})
        entry['savings_ms'] = max(entry['savings_ms'], savings)

# Rank: weighted by (# pages affected) × (severity)
ranked = []
for aid, info in audit_map.items():
    n = len(info['pages'])
    avg_score = sum(p['score'] for p in info['pages']) / n if n else 1
    severity = 1 - avg_score  # 0-1, higher = worse
    impact = n * severity
    ranked.append((impact, aid, info, n, avg_score))

ranked.sort(reverse=True)

out = {
    'total_pages': len(reports),
    'avg_scores': {
        'performance': round(sum(p['performance'] or 0 for p in page_summary) / len(page_summary) * 100),
        'accessibility': round(sum(p['accessibility'] or 0 for p in page_summary) / len(page_summary) * 100),
        'best_practices': round(sum(p['best_practices'] or 0 for p in page_summary) / len(page_summary) * 100),
        'seo': round(sum(p['seo'] or 0 for p in page_summary) / len(page_summary) * 100),
    },
    'worst_pages_performance': sorted(page_summary, key=lambda p: p['performance'] or 1)[:10],
    'worst_pages_accessibility': sorted(page_summary, key=lambda p: p['accessibility'] or 1)[:10],
    'worst_pages_seo': sorted(page_summary, key=lambda p: p['seo'] or 1)[:10],
    'pages_missing_description': [p for p in page_summary if not p.get('description')],
    'largest_pages': sorted(page_summary, key=lambda p: -(p['html_size'] or 0))[:10],
    'top_audits': [],
}

# Only keep audits affecting >=3 pages or severe on homepage
for impact, aid, info, n, avg in ranked[:40]:
    out['top_audits'].append({
        'id': aid,
        'title': info['title'],
        'description': info['description'],
        'pages_affected': n,
        'avg_score': round(avg, 2),
        'impact_score': round(impact, 2),
        'sample_pages': [p['path'] for p in info['pages'][:6]],
    })

args.output.parent.mkdir(parents=True, exist_ok=True)
args.output.write_text(json.dumps(out, indent=2), encoding="utf-8")
print(f"Wrote {args.output}", file=sys.stderr)
print(f"Wrote findings.json — {len(out['top_audits'])} audit types, {out['avg_scores']}")
