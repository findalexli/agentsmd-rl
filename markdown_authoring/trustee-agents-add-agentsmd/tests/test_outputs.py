"""Behavioral checks for trustee-agents-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/trustee")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **libsgx-dcap-default-qpl** (for Intel SGX and TDX verifier features) installed from https://download.01.org/intel-sgx/.' in text, "expected to find: " + '- **libsgx-dcap-default-qpl** (for Intel SGX and TDX verifier features) installed from https://download.01.org/intel-sgx/.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Starts: **setup** (cert generation) → **rvps** (:50003) → **as** (:50004) → **kbs** (:8080) → **keyprovider** (:50000)' in text, "expected to find: " + 'Starts: **setup** (cert generation) → **rvps** (:50003) → **as** (:50004) → **kbs** (:8080) → **keyprovider** (:50000)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **RATS model**: KBS acts as Relying Party, AS acts as Verifier, RVPS provides endorsements/reference values' in text, "expected to find: " + '- **RATS model**: KBS acts as Relying Party, AS acts as Verifier, RVPS provides endorsements/reference values'[:80]

