"""Behavioral checks for csharp-sdk-releasenotes-skill-harvest-coauthoredby-trailers (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/csharp-sdk")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/prepare-release/SKILL.md')
    assert '- For Copilot-authored PRs, additionally check the `copilot_work_started` timeline event to identify the triggering user. That person becomes the primary author; `@Copilot` becomes a co-author.' in text, "expected to find: " + '- For Copilot-authored PRs, additionally check the `copilot_work_started` timeline event to identify the triggering user. That person becomes the primary author; `@Copilot` becomes a co-author.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/prepare-release/SKILL.md')
    assert '- **Copilot timeline missing**: fall back to `Co-authored-by` trailers to determine whether `@Copilot` should be a co-author; if still unclear, use `@Copilot` as primary author' in text, "expected to find: " + '- **Copilot timeline missing**: fall back to `Co-authored-by` trailers to determine whether `@Copilot` should be a co-author; if still unclear, use `@Copilot` as primary author'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/prepare-release/SKILL.md')
    assert '- Harvest `Co-authored-by` trailers from **all commits** in each PR (not just the merge commit) to identify co-authors. Do this for every PR regardless of primary author.' in text, "expected to find: " + '- Harvest `Co-authored-by` trailers from **all commits** in each PR (not just the merge commit) to identify co-authors. Do this for every PR regardless of primary author.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/prepare-release/references/categorization.md')
    assert 'For Copilot-authored PRs, additionally identify who triggered Copilot using the `copilot_work_started` timeline event on the PR. That person becomes the primary author, and @Copilot becomes a co-autho' in text, "expected to find: " + 'For Copilot-authored PRs, additionally identify who triggered Copilot using the `copilot_work_started` timeline event on the PR. That person becomes the primary author, and @Copilot becomes a co-autho'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/prepare-release/references/categorization.md')
    assert 'For PRs with co-authors (harvested from `Co-authored-by` trailers across **all commits** in the PR, not just the merge commit):' in text, "expected to find: " + 'For PRs with co-authors (harvested from `Co-authored-by` trailers across **all commits** in the PR, not just the merge commit):'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/publish-release/SKILL.md')
    assert '- **Copilot timeline missing**: fall back to `Co-authored-by` trailers to determine whether `@Copilot` should be a co-author; if still unclear, use `@Copilot` as primary author' in text, "expected to find: " + '- **Copilot timeline missing**: fall back to `Co-authored-by` trailers to determine whether `@Copilot` should be a co-author; if still unclear, use `@Copilot` as primary author'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/publish-release/SKILL.md')
    assert '3. **Re-attribute** co-authors for any new PRs by harvesting `Co-authored-by` trailers from all commits in each PR.' in text, "expected to find: " + '3. **Re-attribute** co-authors for any new PRs by harvesting `Co-authored-by` trailers from all commits in each PR.'[:80]

