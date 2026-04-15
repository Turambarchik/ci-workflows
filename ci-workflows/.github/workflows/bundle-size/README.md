# Bundle Size CI — PR vs Base

GitHub Action that compares Next.js bundle size between the PR branch and the base branch, then posts a diff table as a PR comment.

## What this workflow does

1. Checks out the PR branch.
2. Creates a Git worktree for the base branch.
3. Runs `npm ci` and `npm run build` for both branches.
4. Analyzes build manifests using `ci-workflows/scripts/ci/bundle-size.mjs`.
5. Produces a summary and PR comment with per-route and total diffs.

## Files

- `bundle-size.yml` — workflow definition.
- `ci-workflows/scripts/ci/bundle-size.mjs` — analyzer script used by the workflow.

## How to use in your project

Copy these files:

```text
your-project/
  .github/workflows/bundle-size/bundle-size.yml
  scripts/ci/bundle-size.mjs
```

> The workflow uses `./scripts/ci/bundle-size.mjs`, so the script should keep this path in the target repository.

If your build requires environment variables, uncomment the `env:` block in `bundle-size.yml` and add GitHub Actions secrets.

## Requirements

- Next.js
- Node.js 20+
- `package-lock.json` (the workflow uses `npm ci`)
