"""Behavioral tests for the apache/airflow#65334 task.

The PR adds a `uv sync --frozen --project <project>` step before invoking
mypy in `scripts/ci/prek/mypy_local_folder.py` (local branch only) and
freezes the `update-uv-lock` prek hook. We test the actual call sequence
the script performs by intercepting `uv` invocations with a fake binary
on PATH, plus a structural check on the YAML hook configuration.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

REPO = Path("/workspace/airflow")
SCRIPT = REPO / "scripts" / "ci" / "prek" / "mypy_local_folder.py"
PRECOMMIT_YAML = REPO / ".pre-commit-config.yaml"


def _make_fake_uv_dir(body: str) -> Path:
    """Create a directory containing a single fake `uv` shell binary."""
    d = Path(tempfile.mkdtemp(prefix="fakeuv_"))
    uv = d / "uv"
    uv.write_text(body)
    uv.chmod(0o755)
    return d


def _run_script(fake_uv_dir: Path, folder: str = "airflow-core", timeout: int = 60):
    """Run mypy_local_folder.py with fake `uv` on PATH; CI env unset."""
    env = os.environ.copy()
    env["PATH"] = f"{fake_uv_dir}:{env.get('PATH', '')}"
    env.pop("CI", None)
    env.pop("GITHUB_ACTIONS", None)
    return subprocess.run(
        [sys.executable, str(SCRIPT), folder],
        capture_output=True,
        text=True,
        env=env,
        cwd=str(REPO),
        timeout=timeout,
    )


def _read_calls(log_path: Path) -> list[str]:
    if not log_path.exists():
        return []
    return [ln for ln in log_path.read_text().splitlines() if ln.strip()]


def _find_call(calls: list[str], leading: str) -> int:
    """Return index of first call whose first whitespace-separated token equals leading."""
    for i, c in enumerate(calls):
        if c.split() and c.split()[0] == leading:
            return i
    return -1


def _find_mypy_run(calls: list[str]) -> int:
    """Find first `run ... mypy ...` call."""
    for i, c in enumerate(calls):
        toks = c.split()
        if toks and toks[0] == "run" and "mypy" in toks:
            return i
    return -1


def _build_logging_uv(log_path: Path) -> Path:
    return _make_fake_uv_dir(
        f"""#!/bin/bash
echo "$@" >> {log_path}
exit 0
"""
    )


def _build_failing_sync_uv(log_path: Path) -> Path:
    return _make_fake_uv_dir(
        f"""#!/bin/bash
echo "$@" >> {log_path}
if [ "$1" = "sync" ]; then
  echo "fake uv sync failure" >&2
  exit 17
