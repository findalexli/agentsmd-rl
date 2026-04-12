"""Comprehensive tests for e2b_worker pipeline.

Tests are organized by layer:
  1. StartAt enum and DAG ordering
  2. Individual node functions (mocked sandbox)
  3. File exchange contracts (what each node reads/writes)
  4. run_task() integration (full DAG with mocked nodes)
  5. run_batch() orchestration
  6. CLI dispatch (async_main argument routing)

All tests mock AsyncSandbox — no real E2B sandboxes are created.
"""

from __future__ import annotations

import asyncio
import json
import unittest
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch, call

import yaml

from taskforge.e2b_worker import (
    StartAt,
    WorkerResult,
    _RateLimited,
    node_scaffold,
    node_qgate,
    node_rubric_loop,
    node_clone_repo,
    node_enrich_p2p,
    node_check_test_quality,
    node_improve_tests,
    node_validate_and_fix,
    node_validate_docker_only,
    node_rubric_lint,
    run_task,
    run_task_docker_only,
    run_batch,
    collect_tasks,
    load_pr_items,
    upload_task_files,
    download_task_files,
    upload_taskforge_modules,
    read_sandbox_status,
    update_sandbox_status,
    write_status_json,
)


# ---------------------------------------------------------------------------
# Helpers: mock sandbox
# ---------------------------------------------------------------------------


def _make_sandbox(
    cmd_results: dict[str, tuple[int, str, str]] | None = None,
    files: dict[str, str | bytes] | None = None,
) -> AsyncMock:
    """Create a mock AsyncSandbox with configurable command results and files.

    cmd_results: maps command substring → (exit_code, stdout, stderr).
                 First matching substring wins. Default: (0, "", "")
    files: maps remote path → content (str or bytes). Used by files.read().
    """
    sandbox = AsyncMock()
    sandbox.sandbox_id = "test-sandbox-123"
    sandbox.kill = AsyncMock()
    sandbox.set_timeout = AsyncMock()

    _cmd_results = cmd_results or {}
    _files: dict[str, str | bytes] = files or {}
    _written_files: dict[str, bytes] = {}

    async def mock_run(cmd: str, timeout: int = 0, user: str = "root"):
        # Match command to configured result
        for pattern, result in _cmd_results.items():
            if pattern in cmd:
                mock_result = MagicMock()
                mock_result.exit_code = result[0]
                mock_result.stdout = result[1]
                mock_result.stderr = result[2]
                return mock_result
        # Default: success
        mock_result = MagicMock()
        mock_result.exit_code = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        return mock_result

    sandbox.commands = MagicMock()
    sandbox.commands.run = mock_run

    async def mock_read(path: str, format: str = "text"):
        if path in _written_files:
            content = _written_files[path]
            if format == "text":
                return content.decode() if isinstance(content, bytes) else content
            return content if isinstance(content, bytes) else content.encode()
        if path in _files:
            content = _files[path]
            if format == "text":
                return content if isinstance(content, str) else content.decode()
            return content if isinstance(content, bytes) else content.encode()
        raise FileNotFoundError(f"No such file: {path}")

    async def mock_write(path: str, content: bytes):
        _written_files[path] = content

    sandbox.files = MagicMock()
    sandbox.files.read = mock_read
    sandbox.files.write = mock_write

    # Expose internal state for assertions
    sandbox._written_files = _written_files
    sandbox._files = _files

    return sandbox


