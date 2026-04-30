"""
Task: slime-wandb-sglang-metrics
Repo: THUDM/slime @ d4c4d3fb24d45c3cd12f47b64b30fc3301286778
PR:   1768

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import json
import subprocess
import textwrap
from pathlib import Path

REPO = "/workspace/slime"

WANDB_UTILS = Path(f"{REPO}/slime/utils/wandb_utils.py")
LOGGING_UTILS = Path(f"{REPO}/slime/utils/logging_utils.py")
ROLLOUT = Path(f"{REPO}/slime/ray/rollout.py")
TRAIN = Path(f"{REPO}/train.py")
TRAIN_ASYNC = Path(f"{REPO}/train_async.py")

MODIFIED_FILES = [WANDB_UTILS, LOGGING_UTILS, ROLLOUT, TRAIN, TRAIN_ASYNC]


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code in a subprocess within the repo directory."""
    return subprocess.run(
        ["python3", "-c", textwrap.dedent(code)],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


def _parse(path: Path) -> ast.Module:
    return ast.parse(path.read_text())


def _find_func(tree: ast.Module, name: str) -> ast.FunctionDef | None:
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    return None


def _non_docstring_stmts(func: ast.FunctionDef) -> list[ast.stmt]:
    return [
        s for s in func.body
        if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))
    ]


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """All modified Python files must parse without errors."""
    for f in MODIFIED_FILES:
        ast.parse(f.read_text())


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests via subprocess
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_router_addr_removed_from_secondary():
    """init_wandb_secondary must not accept router_addr parameter."""
    r = _run_py("""
        import ast, json
        from pathlib import Path

        src = Path("/workspace/slime/slime/utils/wandb_utils.py").read_text()
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "init_wandb_secondary":
                params = [a.arg for a in node.args.args] + [a.arg for a in node.args.kwonlyargs]
                print(json.dumps({"params": params}))
                break
        else:
            print(json.dumps({"error": "init_wandb_secondary not found"}))
    """)
    assert r.returncode == 0, f"Script failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert "error" not in data, data.get("error")
    assert "router_addr" not in data["params"], (
        f"router_addr still in init_wandb_secondary signature: {data['params']}"
    )


# [pr_diff] fail_to_pass
def test_reinit_function_exists():
    """reinit_wandb_primary_with_open_metrics must exist with args + router_addr params."""
    r = _run_py("""
        import ast, json
        from pathlib import Path

        src = Path("/workspace/slime/slime/utils/wandb_utils.py").read_text()
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "reinit_wandb_primary_with_open_metrics":
                params = [a.arg for a in node.args.args] + [a.arg for a in node.args.kwonlyargs]
                print(json.dumps({"params": params}))
                break
        else:
            print(json.dumps({"error": "function not found"}))
    """)
    assert r.returncode == 0, f"Script failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert "error" not in data, data["error"]
    assert "args" in data["params"], "reinit function must accept 'args'"
    assert "router_addr" in data["params"], "reinit function must accept 'router_addr'"


# [pr_diff] fail_to_pass
def test_reinit_calls_wandb_finish_and_init():
    """reinit function calls wandb.finish() then wandb.init() to re-initialize."""
    r = _run_py("""
        import ast, sys, textwrap, json
        from pathlib import Path
        from unittest.mock import MagicMock

        path = Path("/workspace/slime/slime/utils/wandb_utils.py")
        src_lines = path.read_text().splitlines(keepends=True)
        tree = ast.parse(path.read_text())

        func_node = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "reinit_wandb_primary_with_open_metrics":
                func_node = node
                break
        assert func_node is not None, "reinit_wandb_primary_with_open_metrics not found"

        func_src = textwrap.dedent("".join(src_lines[func_node.lineno - 1 : func_node.end_lineno]))

        mock_wandb = MagicMock()
        mock_sglang = MagicMock()
        mock_sglang.__version__ = "slime-custom-0.1"
        sys.modules["sglang_router"] = mock_sglang

        namespace = {
            "wandb": mock_wandb,
            "logger": MagicMock(),
            "_is_offline_mode": lambda args: False,
            "_init_wandb_common": MagicMock(),
        }
        exec(compile(func_src, "<test>", "exec"), namespace)

        call_order = []
        mock_wandb.finish.side_effect = lambda *a, **k: call_order.append("finish")
        mock_wandb.init.side_effect = lambda *a, **k: call_order.append("init")

        args = MagicMock()
        args.use_wandb = True
        args.wandb_run_id = "test-run-id"
        args.wandb_team = "test-team"
        args.wandb_project = "test-project"
        args.wandb_dir = None

        namespace["reinit_wandb_primary_with_open_metrics"](args, "http://10.0.0.1:30000")

        print(json.dumps({"call_order": call_order}))
    """)
    assert r.returncode == 0, f"Failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    order = data["call_order"]
    assert "finish" in order, "reinit must call wandb.finish()"
    assert "init" in order, "reinit must call wandb.init()"
    assert order.index("finish") < order.index("init"), (
        "wandb.finish() must be called before wandb.init()"
    )


