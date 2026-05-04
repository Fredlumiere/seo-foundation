# {project}-audit

Weekly Lighthouse audit of [{site}]({site}) — runs every Monday 10:00 UTC, publishes a dashboard.

This template ships with **two hosting options**. Pick one before pushing:

- **Vercel** — keep `audit.vercel.yml`, `vercel.json`, optionally `middleware.js`. Delete `audit.yml`.
- **Cloudflare Pages** — keep `audit.yml`. Delete `audit.vercel.yml`, `vercel.json`, `middleware.js`.

Then rename `audit.vercel.yml` → `audit.yml` if you went the Vercel route.

## Setup — Vercel

```bash
npm install --package-lock-only
git add package.json package-lock.json .gitignore .github/workflows/audit.yml vercel.json middleware.js README.md
git commit -m "initial audit pipeline"
gh repo create {user}/{project}-audit --private --source=. --remote=origin --push
gh secret set VERCEL_TOKEN  # paste from vercel.com/account/tokens
# If using Basic Auth middleware, also set these as Vercel project env vars (Production):
#   AUDIT_USER, AUDIT_PASSWORD
gh workflow run audit.yml
```

## Setup — Cloudflare Pages

```bash
npm install --package-lock-only
git add package.json package-lock.json .gitignore .github/workflows/audit.yml README.md
git commit -m "initial audit pipeline"
gh repo create {user}/{project}-audit --public --source=. --remote=origin --push
gh secret set CLOUDFLARE_API_TOKEN
gh secret set CLOUDFLARE_ACCOUNT_ID
gh workflow run audit.yml
```

### Cloudflare API token scope

Custom token, minimum permissions:
- Account → Cloudflare Pages → Edit
- User → User Details → Read
- User → Memberships → Read

Account Resources: **Include → Specific account → {your account}**.

Verify with:
```bash
curl 'https://api.cloudflare.com/client/v4/accounts' -H "Authorization: Bearer $TOKEN" | jq '.result | length'
# Should return 1+, not 0
```

## Generating the PDF fix list

After the first audit completes:

```bash
mkdir -p pdf-build
# Vercel: replace {dashboard} with the deployment URL printed by `vercel deploy`
# Cloudflare: replace with https://{project}-audit-reports.pages.dev
curl -s https://{dashboard}/assets/payload.js -o pdf-build/payload.js
curl -s https://{dashboard}/ci-result.json -o pdf-build/ci-result.json
python3 ../seo-foundation/scripts/extract.py
# Then build the HTML report from templates/report.html, render to PDF with headless Chrome.
```

See the parent playbook (`SETUP.md` Phase 3) for the full PDF build flow.
