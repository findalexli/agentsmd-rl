"""Behavioral checks for nanostack-add-next-step-to-every (markdown_authoring task).

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
    assert 'Do NOT run `/review`, `/qa`, or `/security` automatically. Wait for the user to invoke each one.' in text, "expected to find: " + 'Do NOT run `/review`, `/qa`, or `/security` automatically. Wait for the user to invoke each one.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plan/SKILL.md')
    assert '> These three can run in any order. After all pass, `/ship` to create the PR.' in text, "expected to find: " + '> These three can run in any order. After all pass, `/ship` to create the PR.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plan/SKILL.md')
    assert 'After the user approves the plan and you finish building, tell the user:' in text, "expected to find: " + 'After the user approves the plan and you finish building, tell the user:'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('qa/SKILL.md')
    assert "After QA is complete and the artifact is saved, tell the user what's next:" in text, "expected to find: " + "After QA is complete and the artifact is saved, tell the user what's next:"[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('qa/SKILL.md')
    assert '> - `/ship` to create the PR (after review, security and qa pass)' in text, "expected to find: " + '> - `/ship` to create the PR (after review, security and qa pass)'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('qa/SKILL.md')
    assert '> - `/security` to audit for vulnerabilities (if not done yet)' in text, "expected to find: " + '> - `/security` to audit for vulnerabilities (if not done yet)'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('review/SKILL.md')
    assert "After the review is complete and the artifact is saved, tell the user what's next in the sprint:" in text, "expected to find: " + "After the review is complete and the artifact is saved, tell the user what's next in the sprint:"[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('review/SKILL.md')
    assert '> - `/ship` to create the PR (after review, security and qa pass)' in text, "expected to find: " + '> - `/ship` to create the PR (after review, security and qa pass)'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('review/SKILL.md')
    assert '> - `/security` to audit for vulnerabilities (if not done yet)' in text, "expected to find: " + '> - `/security` to audit for vulnerabilities (if not done yet)'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('security/SKILL.md')
    assert "After the security audit is complete and the artifact is saved, tell the user what's next:" in text, "expected to find: " + "After the security audit is complete and the artifact is saved, tell the user what's next:"[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('security/SKILL.md')
    assert '> - `/ship` to create the PR (after review, security and qa pass)' in text, "expected to find: " + '> - `/ship` to create the PR (after review, security and qa pass)'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('security/SKILL.md')
    assert '> - `/qa` to test that everything works (if not done yet)' in text, "expected to find: " + '> - `/qa` to test that everything works (if not done yet)'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('think/SKILL.md')
    assert '> Ready for `/nano-plan`. Say `/nano-plan` to create the implementation plan, or adjust the brief first.' in text, "expected to find: " + '> Ready for `/nano-plan`. Say `/nano-plan` to create the implementation plan, or adjust the brief first.'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('think/SKILL.md')
    assert 'Do NOT proceed to planning automatically. Wait for the user to invoke `/nano-plan`.' in text, "expected to find: " + 'Do NOT proceed to planning automatically. Wait for the user to invoke `/nano-plan`.'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('think/SKILL.md')
    assert 'After the Think Summary and artifact are saved, tell the user:' in text, "expected to find: " + 'After the Think Summary and artifact are saved, tell the user:'[:80]