# [pr_diff] fail_to_pass
def test_reinit_configures_metrics_endpoints():
    """reinit function configures sgl_engine metrics endpoints with resume mode."""
    r = _run_py("""
        import ast, sys, textwrap, json
        from pathlib import Path
        from unittest.mock import MagicMock

        path = Path("/workspace/slime/slime/utils/wandb_utils.py")
        src_lines = path.read_text().splitlines(keepends=True)
        tree = ast.parse(path.read_text())

        func_node = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "reinit_wandb_primary_with_open_metrics":
                func_node = node
                break
        assert func_node is not None, "reinit_wandb_primary_with_open_metrics not found"

        func_src = textwrap.dedent("".join(src_lines[func_node.lineno - 1 : func_node.end_lineno]))

        results = []
        for addr in ["http://10.0.0.1:30000", "http://192.168.1.5:8080", "http://localhost:9090"]:
            mock_wandb = MagicMock()
            mock_sglang = MagicMock()
            mock_sglang.__version__ = "slime-custom-0.1"
            sys.modules["sglang_router"] = mock_sglang

            namespace = {
                "wandb": mock_wandb,
                "logger": MagicMock(),
                "_is_offline_mode": lambda args: False,
                "_init_wandb_common": MagicMock(),
            }
            exec(compile(func_src, "<test>", "exec"), namespace)

            args = MagicMock()
            args.use_wandb = True
            args.wandb_run_id = "test-run-id"
            args.wandb_team = "test-team"
            args.wandb_project = "test-project"
            args.wandb_dir = None

            namespace["reinit_wandb_primary_with_open_metrics"](args, addr)

            init_called = mock_wandb.init.called
            init_kwargs = dict(mock_wandb.init.call_args.kwargs) if init_called else {}
            settings_called = mock_wandb.Settings.called
            settings_kwargs = dict(mock_wandb.Settings.call_args.kwargs) if settings_called else {}

            endpoints = settings_kwargs.get("x_stats_open_metrics_endpoints", {})
            endpoints_str = {k: str(v) for k, v in endpoints.items()}

            results.append({
                "addr": addr,
                "init_called": init_called,
                "resume": init_kwargs.get("resume"),
                "settings_called": settings_called,
                "endpoints": endpoints_str,
            })

        print(json.dumps(results))
    """)
    assert r.returncode == 0, f"Failed: {r.stderr}"
    results = json.loads(r.stdout.strip())
    for item in results:
        addr = item["addr"]
        assert item["init_called"], f"wandb.init not called for addr={addr}"
        assert item["resume"], f"resume not set for addr={addr}"
        assert item["settings_called"], f"wandb.Settings not called for addr={addr}"
        endpoints = item["endpoints"]
        assert any(addr in v for v in endpoints.values()), (
            f"Router addr {addr} not in metrics endpoints: {endpoints}"
        )


