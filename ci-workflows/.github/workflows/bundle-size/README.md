# Bundle Size CI — PR vs Base

GitHub Action, который сравнивает размер Next.js bundle между PR-веткой и базовой веткой и публикует diff-таблицу в комментарии к PR.

## Что делает workflow

1. Checkout PR-ветки.
2. Поднимает worktree для base-ветки.
3. Запускает `npm ci` и `npm run build` для обеих веток.
4. Анализирует build-манифесты через `ci-workflows/scripts/ci/bundle-size.mjs`.
5. Формирует summary + PR comment с изменениями по роутам и total.

## Файлы в этом workflow

- `bundle-size.yml` — workflow.
- `ci-workflows/scripts/ci/bundle-size.mjs` — analyzer script (общий для workflow).

## Как использовать в вашем проекте

Скопируйте файлы:

```text
your-project/
  .github/workflows/bundle-size/bundle-size.yml
  scripts/ci/bundle-size.mjs
```

> В workflow путь к скрипту: `./scripts/ci/bundle-size.mjs`, поэтому в целевом проекте скрипт должен лежать именно там.

Если нужны env-переменные для build, раскомментируйте блок `env:` в `bundle-size.yml` и добавьте Secrets в GitHub Actions.

## Требования

- Next.js
- Node.js 20+
- `package-lock.json` (используется `npm ci`)
