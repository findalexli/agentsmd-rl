"""Behavioral checks for asm-featskills-add-skillupstreampr-for-contributing (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/asm")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/skill-upstream-pr/SKILL.md')
    assert "You are contributing quality improvements to someone else's open-source skill. The workflow is: fork → clone → improve via `skill-auto-improver` → push to fork → open a friendly suggestion PR upstream" in text, "expected to find: " + "You are contributing quality improvements to someone else's open-source skill. The workflow is: fork → clone → improve via `skill-auto-improver` → push to fork → open a friendly suggestion PR upstream"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/skill-upstream-pr/SKILL.md')
    assert "Compute deltas. If the overall score did not improve by at least 3 points **or** no category moved from below 8 to at least 8, stop and tell the user — the change isn't meaningful enough to justify a " in text, "expected to find: " + "Compute deltas. If the overall score did not improve by at least 3 points **or** no category moved from below 8 to at least 8, stop and tell the user — the change isn't meaningful enough to justify a "[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/skill-upstream-pr/SKILL.md')
    assert 'description: "Improve an open-source GitHub skill and open a friendly suggestion PR upstream: fork, run skill-auto-improver, attach asm eval before/after metrics. Don\'t use for local-only skills, auth' in text, "expected to find: " + 'description: "Improve an open-source GitHub skill and open a friendly suggestion PR upstream: fork, run skill-auto-improver, attach asm eval before/after metrics. Don\'t use for local-only skills, auth'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/skill-upstream-pr/docs/README.md')
    assert '> Contribute improvements to an open-source skill on GitHub: evaluate it, lift its scores via `skill-auto-improver`, and open a friendly suggestion PR back to the upstream author with a before/after m' in text, "expected to find: " + '> Contribute improvements to an open-source skill on GitHub: evaluate it, lift its scores via `skill-auto-improver`, and open a friendly suggestion PR back to the upstream author with a before/after m'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/skill-upstream-pr/docs/README.md')
    assert "Don't use for: local skills you own (use `skill-auto-improver` directly), authoring new skills (use `skill-creator`), or publishing to the ASM registry (use `asm publish`)." in text, "expected to find: " + "Don't use for: local skills you own (use `skill-auto-improver` directly), authoring new skills (use `skill-creator`), or publishing to the ASM registry (use `asm publish`)."[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/skill-upstream-pr/docs/README.md')
    assert '| Say this...                                               | Skill will...                                           |' in text, "expected to find: " + '| Say this...                                               | Skill will...                                           |'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/skill-upstream-pr/references/pr-template.md')
    assert 'Hi! 👋 I came across **<skill-name>** while browsing skills and really appreciated <one specific thing you liked>. Wanted to share a few suggestions that surfaced when I ran the skill through [`asm eva' in text, "expected to find: " + 'Hi! 👋 I came across **<skill-name>** while browsing skills and really appreciated <one specific thing you liked>. Wanted to share a few suggestions that surfaced when I ran the skill through [`asm eva'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/skill-upstream-pr/references/pr-template.md')
    assert '<One or two sentences describing the main focus of the changes. E.g. "Tightened the description for better triggering, added an Acceptance Criteria section, and moved the long example list into `refer' in text, "expected to find: " + '<One or two sentences describing the main focus of the changes. E.g. "Tightened the description for better triggering, added an Acceptance Criteria section, and moved the long example list into `refer'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/skill-upstream-pr/references/pr-template.md')
    assert '- **<category>** — <human-readable reason, e.g. "The description was missing a \'Don\'t use for\' clause, which helps Claude skip the skill on adjacent queries. Added one naming the nearby domains.">' in text, "expected to find: " + '- **<category>** — <human-readable reason, e.g. "The description was missing a \'Don\'t use for\' clause, which helps Claude skip the skill on adjacent queries. Added one naming the nearby domains.">'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/skill-upstream-pr/references/tone-guide.md')
    assert '> Hi! 👋 I came across **code-review** while browsing the collection and really liked how the detail-level tiers are structured. Wanted to share a few small suggestions that came up when I ran it throu' in text, "expected to find: " + '> Hi! 👋 I came across **code-review** while browsing the collection and really liked how the detail-level tiers are structured. Wanted to share a few small suggestions that came up when I ran it throu'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/skill-upstream-pr/references/tone-guide.md')
    assert '- Good: "Added a \'Don\'t use for\' clause — helps Claude skip this skill on Vue/Svelte queries so it triggers more reliably on the React ones you actually want."' in text, "expected to find: " + '- Good: "Added a \'Don\'t use for\' clause — helps Claude skip this skill on Vue/Svelte queries so it triggers more reliably on the React ones you actually want."'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/skill-upstream-pr/references/tone-guide.md')
    assert '5. **No jargon dumps.** Translate eval-speak into plain English. A maintainer may not know what "context efficiency" means in `asm eval` terms.' in text, "expected to find: " + '5. **No jargon dumps.** Translate eval-speak into plain English. A maintainer may not know what "context efficiency" means in `asm eval` terms.'[:80]

