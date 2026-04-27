"""Behavioral checks for prefect-docs-document-sigterm-bridge-and (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/prefect")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('src/prefect/utilities/AGENTS.md')
    assert '- `engine/` → Result-to-state linking, SIGTERM bridge management, and control-intent coordination (see `engine/AGENTS.md`)' in text, "expected to find: " + '- `engine/` → Result-to-state linking, SIGTERM bridge management, and control-intent coordination (see `engine/AGENTS.md`)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('src/prefect/utilities/engine/AGENTS.md')
    assert '- **All SIGTERM-state reads and writes must hold `_prefect_sigterm_bridge_lock`.** The lock is a `threading.RLock` that serializes handler install/restore with ack writes. Reading `signal.getsignal(SI' in text, "expected to find: " + '- **All SIGTERM-state reads and writes must hold `_prefect_sigterm_bridge_lock`.** The lock is a `threading.RLock` that serializes handler install/restore with ack writes. Reading `signal.getsignal(SI'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('src/prefect/utilities/engine/AGENTS.md')
    assert "2. **SIGTERM bridge** — installs and tears down Prefect's SIGTERM handler (`TerminationSignal`), coordinates control-intent acknowledgement with the runner, and exposes locked helpers so the engine ca" in text, "expected to find: " + "2. **SIGTERM bridge** — installs and tears down Prefect's SIGTERM handler (`TerminationSignal`), coordinates control-intent acknowledgement with the runner, and exposes locked helpers so the engine ca"[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('src/prefect/utilities/engine/AGENTS.md')
    assert '1. **Result-to-state linking** — glue between Python return values (which callers receive) and the `State` objects that represent them on the server. Maintains the identity-keyed `run_results` map ins' in text, "expected to find: " + '1. **Result-to-state linking** — glue between Python return values (which callers receive) and the `State` objects that represent them on the server. Maintains the identity-keyed `run_results` map ins'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('src/prefect/utilities/processutils/AGENTS.md')
    assert '- `sanitize_subprocess_env(env) -> dict[str, str]` — strip `None` values from an env mapping before passing to subprocess launch APIs; `None` means "omit this key", which `subprocess` and `anyio.open_' in text, "expected to find: " + '- `sanitize_subprocess_env(env) -> dict[str, str]` — strip `None` values from an env mapping before passing to subprocess launch APIs; `None` means "omit this key", which `subprocess` and `anyio.open_'[:80]