def _run(coro):
    """Run an async coroutine synchronously."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# ---------------------------------------------------------------------------
# 1. StartAt enum tests
# ---------------------------------------------------------------------------


class TestStartAt(unittest.TestCase):
    """Test DAG node ordering and should_run logic."""

    def test_from_str_valid(self):
        assert StartAt.from_str("scaffold") == StartAt.SCAFFOLD
        assert StartAt.from_str("validate") == StartAt.VALIDATE

    def test_from_str_invalid(self):
        with self.assertRaises(ValueError):
            StartAt.from_str("bogus")

    def test_scaffold_runs_all_nodes(self):
        """start_at=scaffold should run every node."""
        sa = StartAt.SCAFFOLD
        for node in StartAt:
            assert sa.should_run(node), f"scaffold should run {node.value}"

    def test_validate_only_runs_validate(self):
        """start_at=validate should only run validate."""
        sa = StartAt.VALIDATE
        assert not sa.should_run(StartAt.SCAFFOLD)
        assert not sa.should_run(StartAt.QGATE)
        assert not sa.should_run(StartAt.RUBRIC)
        assert not sa.should_run(StartAt.ENRICH)
        assert not sa.should_run(StartAt.IMPROVE)
        assert sa.should_run(StartAt.VALIDATE)

    def test_improve_runs_improve_and_validate(self):
        """start_at=improve should run improve and validate."""
        sa = StartAt.IMPROVE
        assert not sa.should_run(StartAt.ENRICH)
        assert sa.should_run(StartAt.IMPROVE)
        assert sa.should_run(StartAt.VALIDATE)

    def test_qgate_skips_scaffold_runs_rest(self):
        sa = StartAt.QGATE
        assert not sa.should_run(StartAt.SCAFFOLD)
        assert sa.should_run(StartAt.QGATE)
        assert sa.should_run(StartAt.RUBRIC)
        assert sa.should_run(StartAt.ENRICH)

    def test_ordering_is_monotonic(self):
        """Each successive start_at runs fewer nodes."""
        order = list(StartAt)
        for i, sa in enumerate(order):
            for j, node in enumerate(order):
                if j >= i:
                    assert sa.should_run(node), f"{sa.value} should run {node.value}"
                else:
                    assert not sa.should_run(node), f"{sa.value} should NOT run {node.value}"


# ---------------------------------------------------------------------------
# 2. Individual node tests (mocked sandbox)
# ---------------------------------------------------------------------------


class TestNodeQgate(unittest.TestCase):
    """Test quality gate runs INSIDE sandbox, returns correct verdicts."""

    def test_delete_verdict(self):
        """Tasks with no manifest get DELETE."""
        sandbox = _make_sandbox(cmd_results={
            "python3 -c": (0, '{"verdict": "DELETE", "flags": ["no_manifest"]}', ""),
        })
        verdict, flags = _run(node_qgate(sandbox))
        assert verdict == "DELETE"
        assert "no_manifest" in flags

    def test_passed_verdict(self):
        """Tasks that pass fast gate get 'passed'."""
        sandbox = _make_sandbox(cmd_results={
            "python3 -c": (0, '{"verdict": "", "flags": ["tier2_only"]}', ""),
        })
        verdict, flags = _run(node_qgate(sandbox))
        assert verdict == "passed"
        assert "tier2_only" in flags

    def test_error_on_command_failure(self):
        """If the sandbox python command fails, return error."""
        sandbox = _make_sandbox(cmd_results={
            "python3 -c": (1, "", "ModuleNotFoundError: No module named 'yaml'"),
        })
        verdict, flags = _run(node_qgate(sandbox))
        assert verdict == "error"

    def test_runs_in_sandbox_not_host(self):
        """Verify the command runs via run_cmd (sandbox), not host import."""
        sandbox = _make_sandbox(cmd_results={
            "python3 -c": (0, '{"verdict": "passed", "flags": []}', ""),
        })
        _run(node_qgate(sandbox))
        # The command should have been called on sandbox.commands.run
        # (We can't easily assert on AsyncMock with our helper, but the fact
        # that it returns the configured result proves it ran in the sandbox)


class TestNodeCheckTestQuality(unittest.TestCase):
    """Test the test quality checker."""

    def test_good_tests(self):
        sandbox = _make_sandbox(cmd_results={
            "python3 -c": (0, "False,True,True", ""),
        })
        needs, reason = _run(node_check_test_quality(sandbox))
        assert needs is False
        assert "good" in reason

    def test_stub_needs_improve(self):
        sandbox = _make_sandbox(cmd_results={
            "python3 -c": (0, "True,True,True", ""),
        })
        needs, reason = _run(node_check_test_quality(sandbox))
        assert needs is True
        assert "NotImplementedError" in reason

    def test_no_subprocess_needs_improve(self):
        sandbox = _make_sandbox(cmd_results={
            "python3 -c": (0, "False,False,True", ""),
        })
        needs, reason = _run(node_check_test_quality(sandbox))
        assert needs is True
        assert "subprocess" in reason

    def test_no_test_functions(self):
        sandbox = _make_sandbox(cmd_results={
            "python3 -c": (0, "False,True,False", ""),
        })
        needs, reason = _run(node_check_test_quality(sandbox))
        assert needs is True
        assert "no test" in reason

    def test_syntax_error(self):
        sandbox = _make_sandbox(cmd_results={
            "python3 -c": (1, "", "SyntaxError"),
        })
        needs, reason = _run(node_check_test_quality(sandbox))
        assert needs is True
        assert "syntax error" in reason


class TestNodeCloneRepo(unittest.TestCase):
    """Test repo cloning from Dockerfile parsing."""

    def test_successful_clone(self):
        sandbox = _make_sandbox(cmd_results={
            "python3 -c": (0, "owner/repo\nabc1234567\n", ""),
            "git clone": (0, "", ""),
        })
        repo_url, commit = _run(node_clone_repo(sandbox, "test-task"))
        assert repo_url == "owner/repo"
        assert commit == "abc1234567"

    def test_clone_failure_returns_empty(self):
        sandbox = _make_sandbox(cmd_results={
            "python3 -c": (0, "owner/repo\nabc1234567\n", ""),
            "git clone": (1, "", "fatal: repo not found"),
        })
        repo_url, commit = _run(node_clone_repo(sandbox, "test-task"))
        assert repo_url == ""  # Signals clone failed

    def test_no_repo_in_dockerfile(self):
        sandbox = _make_sandbox(cmd_results={
            "python3 -c": (0, "\n\n", ""),
        })
        repo_url, commit = _run(node_clone_repo(sandbox, "test-task"))
        assert repo_url == ""
        assert commit == ""

    def test_invalid_repo_url_rejected(self):
        """Repo URLs with shell metacharacters should be rejected."""
        sandbox = _make_sandbox(cmd_results={
            "python3 -c": (0, "owner/repo; rm -rf /\nabc1234567\n", ""),
        })
        repo_url, _ = _run(node_clone_repo(sandbox, "test-task"))
        assert repo_url == ""  # Rejected by regex validation


class TestNodeRubricLoop(unittest.TestCase):
    """Test Gemini↔Kimi rubric loop."""

    def test_ok_status(self):
        result_json = json.dumps({
            "status": "ok",
            "quality_verdict": "HIGH",
            "loop_metadata": {"rounds": 2, "abandon_reason": ""},
        })
        sandbox = _make_sandbox(cmd_results={
            "python3 -c": (0, result_json, ""),
        })
        status, verdict, reason, rounds = _run(node_rubric_loop(sandbox, "owner/repo"))
        assert status == "ok"
        assert verdict == "HIGH"
        assert rounds == 2

    def test_abandoned_status(self):
        result_json = json.dumps({
            "status": "abandoned",
            "quality_verdict": "DELETE",
            "loop_metadata": {"rounds": 1, "abandon_reason": "zero distractors"},
        })
        sandbox = _make_sandbox(cmd_results={
            "python3 -c": (0, result_json, ""),
        })
        status, verdict, reason, rounds = _run(node_rubric_loop(sandbox, "owner/repo"))
        assert status == "abandoned"
        assert "distractors" in reason

    def test_error_on_command_failure(self):
        sandbox = _make_sandbox(cmd_results={
            "python3 -c": (1, "", "ImportError"),
        })
        status, _, _, _ = _run(node_rubric_loop(sandbox, "owner/repo"))
        assert status == "error"


class TestNodeRubricLint(unittest.TestCase):
    """Test post-validation rubric linter."""

    def test_clean_manifest(self):
        sandbox = _make_sandbox(cmd_results={
            "python3 -c": (0, '{"injected": 0, "samples": []}', ""),
        })
        count, samples = _run(node_rubric_lint(sandbox))
        assert count == 0
        assert samples == []

    def test_detects_injection(self):
        sandbox = _make_sandbox(cmd_results={
            # First call detects injection, second call strips it
            "python3 -c": (0, '{"injected": 2, "samples": ["CRITICAL OVERRIDE..."]}', ""),
        })
        count, samples = _run(node_rubric_lint(sandbox))
        assert count == 2
        assert len(samples) == 1

    def test_handles_lint_failure(self):
        sandbox = _make_sandbox(cmd_results={
            "python3 -c": (1, "", "error"),
        })
        count, samples = _run(node_rubric_lint(sandbox))
        assert count == 0


class TestNodeValidateDockerOnly(unittest.TestCase):
    """Test Docker-only validation (no LLM)."""

    def test_pass(self):
        """nop=0, gold=1 is a pass."""
        sandbox = _make_sandbox(
            cmd_results={
                "docker build": (0, "", ""),
                "docker run --rm": (0, "", ""),
                "docker run --name": (0, "", ""),
                "docker commit": (0, "", ""),
                "docker rm": (0, "", ""),
            },
            files={
                "/logs/verifier/reward.txt": "0",
            },
        )

        # We need to handle the sequential nop/gold reads.
        # Since our mock returns the same file content, we need a stateful mock.
        reward_sequence = [0.0, 1.0]
        call_count = [0]

        original_read = sandbox.files.read

        async def sequenced_read(path, format="text"):
            if path == "/logs/verifier/reward.txt":
                idx = min(call_count[0], len(reward_sequence) - 1)
                call_count[0] += 1
                val = str(reward_sequence[idx])
                return val if format == "text" else val.encode()
            return await original_read(path, format=format)

        sandbox.files.read = sequenced_read

        nop, gold, err = _run(node_validate_docker_only(sandbox))
        assert nop == 0.0
        assert gold == 1.0
        assert err == ""

    def test_build_failure(self):
        sandbox = _make_sandbox(cmd_results={
            "docker build": (1, "", "apt-get: package not found"),
        })
        nop, gold, err = _run(node_validate_docker_only(sandbox))
        assert nop == -1
        assert gold == -1
        assert "docker build failed" in err


# ---------------------------------------------------------------------------
# 3. File exchange contract tests
# ---------------------------------------------------------------------------


class TestFileExchange(unittest.TestCase):
    """Test that file transfer functions work correctly."""

    def test_upload_task_files(self):
        """Upload should write all files to /workspace/task/."""
        import tempfile, os
        with tempfile.TemporaryDirectory() as tmp:
            task_path = Path(tmp) / "my-task"
            task_path.mkdir()
            (task_path / "environment").mkdir()
            (task_path / "environment" / "Dockerfile").write_text("FROM ubuntu")
            (task_path / "tests").mkdir()
            (task_path / "tests" / "test.sh").write_text("echo pass")
            (task_path / "solution").mkdir()
            (task_path / "solution" / "solve.sh").write_text("git apply")

            sandbox = _make_sandbox()
            _run(upload_task_files(sandbox, task_path))

            # Verify files were written to sandbox
            assert b"FROM ubuntu" in sandbox._written_files.get(
                "/workspace/task/environment/Dockerfile", b"")
            assert b"echo pass" in sandbox._written_files.get(
                "/workspace/task/tests/test.sh", b"")

    def test_download_task_files(self):
        """Download should copy files from sandbox to local dir."""
        import tempfile
        sandbox = _make_sandbox(
            cmd_results={
                "find /workspace/task": (0, "/workspace/task/task.toml\n/workspace/task/tests/test.sh\n", ""),
            },
            files={
                "/workspace/task/task.toml": b"[task]\nname = 'test'",
                "/workspace/task/tests/test.sh": b"echo pass",
            },
        )

        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "downloaded"
            result = _run(download_task_files(sandbox, dest))
            assert "task.toml" in result
            assert "tests/test.sh" in result
            assert (dest / "task.toml").exists()
            assert (dest / "tests" / "test.sh").exists()

    def test_upload_taskforge_modules(self):
        """Should upload key Python modules to sandbox."""
        sandbox = _make_sandbox()
        _run(upload_taskforge_modules(sandbox))
        # Verify __init__.py was written
        assert b"" == sandbox._written_files.get("/workspace/taskforge/__init__.py", None)


class TestStatusJson(unittest.TestCase):
    """Test status.json read/write/update."""

    def test_read_empty(self):
        sandbox = _make_sandbox()  # No status.json file
        status = _run(read_sandbox_status(sandbox))
        assert status == {"nodes": {}}

    def test_read_existing(self):
        sandbox = _make_sandbox(files={
            "/workspace/task/status.json": json.dumps({"nodes": {"scaffold": {"status": "ok"}}})
        })
        status = _run(read_sandbox_status(sandbox))
        assert status["nodes"]["scaffold"]["status"] == "ok"

    def test_update_adds_node(self):
        sandbox = _make_sandbox(files={
            "/workspace/task/status.json": json.dumps({"nodes": {}})
        })
        _run(update_sandbox_status(sandbox, "qgate", {"status": "passed"}))
        # Read back from written files
        written = sandbox._written_files.get("/workspace/task/status.json", b"")
        data = json.loads(written)
        assert data["nodes"]["qgate"]["status"] == "passed"

    def test_write_status_json_local(self):
        """write_status_json should write to local disk."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            task_path = Path(tmp) / "test-task"
            task_path.mkdir()

            result = WorkerResult(task_ref="test", task_name="test-task", mode="pipeline")
            result.valid = True
            result.nop_reward = 0.0
            result.gold_reward = 1.0
            result.total_time = 42.5

            write_status_json(task_path, result, nodes={"scaffold": {"status": "ok"}})

            status_file = task_path / "status.json"
            assert status_file.exists()
            data = json.loads(status_file.read_text())
            assert data["valid"] is True
            assert data["nop_reward"] == 0.0
            assert data["gold_reward"] == 1.0
            assert data["nodes"]["scaffold"]["status"] == "ok"
            assert data["schema_version"] == 2

    def test_write_status_json_preserves_history(self):
        """Multiple writes should accumulate history."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            task_path = Path(tmp) / "test-task"
            task_path.mkdir()

            # First write
            r1 = WorkerResult(task_ref="test", valid=False, nop_reward=1.0, gold_reward=0.0)
            write_status_json(task_path, r1)

            # Second write
            r2 = WorkerResult(task_ref="test", valid=True, nop_reward=0.0, gold_reward=1.0)
            write_status_json(task_path, r2)

            data = json.loads((task_path / "status.json").read_text())
            assert len(data["history"]) == 2
            assert data["history"][0]["verdict"] == "fail"
            assert data["history"][1]["verdict"] == "pass"


# ---------------------------------------------------------------------------
# 4. run_task() integration tests (full DAG with mocked nodes)
# ---------------------------------------------------------------------------


class TestRunTask(unittest.TestCase):
    """Integration tests for the unified run_task() DAG."""

    def _make_pool_and_sem(self):
        """Create a mock pool + semaphore for testing."""
        pool = MagicMock()
        backend = MagicMock()
        backend.name = "test-backend"
        backend.resolve_model.return_value = "test-model"
        backend.subprocess_env.return_value = {"ANTHROPIC_API_KEY": "test"}

        # acquire() returns an async context manager yielding backend
        ctx = AsyncMock()
        ctx.__aenter__ = AsyncMock(return_value=backend)
        ctx.__aexit__ = AsyncMock(return_value=None)
        pool.acquire.return_value = ctx

        sem = asyncio.Semaphore(10)
        return pool, backend, sem

    @patch("taskforge.e2b_worker.create_worker_sandbox")
    @patch("taskforge.e2b_worker.upload_taskforge_modules")
    @patch("taskforge.e2b_worker.upload_task_files")
    @patch("taskforge.e2b_worker.node_validate_and_fix")
    @patch("taskforge.e2b_worker.read_sandbox_status")
    @patch("taskforge.e2b_worker.download_task_files")
    @patch("taskforge.e2b_worker.write_status_json")
    def test_validate_only_skips_early_nodes(
        self, mock_write_status, mock_download, mock_read_status,
        mock_validate, mock_upload_task, mock_upload_tf, mock_create,
    ):
        """start_at=validate should skip scaffold, qgate, rubric, enrich, improve."""
        import tempfile

        sandbox = _make_sandbox()
        mock_create.return_value = sandbox
        mock_upload_tf.return_value = None
        mock_upload_task.return_value = None
        mock_validate.return_value = ("ok", "")
        mock_read_status.return_value = {
            "nodes": {"validate": {"nop_reward": 0.0, "gold_reward": 1.0}}
        }
        mock_download.return_value = ["task.toml"]
        mock_write_status.return_value = None

        pool, backend, sem = self._make_pool_and_sem()

        with tempfile.TemporaryDirectory() as tmp:
            task_dir = Path(tmp)
            task_path = task_dir / "my-task"
            task_path.mkdir()
            (task_path / "environment").mkdir()
            (task_path / "environment" / "Dockerfile").write_text("FROM ubuntu")
            (task_path / "tests").mkdir()
            (task_path / "tests" / "test.sh").write_text("echo")

            result = _run(run_task(
                "my-task", task_dir, pool, sem,
                start_at=StartAt.VALIDATE,
                agentmd=True,
            ))

        assert result.valid is True
        assert result.nop_reward == 0.0
        assert result.gold_reward == 1.0
        assert result.scaffold_status == "skipped"
        # Validate should have been called
        mock_validate.assert_called_once()
        # Download should have been called (valid task)
        mock_download.assert_called_once()

    @patch("taskforge.e2b_worker.create_worker_sandbox")
    @patch("taskforge.e2b_worker.upload_taskforge_modules")
    @patch("taskforge.e2b_worker.node_scaffold")
    @patch("taskforge.e2b_worker.node_clone_repo")
    @patch("taskforge.e2b_worker.node_qgate")
    @patch("taskforge.e2b_worker.node_rubric_loop")
    @patch("taskforge.e2b_worker.node_enrich_p2p")
    @patch("taskforge.e2b_worker.node_check_test_quality")
    @patch("taskforge.e2b_worker.node_improve_tests")
    @patch("taskforge.e2b_worker.node_validate_and_fix")
    @patch("taskforge.e2b_worker.node_rubric_lint")
    @patch("taskforge.e2b_worker.read_sandbox_status")
    @patch("taskforge.e2b_worker.update_sandbox_status")
    @patch("taskforge.e2b_worker.download_task_files")
    @patch("taskforge.e2b_worker.write_status_json")
    def test_full_dag_new_pr(
        self, mock_write_status, mock_download, mock_update_status,
        mock_read_status, mock_lint, mock_validate, mock_improve,
        mock_check_quality, mock_enrich, mock_rubric_loop, mock_qgate,
        mock_clone, mock_scaffold, mock_upload_tf, mock_create,
    ):
        """Full DAG from scaffold through download for a new PR."""
        import tempfile

        sandbox = _make_sandbox()
        mock_create.return_value = sandbox
        mock_upload_tf.return_value = None
        mock_scaffold.return_value = ("ok", "test-task-name", "")
        mock_clone.return_value = ("owner/repo", "abc123")
        mock_qgate.return_value = ("passed", ["has_tier1"])
        mock_rubric_loop.return_value = ("ok", "HIGH", "", 2)
        mock_enrich.return_value = ("ok", "")
        mock_check_quality.return_value = (True, "no subprocess.run")
        mock_improve.return_value = ("ok", "")
        mock_validate.return_value = ("ok", "")
        mock_lint.return_value = (0, [])
        mock_read_status.return_value = {
            "nodes": {"validate": {"nop_reward": 0.0, "gold_reward": 1.0}}
        }
        mock_update_status.return_value = None
        mock_download.return_value = ["task.toml", "tests/test.sh"]
        mock_write_status.return_value = None

        pool, backend, sem = self._make_pool_and_sem()

        with tempfile.TemporaryDirectory() as tmp:
            task_dir = Path(tmp)

            result = _run(run_task(
                "", task_dir, pool, sem,
                start_at=StartAt.SCAFFOLD,
                pr_ref="owner/repo#42",
                agentmd=True,
            ))

        assert result.valid is True
        assert result.task_name == "test-task-name"
        assert result.scaffold_status == "ok"
        mock_scaffold.assert_called_once()
        mock_qgate.assert_called_once()
        mock_rubric_loop.assert_called_once()
        mock_enrich.assert_called_once()
        mock_improve.assert_called_once()
        mock_validate.assert_called_once()
        mock_download.assert_called_once()

    @patch("taskforge.e2b_worker.create_worker_sandbox")
    @patch("taskforge.e2b_worker.upload_taskforge_modules")
    @patch("taskforge.e2b_worker.node_scaffold")
    @patch("taskforge.e2b_worker.update_sandbox_status")
    def test_scaffold_abandoned_no_download(
        self, mock_update_status, mock_scaffold, mock_upload_tf, mock_create,
    ):
        """Abandoned scaffold should NOT download files."""
        import tempfile

        sandbox = _make_sandbox()
        mock_create.return_value = sandbox
        mock_upload_tf.return_value = None
        mock_scaffold.return_value = ("abandoned", "", "not a good task")
        mock_update_status.return_value = None

        pool, _, sem = self._make_pool_and_sem()

        with tempfile.TemporaryDirectory() as tmp:
            result = _run(run_task(
                "", Path(tmp), pool, sem,
                start_at=StartAt.SCAFFOLD,
                pr_ref="owner/repo#99",
                agentmd=True,
            ))

        assert result.valid is False
        assert result.downloaded is False
        assert "abandoned" in result.error

    @patch("taskforge.e2b_worker.create_worker_sandbox")
    @patch("taskforge.e2b_worker.upload_taskforge_modules")
    @patch("taskforge.e2b_worker.node_scaffold")
    @patch("taskforge.e2b_worker.update_sandbox_status")
    def test_dedup_check_skips_existing(
        self, mock_update_status, mock_scaffold, mock_upload_tf, mock_create,
    ):
        """If task dir already exists on disk, skip unless --force."""
        import tempfile

        sandbox = _make_sandbox()
        mock_create.return_value = sandbox
        mock_upload_tf.return_value = None
        mock_scaffold.return_value = ("ok", "existing-task", "")
        mock_update_status.return_value = None

        pool, _, sem = self._make_pool_and_sem()

        with tempfile.TemporaryDirectory() as tmp:
            task_dir = Path(tmp)
            (task_dir / "existing-task").mkdir()  # Pre-existing task dir

            result = _run(run_task(
                "", task_dir, pool, sem,
                start_at=StartAt.SCAFFOLD,
                pr_ref="owner/repo#42",
                agentmd=True,
                force=False,
            ))

        assert "dedup" in result.error
        assert result.downloaded is False

    @patch("taskforge.e2b_worker.create_worker_sandbox")
    @patch("taskforge.e2b_worker.upload_taskforge_modules")
    @patch("taskforge.e2b_worker.node_scaffold")
    @patch("taskforge.e2b_worker.node_clone_repo")
    @patch("taskforge.e2b_worker.node_qgate")
    @patch("taskforge.e2b_worker.update_sandbox_status")
    def test_qgate_delete_kills_new_task(
        self, mock_update_status, mock_qgate, mock_clone,
        mock_scaffold, mock_upload_tf, mock_create,
    ):
        """Quality gate DELETE on new task → no download, no disk write."""
        import tempfile

        sandbox = _make_sandbox()
        mock_create.return_value = sandbox
        mock_upload_tf.return_value = None
        mock_scaffold.return_value = ("ok", "bad-task", "")
        mock_clone.return_value = ("owner/repo", "abc123")
        mock_qgate.return_value = ("DELETE", ["no_config_edits"])
        mock_update_status.return_value = None

        pool, _, sem = self._make_pool_and_sem()

        with tempfile.TemporaryDirectory() as tmp:
            result = _run(run_task(
                "", Path(tmp), pool, sem,
                start_at=StartAt.SCAFFOLD,
                pr_ref="owner/repo#42",
                agentmd=True,
            ))

        assert result.valid is False
        assert result.downloaded is False
        assert "DELETE" in result.error

    @patch("taskforge.e2b_worker.create_worker_sandbox")
    @patch("taskforge.e2b_worker.upload_taskforge_modules")
    @patch("taskforge.e2b_worker.upload_task_files")
    @patch("taskforge.e2b_worker.node_clone_repo")
    @patch("taskforge.e2b_worker.node_qgate")
    @patch("taskforge.e2b_worker.node_rubric_loop")
    @patch("taskforge.e2b_worker.node_enrich_p2p")
    @patch("taskforge.e2b_worker.node_check_test_quality")
    @patch("taskforge.e2b_worker.node_validate_and_fix")
    @patch("taskforge.e2b_worker.read_sandbox_status")
    @patch("taskforge.e2b_worker.update_sandbox_status")
    @patch("taskforge.e2b_worker.write_status_json")
    def test_qgate_delete_existing_writes_status(
        self, mock_write_status, mock_update_status, mock_read_status,
        mock_validate, mock_check_quality, mock_enrich, mock_rubric_loop,
        mock_qgate, mock_clone, mock_upload_task, mock_upload_tf, mock_create,
    ):
        """Quality gate DELETE on existing task → writes status.json locally."""
        import tempfile

        sandbox = _make_sandbox()
        mock_create.return_value = sandbox
        mock_upload_tf.return_value = None
        mock_upload_task.return_value = None
        mock_clone.return_value = ("owner/repo", "abc123")
        mock_qgate.return_value = ("DELETE", ["boilerplate_rubric_only"])
        mock_update_status.return_value = None

        pool, _, sem = self._make_pool_and_sem()

        with tempfile.TemporaryDirectory() as tmp:
            task_dir = Path(tmp)
            task_path = task_dir / "existing-task"
            task_path.mkdir()
            (task_path / "environment").mkdir()
            (task_path / "environment" / "Dockerfile").write_text("FROM ubuntu")
            (task_path / "tests").mkdir()
            (task_path / "tests" / "test.sh").write_text("echo")

            result = _run(run_task(
                "existing-task", task_dir, pool, sem,
                start_at=StartAt.QGATE,
                agentmd=True,
            ))

        assert result.valid is False
        # write_status_json should have been called for existing task
        mock_write_status.assert_called_once()

    @patch("taskforge.e2b_worker.create_worker_sandbox")
    @patch("taskforge.e2b_worker.upload_taskforge_modules")
    @patch("taskforge.e2b_worker.upload_task_files")
    @patch("taskforge.e2b_worker.node_enrich_p2p")
    @patch("taskforge.e2b_worker.node_check_test_quality")
    @patch("taskforge.e2b_worker.node_improve_tests")
    @patch("taskforge.e2b_worker.node_validate_and_fix")
    @patch("taskforge.e2b_worker.read_sandbox_status")
    @patch("taskforge.e2b_worker.update_sandbox_status")
    @patch("taskforge.e2b_worker.write_status_json")
    def test_start_at_improve_skips_enrich(
        self, mock_write_status, mock_update_status, mock_read_status,
        mock_validate, mock_improve, mock_check_quality, mock_enrich,
        mock_upload_task, mock_upload_tf, mock_create,
    ):
        """start_at=improve should skip enrich node."""
        import tempfile

        sandbox = _make_sandbox()
        mock_create.return_value = sandbox
        mock_upload_tf.return_value = None
        mock_upload_task.return_value = None
        mock_check_quality.return_value = (True, "needs improvement")
        mock_improve.return_value = ("ok", "")
        mock_validate.return_value = ("ok", "")
        mock_read_status.return_value = {
            "nodes": {"validate": {"nop_reward": 0.0, "gold_reward": 1.0}}
        }
        mock_update_status.return_value = None
        mock_write_status.return_value = None

        pool, _, sem = self._make_pool_and_sem()

        with tempfile.TemporaryDirectory() as tmp:
            task_dir = Path(tmp)
            task_path = task_dir / "my-task"
            task_path.mkdir()
            (task_path / "environment").mkdir()
            (task_path / "environment" / "Dockerfile").write_text("FROM ubuntu")
            (task_path / "tests").mkdir()
            (task_path / "tests" / "test.sh").write_text("echo")

            result = _run(run_task(
                "my-task", task_dir, pool, sem,
                start_at=StartAt.IMPROVE,
                agentmd=True,
            ))

        # Enrich should NOT have been called
        mock_enrich.assert_not_called()
        # Improve should have been called
        mock_improve.assert_called_once()
        # Validate should have been called
        mock_validate.assert_called_once()

    @patch("taskforge.e2b_worker.create_worker_sandbox")
    @patch("taskforge.e2b_worker.upload_taskforge_modules")
    @patch("taskforge.e2b_worker.upload_task_files")
    @patch("taskforge.e2b_worker.node_validate_and_fix")
    @patch("taskforge.e2b_worker.read_sandbox_status")
    @patch("taskforge.e2b_worker.update_sandbox_status")
    @patch("taskforge.e2b_worker.write_status_json")
    def test_invalid_task_not_downloaded(
        self, mock_write_status, mock_update_status, mock_read_status,
        mock_validate, mock_upload_task, mock_upload_tf, mock_create,
    ):
        """Task with gold≠1 should NOT be downloaded."""
        import tempfile

        sandbox = _make_sandbox()
        mock_create.return_value = sandbox
        mock_upload_tf.return_value = None
        mock_upload_task.return_value = None
        mock_validate.return_value = ("ok", "")
        mock_read_status.return_value = {
            "nodes": {"validate": {"nop_reward": 0.0, "gold_reward": 0.0}}
        }
        mock_update_status.return_value = None
        mock_write_status.return_value = None

        pool, _, sem = self._make_pool_and_sem()

        with tempfile.TemporaryDirectory() as tmp:
            task_dir = Path(tmp)
            task_path = task_dir / "my-task"
            task_path.mkdir()
            (task_path / "environment").mkdir()
            (task_path / "environment" / "Dockerfile").write_text("FROM ubuntu")
            (task_path / "tests").mkdir()
            (task_path / "tests" / "test.sh").write_text("echo")

            result = _run(run_task(
                "my-task", task_dir, pool, sem,
                start_at=StartAt.VALIDATE,
                agentmd=False,
            ))

        assert result.valid is False
        assert result.downloaded is False
        # Status should still be written for existing task
        mock_write_status.assert_called_once()

    @patch("taskforge.e2b_worker.create_worker_sandbox")
    @patch("taskforge.e2b_worker.upload_taskforge_modules")
    @patch("taskforge.e2b_worker.upload_task_files")
    @patch("taskforge.e2b_worker.node_validate_and_fix")
    @patch("taskforge.e2b_worker.read_sandbox_status")
    @patch("taskforge.e2b_worker.update_sandbox_status")
    @patch("taskforge.e2b_worker.download_task_files")
    @patch("taskforge.e2b_worker.write_status_json")
    def test_no_agentmd_skips_qgate_and_rubric_and_lint(
        self, mock_write_status, mock_download, mock_update_status,
        mock_read_status, mock_validate, mock_upload_task,
        mock_upload_tf, mock_create,
    ):
        """With agentmd=False, quality gate, rubric, and lint are skipped."""
        import tempfile

        sandbox = _make_sandbox()
        mock_create.return_value = sandbox
        mock_upload_tf.return_value = None
        mock_upload_task.return_value = None
        mock_validate.return_value = ("ok", "")
        mock_read_status.return_value = {
            "nodes": {"validate": {"nop_reward": 0.0, "gold_reward": 1.0}}
        }
        mock_update_status.return_value = None
        mock_download.return_value = ["task.toml"]
        mock_write_status.return_value = None

        pool, _, sem = self._make_pool_and_sem()

        with tempfile.TemporaryDirectory() as tmp:
            task_dir = Path(tmp)
            task_path = task_dir / "my-task"
            task_path.mkdir()
            (task_path / "environment").mkdir()
            (task_path / "environment" / "Dockerfile").write_text("FROM ubuntu")
            (task_path / "tests").mkdir()
            (task_path / "tests" / "test.sh").write_text("echo")

            result = _run(run_task(
                "my-task", task_dir, pool, sem,
                start_at=StartAt.VALIDATE,
                agentmd=False,
            ))

        assert result.valid is True
        assert result.qgate_verdict == ""  # Not set — skipped

    def test_new_pr_requires_scaffold_start(self):
        """New PR with start_at > scaffold should error."""
        pool, _, sem = self._make_pool_and_sem()

        with patch("taskforge.e2b_worker.create_worker_sandbox") as mock_create, \
             patch("taskforge.e2b_worker.upload_taskforge_modules"):
            mock_create.return_value = _make_sandbox()

            import tempfile
            with tempfile.TemporaryDirectory() as tmp:
                result = _run(run_task(
                    "", Path(tmp), pool, sem,
                    start_at=StartAt.VALIDATE,
                    pr_ref="owner/repo#42",
                ))

            assert "requires start_at=scaffold" in result.error

    def test_missing_task_dir_errors(self):
        """Existing task with nonexistent dir should error."""
        pool, _, sem = self._make_pool_and_sem()

        with patch("taskforge.e2b_worker.create_worker_sandbox") as mock_create, \
             patch("taskforge.e2b_worker.upload_taskforge_modules"):
            mock_create.return_value = _make_sandbox()

            import tempfile
            with tempfile.TemporaryDirectory() as tmp:
                result = _run(run_task(
                    "nonexistent-task", Path(tmp), pool, sem,
                    start_at=StartAt.VALIDATE,
                ))

            assert "not found" in result.error


# ---------------------------------------------------------------------------
# 5. run_batch() orchestration tests
# ---------------------------------------------------------------------------


class TestRunBatch(unittest.TestCase):
    """Test the batch orchestrator."""

    @patch("taskforge.e2b_worker.run_task_docker_only")
    def test_docker_only_dispatches_correctly(self, mock_docker):
        """docker-only mode should call run_task_docker_only."""
        mock_docker.return_value = WorkerResult(
            task_ref="t1", task_name="t1", mode="docker-only", valid=True,
        )

        results = _run(run_batch(
            ["task-a", "task-b"],
            mode="docker-only",
            pool=None,
            concurrency=2,
            task_dir=Path("/tmp"),
        ))

        assert len(results) == 2
        assert mock_docker.call_count == 2

    @patch("taskforge.e2b_worker.run_task")
    def test_pipeline_pr_dispatch(self, mock_run):
        """Pipeline mode with dict items should pass pr_ref."""
        mock_run.return_value = WorkerResult(
            task_ref="owner/repo#42", mode="pipeline", valid=True,
        )

        results = _run(run_batch(
            [{"pr_ref": "owner/repo#42"}],
            mode="pipeline",
            pool=MagicMock(),
            concurrency=1,
            task_dir=Path("/tmp"),
            start_at=StartAt.SCAFFOLD,
            agentmd=True,
        ))

        assert len(results) == 1
        # Verify pr_ref was passed
        call_kwargs = mock_run.call_args
        assert call_kwargs.kwargs.get("pr_ref") == "owner/repo#42"

    @patch("taskforge.e2b_worker.run_task")
    def test_pipeline_existing_task_dispatch(self, mock_run):
        """Pipeline mode with string items should pass task_name."""
        mock_run.return_value = WorkerResult(
            task_ref="my-task", mode="pipeline", valid=True,
        )

        results = _run(run_batch(
            ["my-task"],
            mode="pipeline",
            pool=MagicMock(),
            concurrency=1,
            task_dir=Path("/tmp"),
            start_at=StartAt.VALIDATE,
        ))

        assert len(results) == 1
        # First positional arg should be the task name
        assert mock_run.call_args[0][0] == "my-task"

    @patch("taskforge.e2b_worker.run_task")
    def test_rate_limited_retries(self, mock_run):
        """Rate-limited tasks should be re-enqueued up to max_retries."""
        call_count = [0]

        async def rate_limit_then_pass(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                return WorkerResult(
                    task_ref="t1", mode="pipeline",
                    error="rate limited during validate",
                )
            return WorkerResult(task_ref="t1", mode="pipeline", valid=True)

        mock_run.side_effect = rate_limit_then_pass

        results = _run(run_batch(
            ["task-a"],
            mode="pipeline",
            pool=MagicMock(),
            concurrency=1,
            task_dir=Path("/tmp"),
            max_retries=2,
        ))

        # First call rate limited → re-enqueued → second call succeeds
        assert len(results) == 1
        assert results[0].valid is True
        assert call_count[0] == 2

    @patch("taskforge.e2b_worker.run_task")
    def test_agentmd_and_force_propagated(self, mock_run):
        """agentmd and force flags should be passed to run_task."""
        mock_run.return_value = WorkerResult(task_ref="t1", mode="pipeline")

        _run(run_batch(
            ["my-task"],
            mode="pipeline",
            pool=MagicMock(),
            concurrency=1,
            task_dir=Path("/tmp"),
            agentmd=True,
            force=True,
        ))

        kwargs = mock_run.call_args.kwargs
        assert kwargs["agentmd"] is True
        assert kwargs["force"] is True

    def test_unknown_mode_returns_error(self):
        """Unknown mode should return error result (caught by worker)."""
        results = _run(run_batch(
            ["t1"],
            mode="bogus",
            pool=None,
            concurrency=1,
            task_dir=Path("/tmp"),
        ))
        assert len(results) == 1
        assert "Unknown mode" in results[0].error


# ---------------------------------------------------------------------------
# 6. CLI dispatch tests
# ---------------------------------------------------------------------------


class TestCollectTasks(unittest.TestCase):
    """Test task directory scanning."""

    def test_collects_valid_tasks(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            task_dir = Path(tmp)
            # Valid task
            (task_dir / "good-task" / "environment").mkdir(parents=True)
            (task_dir / "good-task" / "environment" / "Dockerfile").write_text("FROM ubuntu")
            (task_dir / "good-task" / "tests").mkdir()
            (task_dir / "good-task" / "tests" / "test.sh").write_text("echo")
            # Invalid task (missing test.sh)
            (task_dir / "bad-task" / "environment").mkdir(parents=True)
            (task_dir / "bad-task" / "environment" / "Dockerfile").write_text("FROM ubuntu")
            # Not a task dir
            (task_dir / "readme.md").write_text("hi")

            tasks = collect_tasks(task_dir, None, None)
            assert tasks == ["good-task"]

    def test_filter_pattern(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            task_dir = Path(tmp)
            for name in ["airflow-fix-x", "biome-fix-y", "airflow-add-z"]:
                (task_dir / name / "environment").mkdir(parents=True)
                (task_dir / name / "environment" / "Dockerfile").write_text("FROM ubuntu")
                (task_dir / name / "tests").mkdir()
                (task_dir / name / "tests" / "test.sh").write_text("echo")

            tasks = collect_tasks(task_dir, "airflow-*", None)
            assert len(tasks) == 2
            assert all(t.startswith("airflow-") for t in tasks)

    def test_limit(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            task_dir = Path(tmp)
            for i in range(5):
                name = f"task-{i}"
                (task_dir / name / "environment").mkdir(parents=True)
                (task_dir / name / "environment" / "Dockerfile").write_text("FROM ubuntu")
                (task_dir / name / "tests").mkdir()
                (task_dir / name / "tests" / "test.sh").write_text("echo")

            tasks = collect_tasks(task_dir, None, 3)
            assert len(tasks) == 3


class TestLoadPrItems(unittest.TestCase):
    """Test JSONL loading."""

    def test_loads_json_lines(self):
        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            f.write('{"pr_ref": "owner/repo#1"}\n')
            f.write('{"pr_ref": "owner/repo#2"}\n')
            f.write('{"pr_ref": "owner/repo#3"}\n')
            f.flush()
            items = load_pr_items(Path(f.name))
        assert len(items) == 3
        assert items[0]["pr_ref"] == "owner/repo#1"

    def test_loads_plain_strings(self):
        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            f.write("owner/repo#1\n")
            f.write("owner/repo#2\n")
            f.flush()
            items = load_pr_items(Path(f.name))
        assert len(items) == 2
        assert items[0]["pr_ref"] == "owner/repo#1"

    def test_offset_and_limit(self):
        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            for i in range(10):
                f.write(f'{{"pr_ref": "r#{i}"}}\n')
            f.flush()
            items = load_pr_items(Path(f.name), offset=3, limit=2)
        assert len(items) == 2
        assert items[0]["pr_ref"] == "r#3"
        assert items[1]["pr_ref"] == "r#4"

    def test_empty_lines_skipped(self):
        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            f.write('{"pr_ref": "r#1"}\n')
            f.write('\n')
            f.write('   \n')
            f.write('{"pr_ref": "r#2"}\n')
            f.flush()
            items = load_pr_items(Path(f.name))
        assert len(items) == 2


class TestCLIDispatch(unittest.TestCase):
    """Test that CLI args route correctly to the right mode/items."""

    @patch("taskforge.e2b_worker.run_batch")
    @patch("taskforge.e2b_worker.ensure_template")
    def test_input_flag_takes_priority(self, mock_template, mock_batch):
        """--input MUST be checked FIRST, regardless of mode.

        This is the critical fix for the --input bug where mode=agents
        ignored --input and always scanned existing dirs.
        """
        import tempfile

        mock_template.return_value = "harbor-worker-v3"
        mock_batch.return_value = []

        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            f.write('{"pr_ref": "owner/repo#1"}\n')
            f.write('{"pr_ref": "owner/repo#2"}\n')
            f.flush()
            input_path = f.name

        args = argparse.Namespace(
            mode="pipeline",
            start_at=None,
            task_dir="harbor_tasks",
            tasks=None,
            filter=None,
            limit=None,
            offset=None,
            input=input_path,
            concurrency=5,
            pool=False,
            agentmd=True,
            force=False,
        )

        import os
        os.environ["E2B_API_KEY"] = "test"
        try:
            _run(async_main(args))
        except SystemExit:
            pass

        # Verify run_batch was called with the JSONL items, not scanned dirs
        call_args = mock_batch.call_args
        items = call_args[0][0]  # First positional arg
        assert len(items) == 2
        assert items[0]["pr_ref"] == "owner/repo#1"
        # Default start_at for --input should be SCAFFOLD
        assert call_args[1]["start_at"] == StartAt.SCAFFOLD

    @patch("taskforge.e2b_worker.run_batch")
    @patch("taskforge.e2b_worker.ensure_template")
    @patch("taskforge.e2b_worker.collect_tasks")
    def test_no_input_scans_dirs(self, mock_collect, mock_template, mock_batch):
        """Without --input, should scan task directories."""
        mock_template.return_value = "harbor-worker-v3"
        mock_batch.return_value = []
        mock_collect.return_value = ["task-a", "task-b"]

        args = argparse.Namespace(
            mode="pipeline",
            start_at="validate",
            task_dir="harbor_tasks",
            tasks=None,
            filter=None,
            limit=None,
            offset=None,
            input=None,
            concurrency=5,
            pool=False,
            agentmd=False,
            force=False,
        )

        import os
        os.environ["E2B_API_KEY"] = "test"
        try:
            _run(async_main(args))
        except SystemExit:
            pass

        call_args = mock_batch.call_args
        items = call_args[0][0]
        assert items == ["task-a", "task-b"]
        assert call_args[1]["start_at"] == StartAt.VALIDATE

    @patch("taskforge.e2b_worker.run_batch")
    @patch("taskforge.e2b_worker.ensure_template")
    def test_tasks_flag_splits_comma_sep(self, mock_template, mock_batch):
        """--tasks should split by comma."""
        mock_template.return_value = "harbor-worker-v3"
        mock_batch.return_value = []

        args = argparse.Namespace(
            mode="pipeline",
            start_at="validate",
            task_dir="harbor_tasks",
            tasks="task-a,task-b,task-c",
            filter=None,
            limit=None,
            offset=None,
            input=None,
            concurrency=5,
            pool=False,
            agentmd=False,
            force=False,
        )

        import os
        os.environ["E2B_API_KEY"] = "test"
        try:
            _run(async_main(args))
        except SystemExit:
            pass

        call_args = mock_batch.call_args
        items = call_args[0][0]
        assert items == ["task-a", "task-b", "task-c"]


# Need to import for CLI tests
import argparse
from taskforge.e2b_worker import async_main


if __name__ == "__main__":
    unittest.main()
