"""Behavioral checks for red-run-add-privesc-chains-kernel-cve (markdown_authoring task).

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
    text = _read('skills/orchestrator/SKILL.md')
    assert '| vuln w/ "FLAG:" in summary | Always — immediate | Notify operator with prominent callout (see Flag Capture section). Do not interrupt running agent. |' in text, "expected to find: " + '| vuln w/ "FLAG:" in summary | Always — immediate | Notify operator with prominent callout (see Flag Capture section). Do not interrupt running agent. |'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/orchestrator/SKILL.md')
    assert '- Windows: C:\\Users\\Administrator\\Desktop\\root.txt, C:\\Users\\*\\Desktop\\user.txt, C:\\Users\\*\\Desktop\\proof.txt' in text, "expected to find: " + '- Windows: C:\\Users\\Administrator\\Desktop\\root.txt, C:\\Users\\*\\Desktop\\user.txt, C:\\Users\\*\\Desktop\\proof.txt'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/orchestrator/SKILL.md')
    assert '- Any agent that gains NEW access as part of its skill (e.g., file-upload-bypass' in text, "expected to find: " + '- Any agent that gains NEW access as part of its skill (e.g., file-upload-bypass'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/privesc/linux-discovery/SKILL.md')
    assert '| `allow_active=yes` on udisks2, systemd, or other dangerous actions | Active session can perform privileged operations without auth | **linux-sudo-suid-capabilities** |' in text, "expected to find: " + '| `allow_active=yes` on udisks2, systemd, or other dangerous actions | Active session can perform privileged operations without auth | **linux-sudo-suid-capabilities** |'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/privesc/linux-discovery/SKILL.md')
    assert '| `user_readenv=1` in PAM config | Can inject XDG_SEAT/XDG_VTNR via ~/.pam_environment | **linux-sudo-suid-capabilities** |' in text, "expected to find: " + '| `user_readenv=1` in PAM config | Can inject XDG_SEAT/XDG_VTNR via ~/.pam_environment | **linux-sudo-suid-capabilities** |'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/privesc/linux-discovery/SKILL.md')
    assert '| `Active=no` + `user_readenv=1` | SSH session can be upgraded to Active=yes | **linux-sudo-suid-capabilities** |' in text, "expected to find: " + '| `Active=no` + `user_readenv=1` | SSH session can be upgraded to Active=yes | **linux-sudo-suid-capabilities** |'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/privesc/linux-kernel-exploits/SKILL.md')
    assert '| "failed to detect overwritten pte" | PTE spray didn\'t land | Race condition — retry 3-5 times. Try alternative PoC repos with different spray strategies |' in text, "expected to find: " + '| "failed to detect overwritten pte" | PTE spray didn\'t land | Race condition — retry 3-5 times. Try alternative PoC repos with different spray strategies |'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/privesc/linux-kernel-exploits/SKILL.md')
    assert '| "Operation not permitted" on CLONE_NEWUSER | User namespaces disabled | Check `kernel.unprivileged_userns_clone`. If 0, this exploit won\'t work |' in text, "expected to find: " + '| "Operation not permitted" on CLONE_NEWUSER | User namespaces disabled | Check `kernel.unprivileged_userns_clone`. If 0, this exploit won\'t work |'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/privesc/linux-kernel-exploits/SKILL.md')
    assert '| "pmd: 00000000cafebabe" | Sentinel value, spray completely missed | Kernel config may differ from what exploit expects. Try alternative PoC |' in text, "expected to find: " + '| "pmd: 00000000cafebabe" | Sentinel value, spray completely missed | Kernel config may differ from what exploit expects. Try alternative PoC |'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/privesc/linux-sudo-suid-capabilities/SKILL.md')
    assert '3. Polkit policies with `allow_active=yes` now grant access without authentication' in text, "expected to find: " + '3. Polkit policies with `allow_active=yes` now grant access without authentication'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/privesc/linux-sudo-suid-capabilities/SKILL.md')
    assert '4. `udisksctl loop-setup` + `Filesystem.Resize`/`Check` triggers a temporary mount' in text, "expected to find: " + '4. `udisksctl loop-setup` + `Filesystem.Resize`/`Check` triggers a temporary mount'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/privesc/linux-sudo-suid-capabilities/SKILL.md')
    assert '**Disconnect the SSH session** (exit), then **reconnect**. The new session will be' in text, "expected to find: " + '**Disconnect the SSH session** (exit), then **reconnect**. The new session will be'[:80]

