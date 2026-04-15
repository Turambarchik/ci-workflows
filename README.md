# CI Workflows Repository

Этот репозиторий хранит переиспользуемые CI workflows для Next.js проектов.

## Структура

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
    ci/
      bundle-size.mjs

docs/
  linkedin-lighthouse-workflow-post.md
```

## Workflows

- **Bundle Size (PR vs Base)**  
  Папка: `ci-workflows/.github/workflows/bundle-size/`  
  Описание и инструкции: `ci-workflows/.github/workflows/bundle-size/README.md`

- **Perf Audit (Preview vs Production)**  
  Папка: `ci-workflows/.github/workflows/perf-audit-preview-vs-production/`  
  Описание и инструкции: `ci-workflows/.github/workflows/perf-audit-preview-vs-production/README.md`

## Примечания

- Bundle Size analyzer скрипт находится в `ci-workflows/scripts/ci/bundle-size.mjs`.
- Существующий Bundle Size workflow не изменён по логике, изменена только структура документации/размещения файлов.
