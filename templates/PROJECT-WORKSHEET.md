# {project} SEO Foundation — Adaptation Worksheet

Fill this out **before** starting Phase 1. Save the completed copy in the project's repo as `PROJECT-WORKSHEET.md` so future re-runs and collaborators have the same context.

Replace every `{ }` with the project's specifics.

---

## Site basics

- Site URL: `{https://example.com}`
- Project slug (used for repo names + Pages URL): `{project-slug}`
- CMS / platform: `{wordpress | webflow | custom-static | nextjs | hugo | jekyll | astro | other}`
- Day-to-day content owner: `{name + email + role}`
- Audience tone for the fix report: `{non-technical | technical | mixed}`
- Hosting / deploy path (informational): `{static, Vercel, Netlify, AWS, Cloudflare, ...}`

## Existing infrastructure

- GA4 already installed: `{yes / no — if yes, Measurement ID}`
- Search Console already verified: `{yes / no}`
- Cloudflare account: `{yes / no — if no, user must create}`
- GitHub org/user for audit repo: `{github-handle}`
- Existing sitemap path: `{/sitemap.xml | /sitemap_index.xml | none}`
- Existing schema markup: `{none | partial | full}`
- Existing canonical / hreflang setup: `{none | partial | full}`

## Brand

- Primary brand colors (hex): `{#aaaaaa, #bbbbbb}`
- Typography preference: `{default serif+sans (Fraunces+Inter) | technical (Inter+JetBrains Mono) | other}`
- Logo file: `{path or URL}`

## CMS-specific fix locations

For each Phase 3 fix type, document where to actually edit in this CMS:

- Meta description: `{settings page | code template path | plugin}`
- Alt text: `{media library | image-block field | code template}`
- H1 / page title: `{page settings | code template}`
- Schema markup: `{plugin | hand-coded JSON-LD}`
- Canonical / hreflang: `{plugin | code template | server-side rewrite}`

## Project-specific signals to watch for

- Does the site already have any of these that should NOT be duplicated?
  - GTM container: `{yes / no}`
  - Existing GA4 / UA tags: `{yes / no — list IDs}`
  - Existing schema markup: `{yes / no}`
  - Existing canonical / hreflang setup: `{yes / no}`
- Are there any noindex pages that should stay noindex? `{list}`
- Are there any servlet/template-rendered pages that need special handling (do not give them static canonicals)? `{list}`
- Are there any server-side rewrites already in place (extensionless URLs, locale redirects)? `{list}`

## Phase priorities for this project

For each phase, choose: **Run** | **Audit existing** | **Skip** (with reason).

- Phase 1 — GA4 + Search Console + sitemap: `{ Run | Audit existing | Skip — reason }`
- Phase 2 — Audit pipeline + dashboard: `{ Run | Skip — reason }`
- Phase 3 — PDF fix list: `{ Run | Substitute with GitHub issues | Skip — reason }`
- Phase 4 — Stakeholder email or summary: `{ Run | Substitute with markdown summary | Skip — reason }`

## Analytics / search-indexing context

- Analytics provider in use: `{ GA4 | Plausible | Fathom | Mixpanel | server-side | none | other }`
- Search indexing posture: `{ public + indexed | public + intentionally noindex | private/auth-walled }`
- Existing sitemap: `{ server-generated | static file at /sitemap.xml | none }`

## Deliverables expected

- [ ] Live GA4 with realtime data
- [ ] Verified Search Console with sitemap submitted
- [ ] {project}-audit GitHub repo with passing weekly workflow
- [ ] Public dashboard at https://{project}-audit-reports.pages.dev
- [ ] {Project}-Fix-List.pdf (or GitHub issue list) on Desktop / in repo
- [ ] Stakeholder email draft on Desktop (or markdown summary in repo)
