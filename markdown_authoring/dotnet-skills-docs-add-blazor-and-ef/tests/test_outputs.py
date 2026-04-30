"""Behavioral checks for dotnet-skills-docs-add-blazor-and-ef (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/dotnet-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/crap-analysis/SKILL.md')
    assert '<ExcludeByAttribute>Obsolete,GeneratedCodeAttribute,CompilerGeneratedAttribute,ExcludeFromCodeCoverageAttribute</ExcludeByAttribute>' in text, "expected to find: " + '<ExcludeByAttribute>Obsolete,GeneratedCodeAttribute,CompilerGeneratedAttribute,ExcludeFromCodeCoverageAttribute</ExcludeByAttribute>'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/crap-analysis/SKILL.md')
    assert '| `ExcludeByAttribute` | Skip generated, obsolete, and explicitly excluded code (includes `ExcludeFromCodeCoverageAttribute`) |' in text, "expected to find: " + '| `ExcludeByAttribute` | Skip generated, obsolete, and explicitly excluded code (includes `ExcludeFromCodeCoverageAttribute`) |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/crap-analysis/SKILL.md')
    assert '<ExcludeByFile>**/obj/**/*,**/*.g.cs,**/*.designer.cs,**/*.razor.g.cs,**/*.razor.css.g.cs,**/Migrations/**/*</ExcludeByFile>' in text, "expected to find: " + '<ExcludeByFile>**/obj/**/*,**/*.g.cs,**/*.designer.cs,**/*.razor.g.cs,**/*.razor.css.g.cs,**/Migrations/**/*</ExcludeByFile>'[:80]

