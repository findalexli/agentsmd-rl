"""
Task: areal-rpc-error-response-key
Repo: inclusionAI/AReaL @ a3e36d4af66ac6fa88e723675060cde591ca133e
PR:   1019

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import re
import subprocess
from pathlib import Path

REPO = "/workspace/AReaL"

SERVER = f"{REPO}/areal/infra/rpc/rpc_server.py"
LOCAL = f"{REPO}/areal/infra/scheduler/local.py"
SLURM = f"{REPO}/areal/infra/scheduler/slurm.py"
MODIFIED_FILES = [SERVER, LOCAL, SLURM]


def _run_python(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code in the repo directory."""
    return subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without errors."""
    for path in MODIFIED_FILES:
        source = Path(path).read_text()
        ast.parse(source)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests via subprocess
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_server_configure_uses_error_key():
    """rpc_server /configure error responses use 'error' key, not 'detail'."""
    r = _run_python(r"""
import ast
from pathlib import Path

source = Path("areal/infra/rpc/rpc_server.py").read_text()
tree = ast.parse(source)

func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "configure":
        func_node = node
        break
assert func_node is not None, "configure() not found"

# Extract the function source
lines = source.splitlines()
func_code = "\n".join(lines[func_node.lineno - 1 : func_node.end_lineno])

# Execute configure() with mocked Flask for each error path
test_cases = [
    (None, "Invalid JSON in request body"),
    ({}, "Missing 'config' field in request"),
    ({"config": "x"}, "Missing 'rank' field in request"),
]

for json_input, expected_msg in test_cases:
    captured = {}

    class MockRequest:
        def get_json(self):
            return json_input

    def mock_jsonify(d, **kw):
        captured["resp"] = d
        return (d, 400)

    ns = {
        "request": MockRequest(),
        "jsonify": mock_jsonify,
        "deserialize_value": lambda x: x,
    }
    exec(func_code, ns)
    ns["configure"]()

    resp = captured["resp"]
    assert "error" in resp, f"Response missing 'error' key: {resp}"
    assert resp["error"] == expected_msg, f"Expected '{expected_msg}', got '{resp['error']}'"
    assert "detail" not in resp, f"Found 'detail' key (should be 'error'): {resp}"

