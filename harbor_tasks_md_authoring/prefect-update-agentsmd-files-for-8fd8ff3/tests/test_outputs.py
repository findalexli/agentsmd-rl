"""Behavioral checks for prefect-update-agentsmd-files-for-8fd8ff3 (markdown_authoring task).

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
    assert '- **`command_to_string` always uses POSIX quoting (`shlex.join`), even on Windows.** This is intentional for platform-neutral storage — bundle commands are serialized by one platform and may be deseri' in text, "expected to find: " + '- **`command_to_string` always uses POSIX quoting (`shlex.join`), even on Windows.** This is intentional for platform-neutral storage — bundle commands are serialized by one platform and may be deseri'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('src/prefect/utilities/AGENTS.md')
    assert '- **`get_sys_executable()` no longer quotes the Python path on Windows.** It previously returned `\'"path/to/python"\'` (with embedded quotes) on Windows; now it returns the raw path. Code relying on th' in text, "expected to find: " + '- **`get_sys_executable()` no longer quotes the Python path on Windows.** It previously returned `\'"path/to/python"\'` (with embedded quotes) on Windows; now it returns the raw path. Code relying on th'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('src/prefect/utilities/AGENTS.md')
    assert '- `processutils.py` — Subprocess execution, output streaming, and command serialization helpers (`run_process`, `consume_process_output`, `stream_text`, `command_to_string`, `command_from_string`)' in text, "expected to find: " + '- `processutils.py` — Subprocess execution, output streaming, and command serialization helpers (`run_process`, `consume_process_output`, `stream_text`, `command_to_string`, `command_from_string`)'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('src/prefect/workers/AGENTS.md')
    assert 'When a flow is decorated with an infrastructure decorator (`@docker`, `@ecs`, `@kubernetes`, etc.) and a `launcher` argument is supplied, `InfrastructureBoundFlow` stores a normalized `BundleLauncherO' in text, "expected to find: " + 'When a flow is decorated with an infrastructure decorator (`@docker`, `@ecs`, `@kubernetes`, etc.) and a `launcher` argument is supplied, `InfrastructureBoundFlow` stores a normalized `BundleLauncherO'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('src/prefect/workers/AGENTS.md')
    assert '**Non-obvious:** the launcher replaces the `uv run ...` prefix entirely. With a launcher, the resulting command is `[*launcher, "-m", "<module>", "--key", "<path>"]` rather than `["uv", "run", "--with' in text, "expected to find: " + '**Non-obvious:** the launcher replaces the `uv run ...` prefix entirely. With a launcher, the resulting command is `[*launcher, "-m", "<module>", "--key", "<path>"]` rather than `["uv", "run", "--with'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('src/prefect/workers/AGENTS.md')
    assert 'Work-pool-level launchers are configured via `prefect work-pool storage configure s3|gcs|azure --launcher <executable>` and are stored in the step dict itself. Flow-level launchers (via the decorator)' in text, "expected to find: " + 'Work-pool-level launchers are configured via `prefect work-pool storage configure s3|gcs|azure --launcher <executable>` and are stored in the step dict itself. Flow-level launchers (via the decorator)'[:80]

