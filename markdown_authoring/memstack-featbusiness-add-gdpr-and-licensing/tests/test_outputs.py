"""Behavioral checks for memstack-featbusiness-add-gdpr-and-licensing (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/memstack")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/business/gdpr/SKILL.md')
    assert 'description: "Use this skill when the user says \'GDPR\', \'data protection\', \'privacy compliance\', \'DPA\', \'DSAR\', \'data subject request\', \'cookie consent\', \'privacy audit\', \'CCPA\', or asks \'do I need GD' in text, "expected to find: " + 'description: "Use this skill when the user says \'GDPR\', \'data protection\', \'privacy compliance\', \'DPA\', \'DSAR\', \'data subject request\', \'cookie consent\', \'privacy audit\', \'CCPA\', or asks \'do I need GD'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/business/gdpr/SKILL.md')
    assert '- **Lv.1** — Base: repo-driven scan across schemas/forms/DTOs/auth/analytics/cookies/logging/third parties, sensitivity classification (identifier/financial/location/behavioral/Art 9/Art 8/Art 10), ve' in text, "expected to find: " + '- **Lv.1** — Base: repo-driven scan across schemas/forms/DTOs/auth/analytics/cookies/logging/third parties, sensitivity classification (identifier/financial/location/behavioral/Art 9/Art 8/Art 10), ve'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/business/gdpr/SKILL.md')
    assert '[2–4 sentences referencing the specific data found in Step 1: e.g. "The repo collects user emails, phone numbers, dates of birth, and self-reported medical conditions through src/forms/Health.tsx. The' in text, "expected to find: " + '[2–4 sentences referencing the specific data found in Step 1: e.g. "The repo collects user emails, phone numbers, dates of birth, and self-reported medical conditions through src/forms/Health.tsx. The'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/business/licensing/SKILL.md')
    assert 'description: "Use this skill when the user says \'licensing\', \'license audit\', \'can I use this commercially\', \'OSS license check\', \'license compatibility\', \'GPL\', \'MIT\', \'AGPL\', \'copyleft\'. Scans the r' in text, "expected to find: " + 'description: "Use this skill when the user says \'licensing\', \'license audit\', \'can I use this commercially\', \'OSS license check\', \'license compatibility\', \'GPL\', \'MIT\', \'AGPL\', \'copyleft\'. Scans the r'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/business/licensing/SKILL.md')
    assert '- **Lv.1** — Base: distribution-model question, multi-language repo scan (Node/Python/Rust/Go/Java/Ruby/PHP/.NET/containers/vendored/assets), upstream LICENSE verification, version-change traps (Elast' in text, "expected to find: " + '- **Lv.1** — Base: distribution-model question, multi-language repo scan (Node/Python/Rust/Go/Java/Ruby/PHP/.NET/containers/vendored/assets), upstream LICENSE verification, version-change traps (Elast'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/business/licensing/SKILL.md')
    assert '| **Citation / attribution required** | 📝 | Commercial use is allowed but the license **requires** the copyright notice and license text to be reproduced (typically in `THIRD_PARTY_LICENSES.md`, an Ab' in text, "expected to find: " + '| **Citation / attribution required** | 📝 | Commercial use is allowed but the license **requires** the copyright notice and license text to be reproduced (typically in `THIRD_PARTY_LICENSES.md`, an Ab'[:80]

