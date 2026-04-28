"""Behavioral checks for cityenergyanalyst-create-agentmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cityenergyanalyst")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "In `databases/sg/assemblies/supply/supply_electricity.csv`'s CAPEX_USD2015kW and in `components/feedstocks/feedstocks_library/grid.csv`'s opex_var_buy_usd2015kWh and opex_var_sell_usd2015kwh. I believ" in text, "expected to find: " + "In `databases/sg/assemblies/supply/supply_electricity.csv`'s CAPEX_USD2015kW and in `components/feedstocks/feedstocks_library/grid.csv`'s opex_var_buy_usd2015kWh and opex_var_sell_usd2015kwh. I believ"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "My understanding is .csv files in components/conversion make up the csv files in assemblies/supply. However, I saw Supply_hotwater.csv has electrical boiler while BOILERS.csv does have BO5. Aren't the" in text, "expected to find: " + "My understanding is .csv files in components/conversion make up the csv files in assemblies/supply. However, I saw Supply_hotwater.csv has electrical boiler while BOILERS.csv does have BO5. Aren't the"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This document contains frequently asked questions and detailed explanations about the City Energy Analyst (CEA) database structure, calculations, and relationships between different data files.' in text, "expected to find: " + 'This document contains frequently asked questions and detailed explanations about the City Energy Analyst (CEA) database structure, calculations, and relationships between different data files.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

