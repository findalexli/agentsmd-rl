"""Minimal CTRF JSON reporter so the harness can introspect per-test results."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path


def pytest_configure(config):
    config._ctrf_start_ms = int(time.time() * 1000)


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    entries = []
    seen = set()
    status_map = {
        "passed": "passed",
        "failed": "failed",
        "error": "failed",
        "skipped": "skipped",
    }
    for stats_key, ctrf_status in status_map.items():
        for rep in terminalreporter.stats.get(stats_key, []):
            when = getattr(rep, "when", "call")
            if ctrf_status == "passed" and when != "call":
                continue
            nodeid = getattr(rep, "nodeid", "<unknown>")
            if nodeid in seen:
                continue
            seen.add(nodeid)
            duration = getattr(rep, "duration", 0.0)
            longrepr = getattr(rep, "longrepr", "")
            entries.append({
                "name": nodeid,
                "status": ctrf_status,
                "duration": int(duration * 1000),
                "message": str(longrepr) if longrepr else "",
            })

    summary = {
        "tests": len(entries),
        "passed": sum(1 for e in entries if e["status"] == "passed"),
        "failed": sum(1 for e in entries if e["status"] == "failed"),
        "skipped": sum(1 for e in entries if e["status"] == "skipped"),
        "pending": 0,
        "other": 0,
        "start": config._ctrf_start_ms,
        "stop": int(time.time() * 1000),
    }
    payload = {
        "results": {
            "tool": {"name": "pytest"},
            "summary": summary,
            "tests": entries,
        }
    }
    out = Path(os.environ.get("CTRF_OUTPUT", "/logs/verifier/ctrf.json"))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2))


def pytest_collection_modifyitems(config, items):
    order = [
        "test_signal_cancellation_resource_and_analyzer_concurrent",
        "test_signal_cancellation_language_runtimes_concurrent",
        "test_signal_cancellation_passes_deadline_context",
        "test_existing_plugin_unit_tests",
        "test_plugin_package_builds",
    ]

    def keyfn(item):
        try:
            return order.index(item.name)
        except ValueError:
            return len(order)

    items.sort(key=keyfn)
