"""Behavioral checks for documentation-add-charting-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/documentation")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('03 Writing Algorithms/36 Charting/SKILL.md')
    assert 'description: Use when adding or reviewing custom charts in a QuantConnect/LEAN algorithm (self.plot, self.plot_indicator, Chart/Series, CandlestickSeries). Covers SeriesType selection, series index fo' in text, "expected to find: " + 'description: Use when adding or reviewing custom charts in a QuantConnect/LEAN algorithm (self.plot, self.plot_indicator, Chart/Series, CandlestickSeries). Covers SeriesType selection, series index fo'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('03 Writing Algorithms/36 Charting/SKILL.md')
    assert '**`plot_indicator` is the right default at daily or hourly resolution** — update frequency naturally fits under the cap (daily: ~250/yr; US Equities hourly: ~7/day; 24h Crypto hourly: 24/day — run the' in text, "expected to find: " + '**`plot_indicator` is the right default at daily or hourly resolution** — update frequency naturally fits under the cap (daily: ~250/yr; US Equities hourly: ~7/day; 24h Crypto hourly: 24/day — run the'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('03 Writing Algorithms/36 Charting/SKILL.md')
    assert "4. **For dense structured data you'll analyze in Research, use the Object Store** — accumulate rows in memory and `object_store.save(key, content)` in `on_end_of_algorithm`, then read from a notebook." in text, "expected to find: " + "4. **For dense structured data you'll analyze in Research, use the Object Store** — accumulate rows in memory and `object_store.save(key, content)` in `on_end_of_algorithm`, then read from a notebook."[:80]

