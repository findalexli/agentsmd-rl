"""Behavioral checks for exram.gremlinq-add-copilotinstructionsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/exram.gremlinq")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Each provider follows a consistent pattern: a core project (`Providers.X`) and an ASP.NET integration project (`Providers.X.AspNet`). Tests mirror this with `Providers.X.Tests` and `Providers.X.AspNet' in text, "expected to find: " + 'Each provider follows a consistent pattern: a core project (`Providers.X`) and an ASP.NET integration project (`Providers.X.AspNet`). Tests mirror this with `Providers.X.Tests` and `Providers.X.AspNet'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'ExRam.Gremlinq is a .NET object-graph-mapper (OGM) for Apache TinkerPop™ Gremlin-enabled graph databases. It translates strongly-typed C# LINQ-style queries into Gremlin bytecode/scripts and handles s' in text, "expected to find: " + 'ExRam.Gremlinq is a .NET object-graph-mapper (OGM) for Apache TinkerPop™ Gremlin-enabled graph databases. It translates strongly-typed C# LINQ-style queries into Gremlin bytecode/scripts and handles s'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '`test/PublicApi.Tests` generates and verifies the public API surface of every src assembly. If you add/remove/change public types or members, the corresponding `.verified.cs` files must be updated. Th' in text, "expected to find: " + '`test/PublicApi.Tests` generates and verifies the public API surface of every src assembly. If you add/remove/change public types or members, the corresponding `.verified.cs` files must be updated. Th'[:80]

