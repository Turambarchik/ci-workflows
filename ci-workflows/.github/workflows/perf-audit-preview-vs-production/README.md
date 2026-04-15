# Perf Audit — Preview vs Production

Workflow для сравнения Lighthouse метрик между **Preview deployment** и **Production** после успешного `deployment_status` события.

## Что делает workflow

1. Берёт Preview URL из `github.event.deployment_status.environment_url`.
2. Берёт Production URL из секрета `PROD_URL`.
3. Добавляет Vercel bypass query params (секрет `VERCEL_AUTOMATION_BYPASS_SECRET`) для защищённых preview-окружений.
4. Запускает Lighthouse CI для Preview и Production.
5. Генерирует comparison summary в `GITHUB_STEP_SUMMARY`:
   - Performance
   - FCP
   - LCP
   - Speed Index
   - TBT
   - CLS
6. Фейлит job, если один из аудитов завершился неуспешно.

## Файлы в этом workflow

- `perf-audit-preview-vs-production.yml` — workflow.

## Required secrets

- `PROD_URL` — production URL (например, `https://your-domain.com`).
- `VERCEL_AUTOMATION_BYPASS_SECRET` — секрет для обхода preview protection в CI.

## Как использовать в вашем проекте

Скопируйте файл:

```text
your-project/
  .github/workflows/perf-audit-preview-vs-production/perf-audit-preview-vs-production.yml
```

Также в корне целевого проекта должен быть `lighthouserc.json`, так как workflow валидирует его наличие перед запуском.

## Важное замечание о Lighthouse

Lighthouse метрики недетерминированы: одиночный прогон может заметно отличаться из-за шума CI-окружения (CPU/сеть), кэшей, состояния third-party скриптов и backend latency.

Для более стабильных решений рекомендуется:

- делать несколько прогонов и сравнивать median/p75,
- добавлять performance budgets,
- отслеживать тренд метрик во времени.
