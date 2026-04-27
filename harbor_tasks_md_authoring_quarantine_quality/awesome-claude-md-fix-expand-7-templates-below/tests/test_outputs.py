"""Behavioral checks for awesome-claude-md-fix-expand-7-templates-below (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/awesome-claude-md")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('templates/conventional-changelog/CLAUDE.md')
    assert '- Test changelog generates with correct sections for features, fixes, and breaking changes.' in text, "expected to find: " + '- Test changelog generates with correct sections for features, fixes, and breaking changes.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('templates/conventional-changelog/CLAUDE.md')
    assert '- Config: `conventional-changelog.config.js` or `.changelogrc` at project root' in text, "expected to find: " + '- Config: `conventional-changelog.config.js` or `.changelogrc` at project root'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('templates/conventional-changelog/CLAUDE.md')
    assert '- Test `releaseCount: 0` regenerates the full changelog from all commits.' in text, "expected to find: " + '- Test `releaseCount: 0` regenerates the full changelog from all commits.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('templates/knip/CLAUDE.md')
    assert '- Config: `knip.config.ts`, `knip.json`, or `knip.config.js` at project root' in text, "expected to find: " + '- Config: `knip.config.ts`, `knip.json`, or `knip.config.js` at project root'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('templates/knip/CLAUDE.md')
    assert '- Workspace configs: one `knip.config.ts` per workspace root in monorepos' in text, "expected to find: " + '- Workspace configs: one `knip.config.ts` per workspace root in monorepos'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('templates/knip/CLAUDE.md')
    assert '- Test `--fix` removes correct code without breaking imports.' in text, "expected to find: " + '- Test `--fix` removes correct code without breaking imports.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('templates/lint-staged/CLAUDE.md')
    assert '- Config: `.lintstagedrc.js`, `lint-staged.config.js`, or `lint-staged` field in `package.json`' in text, "expected to find: " + '- Config: `.lintstagedrc.js`, `lint-staged.config.js`, or `lint-staged` field in `package.json`'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('templates/lint-staged/CLAUDE.md')
    assert '- Test with a staged file that has a lint error and verify commit is blocked.' in text, "expected to find: " + '- Test with a staged file that has a lint error and verify commit is blocked.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('templates/lint-staged/CLAUDE.md')
    assert '- Test commit is blocked when unfixable errors exist in staged files.' in text, "expected to find: " + '- Test commit is blocked when unfixable errors exist in staged files.'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('templates/oklch-colors/CLAUDE.md')
    assert '- Test OKLCH colors render correctly in browsers supporting the `oklch()` function.' in text, "expected to find: " + '- Test OKLCH colors render correctly in browsers supporting the `oklch()` function.'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('templates/oklch-colors/CLAUDE.md')
    assert '- Theme files: `theme.css` or `tokens.css` for OKLCH color definitions' in text, "expected to find: " + '- Theme files: `theme.css` or `tokens.css` for OKLCH color definitions'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('templates/oklch-colors/CLAUDE.md')
    assert '- Test gradients appear smooth compared to equivalent HSL gradients.' in text, "expected to find: " + '- Test gradients appear smooth compared to equivalent HSL gradients.'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('templates/renovate/CLAUDE.md')
    assert '- Config: `renovate.json`, `.github/renovate.json`, or `renovate.json5` at project root' in text, "expected to find: " + '- Config: `renovate.json`, `.github/renovate.json`, or `renovate.json5` at project root'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('templates/renovate/CLAUDE.md')
    assert '- Presets: shared configs via `extends` from npm packages or GitHub repos' in text, "expected to find: " + '- Presets: shared configs via `extends` from npm packages or GitHub repos'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('templates/renovate/CLAUDE.md')
    assert '- Test private package updates resolve through configured registries.' in text, "expected to find: " + '- Test private package updates resolve through configured registries.'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('templates/simple-git-hooks/CLAUDE.md')
    assert '- Test hooks reinstall correctly after `rm -rf .git/hooks` and `npx simple-git-hooks`.' in text, "expected to find: " + '- Test hooks reinstall correctly after `rm -rf .git/hooks` and `npx simple-git-hooks`.'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('templates/simple-git-hooks/CLAUDE.md')
    assert '- Config: `simple-git-hooks` field in `package.json` — no separate config file needed' in text, "expected to find: " + '- Config: `simple-git-hooks` field in `package.json` — no separate config file needed'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('templates/simple-git-hooks/CLAUDE.md')
    assert '- Test with multiple hooks configured (pre-commit and commit-msg simultaneously).' in text, "expected to find: " + '- Test with multiple hooks configured (pre-commit and commit-msg simultaneously).'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('templates/verdaccio/CLAUDE.md')
    assert '- Test uplink fallback when the upstream npmjs registry is unreachable.' in text, "expected to find: " + '- Test uplink fallback when the upstream npmjs registry is unreachable.'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('templates/verdaccio/CLAUDE.md')
    assert '- Test `max_body_size` rejects packages exceeding the configured limit.' in text, "expected to find: " + '- Test `max_body_size` rejects packages exceeding the configured limit.'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('templates/verdaccio/CLAUDE.md')
    assert '- Test publishing and installing private scoped packages end-to-end.' in text, "expected to find: " + '- Test publishing and installing private scoped packages end-to-end.'[:80]

