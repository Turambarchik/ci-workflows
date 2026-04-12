# Bundle Size CI — PR vs Base

GitHub Action that compares Next.js bundle size between a PR branch and the base branch. Posts a diff table as a PR comment on every push.

## How it works

1. Checks out both branches simultaneously using Git worktrees
2. Runs `npm run build` on each
3. Parses `.next/build-manifest.json` and `.next/app-build-manifest.json`
4. Diffs the output per route and posts a Markdown report as a PR comment (updates in-place on re-push)

## Repository structure

```
.github/workflows/bundle-size/
  scripts/
    bundle-size.mjs   ← analyzer (zero dependencies, pure Node.js)
  bundle-size.yml     ← workflow
README.md
```

## Usage in your project

Copy the two files into **your Next.js repo** at the same paths:

```
your-project/
  .github/workflows/bundle-size/
    scripts/bundle-size.mjs
    bundle-size.yml
```

If your build needs environment variables, uncomment the `env:` blocks in `bundle-size.yml` and add secrets in **GitHub → Settings → Secrets and variables → Actions**:

```yaml
env:
  NEXT_PUBLIC_API_URL: ${{ secrets.NEXT_PUBLIC_API_URL }}
```

That's it. The action triggers automatically on every PR.

## PR comment output

```
📦 Bundle Size Report
✅ Decreased by 2.1 kB

| Route        | Base     | PR       | Diff        |
|:-------------|--------: |--------: |-----------: |
| `/`          | 120.0 kB | 118.0 kB | ✅ -2.0 kB  |
| `/dashboard` | 340.0 kB | 340.0 kB | ➡️ 0 B      |
| **Total**    | **460 kB**| **458 kB**| **✅ -2.0 kB** |
```

## Why a custom analyzer

Standard Next.js bundle analyzer is built for visual inspection (treemaps). This one is built for CI:

- PR vs base diff out of the box
- Structured JSON output — easy to feed into scripts or AI agents
- Zero dependencies — just Node.js and the build output
- Comment updates in-place — no PR spam

## AI workflow

The structured summary makes it easy to close the loop with an agent:

```
AI writes code → pipeline measures → feed summary back → AI evaluates → you decide
```

## Requirements

- Next.js (any version)
- Node.js 20+
- `package-lock.json` (uses `npm ci`)
