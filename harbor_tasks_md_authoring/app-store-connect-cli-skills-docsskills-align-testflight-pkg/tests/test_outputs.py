"""Behavioral checks for app-store-connect-cli-skills-docsskills-align-testflight-pkg (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/app-store-connect-cli-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/asc-release-flow/SKILL.md')
    assert '- `asc publish appstore` currently supports `--ipa` workflows; for macOS `.pkg`, use `asc builds upload --pkg` + attach/submit steps below.' in text, "expected to find: " + '- `asc publish appstore` currently supports `--ipa` workflows; for macOS `.pkg`, use `asc builds upload --pkg` + attach/submit steps below.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/asc-release-flow/SKILL.md')
    assert '- `--pkg` automatically sets platform to `MAC_OS`.' in text, "expected to find: " + '- `--pkg` automatically sets platform to `MAC_OS`.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/asc-release-flow/SKILL.md')
    assert 'Upload the exported `.pkg` using `asc`:' in text, "expected to find: " + 'Upload the exported `.pkg` using `asc`:'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/asc-testflight-orchestration/SKILL.md')
    assert '- `asc testflight beta-testers add --app "APP_ID" --email "tester@example.com" --group "Beta Testers"`' in text, "expected to find: " + '- `asc testflight beta-testers add --app "APP_ID" --email "tester@example.com" --group "Beta Testers"`'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/asc-testflight-orchestration/SKILL.md')
    assert '- `asc testflight beta-testers invite --app "APP_ID" --email "tester@example.com"`' in text, "expected to find: " + '- `asc testflight beta-testers invite --app "APP_ID" --email "tester@example.com"`'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/asc-testflight-orchestration/SKILL.md')
    assert '- `asc testflight beta-groups create --app "APP_ID" --name "Beta Testers"`' in text, "expected to find: " + '- `asc testflight beta-groups create --app "APP_ID" --name "Beta Testers"`'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/asc-xcode-build/SKILL.md')
    assert '- For `.pkg` uploads, `--version` and `--build-number` are required (they are not auto-extracted like IPA uploads).' in text, "expected to find: " + '- For `.pkg` uploads, `--version` and `--build-number` are required (they are not auto-extracted like IPA uploads).'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/asc-xcode-build/SKILL.md')
    assert '- Add `--wait` if you want to wait for build processing to complete.' in text, "expected to find: " + '- Add `--wait` if you want to wait for build processing to complete.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/asc-xcode-build/SKILL.md')
    assert 'macOS apps export as `.pkg` files. Upload with `asc`:' in text, "expected to find: " + 'macOS apps export as `.pkg` files. Upload with `asc`:'[:80]

