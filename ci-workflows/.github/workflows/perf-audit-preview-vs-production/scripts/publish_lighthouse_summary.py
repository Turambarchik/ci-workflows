import json
import os
from urllib.parse import urlsplit, urlunsplit
from pathlib import Path

preview_url = os.environ.get("PREVIEW_URL", "")
production_url = os.environ.get("PRODUCTION_URL", "")
preview_manifest_raw = os.environ.get("PREVIEW_MANIFEST", "")
production_manifest_raw = os.environ.get("PRODUCTION_MANIFEST", "")
preview_results_path = os.environ.get("PREVIEW_RESULTS_PATH", "")
production_results_path = os.environ.get("PRODUCTION_RESULTS_PATH", "")
preview_outcome = os.environ.get("PREVIEW_OUTCOME", "")
production_outcome = os.environ.get("PRODUCTION_OUTCOME", "")


def sanitize_url(url):
    if not url:
        return ""
    try:
        parts = urlsplit(url)
        return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))
    except Exception:
        return url.split("?")[0]


def parse_json(raw, default):
    try:
        return json.loads(raw) if raw else default
    except Exception:
        return default


def parse_manifest(raw):
    data = parse_json(raw, [])
    return data if isinstance(data, list) else []


def find_lhr_json_from_manifest(manifest_items):
    for item in manifest_items:
        if item.get("isRepresentativeRun") and item.get("jsonPath"):
            return item["jsonPath"]
    for item in manifest_items:
        if item.get("jsonPath"):
            return item["jsonPath"]
    return None


def fallback_find_json(results_path):
    if not results_path:
        return None
    path = Path(results_path)
    if not path.exists():
        return None
    candidates = sorted(path.glob("*.report.json"))
    return str(candidates[-1]) if candidates else None


def load_lhr(json_path):
    if not json_path:
        return None
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def extract_metrics_from_lhr(lhr):
    if not lhr:
        return {}

    categories = lhr.get("categories") or {}
    audits = lhr.get("audits") or {}

    return {
        "performance": ((categories.get("performance") or {}).get("score")),
        "fcp": ((audits.get("first-contentful-paint") or {}).get("numericValue")),
        "lcp": ((audits.get("largest-contentful-paint") or {}).get("numericValue")),
        "speed_index": ((audits.get("speed-index") or {}).get("numericValue")),
        "tbt": ((audits.get("total-blocking-time") or {}).get("numericValue")),
        "cls": ((audits.get("cumulative-layout-shift") or {}).get("numericValue")),
    }


def normalize_score(value):
    if value is None:
        return None
    return value * 100 if value <= 1 else value


def fmt_score(value):
    value = normalize_score(value)
    if value is None:
        return "—"
    return f"{value:.0f}"


def fmt_ms(value):
    if value is None:
        return "—"
    return f"{value:.0f} ms"


def fmt_cls(value):
    if value is None:
        return "—"
    return f"{value:.3f}"


def delta(a, b):
    if a is None or b is None:
        return None
    return a - b


def fmt_delta(value, kind):
    if value is None:
        return "—"
    sign = "+" if value > 0 else ""
    if kind == "score":
        return f"{sign}{value:.0f}"
    if kind == "ms":
        return f"{sign}{value:.0f} ms"
    return f"{sign}{value:.3f}"


def interpret_delta(metric_key, delta_value):
    if delta_value is None:
        return "⚪ Not available"

    if metric_key == "performance":
        if delta_value >= 5:
            return "🚀 Preview is meaningfully better"
        if delta_value <= -5:
            return "❌ Preview is meaningfully worse"
        return "😐 About the same"

    if metric_key in {"fcp", "lcp", "speed_index", "tbt"}:
        if delta_value <= -200:
            return "✅ Preview is better"
        if delta_value >= 200:
            return "⚠️ Preview is worse"
        return "😐 About the same"

    if metric_key == "cls":
        if delta_value <= -0.02:
            return "✅ Preview is better"
        if delta_value >= 0.02:
            return "⚠️ Preview is worse"
        return "😐 About the same"

    return "⚪ Not available"


def build_overall_result(performance_delta):
    if performance_delta is None:
        return "Result: ⚪ Performance comparison is unavailable."
    if performance_delta >= 5:
        return "Result: 🚀 Preview performance is much better."
    if performance_delta <= -5:
        return "Result: ❌ Preview performance is much worse."
    return "Result: 😐 Preview performance is effectively unchanged."


preview_manifest = parse_manifest(preview_manifest_raw)
production_manifest = parse_manifest(production_manifest_raw)

preview_json_path = find_lhr_json_from_manifest(preview_manifest) or fallback_find_json(preview_results_path)
production_json_path = find_lhr_json_from_manifest(production_manifest) or fallback_find_json(production_results_path)

preview_lhr = load_lhr(preview_json_path)
production_lhr = load_lhr(production_json_path)

