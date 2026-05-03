# SEO Foundation

A reusable playbook for setting up SEO, analytics, automated weekly audits, fix reports, and stakeholder communication on any website.

This repo is the canonical source. The Claude Code skill at `~/.claude/skills/seo-foundation/SKILL.md` references it.

## What's in here

- **`SETUP.md`** — the playbook itself. Phase 1–4 instructions, scope decisions, gotchas, project worksheet template.
- **`scripts/`** — reusable Python scripts:
  - `generate_sitemap.py` — config-driven sitemap generator for static / hand-built sites
  - `inject_seo.py.starter` — canonical / schema / hreflang injector (adapt per project)
  - `extract.py` — Lighthouse payload parser for the PDF fix list
- **`templates/`**:
  - `PROJECT-WORKSHEET.md` — empty worksheet to fill in per project
  - `audit-repo/` — full scaffold for the `{project}-audit` GitHub repo (Cloudflare Pages dashboard)
  - `report.html` — PDF fix-list template
  - `stakeholder-email.txt` — stakeholder email template

## Using this on a new project

One-time setup on your machine:

```bash
git clone git@github.com:Fredlumiere/seo-foundation.git ~/playbooks/seo-foundation
```

Then in any new Claude Code project, type a phrase like **"set up SEO foundation"** and the skill kicks in. Walks you through Phase 1.1 → Phase 4, copies the relevant scripts/templates from `~/playbooks/seo-foundation/` into your project (or spawns the audit repo as a sibling), parameterizes everything via `PROJECT-WORKSHEET.md`.

Files copied into your project become part of *its* repo. No git submodules, no remote dependency. Drift from this upstream is fine.

## Updating

When the playbook or scripts improve, push to this repo. Existing projects don't auto-receive updates — you pull selectively if and when you want them.

## Provenance

Distilled from setups originally shipped to tmpc.org (2026-04) and apiant.com (2026-04). Project-specific contamination has been stripped.
