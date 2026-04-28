"""Behavioral checks for butane-opencodeskills (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/butane")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/add-sugar/SKILL.md')
    assert "- **Config merging** (recommended): Generate a fresh Ignition config struct, then use `baseutil.MergeTranslatedConfigs()` to merge with the user's config. The desugared struct is the merge parent, use" in text, "expected to find: " + "- **Config merging** (recommended): Generate a fresh Ignition config struct, then use `baseutil.MergeTranslatedConfigs()` to merge with the user's config. The desugared struct is the merge parent, use"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/add-sugar/SKILL.md')
    assert 'The pattern is the same, but the processing function is called from the base `ToIgn3_7Unvalidated()` and operates on base types. When modifying translation at the base level, you may need to:' in text, "expected to find: " + 'The pattern is the same, but the processing function is called from the base `ToIgn3_7Unvalidated()` and operates on base types. When modifying translation at the base level, you may need to:'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/add-sugar/SKILL.md')
    assert '**IMPORTANT**: The Ignition version in test expectations (e.g., `"3.7.0-experimental"`) must match the version used in the spec\'s translate.go. Check the existing tests for the correct value.' in text, "expected to find: " + '**IMPORTANT**: The Ignition version in test expectations (e.g., `"3.7.0-experimental"`) must match the version used in the spec\'s translate.go. Check the existing tests for the correct value.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/remove-feature/SKILL.md')
    assert 'Read the file and identify the test case block for the removed feature. Test cases are typically marked with a comment like `// Test Grub config` and consist of a struct literal in the test table.' in text, "expected to find: " + 'Read the file and identify the test case block for the removed feature. Test cases are typically marked with a comment like `// Test Grub config` and consist of a struct literal in the test table.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/remove-feature/SKILL.md')
    assert '**Expected outcome**: The `docs/config-openshift-{version}.md` file is updated, with the removed feature\'s fields now showing "Unsupported" instead of their original descriptions.' in text, "expected to find: " + '**Expected outcome**: The `docs/config-openshift-{version}.md` file is updated, with the removed feature\'s fields now showing "Unsupported" instead of their original descriptions.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/remove-feature/SKILL.md')
    assert '- ❌ **Removing schema definitions** - this skill only removes translation/test code; schemas are inherited from parent and remain (they just become dead code for that version)' in text, "expected to find: " + '- ❌ **Removing schema definitions** - this skill only removes translation/test code; schemas are inherited from parent and remain (they just become dead code for that version)'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/stabilize-spec/SKILL.md')
    assert '**Note**: This step implements lines 20-21 (base) and 28-30 (distro) from `.github/ISSUE_TEMPLATE/stabilize-checklist.md`.' in text, "expected to find: " + '**Note**: This step implements lines 20-21 (base) and 28-30 (distro) from `.github/ISSUE_TEMPLATE/stabilize-checklist.md`.'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/stabilize-spec/SKILL.md')
    assert '6. Copying the newly stabilized version to create the next experimental version (e.g., `v1_7` → `v1_8_exp`)' in text, "expected to find: " + '6. Copying the newly stabilized version to create the next experimental version (e.g., `v1_7` → `v1_8_exp`)'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/stabilize-spec/SKILL.md')
    assert '- Base specs: schema.go, translate.go, translate_test.go, util.go, validate.go, validate_test.go (6 files)' in text, "expected to find: " + '- Base specs: schema.go, translate.go, translate_test.go, util.go, validate.go, validate_test.go (6 files)'[:80]

