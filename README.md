# CI Workflows Repository

This repository stores reusable CI workflows for Next.js projects.

## Structure

```text
ci-workflows/
  .github/
    workflows/
      bundle-size/
        bundle-size.yml
        README.md
      perf-audit-preview-vs-production/
        perf-audit-preview-vs-production.yml
        README.md
        scripts/
          publish_lighthouse_summary.py
  scripts/
    ci/
      bundle-size.mjs
```

## Workflows

- **Bundle Size (PR vs Base)**  
  Folder: `ci-workflows/.github/workflows/bundle-size/`  
  Documentation: `ci-workflows/.github/workflows/bundle-size/README.md`

- **Perf Audit (Preview vs Production)**  
  Folder: `ci-workflows/.github/workflows/perf-audit-preview-vs-production/`  
  Documentation: `ci-workflows/.github/workflows/perf-audit-preview-vs-production/README.md`

## Notes

- The Bundle Size analyzer script is located at `ci-workflows/scripts/ci/bundle-size.mjs`.
- Bundle Size workflow logic was not modified; only structure and documentation were improved.
