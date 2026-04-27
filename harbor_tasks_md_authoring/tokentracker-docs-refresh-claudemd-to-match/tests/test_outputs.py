"""Behavioral checks for tokentracker-docs-refresh-claudemd-to-match (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/tokentracker")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**macOS App (`TokenTrackerBar/`)** — Native Swift 5.9 menu bar + widget app. Embeds a complete Node.js + tokentracker runtime (`EmbeddedServer/`, universal arm64+x64). Hosts the React dashboard via WK' in text, "expected to find: " + '**macOS App (`TokenTrackerBar/`)** — Native Swift 5.9 menu bar + widget app. Embeds a complete Node.js + tokentracker runtime (`EmbeddedServer/`, universal arm64+x64). Hosts the React dashboard via WK'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- `dashboard/src/ui/share/ShareModal.tsx` + `variants/BroadsheetCard.jsx` + `variants/AnnualReportCard.jsx` — Shareable screenshot cards (Broadsheet + Neon annual-report variant with glassmorphism). `' in text, "expected to find: " + '- `dashboard/src/ui/share/ShareModal.tsx` + `variants/BroadsheetCard.jsx` + `variants/AnnualReportCard.jsx` — Shareable screenshot cards (Broadsheet + Neon annual-report variant with glassmorphism). `'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- `TokenTrackerBar/Views/UsageTrendChart.swift` / `TopModelsView.swift` / `SummaryCardsView.swift` / `ActivityHeatmapView.swift` — Native panel components. Charts module is hidden on macOS < 13 (the p' in text, "expected to find: " + '- `TokenTrackerBar/Views/UsageTrendChart.swift` / `TopModelsView.swift` / `SummaryCardsView.swift` / `ActivityHeatmapView.swift` — Native panel components. Charts module is hidden on macOS < 13 (the p'[:80]

