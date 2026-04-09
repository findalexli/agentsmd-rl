"""
Task: prime-rl-eval-samples-table
Repo: PrimeIntellect-ai/prime-rl @ 714d0ea90421ddfe4b5b5c6dca250e330f5ebe65
PR:   2124

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import importlib.util
import subprocess
import sys
import textwrap
from pathlib import Path
from unittest.mock import MagicMock

# Mock heavy dependencies before any prime_rl imports
_vf_mock = MagicMock()
sys.modules.setdefault("verifiers", _vf_mock)

REPO = "/workspace/prime-rl"
SRC = f"{REPO}/src"

MONITOR_BASE = f"{SRC}/prime_rl/utils/monitor/base.py"
MONITOR_MULTI = f"{SRC}/prime_rl/utils/monitor/multi.py"
MONITOR_WANDB = f"{SRC}/prime_rl/utils/monitor/wandb.py"
MONITOR_PRIME = f"{SRC}/prime_rl/utils/monitor/prime.py"
EVAL_UTILS = f"{SRC}/prime_rl/orchestrator/eval_utils.py"

MODIFIED_FILES = [MONITOR_BASE, MONITOR_MULTI, MONITOR_WANDB, MONITOR_PRIME, EVAL_UTILS]


def _load_base_module():
    """Load base.py directly via importlib, bypassing monitor/__init__.py.

    The __init__.py imports transformers, wandb, pandas, etc. which are not
    installed. base.py only needs abc, typing, and verifiers (mocked).
    """
    spec = importlib.util.spec_from_file_location("_monitor_base", MONITOR_BASE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _extract_method(filepath, class_name, method_name):
    """Extract a method's source from a class via AST (for modules with heavy deps)."""
    source = Path(filepath).read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == method_name:
                    lines = source.splitlines(keepends=True)
                    return "".join(lines[item.lineno - 1 : item.end_lineno])
    return None


def _strip_type_hints(func_src):
    """Remove type annotations from function source to avoid NameError on exec."""
    tree = ast.parse(textwrap.dedent(func_src))
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            node.returns = None
            for arg in node.args.args + node.args.kwonlyargs:
                arg.annotation = None
    return ast.unparse(tree)


def _exec_wandb_method(func_src):
    """Compile extracted WandbMonitor method into a callable with mocked globals."""
    wandb_mock = MagicMock()
    table_mock = MagicMock()

    class FakeConfig:
        class _Extras:
            samples = True
        log_extras = _Extras()

    mock_self = MagicMock()
    mock_self.is_master = True
    mock_self.config = FakeConfig()
    mock_self.eval_samples_table = table_mock

    clean_src = _strip_type_hints(func_src)
    wrapper = "class _W:\n" + textwrap.indent(clean_src, "    ")
    ns = {"wandb": wandb_mock, "WandbWithExtrasConfig": FakeConfig, "__builtins__": __builtins__}
    exec(wrapper, ns)
    method = ns["_W"].__dict__["log_eval_samples"]
    return method, mock_self, table_mock, wandb_mock


