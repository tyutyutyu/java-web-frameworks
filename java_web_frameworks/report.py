"""Generate a polished, self-contained HTML report from benchmark results.

The report visualizes the JSON file produced by :mod:`java_web_frameworks.start`
(`benchmark-results/results.json`) with sortable tables and Chart.js bar charts.
The output is written to ``site/index.html`` and is ready to be published as a
static site (e.g. GitHub Pages).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape


# Metric definitions: (key, label, unit, transform, lower_is_better)
METRICS: list[tuple[str, str, str, str, bool]] = [
    ("build_duration", "Build duration", "ms", "ms", True),
    ("memory_used_mb", "Peak memory", "MB", "mb_from_kb", True),
    ("java_start_ms", "JVM startup", "ms", "passthrough", True),
    ("framework_start_ms", "Framework startup", "ms", "passthrough", True),
    ("framework_stop_ms", "Framework shutdown", "ms", "passthrough", True),
    ("total_runtime_ms", "Total runtime", "ms", "passthrough", True),
    ("image_size_mb", "Image size", "MB", "passthrough", True),
    ("efficiency_pct", "Image efficiency", "%", "passthrough", False),
]


def _normalize(name: str, raw: dict[str, Any]) -> dict[str, Any]:
    """Flatten the raw record into a friendlier shape used in the report."""
    framework, _, build = name.rpartition("_")
    framework = framework.removesuffix("-maven")
    return {
        "id": name,
        "framework": framework or name,
        "build_type": build or "basic",
        "build_duration": raw["build_duration"],
        "user_time_s": float(raw["user_time"]),
        "system_time_s": float(raw["system_time"]),
        "cpu_percent": int(raw["cpu_percent"]),
        "memory_used_mb": round(int(raw["memory_used"]) / 1024),
        "java_start_ms": raw["java_started_time"] - raw["starting_java_time"],
        "framework_start_ms": raw["framework_started_time"] - raw["java_started_time"],
        "framework_stop_ms": raw["java_stopped_time"]
            - raw["framework_shutdown_start_time"],
        "total_runtime_ms": raw["java_stopped_time"] - raw["starting_java_time"],
        "image_size_mb": round(int(raw["sizeBytes"]) / 1024 / 1024),
        "efficiency_pct": round(float(raw["efficiencyScore"]) * 100, 2),
    }


def build_context(results: dict[str, Any]) -> dict[str, Any]:
    rows = [_normalize(name, raw) for name, raw in results.items()]
    rows.sort(key=lambda r: (r["framework"], r["build_type"]))

    charts = []
    for key, label, unit, _, lower_is_better in METRICS:
        values = [row[key] for row in rows]
        winner = (min if lower_is_better else max)(values)
        charts.append(
            {
                "key": key,
                "label": label,
                "unit": unit,
                "lower_is_better": lower_is_better,
                "labels": [row["id"] for row in rows],
                "values": values,
                "winner": winner,
            }
        )

    return {
        "rows": rows,
        "charts": charts,
        "metrics": METRICS,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    }


def render(results_path: Path, output_path: Path) -> Path:
    if not results_path.exists():
        raise FileNotFoundError(f"Results file not found: {results_path}")

    with results_path.open("r", encoding="utf-8") as f:
        results = json.load(f)

    template_dir = Path(__file__).parent / "templates"
    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template("report.html.j2")
    context = build_context(results)
    html = template.render(**context)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    return output_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--results",
        type=Path,
        default=Path(os.getcwd()) / "benchmark-results" / "results.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(os.getcwd()) / "site" / "index.html",
    )
    args = parser.parse_args(argv)

    out = render(args.results, args.output)
    print(f"HTML report written to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
