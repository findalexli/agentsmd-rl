"""Behavioral checks for skills-add-sdk-deprecation-and-rebranding (markdown_authoring task).

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
    text = _read('.github/skills/skill-creator/SKILL.md')
    assert '> **⚠️ MIGRATION NOTICE**: The [Old Service Name] has been rebranded to **[New Service Name]**. While the package `old-package-name` remains available for compatibility, **new projects should use `new' in text, "expected to find: " + '> **⚠️ MIGRATION NOTICE**: The [Old Service Name] has been rebranded to **[New Service Name]**. While the package `old-package-name` remains available for compatibility, **new projects should use `new'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/skill-creator/SKILL.md')
    assert "> **This skill remains valid** for existing projects using `old-package-name`, but be aware you're using the legacy package name. The API patterns shown here are compatible with both packages." in text, "expected to find: " + "> **This skill remains valid** for existing projects using `old-package-name`, but be aware you're using the legacy package name. The API patterns shown here are compatible with both packages."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/skill-creator/SKILL.md')
    assert 'When an Azure SDK has been deprecated or rebranded, update skills to guide users toward the current package while maintaining backward compatibility:' in text, "expected to find: " + 'When an Azure SDK has been deprecated or rebranded, update skills to guide users toward the current package while maintaining backward compatibility:'[:80]

