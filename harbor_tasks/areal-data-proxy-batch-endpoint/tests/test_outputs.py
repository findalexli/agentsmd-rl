"""
Task: areal-data-proxy-batch-endpoint
Repo: inclusionAI/AReaL @ 0405b5c30c815044d858f15d04d2033c9a3d7760
PR:   1105

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

NOTE: app.py transitively imports torch/transformers/peft which are unavailable
in the CPU-only test container. We AST-extract the POST /data/batch handler,
exec it inside a minimal FastAPI app with mocked deps, and test real HTTP
behavior via subprocess + httpx AsyncClient.
"""

import ast
import re
import subprocess
import textwrap
from pathlib import Path

import pytest

APP_FILE = Path(
    "/workspace/AReaL/areal/experimental/inference_service/data_proxy/app.py"
)
REPO = "/workspace/AReaL"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Preamble for subprocess scripts: AST-extracts the POST /data/batch handler
# from app.py and mounts it on a minimal FastAPI app with mocked storage.
# Cannot import app.py directly because it transitively requires torch/GPU deps.
_PREAMBLE = textwrap.dedent("""\
    import ast, json, logging, textwrap, asyncio
    import fastapi, httpx, orjson
    from fastapi import HTTPException, Request
    from fastapi.responses import JSONResponse, StreamingResponse
    from fastapi.responses import Response as RawResponse
    from httpx import ASGITransport
    from pathlib import Path

    APP_FILE = Path("/workspace/AReaL/areal/experimental/inference_service/data_proxy/app.py")
    source = APP_FILE.read_text()
    tree = ast.parse(source)

    handler_node = None
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for dec in node.decorator_list:
                if (isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute)
                    and dec.func.attr == "post" and dec.args
                    and isinstance(dec.args[0], ast.Constant)
                    and dec.args[0].value == "/data/batch"):
                    handler_node = node
                    break
            if handler_node:
                break

    assert handler_node is not None, "POST /data/batch handler not found in app.py"
    lines = source.splitlines(keepends=True)
    func_source = textwrap.dedent("".join(lines[handler_node.lineno - 1 : handler_node.end_lineno]))

    app = fastapi.FastAPI()

    class MockStorage:
        def __init__(self):
            self.data = {
                "shard_a": [1, 2, 3],
                "shard_b": [4, 5, 6],
                "shard_c": {"key": "value"},
                "shard_d": [10, 20],
                "shard_e": "scalar_string",
            }
        def fetch(self, sid):
            if sid in self.data:
                return self.data[sid]
            raise KeyError(sid)

    ns = {
        "Request": Request, "HTTPException": HTTPException,
        "JSONResponse": JSONResponse, "StreamingResponse": StreamingResponse,
        "RawResponse": RawResponse, "Response": fastapi.Response,
        "rtensor_storage": MockStorage(), "serialize_value": lambda v: v,
        "orjson": orjson, "json": json,
        "logger": logging.getLogger("test_batch"), "app": app,
        "__builtins__": __builtins__,
    }
    exec('@app.post("/data/batch")\\n' + func_source, ns)

    @app.put("/data/{shard_id}")
    async def _store(shard_id: str):
        return {"status": "ok"}

    @app.get("/data/{shard_id}")
    async def _get(shard_id: str):
        return {"status": "ok"}
""")