preview = extract_metrics_from_lhr(preview_lhr)
production = extract_metrics_from_lhr(production_lhr)

performance_delta = delta(normalize_score(preview.get("performance")), normalize_score(production.get("performance")))
fcp_delta = delta(preview.get("fcp"), production.get("fcp"))
lcp_delta = delta(preview.get("lcp"), production.get("lcp"))
speed_index_delta = delta(preview.get("speed_index"), production.get("speed_index"))
tbt_delta = delta(preview.get("tbt"), production.get("tbt"))
cls_delta = delta(preview.get("cls"), production.get("cls"))

rows = [
    (
        "Performance",
        fmt_score(preview.get("performance")),
        fmt_score(production.get("performance")),
        fmt_delta(performance_delta, "score"),
        "Overall Lighthouse score for the page",
        interpret_delta("performance", performance_delta),
    ),
    (
        "FCP",
        fmt_ms(preview.get("fcp")),
        fmt_ms(production.get("fcp")),
        fmt_delta(fcp_delta, "ms"),
        "Time until the first visible content appears",
        interpret_delta("fcp", fcp_delta),
    ),
    (
        "LCP",
        fmt_ms(preview.get("lcp")),
        fmt_ms(production.get("lcp")),
        fmt_delta(lcp_delta, "ms"),
        "Time until the main visible content finishes rendering",
        interpret_delta("lcp", lcp_delta),
    ),
    (
        "Speed Index",
        fmt_ms(preview.get("speed_index")),
        fmt_ms(production.get("speed_index")),
        fmt_delta(speed_index_delta, "ms"),
        "How quickly the page becomes visually complete",
        interpret_delta("speed_index", speed_index_delta),
    ),
    (
        "TBT",
        fmt_ms(preview.get("tbt")),
        fmt_ms(production.get("tbt")),
        fmt_delta(tbt_delta, "ms"),
        "How much the main thread is blocked during load",
        interpret_delta("tbt", tbt_delta),
    ),
    (
        "CLS",
        fmt_cls(preview.get("cls")),
        fmt_cls(production.get("cls")),
        fmt_delta(cls_delta, "cls"),
        "How much the layout shifts unexpectedly during load",
        interpret_delta("cls", cls_delta),
    ),
]

lines = []
lines.append("## Lighthouse comparison")
lines.append("")
lines.append(build_overall_result(performance_delta))
lines.append("")
lines.append("**Preview URL**  ")
lines.append(sanitize_url(preview_url) or "—")
lines.append("")
lines.append("**Production URL**  ")
lines.append(sanitize_url(production_url) or "—")
lines.append("")

if preview_outcome != "success":
    lines.append("> Preview audit failed. Most likely causes: preview protection still blocks CI, the bypass secret is incorrect, or the preview page itself failed to load consistently.")
    lines.append("")

lines.append("| Metric | Preview | Production | Delta (Preview - Production) | Meaning | Interpretation |")
lines.append("|---|---:|---:|---:|---|---|")

for name, a, b, d, meaning, interpretation in rows:
    lines.append(f"| {name} | {a} | {b} | {d} | {meaning} | {interpretation} |")

lines.append("")
lines.append("### How to read delta")
lines.append("")
lines.append("- For **Performance**, a **positive** delta means Preview is better; a **negative** delta means Preview is worse.")
lines.append("- For **FCP, LCP, Speed Index, TBT**, a **negative** delta means Preview is faster/better; a **positive** delta means Preview is slower/worse.")
lines.append("- For **CLS**, a **negative** delta means Preview is more stable; a **positive** delta means Preview shifts more and is worse.")
lines.append("")
lines.append("### Why Preview can be worse than Production")
lines.append("")
lines.append("- Preview deployments often run on a cold path with less warm caching than production.")
lines.append("- Production may benefit from better CDN cache hit rates and already-optimized assets.")
lines.append("- Small code changes can disproportionately hurt **LCP** and **TBT**, which heavily affect the Lighthouse score.")
lines.append("- Third-party scripts, heavier images/fonts, or more client-side work can make preview slower even when functionality is unchanged.")
lines.append("")
lines.append("### Metric guide")
lines.append("")
lines.append("- **Performance** — overall synthetic Lighthouse score.")
lines.append("- **FCP** — when the first visible content appears.")
lines.append("- **LCP** — when the largest main content element becomes visible.")
lines.append("- **Speed Index** — how fast the page looks visually complete.")
lines.append("- **TBT** — how long JavaScript blocks the main thread.")
lines.append("- **CLS** — how much the layout jumps around unexpectedly.")
lines.append("")
lines.append(f"**Preview audit outcome:** `{preview_outcome or 'unknown'}`  ")
lines.append(f"**Production audit outcome:** `{production_outcome or 'unknown'}`")

with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")