def _exec_multi_method(func_src):
    """Compile extracted MultiMonitor method into a callable with mocked globals."""
    clean_src = _strip_type_hints(func_src)
    wrapper = "class _M:\n" + textwrap.indent(clean_src, "    ")
    ns = {"__builtins__": __builtins__}
    exec(wrapper, ns)
    method = ns["_M"].__dict__["log_eval_samples"]
    return method


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """All modified files must parse without errors."""
    for fpath in MODIFIED_FILES:
        ast.parse(Path(fpath).read_text())


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_abc_enforces_log_eval_samples():
    """Monitor ABC requires log_eval_samples; omitting it raises TypeError."""
    r = subprocess.run(
        ["python3", "-c", textwrap.dedent("""\
            import sys
            from unittest.mock import MagicMock
            sys.modules['verifiers'] = MagicMock()
            from prime_rl.utils.monitor.base import Monitor

            class Incomplete(Monitor):
                def log(self, metrics, step): pass
                def log_samples(self, rollouts, step): pass
                def log_final_samples(self): pass

            try:
                Incomplete()
                print("FAIL: instantiated without log_eval_samples")
                sys.exit(1)
            except TypeError as e:
                if "log_eval_samples" in str(e):
                    print("PASS")
                else:
                    print(f"FAIL: TypeError but wrong cause: {e}")
                    sys.exit(1)
        """)],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_noop_monitor_accepts_log_eval_samples():
    """NoOpMonitor implements log_eval_samples without crashing, for varied inputs."""
    r = subprocess.run(
        ["python3", "-c", textwrap.dedent("""\
            import sys
            from unittest.mock import MagicMock
            sys.modules['verifiers'] = MagicMock()
            from prime_rl.utils.monitor.base import NoOpMonitor

            noop = object.__new__(NoOpMonitor)
            noop.log_eval_samples(
                rollouts=[{"example_id": "ex1", "completion": "hello", "reward": 1.0, "task": "math"}],
                env_name="env_a", step=1,
            )
            noop.log_eval_samples(
                rollouts=[{"example_id": "ex2", "completion": "world", "reward": 0.5, "task": "code"},
                          {"example_id": "ex3", "completion": "foo", "reward": 0.0, "task": "logic"}],
                env_name="env_b", step=100,
            )
            noop.log_eval_samples(rollouts=[], env_name="empty_env", step=0)
            print("PASS")
        """)],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_multi_monitor_delegates_eval_samples():
    """MultiMonitor forwards log_eval_samples to all sub-monitors with correct args."""
    # AST-only because: multi.py imports from prime_rl.utils.logger and monitor __init__
    func_src = _extract_method(MONITOR_MULTI, "MultiMonitor", "log_eval_samples")
    assert func_src is not None, "MultiMonitor.log_eval_samples not found"

    method = _exec_multi_method(func_src)

    for rollouts, env_name, step in [
        ([{"example_id": "1", "completion": "answer", "reward": 0.9}], "gsm8k", 42),
        ([{"example_id": "2", "completion": "x", "reward": 0.1},
          {"example_id": "3", "completion": "y", "reward": 0.7}], "humaneval", 200),
    ]:
        mock_a, mock_b, mock_c = MagicMock(), MagicMock(), MagicMock()
        mock_self = MagicMock()
        mock_self.monitors = [mock_a, mock_b, mock_c]

        method(mock_self, rollouts=rollouts, env_name=env_name, step=step)
        for m in [mock_a, mock_b, mock_c]:
            m.log_eval_samples.assert_called_once_with(
                rollouts=rollouts, env_name=env_name, step=step,
            )


# [pr_diff] fail_to_pass
def test_wandb_log_eval_samples_processes_rollouts():
    """WandbMonitor.log_eval_samples adds rows to table and calls wandb.log."""
    # AST-only because: WandbMonitor.__init__ requires wandb credentials and GPU context
    func_src = _extract_method(MONITOR_WANDB, "WandbMonitor", "log_eval_samples")
    assert func_src is not None, "WandbMonitor.log_eval_samples not found"

    method, mock_self, table_mock, wandb_mock = _exec_wandb_method(func_src)

    rollouts = [
        {"example_id": "ex1", "completion": "ans1", "reward": 0.8, "task": "math"},
        {"example_id": "ex2", "completion": "ans2", "reward": 0.5, "task": "code"},
        {"example_id": "ex3", "completion": "ans3", "reward": 1.0, "task": "logic"},
    ]
    method(mock_self, rollouts=rollouts, env_name="gsm8k", step=100)

    assert table_mock.add_data.call_count == 3, (
        f"Expected 3 rows, got {table_mock.add_data.call_count}"
    )
    assert wandb_mock.log.called, "wandb.log not called"

    first_call_args = table_mock.add_data.call_args_list[0][0]
    assert 100 in first_call_args, f"step=100 not in row data: {first_call_args}"
    assert "gsm8k" in first_call_args, f"env_name 'gsm8k' not in row data: {first_call_args}"
    assert "ex1" in first_call_args, f"example_id 'ex1' not in row data: {first_call_args}"


# [pr_diff] fail_to_pass
def test_wandb_log_eval_samples_skips_empty_completion():
    """Rollouts with empty/missing completion are not added to the table."""
    # AST-only because: WandbMonitor.__init__ requires wandb credentials and GPU context
    func_src = _extract_method(MONITOR_WANDB, "WandbMonitor", "log_eval_samples")
    assert func_src is not None, "WandbMonitor.log_eval_samples not found"

    method, mock_self, table_mock, wandb_mock = _exec_wandb_method(func_src)

    rollouts = [
        {"example_id": "ex1", "completion": "", "reward": 0.0, "task": "math"},
        {"example_id": "ex2", "reward": 0.5, "task": "code"},  # missing completion key
        {"example_id": "ex3", "completion": "valid answer", "reward": 1.0, "task": "math"},
        {"example_id": "ex4", "completion": "also valid", "reward": 0.3, "task": "logic"},
    ]
    method(mock_self, rollouts=rollouts, env_name="test", step=50)

    assert table_mock.add_data.call_count == 2, (
        f"Expected 2 rows (only valid completions), got {table_mock.add_data.call_count}"
    )


# [pr_diff] fail_to_pass
def test_evaluate_env_calls_log_eval_samples():
    """evaluate_env function calls monitor.log_eval_samples after logging metrics."""
    # AST-only because: evaluate_env is async and requires distributed training env (vLLM, torch)
    source = Path(EVAL_UTILS).read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "evaluate_env":
            calls = [
                n for n in ast.walk(node)
                if isinstance(n, ast.Call)
                and isinstance(n.func, ast.Attribute)
                and n.func.attr == "log_eval_samples"
            ]
            assert len(calls) >= 1, "evaluate_env does not call log_eval_samples"
            return
    assert False, "evaluate_env function not found"


# [pr_diff] fail_to_pass
def test_prime_monitor_implements_log_eval_samples():
    """PrimeMonitor implements log_eval_samples (callable, no crash)."""
    func_src = _extract_method(MONITOR_PRIME, "PrimeMonitor", "log_eval_samples")
    assert func_src is not None, "PrimeMonitor.log_eval_samples not found"

    clean_src = _strip_type_hints(func_src)
    wrapper = "class _P:\n" + textwrap.indent(clean_src, "    ")
    ns = {"__builtins__": __builtins__}
    exec(wrapper, ns)
    method = ns["_P"].__dict__["log_eval_samples"]

    mock_self = MagicMock()
    rollouts = [{"example_id": "ex1", "completion": "ans", "reward": 0.8, "task": "math"}]
    method(mock_self, rollouts=rollouts, env_name="test", step=1)


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_abstract_methods_preserved():
    """Original abstract methods (log, log_samples, log_final_samples) are still enforced."""
    mod = _load_base_module()
    Monitor = mod.Monitor

    for missing in ["log", "log_samples", "log_final_samples"]:
        methods = {
            "log": lambda self, metrics, step: None,
            "log_samples": lambda self, rollouts, step: None,
            "log_final_samples": lambda self: None,
            "log_eval_samples": lambda self, rollouts, env_name, step: None,
        }
        del methods[missing]
        Cls = type("Partial", (Monitor,), methods)
        try:
            Cls()
            assert False, f"Instantiated without {missing}"
        except TypeError:
            pass


# [repo_tests] pass_to_pass — CI/CD: ruff lint check
def test_repo_ruff_check():
    """Repo's ruff lint check passes on modified files (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    # Ignore pip warnings, just check ruff gets installed
    r = subprocess.run(
        ["ruff", "check", "src/prime_rl/utils/monitor", "--config=pyproject.toml"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass — CI/CD: ruff format check
def test_repo_ruff_format():
    """Repo's ruff format check passes on modified files (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    r = subprocess.run(
        ["ruff", "format", "--check", "src/prime_rl/utils/monitor", "--config=pyproject.toml"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout}\n{r.stderr}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — AGENTS.md rules
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:7 @ 714d0ea9
def test_no_excessive_comments_in_new_methods():
    """log_eval_samples methods should not have excessive inline comments (AGENTS.md:7)."""
    total_comments = 0
    for fpath in [MONITOR_BASE, MONITOR_MULTI, MONITOR_WANDB, MONITOR_PRIME]:
        source = Path(fpath).read_text()
        in_method = False
        method_indent = 0
        for line in source.splitlines():
            stripped = line.strip()
            if "def log_eval_samples" in stripped:
                in_method = True
                method_indent = len(line) - len(line.lstrip())
                continue
            if in_method:
                if stripped and (len(line) - len(line.lstrip())) <= method_indent:
                    in_method = False
                    continue
                if stripped.startswith("#"):
                    total_comments += 1
    assert total_comments <= 8, f"{total_comments} comment lines in log_eval_samples methods (excessive)"


# [agent_config] pass_to_pass — AGENTS.md:5 @ 714d0ea9
def test_no_unnecessary_try_except_in_new_methods():
    """WandbMonitor and PrimeMonitor log_eval_samples should avoid unnecessary try/except (AGENTS.md:5)."""
    for fpath, cls_name in [
        (MONITOR_WANDB, "WandbMonitor"),
        (MONITOR_PRIME, "PrimeMonitor"),
    ]:
        source = Path(fpath).read_text()
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == cls_name:
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == "log_eval_samples":
                        try_count = sum(1 for s in ast.walk(item) if isinstance(s, ast.Try))
                        assert try_count <= 1, (
                            f"{cls_name}.log_eval_samples has {try_count} try/except blocks (excessive)"
                        )
