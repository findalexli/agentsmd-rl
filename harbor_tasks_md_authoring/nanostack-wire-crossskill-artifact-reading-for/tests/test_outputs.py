"""Behavioral checks for nanostack-wire-crossskill-artifact-reading-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/nanostack")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plan/SKILL.md')
    assert '- `scope_mode` → if /think said "reduce," plan the smallest version. If "expand," plan bigger.' in text, "expected to find: " + '- `scope_mode` → if /think said "reduce," plan the smallest version. If "expand," plan bigger.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plan/SKILL.md')
    assert "- `premise_validated` → if false, flag it. Don't plan for an unvalidated premise." in text, "expected to find: " + "- `premise_validated` → if false, flag it. Don't plan for an unvalidated premise."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plan/SKILL.md')
    assert '- `key_risk` → add to your Risks section. This was already validated by /think.' in text, "expected to find: " + '- `key_risk` → add to your Risks section. This was already validated by /think.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('qa/SKILL.md')
    assert "If the plan specifies product standards (shadcn/ui, Tailwind, dark mode, specific component library), use those as your checklist. Don't guess what the UI should look like. The plan defines the spec. " in text, "expected to find: " + "If the plan specifies product standards (shadcn/ui, Tailwind, dark mode, specific component library), use those as your checklist. Don't guess what the UI should look like. The plan defines the spec. "[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('qa/SKILL.md')
    assert '**Read the plan artifact first:**' in text, "expected to find: " + '**Read the plan artifact first:**'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('qa/SKILL.md')
    assert 'bin/find-artifact.sh plan 2' in text, "expected to find: " + 'bin/find-artifact.sh plan 2'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('review/SKILL.md')
    assert '- **`risks[]`** → create a risk checklist. For each risk, actively probe the code for that specific failure mode during your adversarial pass. These risks were identified during planning and should be' in text, "expected to find: " + '- **`risks[]`** → create a risk checklist. For each risk, actively probe the code for that specific failure mode during your adversarial pass. These risks were identified during planning and should be'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('review/SKILL.md')
    assert '- **`out_of_scope[]`** → verify none of these were implemented. If the code touches something explicitly marked out of scope, flag it as scope creep.' in text, "expected to find: " + '- **`out_of_scope[]`** → verify none of these were implemented. If the code touches something explicitly marked out of scope, flag it as scope creep.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('review/SKILL.md')
    assert '- **`planned_files[]`** → used by scope drift check (below)' in text, "expected to find: " + '- **`planned_files[]`** → used by scope drift check (below)'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('security/SKILL.md')
    assert 'Then read project config: `bin/init-config.sh`. Use `detected` to scope which checks to run (skip Python checks in a Go project). Use `preferences.conflict_precedence` for cross-skill conflicts.' in text, "expected to find: " + 'Then read project config: `bin/init-config.sh`. Use `detected` to scope which checks to run (skip Python checks in a Go project). Use `preferences.conflict_precedence` for cross-skill conflicts.'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('security/SKILL.md')
    assert '- **`risks[]`** → treat each planned risk as a security hypothesis to verify. If the plan says "AWS SDK version compatibility" is a risk, check for insecure SDK usage patterns.' in text, "expected to find: " + '- **`risks[]`** → treat each planned risk as a security hypothesis to verify. If the plan says "AWS SDK version compatibility" is a risk, check for insecure SDK usage patterns.'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('security/SKILL.md')
    assert '- **`planned_files[]`** → focus your audit on these files and their dependencies. Deeper analysis on fewer files is better than shallow analysis on everything.' in text, "expected to find: " + '- **`planned_files[]`** → focus your audit on these files and their dependencies. Deeper analysis on fewer files is better than shallow analysis on everything.'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('ship/SKILL.md')
    assert 'If a review artifact exists, check that all **blocking** findings have been addressed. For each blocking finding, verify the code at the reported file and line no longer has the issue. If a blocking f' in text, "expected to find: " + 'If a review artifact exists, check that all **blocking** findings have been addressed. For each blocking finding, verify the code at the reported file and line no longer has the issue. If a blocking f'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('ship/SKILL.md')
    assert '**Verify review findings were resolved:**' in text, "expected to find: " + '**Verify review findings were resolved:**'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('ship/SKILL.md')
    assert 'bin/find-artifact.sh review 2' in text, "expected to find: " + 'bin/find-artifact.sh review 2'[:80]