def _run_batch_test(test_code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Write a self-contained test script and execute it via subprocess.

    The script AST-extracts the POST /data/batch handler from app.py,
    mounts it on a minimal FastAPI app with mocked storage, then runs
    the given async test assertions via httpx AsyncClient.
    """
    script = Path(REPO) / "_eval_batch_test.py"
    script.write_text(_PREAMBLE + "\n" + textwrap.dedent(test_code))
    try:
        return subprocess.run(
            ["python3", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

def test_syntax_check():
    """app.py must be valid Python."""
    import py_compile

    py_compile.compile(str(APP_FILE), doraise=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests via subprocess
# ---------------------------------------------------------------------------

def test_batch_valid_request():
    """POST /data/batch with valid shard_ids returns 200 and correct payload."""
    r = _run_batch_test("""\
        async def _test():
            transport = ASGITransport(app=app)
            async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.post("/data/batch", json={"shard_ids": ["shard_a", "shard_b"]})
                assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
                body = orjson.loads(resp.content)
                assert isinstance(body, list), f"Expected list, got {type(body)}"
                assert len(body) == 2, f"Expected 2 items, got {len(body)}"
                assert body[0] == [1, 2, 3], f"First shard mismatch: {body[0]}"
                assert body[1] == [4, 5, 6], f"Second shard mismatch: {body[1]}"

                resp2 = await client.post("/data/batch", json={"shard_ids": ["shard_c", "shard_a", "shard_d"]})
                assert resp2.status_code == 200
                body2 = orjson.loads(resp2.content)
                assert len(body2) == 3
                assert body2[0] == {"key": "value"}
                assert body2[1] == [1, 2, 3]
                assert body2[2] == [10, 20]
                print("PASS")

        asyncio.run(_test())
    """)
    assert r.returncode == 0, f"Script failed:\nstdout: {r.stdout}\nstderr: {r.stderr}"
    assert "PASS" in r.stdout


def test_batch_single_shard():
    """POST /data/batch with a single shard_id returns a list of one item."""
    r = _run_batch_test("""\
        async def _test():
            transport = ASGITransport(app=app)
            async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.post("/data/batch", json={"shard_ids": ["shard_c"]})
                assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
                body = orjson.loads(resp.content)
                assert isinstance(body, list) and len(body) == 1
                assert body[0] == {"key": "value"}, f"Unexpected payload: {body[0]}"

                resp2 = await client.post("/data/batch", json={"shard_ids": ["shard_e"]})
                assert resp2.status_code == 200
                body2 = orjson.loads(resp2.content)
                assert len(body2) == 1
                assert body2[0] == "scalar_string"
                print("PASS")

        asyncio.run(_test())
    """)
    assert r.returncode == 0, f"Script failed:\nstdout: {r.stdout}\nstderr: {r.stderr}"
    assert "PASS" in r.stdout


def test_batch_missing_shard_error():
    """POST /data/batch with a nonexistent shard returns an error status."""
    r = _run_batch_test("""\
        async def _test():
            transport = ASGITransport(app=app)
            async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.post("/data/batch", json={"shard_ids": ["nonexistent_xyz_123"]})
                assert resp.status_code != 200, f"Missing shard should not return 200, got {resp.status_code}"
                assert resp.status_code in (400, 404, 422, 500), f"Expected error status, got {resp.status_code}"

                resp2 = await client.post("/data/batch", json={"shard_ids": ["shard_a", "does_not_exist"]})
                assert resp2.status_code != 200, "Mix with missing shard should not return 200"
                print("PASS")

        asyncio.run(_test())
    """)
    assert r.returncode == 0, f"Script failed:\nstdout: {r.stdout}\nstderr: {r.stderr}"
    assert "PASS" in r.stdout


def test_batch_invalid_input_rejected():
    """POST /data/batch with non-list shard_ids is rejected with 400 or 422."""
    r = _run_batch_test("""\
        async def _test():
            transport = ASGITransport(app=app)
            async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.post("/data/batch", json={"shard_ids": "not_a_list"})
                assert resp.status_code in (400, 422), f"Expected 400/422 for string, got {resp.status_code}"

                resp2 = await client.post("/data/batch", json={"shard_ids": 42})
                assert resp2.status_code in (400, 422), f"Expected 400/422 for int, got {resp2.status_code}"

                resp3 = await client.post("/data/batch", json={"shard_ids": [1, 2, 3]})
                assert resp3.status_code in (400, 422), f"Expected 400/422 for non-string list, got {resp3.status_code}"
                print("PASS")

        asyncio.run(_test())
    """)
    assert r.returncode == 0, f"Script failed:\nstdout: {r.stdout}\nstderr: {r.stderr}"
    assert "PASS" in r.stdout


def test_batch_empty_shard_ids():
    """POST /data/batch with empty shard_ids list returns 200 with empty result."""
    r = _run_batch_test("""\
        async def _test():
            transport = ASGITransport(app=app)
            async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.post("/data/batch", json={"shard_ids": []})
                assert resp.status_code == 200, f"Empty list should return 200, got {resp.status_code}"
                body = orjson.loads(resp.content)
                assert isinstance(body, list), f"Expected list, got {type(body)}"
                assert len(body) == 0, f"Expected empty list, got {len(body)} items"
                print("PASS")

        asyncio.run(_test())
    """)
    assert r.returncode == 0, f"Script failed:\nstdout: {r.stdout}\nstderr: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — route ordering
# ---------------------------------------------------------------------------

def test_batch_route_before_param_route():
    """/data/batch must be declared before /data/{shard_id} in app.py.

    FastAPI matches routes in declaration order; if the parametric route comes
    first, POST /data/batch will be swallowed by /data/{shard_id}.
    """
    source = APP_FILE.read_text()
    tree = ast.parse(source)

    batch_line = None
    param_line = None

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for dec in node.decorator_list:
                if (
                    isinstance(dec, ast.Call)
                    and isinstance(dec.func, ast.Attribute)
                    and dec.args
                    and isinstance(dec.args[0], ast.Constant)
                ):
                    path = dec.args[0].value
                    method = dec.func.attr
                    if path == "/data/batch" and method == "post":
                        batch_line = node.lineno
                    elif "{shard_id}" in str(path) and param_line is None:
                        param_line = node.lineno

    assert batch_line is not None, "POST /data/batch route not found"
    if param_line is not None:
        assert batch_line < param_line, (
            f"/data/batch (L{batch_line}) must come before "
            f"/data/{{shard_id}} (L{param_line})"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression
# ---------------------------------------------------------------------------

def test_existing_routes_preserved():
    """Existing PUT/GET/DELETE data routes must still be registered."""
    source = APP_FILE.read_text()
    tree = ast.parse(source)

    routes = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for dec in node.decorator_list:
                if (
                    isinstance(dec, ast.Call)
                    and isinstance(dec.func, ast.Attribute)
                    and dec.args
                    and isinstance(dec.args[0], ast.Constant)
                ):
                    routes.add((dec.func.attr, dec.args[0].value))

    required = [
        ("put", "/data/{shard_id}"),
        ("get", "/data/{shard_id}"),
        ("delete", "/data/clear"),
    ]
    for method, path in required:
        assert (method, path) in routes, f"Missing route: {method.upper()} {path}"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

def test_not_stub():
    """POST /data/batch handler must have meaningful logic, not just pass/return."""
    source = APP_FILE.read_text()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for dec in node.decorator_list:
                if (
                    isinstance(dec, ast.Call)
                    and isinstance(dec.func, ast.Attribute)
                    and dec.func.attr == "post"
                    and dec.args
                    and isinstance(dec.args[0], ast.Constant)
                    and dec.args[0].value == "/data/batch"
                ):
                    body_stmts = [
                        s
                        for s in ast.walk(node)
                        if isinstance(s, ast.stmt)
                        and not isinstance(s, (ast.Pass, ast.Expr))
                    ]
                    assert len(body_stmts) >= 5, (
                        f"Handler body too small ({len(body_stmts)} stmts) — likely a stub"
                    )
                    return
    assert False, "POST /data/batch handler not found"


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

def test_no_wildcard_imports():
    """No wildcard imports in app.py (AGENTS.md hard rule)."""
    source = APP_FILE.read_text()
    wildcard = re.findall(r"^\s*from\s+\S+\s+import\s+\*", source, re.MULTILINE)
    assert not wildcard, f"Wildcard imports found: {wildcard}"


def test_no_hardcoded_endpoints():
    """No hardcoded host:port endpoints in app.py (AGENTS.md hard rule)."""
    source = APP_FILE.read_text()
    lines = [l for l in source.splitlines() if not l.strip().startswith("#")]
    code = "\n".join(lines)
    matches = re.findall(r"(?:localhost|127\.0\.0\.1|0\.0\.0\.0):\d+", code)
    assert not matches, f"Hardcoded endpoints found: {matches}"


def test_no_print_statements():
    """No print() calls in app.py — must use areal.utils.logging (AGENTS.md rule)."""
    source = APP_FILE.read_text()
    tree = ast.parse(source)

    prints_found = []
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "print"
        ):
            prints_found.append(f"line {node.lineno}")

    assert not prints_found, (
        f"print() calls found at {', '.join(prints_found)}. "
        "Use areal.utils.logging.getLogger() instead."
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks from repo
# ---------------------------------------------------------------------------

def test_repo_ruff_lint():
    """Ruff linter passes on data_proxy module (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed to install ruff: {r.stderr}"

    r = subprocess.run(
        ["ruff", "check", "areal/experimental/inference_service/data_proxy/app.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff lint failed:\n{r.stdout}\n{r.stderr}"


def test_repo_ruff_format():
    """Ruff format check passes on data_proxy module (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed to install ruff: {r.stderr}"

    r = subprocess.run(
        ["ruff", "format", "--check", "areal/experimental/inference_service/data_proxy/app.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_precommit_trailing_whitespace():
    """No trailing whitespace in app.py (pass_to_pass)."""
    source = APP_FILE.read_text()
    lines_with_ws = []
    for i, line in enumerate(source.splitlines(), 1):
        if line != line.rstrip():
            lines_with_ws.append(i)
    assert not lines_with_ws, (
        f"Trailing whitespace found on lines: {lines_with_ws}"
    )


def test_repo_precommit_end_of_file():
    """app.py ends with exactly one newline (pass_to_pass)."""
    source = APP_FILE.read_text()
    # File should not be empty and should end with exactly one newline
    if not source:
        assert False, "app.py is empty"
    # Remove trailing newlines and check original ended with exactly one
    stripped = source.rstrip('\n')
    if source != stripped + '\n':
        # Check if missing newline or has multiple
        if not source.endswith('\n'):
            assert False, "app.py does not end with a newline"
        elif source.endswith('\n\n'):
            assert False, "app.py ends with multiple newlines"


def test_repo_check_json_valid():
    """JSON files in data_proxy are valid (pass_to_pass)."""
    import json

    data_proxy_dir = Path(REPO) / "areal" / "experimental" / "inference_service" / "data_proxy"
    for json_file in data_proxy_dir.rglob("*.json"):
        content = json_file.read_text()
        if content.strip():  # Only parse non-empty files
            try:
                json.loads(content)
            except json.JSONDecodeError as e:
                assert False, f"Invalid JSON in {json_file}: {e}"


def test_repo_no_private_keys():
    """No private keys detected in repo Python files (pass_to_pass)."""
    data_proxy_dir = Path(REPO) / "areal" / "experimental" / "inference_service" / "data_proxy"
    private_key_patterns = [
        r"BEGIN RSA PRIVATE KEY",
        r"BEGIN DSA PRIVATE KEY",
        r"BEGIN EC PRIVATE KEY",
        r"BEGIN OPENSSH PRIVATE KEY",
        r"BEGIN PRIVATE KEY",
        r"PuTTY-User-Key-File",
    ]
    for py_file in data_proxy_dir.rglob("*.py"):
        source = py_file.read_text()
        for pattern in private_key_patterns:
            matches = re.findall(pattern, source)
            assert not matches, f"Potential private key in {py_file}: {pattern}"


def test_repo_python_syntax_valid():
    """All Python files in data_proxy have valid syntax (pass_to_pass)."""
    data_proxy_dir = Path(REPO) / "areal" / "experimental" / "inference_service" / "data_proxy"
    for py_file in data_proxy_dir.glob("*.py"):
        source = py_file.read_text()
        try:
            ast.parse(source)
        except SyntaxError as e:
            assert False, f"Syntax error in {py_file}: {e}"


def test_repo_py_compile():
    """All Python files in data_proxy compile successfully (pass_to_pass)."""
    r = subprocess.run(
        [
            "python3", "-m", "py_compile",
            "areal/experimental/inference_service/data_proxy/app.py",
            "areal/experimental/inference_service/data_proxy/__init__.py",
            "areal/experimental/inference_service/data_proxy/__main__.py",
            "areal/experimental/inference_service/data_proxy/backend.py",
            "areal/experimental/inference_service/data_proxy/config.py",
            "areal/experimental/inference_service/data_proxy/inf_bridge.py",
            "areal/experimental/inference_service/data_proxy/pause.py",
            "areal/experimental/inference_service/data_proxy/session.py",
            "areal/experimental/inference_service/data_proxy/tokenizer_proxy.py",
        ],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"py_compile failed:\n{r.stderr}"


def test_repo_check_yaml_valid():
    """YAML workflow files are valid (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c",
         """import yaml
import sys
from pathlib import Path
repo = '/workspace/AReaL'
errors = []
for yaml_file in Path(repo).glob('.github/workflows/*.yml'):
    try:
        yaml.safe_load(yaml_file.read_text())
    except yaml.YAMLError as e:
        errors.append(f'{yaml_file}: {e}')
if errors:
    print('YAML errors:')
    for e in errors:
        print(e)
    sys.exit(1)
print('All YAML files valid')"""],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"YAML validation failed:\n{r.stdout}\n{r.stderr}"
