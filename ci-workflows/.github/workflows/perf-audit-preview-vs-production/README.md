# Perf Audit — Preview vs Production

Workflow that compares Lighthouse metrics between a Preview deployment and Production after a successful `deployment_status` event.

## What this workflow does

1. Reads Preview URL from `github.event.deployment_status.environment_url`.
2. Reads Production URL from the `PROD_URL` secret.
3. Adds Vercel bypass query parameters (using `VERCEL_AUTOMATION_BYPASS_SECRET`) for protected preview environments.
4. Runs Lighthouse CI for Preview and Production.
5. Generates a comparison summary in `GITHUB_STEP_SUMMARY` for:
   - Performance
   - FCP
   - LCP
   - Speed Index
   - TBT
   - CLS
6. Fails the job if at least one audit is unsuccessful.

## Files

- `perf-audit-preview-vs-production.yml` — workflow definition.
- `scripts/publish_lighthouse_summary.py` — summary generation script extracted from workflow YAML.

## Required secrets

- `PROD_URL` — production URL (example: `https://your-domain.com`).
- `VERCEL_AUTOMATION_BYPASS_SECRET` — secret for bypassing preview protection in CI.

## How to use in your project

Copy these files:

```text
your-project/
  .github/workflows/perf-audit-preview-vs-production/perf-audit-preview-vs-production.yml
  .github/workflows/perf-audit-preview-vs-production/scripts/publish_lighthouse_summary.py
```

Also ensure `lighthouserc.json` exists in the target repository root, because the workflow validates it before running Lighthouse.

## Lighthouse stability note

Lighthouse metrics are not fully deterministic. A single run can vary due to CI runner noise (CPU/network), cache state, third-party scripts, and backend latency.

For more stable decisions, use:

- multiple runs and median/p75 comparison,
- performance budgets,
- historical trend tracking.
