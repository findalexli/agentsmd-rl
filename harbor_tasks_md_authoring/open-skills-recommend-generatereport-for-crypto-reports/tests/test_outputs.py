"""Behavioral checks for open-skills-recommend-generatereport-for-crypto-reports (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/open-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/city-distance/SKILL.md')
    assert '> Calculate both the straight-line (Haversine) distance and the driving distance between {cityA} and {cityB} using free OpenStreetMap services. Return distances in km and optionally list major towns a' in text, "expected to find: " + '> Calculate both the straight-line (Haversine) distance and the driving distance between {cityA} and {cityB} using free OpenStreetMap services. Return distances in km and optionally list major towns a'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/city-distance/SKILL.md')
    assert 'const url = `https://routing.openstreetmap.de/routed-car/route/v1/driving/${paris.lon},${paris.lat};${berlin.lon},${berlin.lat}?overview=false`;' in text, "expected to find: " + 'const url = `https://routing.openstreetmap.de/routed-car/route/v1/driving/${paris.lon},${paris.lat};${berlin.lon},${berlin.lat}?overview=false`;'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/city-distance/SKILL.md')
    assert 'URL="https://routing.openstreetmap.de/routed-car/route/v1/driving/${CITY_A_LON},${CITY_A_LAT};${CITY_B_LON},${CITY_B_LAT}?overview=false"' in text, "expected to find: " + 'URL="https://routing.openstreetmap.de/routed-car/route/v1/driving/${CITY_A_LON},${CITY_A_LAT};${CITY_B_LON},${CITY_B_LAT}?overview=false"'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/get-crypto-price/SKILL.md')
    assert 'Agent note: When producing human-friendly reports, agents should use the `skills/generate-report` skill to produce formatted outputs (markdown or PDF). See `skills/generate-report/SKILL.md` for exampl' in text, "expected to find: " + 'Agent note: When producing human-friendly reports, agents should use the `skills/generate-report` skill to produce formatted outputs (markdown or PDF). See `skills/generate-report/SKILL.md` for exampl'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/get-crypto-price/SKILL.md')
    assert '> Use the generate-report skill to create a short Bitcoin price report (current price, 24h change, 7d change) in markdown and PDF. Include source URLs.' in text, "expected to find: " + '> Use the generate-report skill to create a short Bitcoin price report (current price, 24h change, 7d change) in markdown and PDF. Include source URLs.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/get-crypto-price/SKILL.md')
    assert 'Example agent prompt:' in text, "expected to find: " + 'Example agent prompt:'[:80]

