"""Behavioral checks for waf-detector-chore-add-securityaudit-testdashboard-and (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/waf-detector")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/security-audit.md')
    assert '1. **Dependency scan**: Run `cargo audit` (install with `cargo install cargo-audit` if missing)' in text, "expected to find: " + '1. **Dependency scan**: Run `cargo audit` (install with `cargo install cargo-audit` if missing)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/security-audit.md')
    assert '5. **Report**: Output findings with severity (CRITICAL/HIGH/MEDIUM/LOW) and remediation steps' in text, "expected to find: " + '5. **Report**: Output findings with severity (CRITICAL/HIGH/MEDIUM/LOW) and remediation steps'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/security-audit.md')
    assert '4. **Test coverage gaps**: Identify security-critical paths without test coverage' in text, "expected to find: " + '4. **Test coverage gaps**: Identify security-critical paths without test coverage'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/test-dashboard.md')
    assert '- [ ] **Detect tab**: Single URL scan — enter `https://cloudflare.com`, click Scan, verify CloudFlare detected' in text, "expected to find: " + '- [ ] **Detect tab**: Single URL scan — enter `https://cloudflare.com`, click Scan, verify CloudFlare detected'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/test-dashboard.md')
    assert '- [ ] **Evidence**: Click "View Evidence" — verify items expand/collapse, no `Some(...)` or `None` in data' in text, "expected to find: " + '- [ ] **Evidence**: Click "View Evidence" — verify items expand/collapse, no `Some(...)` or `None` in data'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/test-dashboard.md')
    assert '- [ ] **Responsive**: Resize to 390px (mobile), 768px (tablet), 1440px (desktop) — verify layout adapts' in text, "expected to find: " + '- [ ] **Responsive**: Resize to 390px (mobile), 768px (tablet), 1440px (desktop) — verify layout adapts'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/validate-build.md')
    assert 'Report pass/fail for each step with counts (e.g., "298 tests passed"). Do not truncate test output if there are failures.' in text, "expected to find: " + 'Report pass/fail for each step with counts (e.g., "298 tests passed"). Do not truncate test output if there are failures.'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/validate-build.md')
    assert '2. `cargo clippy --all-targets --all-features -- -D warnings` — lint with strict warnings' in text, "expected to find: " + '2. `cargo clippy --all-targets --all-features -- -D warnings` — lint with strict warnings'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/validate-build.md')
    assert 'description: Full build validation — compile, test, lint, and verify' in text, "expected to find: " + 'description: Full build validation — compile, test, lint, and verify'[:80]

