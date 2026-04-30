"""Behavioral checks for premailer.net-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/premailer.net")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'The .sln and all projects live in the nested `PreMailer.Net/` folder, not the repo root. **Run all `dotnet` commands from `./PreMailer.Net/`** (matches `working-directory` in `.github/workflows/dotnet' in text, "expected to find: " + 'The .sln and all projects live in the nested `PreMailer.Net/` folder, not the repo root. **Run all `dotnet` commands from `./PreMailer.Net/`** (matches `working-directory` in `.github/workflows/dotnet'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Library multi-targets **`netstandard2.0;net461`** — keep code compatible with both. No C# nullable reference types in the library (only Benchmarks has `<Nullable>enable</Nullable>`).' in text, "expected to find: " + '- Library multi-targets **`netstandard2.0;net461`** — keep code compatible with both. No C# nullable reference types in the library (only Benchmarks has `<Nullable>enable</Nullable>`).'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Library depends only on **AngleSharp 1.4.0**. The DOM is an `IHtmlDocument`; expose it via `PreMailer.Document` (see README "Custom DOM Processing").' in text, "expected to find: " + '- Library depends only on **AngleSharp 1.4.0**. The DOM is an `IHtmlDocument`; expose it via `PreMailer.Document` (see README "Custom DOM Processing").'[:80]

