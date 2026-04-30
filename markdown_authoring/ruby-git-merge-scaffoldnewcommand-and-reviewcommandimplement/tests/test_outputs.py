"""Behavioral checks for ruby-git-merge-scaffoldnewcommand-and-reviewcommandimplement (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ruby-git")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/command-implementation/REFERENCE.md')
    assert '- [Rule 2 — SYNOPSIS does NOT show `--`: protect operands from flag misinterpretation](#rule-2--synopsis-does-not-show----protect-operands-from-flag-misinterpretation)' in text, "expected to find: " + '- [Rule 2 — SYNOPSIS does NOT show `--`: protect operands from flag misinterpretation](#rule-2--synopsis-does-not-show----protect-operands-from-flag-misinterpretation)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/command-implementation/REFERENCE.md')
    assert '- [Policy/output-control flag hardcoded as `literal` (neutrality violation)](#policyoutput-control-flag-hardcoded-as-literal-neutrality-violation)' in text, "expected to find: " + '- [Policy/output-control flag hardcoded as `literal` (neutrality violation)](#policyoutput-control-flag-hardcoded-as-literal-neutrality-violation)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/command-implementation/REFERENCE.md')
    assert '- [Options completeness — consult the latest-version docs first](#options-completeness--consult-the-latest-version-docs-first)' in text, "expected to find: " + '- [Options completeness — consult the latest-version docs first](#options-completeness--consult-the-latest-version-docs-first)'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/command-implementation/SKILL.md')
    assert 'description: "Scaffolds new and reviews existing Git::Commands::* classes with unit tests, integration tests, and YARD docs using the Base architecture. Use when creating a new command from scratch, u' in text, "expected to find: " + 'description: "Scaffolds new and reviews existing Git::Commands::* classes with unit tests, integration tests, and YARD docs using the Base architecture. Use when creating a new command from scratch, u'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/command-implementation/SKILL.md')
    assert 'bundle exec ruby -e "require \'rake\'; load \'Rakefile\'; puts Rake::Task[\'default:parallel\'].prerequisites"' in text, "expected to find: " + 'bundle exec ruby -e "require \'rake\'; load \'Rakefile\'; puts Rake::Task[\'default:parallel\'].prerequisites"'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/command-implementation/SKILL.md')
    assert '[Options completeness](REFERENCE.md#options-completeness--consult-the-latest-version-docs-first),' in text, "expected to find: " + '[Options completeness](REFERENCE.md#options-completeness--consult-the-latest-version-docs-first),'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/command-test-conventions/SKILL.md')
    assert '- [Command Implementation](../command-implementation/SKILL.md) — class' in text, "expected to find: " + '- [Command Implementation](../command-implementation/SKILL.md) — class'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/command-yard-documentation/SKILL.md')
    assert '[Command Implementation](../command-implementation/SKILL.md) skill, not YARD review.' in text, "expected to find: " + '[Command Implementation](../command-implementation/SKILL.md) skill, not YARD review.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/command-yard-documentation/SKILL.md')
    assert '- [Command Implementation](../command-implementation/SKILL.md) — class' in text, "expected to find: " + '- [Command Implementation](../command-implementation/SKILL.md) — class'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/extract-command-from-lib/SKILL.md')
    assert '- [Command Implementation](../command-implementation/SKILL.md) — generates and reviews `Git::Commands::*`' in text, "expected to find: " + '- [Command Implementation](../command-implementation/SKILL.md) — generates and reviews `Git::Commands::*`'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/extract-command-from-lib/SKILL.md')
    assert '[Command Implementation](../command-implementation/SKILL.md) skill. This produces:' in text, "expected to find: " + '[Command Implementation](../command-implementation/SKILL.md) skill. This produces:'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/extract-command-from-lib/SKILL.md')
    assert 'classes, unit tests, integration tests, and YARD docs (used in Step 4 if the' in text, "expected to find: " + 'classes, unit tests, integration tests, and YARD docs (used in Step 4 if the'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/project-context/SKILL.md')
    assert '- [Command Implementation](../command-implementation/SKILL.md) — generating and' in text, "expected to find: " + '- [Command Implementation](../command-implementation/SKILL.md) — generating and'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/project-context/SKILL.md')
    assert '[Command Implementation](../command-implementation/SKILL.md).' in text, "expected to find: " + '[Command Implementation](../command-implementation/SKILL.md).'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/project-context/SKILL.md')
    assert 'reviewing command classes in the layered architecture' in text, "expected to find: " + 'reviewing command classes in the layered architecture'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/refactor-command-to-commandlineresult/SKILL.md')
    assert 'See [Command Implementation](../command-implementation/SKILL.md) for the canonical phased rollout checklist' in text, "expected to find: " + 'See [Command Implementation](../command-implementation/SKILL.md) for the canonical phased rollout checklist'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/refactor-command-to-commandlineresult/SKILL.md')
    assert '- [Command Implementation](../command-implementation/SKILL.md) — canonical class-shape checklist, phased' in text, "expected to find: " + '- [Command Implementation](../command-implementation/SKILL.md) — canonical class-shape checklist, phased'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/review-arguments-dsl/CHECKLIST.md')
    assert 'and [`requires_git_version` convention](../command-implementation/REFERENCE.md#requires_git_version-convention). Briefly:' in text, "expected to find: " + 'and [`requires_git_version` convention](../command-implementation/REFERENCE.md#requires_git_version-convention). Briefly:'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/review-arguments-dsl/CHECKLIST.md')
    assert '[Exit status guidance](../command-implementation/REFERENCE.md#exit-status-guidance)' in text, "expected to find: " + '[Exit status guidance](../command-implementation/REFERENCE.md#exit-status-guidance)'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/review-arguments-dsl/CHECKLIST.md')
    assert 'be verified alongside DSL entries. The canonical rules live in [Command' in text, "expected to find: " + 'be verified alongside DSL entries. The canonical rules live in [Command'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/review-arguments-dsl/SKILL.md')
    assert '- [Command Implementation](../command-implementation/SKILL.md) — class structure, phased rollout gates, and' in text, "expected to find: " + '- [Command Implementation](../command-implementation/SKILL.md) — class structure, phased rollout gates, and'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/review-arguments-dsl/SKILL.md')
    assert 'Read the **entire** official git documentation online man page for the command' in text, "expected to find: " + 'Read the **entire** official git documentation online man page for the command'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/review-arguments-dsl/SKILL.md')
    assert 'Fetch this version from the URL `https://git-scm.com/docs/git-{command}`' in text, "expected to find: " + 'Fetch this version from the URL `https://git-scm.com/docs/git-{command}`'[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/review-backward-compatibility/SKILL.md')
    assert '- [Command Implementation](../command-implementation/SKILL.md) — class structure, phased rollout gates, and' in text, "expected to find: " + '- [Command Implementation](../command-implementation/SKILL.md) — class structure, phased rollout gates, and'[:80]


def test_signal_24():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/review-command-implementation/SKILL.md')
    assert '.github/skills/review-command-implementation/SKILL.md' in text, "expected to find: " + '.github/skills/review-command-implementation/SKILL.md'[:80]


def test_signal_25():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/review-command-tests/SKILL.md')
    assert '- [Command Implementation](../command-implementation/SKILL.md) — class' in text, "expected to find: " + '- [Command Implementation](../command-implementation/SKILL.md) — class'[:80]


def test_signal_26():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/review-cross-command-consistency/SKILL.md')
    assert '- [Command Implementation](../command-implementation/REFERENCE.md#phased-rollout-requirements) — canonical class-shape checklist, phased' in text, "expected to find: " + '- [Command Implementation](../command-implementation/REFERENCE.md#phased-rollout-requirements) — canonical class-shape checklist, phased'[:80]


def test_signal_27():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/review-cross-command-consistency/SKILL.md')
    assert 'See **[Command Implementation § Phased rollout requirements](../command-implementation/REFERENCE.md#phased-rollout-requirements)** for' in text, "expected to find: " + 'See **[Command Implementation § Phased rollout requirements](../command-implementation/REFERENCE.md#phased-rollout-requirements)** for'[:80]


def test_signal_28():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/reviewing-skills/SKILL.md')
    assert 'Using the Reviewing Skills skill, review .github/skills/command-implementation/.' in text, "expected to find: " + 'Using the Reviewing Skills skill, review .github/skills/command-implementation/.'[:80]