# [pr_diff] fail_to_pass
def test_reinit_noop_when_no_router():
    """reinit returns early without touching wandb when router_addr is None."""
    r = _run_py("""
        import ast, sys, textwrap, json
        from pathlib import Path
        from unittest.mock import MagicMock

        path = Path("/workspace/slime/slime/utils/wandb_utils.py")
        src_lines = path.read_text().splitlines(keepends=True)
        tree = ast.parse(path.read_text())

        func_node = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "reinit_wandb_primary_with_open_metrics":
                func_node = node
                break
        assert func_node is not None, "reinit_wandb_primary_with_open_metrics not found"

        func_src = textwrap.dedent("".join(src_lines[func_node.lineno - 1 : func_node.end_lineno]))

        mock_wandb = MagicMock()
        mock_sglang = MagicMock()
        mock_sglang.__version__ = "slime-custom-0.1"
        sys.modules["sglang_router"] = mock_sglang

        namespace = {
            "wandb": mock_wandb,
            "logger": MagicMock(),
            "_is_offline_mode": lambda args: False,
            "_init_wandb_common": MagicMock(),
        }
        exec(compile(func_src, "<test>", "exec"), namespace)

        args = MagicMock()
        args.use_wandb = True

        namespace["reinit_wandb_primary_with_open_metrics"](args, None)

        print(json.dumps({
            "finish_called": mock_wandb.finish.called,
            "init_called": mock_wandb.init.called,
        }))
    """)
    assert r.returncode == 0, f"Failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert not data["finish_called"], "wandb.finish() must not be called when router_addr is None"
    assert not data["init_called"], "wandb.init() must not be called when router_addr is None"


# [pr_diff] fail_to_pass
def test_update_tracking_bridge_exists():
    """logging_utils exposes update_tracking_open_metrics bridging to wandb_utils."""
    r = _run_py("""
        import ast, json
        from pathlib import Path

        src = Path("/workspace/slime/slime/utils/logging_utils.py").read_text()
        tree = ast.parse(src)

        func = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "update_tracking_open_metrics":
                func = node
                break

        if func is None:
            print(json.dumps({"error": "update_tracking_open_metrics not found"}))
        else:
            params = [a.arg for a in func.args.args] + [a.arg for a in func.args.kwonlyargs]
            body_src = ast.unparse(func)
            print(json.dumps({
                "params": params,
                "delegates_to_reinit": "reinit_wandb_primary_with_open_metrics" in body_src,
            }))
    """)
    assert r.returncode == 0, f"Script failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert "error" not in data, data.get("error")
    assert "args" in data["params"], "must accept args"
    assert "router_addr" in data["params"], "must accept router_addr"
    assert data["delegates_to_reinit"], "must delegate to reinit_wandb_primary_with_open_metrics"


# [pr_diff] fail_to_pass
def test_public_get_metrics_router_addr():
    """Rollout manager exposes public get_metrics_router_addr method."""
    r = _run_py("""
        import ast, json
        from pathlib import Path

        src = Path("/workspace/slime/slime/ray/rollout.py").read_text()
        tree = ast.parse(src)

        func = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "get_metrics_router_addr":
                func = node
                break

        if func is None:
            print(json.dumps({"error": "get_metrics_router_addr not found"}))
        else:
            body = [s for s in func.body
                    if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))]
            body_src = ast.unparse(func)
            print(json.dumps({
                "body_stmts": len(body),
                "references_router": "_get_metrics_router_addr" in body_src or "router" in body_src.lower(),
            }))
    """)
    assert r.returncode == 0, f"Script failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert "error" not in data, data["error"]
    assert data["body_stmts"] >= 1, "get_metrics_router_addr must have a real body"
    assert data["references_router"], "get_metrics_router_addr must return router address info"


# [pr_diff] fail_to_pass
def test_train_calls_update_tracking():
    """train.py imports and calls update_tracking_open_metrics after rollout manager."""
    r = _run_py("""
        import ast, json
        from pathlib import Path

        src = Path("/workspace/slime/train.py").read_text()
        tree = ast.parse(src)

        has_ref = "update_tracking_open_metrics" in src

        calls = [
            node for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and (
                (isinstance(node.func, ast.Name) and node.func.id == "update_tracking_open_metrics")
                or (isinstance(node.func, ast.Attribute) and node.func.attr == "update_tracking_open_metrics")
            )
        ]

        print(json.dumps({"has_ref": has_ref, "call_count": len(calls)}))
    """)
    assert r.returncode == 0, f"Script failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data["has_ref"], "train.py must reference update_tracking_open_metrics"
    assert data["call_count"] >= 1, "train.py must call update_tracking_open_metrics"