print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_local_scheduler_reads_error_key():
    """local.py scheduler reads 'error' key from RPC JSON responses."""
    r = _run_python(r"""
import ast
from pathlib import Path

source = Path("areal/infra/scheduler/local.py").read_text()
tree = ast.parse(source)

# Find all .get(key, "Unknown error") patterns via AST
get_keys = []
for node in ast.walk(tree):
    if (isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "get"
        and len(node.args) >= 2):
        key_arg, default_arg = node.args[0], node.args[1]
        if (isinstance(key_arg, ast.Constant) and isinstance(key_arg.value, str)
            and isinstance(default_arg, ast.Constant)
            and default_arg.value == "Unknown error"):
            get_keys.append(key_arg.value)

detail_keys = [k for k in get_keys if k == "detail"]
assert len(detail_keys) == 0, f"local.py still reads 'detail' key in {len(detail_keys)} places"
error_keys = [k for k in get_keys if k == "error"]
assert len(error_keys) >= 2, f"Expected >= 2 .get('error', ...) calls, found {len(error_keys)}"

# Behavioral: simulate actual data flow — server sends {"error": msg}, client reads it
server_response = {"error": "Configuration failed: missing parameter"}
for key in get_keys:
    msg = server_response.get(key, "Unknown error")
    assert msg != "Unknown error", f"Error message lost with key '{key}'"

print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_slurm_scheduler_reads_error_key():
    """slurm.py scheduler reads 'error' key from RPC JSON responses."""
    r = _run_python(r"""
import ast
from pathlib import Path

source = Path("areal/infra/scheduler/slurm.py").read_text()
tree = ast.parse(source)

get_keys = []
for node in ast.walk(tree):
    if (isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "get"
        and len(node.args) >= 2):
        key_arg, default_arg = node.args[0], node.args[1]
        if (isinstance(key_arg, ast.Constant) and isinstance(key_arg.value, str)
            and isinstance(default_arg, ast.Constant)
            and default_arg.value == "Unknown error"):
            get_keys.append(key_arg.value)

detail_keys = [k for k in get_keys if k == "detail"]
assert len(detail_keys) == 0, f"slurm.py still reads 'detail' key in {len(detail_keys)} places"
error_keys = [k for k in get_keys if k == "error"]
assert len(error_keys) >= 2, f"Expected >= 2 .get('error', ...) calls, found {len(error_keys)}"

server_response = {"error": "Configuration failed: missing parameter"}
for key in get_keys:
    msg = server_response.get(key, "Unknown error")
    assert msg != "Unknown error", f"Error message lost with key '{key}'"

print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_server_client_key_consistency():
    """Server and schedulers use the same JSON key for error responses."""
    r = _run_python(r"""
import ast
from pathlib import Path

# Find server's error key in configure()
server_src = Path("areal/infra/rpc/rpc_server.py").read_text()
tree = ast.parse(server_src)
func_node = next(
    n for n in ast.walk(tree)
    if isinstance(n, ast.FunctionDef) and n.name == "configure"
)
func_src = "\n".join(server_src.splitlines()[func_node.lineno-1:func_node.end_lineno])
func_tree = ast.parse(func_src)

server_keys = set()
for n in ast.walk(func_tree):
    if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "jsonify":
        for arg in n.args:
            if isinstance(arg, ast.Dict):
                for key in arg.keys:
                    if isinstance(key, ast.Constant) and key.value in ("error", "detail"):
                        server_keys.add(key.value)

# configure() must use "error" exclusively (matching the other 42 endpoints)
assert server_keys == {"error"}, f"configure() error keys must be {{'error'}}, got {server_keys}"

# Verify each client reads "error" for "Unknown error" fallbacks
for path in ["areal/infra/scheduler/local.py", "areal/infra/scheduler/slurm.py"]:
    src = Path(path).read_text()
    tree = ast.parse(src)
    client_keys = set()
    for n in ast.walk(tree):
        if (isinstance(n, ast.Call)
            and isinstance(n.func, ast.Attribute)
            and n.func.attr == "get"
            and len(n.args) >= 2):
            k, d = n.args[0], n.args[1]
            if (isinstance(k, ast.Constant) and isinstance(d, ast.Constant)
                and d.value == "Unknown error"
                and k.value in ("error", "detail")):
                client_keys.add(k.value)

    assert client_keys == {"error"}, f"{path} error keys must be {{'error'}}, got {client_keys}"

    # Behavioral round-trip: server sends {"error": msg}, client reads it
    server_response = {"error": "Test error message"}
    for ck in client_keys:
        actual = server_response.get(ck, "Unknown error")
        assert actual == "Test error message", f"Round-trip failed for '{ck}': got '{actual}'"

print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """Modified files retain substantial logic (not stubbed out)."""
    min_statements = {
        SERVER: 250,
        LOCAL: 200,
        SLURM: 200,
    }
    for path, threshold in min_statements.items():
        source = Path(path).read_text()
        tree = ast.parse(source)
        count = sum(
            1
            for node in ast.walk(tree)
            if isinstance(
                node,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                    ast.ClassDef,
                    ast.If,
                    ast.For,
                    ast.While,
                    ast.With,
                    ast.Try,
                    ast.Assign,
                    ast.Return,
                    ast.Raise,
                ),
            )
        )
        assert count >= threshold, (
            f"{path} has only {count} statements (expected >= {threshold})"
        )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:30 @ a3e36d4
def test_no_wildcard_imports():
    """No wildcard imports in modified files (AGENTS.md hard rule)."""
    for path in MODIFIED_FILES:
        source = Path(path).read_text()
        wildcards = re.findall(r"^from\s+\S+\s+import\s+\*", source, re.MULTILINE)
        assert len(wildcards) == 0, f"Wildcard import in {path}: {wildcards}"


# [agent_config] pass_to_pass — AGENTS.md:31 @ a3e36d4
def test_no_hardcoded_secrets():
    """No hardcoded secrets (passwords, tokens, API keys) in modified files (AGENTS.md rule)."""
    secret_pattern = re.compile(
        r'(?:password|passwd|secret|api_key|apikey|token|bearer|auth_token)\s*=\s*["\'][^"\']{4,}["\']',
        re.IGNORECASE,
    )
    for path in MODIFIED_FILES:
        source = Path(path).read_text()
        matches = secret_pattern.findall(source)
        assert len(matches) == 0, (
            f"Hardcoded secret-like literal in {path}: {matches}"
        )


# [agent_config] pass_to_pass — AGENTS.md:89-91 @ a3e36d4
def test_no_print_statements():
    """No bare print() calls in modified files — must use areal logger (AGENTS.md rule)."""
    for path in MODIFIED_FILES:
        source = Path(path).read_text()
        tree = ast.parse(source)
        prints = []
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Expr)
                and isinstance(node.value, ast.Call)
                and isinstance(node.value.func, ast.Name)
                and node.value.func.id == "print"
            ):
                prints.append(node.lineno)
        assert len(prints) == 0, (
            f"print() calls found in {path} at lines {prints} — use logger instead"
        )
