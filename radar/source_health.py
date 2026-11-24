"""Track per-source fetch results across runs and flag unreliable sources.

A source is flagged when it failed (HTTP/parse error) in more than half of its
runs over the last 7 days. Sources that work but return nothing are reported
separately as "quiet", since a niche Google News query can be legitimately empty.
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path

HEALTH_FILE = "source_health.json"
KEEP_RUNS = 60


def load(data_dir: Path) -> dict:
    path = data_dir / HEALTH_FILE
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def record(data_dir: Path, results, when: str) -> dict:
    """Append this run's results (list of fetch.SourceResult) and save."""
    health = load(data_dir)
    for r in results:
        runs = health.setdefault(r.name, [])
        runs.append({"at": when, "ok": r.ok, "count": r.count, "error": r.error})
        del runs[:-KEEP_RUNS]
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / HEALTH_FILE).write_text(json.dumps(health, indent=1, ensure_ascii=False), encoding="utf-8")
    return health


def flagged(health: dict, now: datetime, days: int = 7, threshold: float = 0.5) -> dict[str, dict]:
    """Sources failing more than `threshold` of runs in the last `days` days."""
    cutoff = (now - timedelta(days=days)).isoformat()
    out = {}
    for name, runs in health.items():
        recent = [r for r in runs if r["at"] >= cutoff]
        if not recent:
            continue
        failures = sum(1 for r in recent if not r["ok"])
        rate = failures / len(recent)
        if rate > threshold:
            last_error = next((r["error"] for r in reversed(recent) if r["error"]), None)
            out[name] = {"runs": len(recent), "failures": failures, "rate": round(rate, 2), "last_error": last_error}
    return out


def quiet(health: dict, now: datetime, days: int = 7) -> list[str]:
    """Sources that worked but returned zero items on every run in the window."""
    cutoff = (now - timedelta(days=days)).isoformat()
    out = []
    for name, runs in health.items():
        recent = [r for r in runs if r["at"] >= cutoff and r["ok"]]
        if len(recent) >= 2 and all(r["count"] == 0 for r in recent):
            out.append(name)
    return out
