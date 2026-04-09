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
