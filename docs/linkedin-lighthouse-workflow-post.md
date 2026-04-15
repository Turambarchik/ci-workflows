# LinkedIn post — Lighthouse workflow in CI (Preview vs Production)

🚀 **Automating Lighthouse checks in CI is a game changer for AI-assisted development**

I just added a workflow that compares **Lighthouse metrics between Preview and Production** on every successful deployment status.

Why it’s 🔥

- You instantly see whether a change improved or degraded real performance signals.
- Works for both manual development and AI-generated PRs.
- Replaces subjective opinions (“feels faster”) with measurable outcomes.

The biggest win with AI agents 🤖

After an agent creates a PR, you can feed the CI summary back and ask:

> “Did these changes improve performance vs production?”

That creates a clean feedback loop:

**AI writes code → pipeline measures → AI evaluates → human decides**

---

## Why Lighthouse metrics are often non-deterministic

Lighthouse can vary run-to-run, even on unchanged code. Typical reasons:

- Shared CI runners have noisy CPU and network conditions.
- Preview deployments are often on colder caches than production.
- Third-party scripts (analytics/chat/ads) load with variable latency.
- Dynamic content and async hydration timing can shift scores.
- Different backend response time/cache state affects render milestones.

So treat single-run numbers as a signal, not absolute truth.

---

## What this workflow adds

- Audits **Preview URL** and **Production URL** in one pipeline.
- Generates a summary table for:
  - Performance score
  - FCP
  - LCP
  - Speed Index
  - TBT
  - CLS
- Adds interpretation text so the output is decision-friendly.
- Fails the workflow if one of the audits fails.

---

## Next improvements I plan

- Run multiple Lighthouse samples per environment and compare median/p75.
- Add path-level audits for key routes (`/`, `/pricing`, `/dashboard`).
- Add budget thresholds (e.g., LCP/TBT guardrails) to block regressions.
- Store historical results to visualize trends over time.
- Post PR comments with “regression risk” labels for faster triage.

---

🛠️ Stack:

- Next.js
- GitHub Actions
- Lighthouse CI (`treosh/lighthouse-ci-action`)
- Custom summary parser in Python
- Codex Agent loop (generation + evaluation)

If you use AI agents but don’t validate output with real performance metrics, you’re missing half the value.
