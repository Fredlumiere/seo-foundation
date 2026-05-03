# {project}-audit

Weekly Lighthouse audit of [{site}]({site}) — runs every Monday 10:00 UTC, publishes a public dashboard at `https://{project}-audit-reports.pages.dev`.

## Setup

```bash
npm install --package-lock-only
git add package.json package-lock.json .gitignore .github/workflows/audit.yml README.md
git commit -m "initial audit pipeline"
gh repo create {user}/{project}-audit --public --source=. --remote=origin --push
gh secret set CLOUDFLARE_API_TOKEN
gh secret set CLOUDFLARE_ACCOUNT_ID
gh workflow run audit.yml
```

## Cloudflare API token scope

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
curl -s https://{project}-audit-reports.pages.dev/assets/payload.js -o pdf-build/payload.js
curl -s https://{project}-audit-reports.pages.dev/ci-result.json -o pdf-build/ci-result.json
python3 ../seo-foundation/scripts/extract.py
# Then build the HTML report from templates/report.html, render to PDF with headless Chrome.
```

See the parent playbook (`SETUP.md` Phase 3) for the full PDF build flow.