fi
exit 0
"""
    )


# ---------------------------------------------------------------------------
# Fail-to-pass: behavioral tests of the local mypy script
# ---------------------------------------------------------------------------


def test_uv_sync_runs_before_mypy():
    """When run locally, the script must call `uv sync --frozen --project <P>` before `uv run ... mypy`."""
    log = Path(tempfile.mkstemp(prefix="uvcalls_", suffix=".log")[1])
    log.unlink(missing_ok=True)
    fake = _build_logging_uv(log)

    r = _run_script(fake, folder="airflow-core")
    assert r.returncode == 0, (
        f"Script exited {r.returncode}.\nstdout:\n{r.stdout}\nstderr:\n{r.stderr}"
    )

    calls = _read_calls(log)
    sync_idx = _find_call(calls, "sync")
    run_idx = _find_mypy_run(calls)

    assert sync_idx >= 0, (
        f"`uv sync` was never invoked. Recorded uv calls: {calls!r}"
    )
    assert run_idx >= 0, (
        f"`uv run ... mypy` was never invoked. Recorded uv calls: {calls!r}"
    )
    assert sync_idx < run_idx, (
        f"`uv sync` must precede `uv run ... mypy`, got order: {calls!r}"
    )

    sync_call = calls[sync_idx].split()
    assert "--frozen" in sync_call, (
        f"`uv sync` must be invoked with --frozen so uv.lock is not modified. Got: {calls[sync_idx]!r}"
    )
    assert "--project" in sync_call, (
        f"`uv sync` must specify --project. Got: {calls[sync_idx]!r}"
    )


def test_uv_sync_uses_project_matching_input_folder():
    """The project passed to `uv sync` must match the existing folder→project mapping (same value used by `uv run`)."""
    cases = [
        ("airflow-core", "airflow-core"),
        ("task-sdk", "task-sdk"),
        ("dev", "dev"),
    ]
    for folder, expected_project in cases:
        log = Path(tempfile.mkstemp(prefix=f"uvcalls_{folder}_", suffix=".log")[1])
        log.unlink(missing_ok=True)
        fake = _build_logging_uv(log)

        r = _run_script(fake, folder=folder)
        assert r.returncode == 0, (
            f"Script exited {r.returncode} for folder={folder}.\nstderr: {r.stderr}"
        )
        calls = _read_calls(log)
        sync_idx = _find_call(calls, "sync")
        run_idx = _find_mypy_run(calls)
        assert sync_idx >= 0 and run_idx >= 0, (
            f"missing sync/run for folder={folder}: {calls!r}"
        )

        sync_tokens = calls[sync_idx].split()
        run_tokens = calls[run_idx].split()

        def project_of(tokens):
            try:
                i = tokens.index("--project")
                return tokens[i + 1]
            except (ValueError, IndexError):
                return None

        sync_project = project_of(sync_tokens)
        run_project = project_of(run_tokens)
        assert sync_project == expected_project, (
            f"For folder={folder!r} expected sync --project {expected_project!r}, got {sync_project!r}"
        )
        assert run_project == expected_project, (
            f"For folder={folder!r} expected run --project {expected_project!r}, got {run_project!r}"
        )
        assert sync_project == run_project, (
            f"For folder={folder!r} sync project ({sync_project!r}) and run project ({run_project!r}) diverge"
        )


def test_sync_failure_aborts_before_mypy():
    """If `uv sync` fails (non-zero exit), the script must exit non-zero AND must not invoke mypy."""
    log = Path(tempfile.mkstemp(prefix="uvcalls_fail_", suffix=".log")[1])
    log.unlink(missing_ok=True)
    fake = _build_failing_sync_uv(log)

    r = _run_script(fake, folder="airflow-core")
    calls = _read_calls(log)

    assert r.returncode != 0, (
        f"Script must exit non-zero when `uv sync` fails. Got returncode=0.\nstdout: {r.stdout}\nstderr: {r.stderr}\ncalls: {calls!r}"
    )

    mypy_idx = _find_mypy_run(calls)
    assert mypy_idx == -1, (
        f"`uv run ... mypy` must NOT be invoked after `uv sync` fails. Calls recorded: {calls!r}"
    )

    sync_idx = _find_call(calls, "sync")
    assert sync_idx >= 0, (
        f"`uv sync` must have been attempted. Calls recorded: {calls!r}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass: structural check on the prek hook configuration
# ---------------------------------------------------------------------------


def _find_hook(config: dict, hook_id: str) -> dict | None:
    for repo in config.get("repos", []):
        for hook in repo.get("hooks", []):
            if hook.get("id") == hook_id:
                return hook
    return None


def test_update_uv_lock_hook_is_frozen():
    """The `update-uv-lock` prek hook must run `uv lock --frozen`, not `uv lock`."""
    config = yaml.safe_load(PRECOMMIT_YAML.read_text())
    hook = _find_hook(config, "update-uv-lock")
    assert hook is not None, (
        "`update-uv-lock` hook not found in .pre-commit-config.yaml"
    )
    entry = hook.get("entry", "")
    tokens = entry.split()
    assert tokens[:2] == ["uv", "lock"], (
        f"`update-uv-lock` hook entry must invoke `uv lock`. Got: {entry!r}"
    )
    assert "--frozen" in tokens, (
        f"`update-uv-lock` hook entry must include --frozen so a stale lock fails the hook "
        f"instead of being silently rewritten. Got: {entry!r}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass: structural sanity checks (pass at base AND at gold)
# ---------------------------------------------------------------------------


def test_mypy_script_compiles():
    """The local mypy script must remain syntactically valid Python."""
    r = subprocess.run(
        [sys.executable, "-m", "py_compile", str(SCRIPT)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"py_compile failed:\n{r.stderr}"


def test_pre_commit_yaml_parses():
    """The pre-commit config must remain valid YAML and contain the update-uv-lock hook."""
    config = yaml.safe_load(PRECOMMIT_YAML.read_text())
    assert isinstance(config, dict) and "repos" in config
    assert _find_hook(config, "update-uv-lock") is not None, (
        "`update-uv-lock` hook should remain present"
    )


def test_ci_branch_unchanged():
    """The CI/breeze branch of the script should still call `run_command_via_breeze_shell` — the local sync logic must not affect the CI path."""
    src = SCRIPT.read_text()
    assert "run_command_via_breeze_shell" in src, (
        "CI branch must still dispatch via `run_command_via_breeze_shell`"
    )
    assert "if CI:" in src or "if CI :" in src, (
        "CI branch gate (`if CI:`) must remain"
    )
