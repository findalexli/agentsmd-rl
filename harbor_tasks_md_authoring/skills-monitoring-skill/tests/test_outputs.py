"""Behavioral checks for skills-monitoring-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-monitoring/SKILL.md')
    assert 'description: "Guides Qdrant monitoring and observability setup. Use when someone asks \'how to monitor Qdrant\', \'what metrics to track\', \'is Qdrant healthy\', \'optimizer stuck\', \'why is memory growing\',' in text, "expected to find: " + 'description: "Guides Qdrant monitoring and observability setup. Use when someone asks \'how to monitor Qdrant\', \'what metrics to track\', \'is Qdrant healthy\', \'optimizer stuck\', \'why is memory growing\','[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-monitoring/SKILL.md')
    assert 'Qdrant monitoring allows tracking performance and health of your deployment, and identifying issues before they become outages. First determine whether you need to set up monitoring or diagnose an act' in text, "expected to find: " + 'Qdrant monitoring allows tracking performance and health of your deployment, and identifying issues before they become outages. First determine whether you need to set up monitoring or diagnose an act'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-monitoring/SKILL.md')
    assert 'Optimizer stuck, memory growth, slow requests. Using metrics to diagnose active production issues. [Debugging with Metrics](debugging/SKILL.md)' in text, "expected to find: " + 'Optimizer stuck, memory growth, slow requests. Using metrics to diagnose active production issues. [Debugging with Metrics](debugging/SKILL.md)'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-monitoring/debugging/SKILL.md')
    assert 'description: "Diagnoses Qdrant production issues using metrics and observability tools. Use when someone reports \'optimizer stuck\', \'indexing too slow\', \'memory too high\', \'OOM crash\', \'queries are sl' in text, "expected to find: " + 'description: "Diagnoses Qdrant production issues using metrics and observability tools. Use when someone reports \'optimizer stuck\', \'indexing too slow\', \'memory too high\', \'OOM crash\', \'queries are sl'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-monitoring/debugging/SKILL.md')
    assert '- Qdrant uses two types of RAM: resident memory (data structures, quantized vectors) and OS page cache (cached disk reads). Page cache filling available RAM is normal. [Memory article](https://qdrant.' in text, "expected to find: " + '- Qdrant uses two types of RAM: resident memory (data structures, quantized vectors) and OS page cache (cached disk reads). Page cache filling available RAM is normal. [Memory article](https://qdrant.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-monitoring/debugging/SKILL.md')
    assert '- Estimate expected memory: `num_vectors * dimensions * 4 bytes * 1.5` for vectors, plus payload and index overhead [Capacity planning](https://qdrant.tech/documentation/guides/capacity-planning/)' in text, "expected to find: " + '- Estimate expected memory: `num_vectors * dimensions * 4 bytes * 1.5` for vectors, plus payload and index overhead [Capacity planning](https://qdrant.tech/documentation/guides/capacity-planning/)'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-monitoring/setup/SKILL.md')
    assert 'description: "Guides Qdrant monitoring setup including Prometheus scraping, health probes, Hybrid Cloud metrics, alerting, and log centralization. Use when someone asks \'how to set up monitoring\', \'Pr' in text, "expected to find: " + 'description: "Guides Qdrant monitoring setup including Prometheus scraping, health probes, Hybrid Cloud metrics, alerting, and log centralization. Use when someone asks \'how to set up monitoring\', \'Pr'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-monitoring/setup/SKILL.md')
    assert '- Audit logs (v1.17+) write to local filesystem (`/qdrant/storage/audit/`), not stdout. Mount a Persistent Volume and deploy a sidecar container to tail these files to stdout so DaemonSets can pick th' in text, "expected to find: " + '- Audit logs (v1.17+) write to local filesystem (`/qdrant/storage/audit/`), not stdout. Mount a Persistent Volume and deploy a sidecar container to tail these files to stdout so DaemonSets can pick th'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-monitoring/setup/SKILL.md')
    assert 'Do not just scrape Qdrant nodes. In Hybrid Cloud, you manage the Kubernetes data plane. You must also scrape the cluster-exporter and operator pods for full cluster visibility and operator state.' in text, "expected to find: " + 'Do not just scrape Qdrant nodes. In Hybrid Cloud, you manage the Kubernetes data plane. You must also scrape the cluster-exporter and operator pods for full cluster visibility and operator state.'[:80]