# [pr_diff] fail_to_pass
def test_train_async_calls_update_tracking():
    """train_async.py imports and calls update_tracking_open_metrics after rollout manager."""
    r = _run_py("""
        import ast, json
        from pathlib import Path

        src = Path("/workspace/slime/train_async.py").read_text()
        tree = ast.parse(src)

        has_ref = "update_tracking_open_metrics" in src

        calls = [
            node for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and (
                (isinstance(node.func, ast.Name) and node.func.id == "update_tracking_open_metrics")
                or (isinstance(node.func, ast.Attribute) and node.func.attr == "update_tracking_open_metrics")
            )
        ]

        print(json.dumps({"has_ref": has_ref, "call_count": len(calls)}))
    """)
    assert r.returncode == 0, f"Script failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data["has_ref"], "train_async.py must reference update_tracking_open_metrics"
    assert data["call_count"] >= 1, "train_async.py must call update_tracking_open_metrics"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_reinit_not_stub():
    """reinit_wandb_primary_with_open_metrics has substantial implementation."""
    tree = _parse(WANDB_UTILS)
    func = _find_func(tree, "reinit_wandb_primary_with_open_metrics")
    assert func is not None, "reinit function not found"
    body = _non_docstring_stmts(func)
    assert len(body) >= 5, (
        f"reinit body too small ({len(body)} stmts) — likely a stub"
    )


# [static] pass_to_pass
def test_secondary_still_functional():
    """init_wandb_secondary must still exist and have non-trivial body."""
    tree = _parse(WANDB_UTILS)
    func = _find_func(tree, "init_wandb_secondary")
    assert func is not None, "init_wandb_secondary must still exist"
    body = _non_docstring_stmts(func)
    assert len(body) >= 3, (
        f"init_wandb_secondary body too small ({len(body)} stmts)"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI commands that run on the repo
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_ruff():
    """Ruff linting passes on modified files (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed to install ruff: {r.stderr}"

    r = subprocess.run(
        ["ruff", "check", "slime/utils/wandb_utils.py", "slime/utils/logging_utils.py",
         "slime/ray/rollout.py", "train.py", "train_async.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_black():
    """Black formatting check passes on modified files (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "black", "-q"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed to install black: {r.stderr}"

    r = subprocess.run(
        ["black", "--check", "slime/utils/wandb_utils.py", "slime/utils/logging_utils.py",
         "slime/ray/rollout.py", "train.py", "train_async.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Black failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_isort():
    """isort formatting check passes on modified files (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "isort", "-q"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed to install isort: {r.stderr}"

    r = subprocess.run(
        ["isort", "--check", "slime/utils/wandb_utils.py", "slime/utils/logging_utils.py",
         "slime/ray/rollout.py", "train.py", "train_async.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"isort failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_precommit_yaml():
    """YAML syntax check passes via pre-commit (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "pre-commit", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed to install pre-commit: {r.stderr}"

    r = subprocess.run(
        ["pre-commit", "run", "check-yaml", "--all-files"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Pre-commit check-yaml failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_precommit_private_key():
    """Private key detection check passes via pre-commit (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "pre-commit", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed to install pre-commit: {r.stderr}"

    r = subprocess.run(
        ["pre-commit", "run", "detect-private-key", "--all-files"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Pre-commit detect-private-key failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_precommit_large_files():
    """Large files check passes via pre-commit (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "pre-commit", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed to install pre-commit: {r.stderr}"

    r = subprocess.run(
        ["pre-commit", "run", "check-added-large-files", "--all-files"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Pre-commit check-added-large-files failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_precommit_case_conflict():
    """Case conflict check passes via pre-commit (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "pre-commit", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed to install pre-commit: {r.stderr}"

    r = subprocess.run(
        ["pre-commit", "run", "check-case-conflict", "--all-files"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Pre-commit check-case-conflict failed:\n{r.stderr[-500:]}"
