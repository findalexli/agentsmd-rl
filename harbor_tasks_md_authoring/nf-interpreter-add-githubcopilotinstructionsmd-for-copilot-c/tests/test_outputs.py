"""Behavioral checks for nf-interpreter-add-githubcopilotinstructionsmd-for-copilot-c (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/nf-interpreter")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'This is the **nf-interpreter** repository — the C/C++ firmware for **.NET nanoFramework**, a managed-code runtime (CLR) for resource-constrained embedded devices. It produces two binaries per target b' in text, "expected to find: " + 'This is the **nf-interpreter** repository — the C/C++ firmware for **.NET nanoFramework**, a managed-code runtime (CLR) for resource-constrained embedded devices. It produces two binaries per target b'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **User local config**: Copy `config/user-prefs.TEMPLATE.json` → `config/user-prefs.json` and `config/user-tools-repos.TEMPLATE.json` → `config/user-tools-repos.json`, then `config/user-kconfig.conf.' in text, "expected to find: " + '- **User local config**: Copy `config/user-prefs.TEMPLATE.json` → `config/user-prefs.json` and `config/user-tools-repos.TEMPLATE.json` → `config/user-tools-repos.json`, then `config/user-kconfig.conf.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '1. **Cannot build locally without toolchains**: This repo requires embedded cross-compilers (ARM GCC, Xtensa, RISC-V) and RTOS SDKs. Use the dev containers for building. The cloud agent environment do' in text, "expected to find: " + '1. **Cannot build locally without toolchains**: This repo requires embedded cross-compilers (ARM GCC, Xtensa, RISC-V) and RTOS SDKs. Use the dev containers for building. The cloud agent environment do'[:80]

