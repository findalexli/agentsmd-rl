"""Behavioral checks for red-run-fix-kerbrute-spray-loop-and (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/red-run")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/credential/password-spraying/SKILL.md')
    assert 'echo "[*] Round 2: context wordlist ($(wc -l < "$WORDLIST") passwords)" | tee -a "$RESULTS"' in text, "expected to find: " + 'echo "[*] Round 2: context wordlist ($(wc -l < "$WORDLIST") passwords)" | tee -a "$RESULTS"'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/credential/password-spraying/SKILL.md')
    assert 'grep -i \'valid pass\' "$RESULTS" 2>/dev/null || echo "(none found)" | tee -a "$RESULTS"' in text, "expected to find: " + 'grep -i \'valid pass\' "$RESULTS" 2>/dev/null || echo "(none found)" | tee -a "$RESULTS"'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/credential/password-spraying/SKILL.md')
    assert 'nxc smb TARGET -u USERFILE -p PASSFILE --continue-on-success -d DOMAIN --kerberos' in text, "expected to find: " + 'nxc smb TARGET -u USERFILE -p PASSFILE --continue-on-success -d DOMAIN --kerberos'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/network/network-recon/SKILL.md')
    assert '- That the host appears unreachable or has no open ports in the scanned range' in text, "expected to find: " + '- That the host appears unreachable or has no open ports in the scanned range'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/network/network-recon/SKILL.md')
    assert 'response), retry with `-Pn` added to the **same scan options**. Many targets' in text, "expected to find: " + 'response), retry with `-Pn` added to the **same scan options**. Many targets'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/network/network-recon/SKILL.md')
    assert 'range, or any other flags. If the operator chose quick (`--top-ports 1000`),' in text, "expected to find: " + 'range, or any other flags. If the operator chose quick (`--top-ports 1000`),'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/orchestrator/SKILL.md')
    assert 'The technique skill contains curated bypass sequences (alternative extensions,' in text, "expected to find: " + 'The technique skill contains curated bypass sequences (alternative extensions,'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/orchestrator/SKILL.md')
    assert "not as directives to skip techniques. The skill's methodology determines what" in text, "expected to find: " + "not as directives to skip techniques. The skill's methodology determines what"[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/orchestrator/SKILL.md')
    assert 'never tested. Telling the agent to skip a technique class defeats the purpose' in text, "expected to find: " + 'never tested. Telling the agent to skip a technique class defeats the purpose'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/web/file-upload-bypass/SKILL.md')
    assert "Where `shell.php` contains a standard webshell (`<?php system($_GET['cmd']); ?>`)." in text, "expected to find: " + "Where `shell.php` contains a standard webshell (`<?php system($_GET['cmd']); ?>`)."[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/web/file-upload-bypass/SKILL.md')
    assert 'bytes inside **ZIP entry filenames** work against modern PHP because truncation' in text, "expected to find: " + 'bytes inside **ZIP entry filenames** work against modern PHP because truncation'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/web/file-upload-bypass/SKILL.md')
    assert 'Most PHP/Java ZIP libraries read filenames from the central directory, but some' in text, "expected to find: " + 'Most PHP/Java ZIP libraries read filenames from the central directory, but some'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/web/web-discovery/SKILL.md')
    assert '> **→ ROUTE ON HIT:** Uploaded file executed server-side → **file-upload-bypass**. Alternative extension accepted → **file-upload-bypass**. Config file accepted (`.htaccess`, `web.config`) → **file-up' in text, "expected to find: " + '> **→ ROUTE ON HIT:** Uploaded file executed server-side → **file-upload-bypass**. Alternative extension accepted → **file-upload-bypass**. Config file accepted (`.htaccess`, `web.config`) → **file-up'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/web/web-discovery/SKILL.md')
    assert '| Upload endpoint found, basic server-side content blocked | **file-upload-bypass** (discovery testing is preliminary — technique skill has 20+ bypass variants) |' in text, "expected to find: " + '| Upload endpoint found, basic server-side content blocked | **file-upload-bypass** (discovery testing is preliminary — technique skill has 20+ bypass variants) |'[:80]

