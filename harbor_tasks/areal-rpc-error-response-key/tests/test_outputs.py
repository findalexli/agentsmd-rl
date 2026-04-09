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
    assert resp["error"] == expected_msg, f"Expected '{expected_msg}', got '{resp['error']}"
    assert "detail" not in resp, f"Found 'detail' key (should be 'error'): {resp}"

print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_local_scheduler_reads_error_key():
    """local.py extracts actual error messages from server's {"error": "..."} responses."""
    r = _run_python(r"""
import re
from pathlib import Path

source = Path("areal/infra/scheduler/local.py").read_text()

# Mock response matching what the majority of RPC server endpoints return
class MockResponse:
    def json(self):
        return {"error": "Engine onload failed: CUDA OOM on device 0"}

response = MockResponse()

# Find every error-extraction expression in the actual source and eval() it.
# Sync pattern: response.json().get("KEY", "Unknown error")
sync_exprs = re.findall(
    r'response\.json\(\)\.get\(\s*"[^"]+"\s*,\s*"Unknown error"\s*\)',
    source
)

# Async pattern: (await response.json()).get("KEY", "Unknown error")
# May span multiple lines; strip 'await' so eval works with our sync mock.
async_exprs_raw = re.findall(
    r'\(await response\.json\(\)\)\.get\(\s*"[^"]+"\s*,\s*"Unknown error"\s*\)',
    source
)
async_exprs = [e.replace("await ", "") for e in async_exprs_raw]

all_exprs = sync_exprs + async_exprs
assert len(all_exprs) >= 2, f"Expected >=2 error extraction calls, found {len(all_exprs)}"

expected = "Engine onload failed: CUDA OOM on device 0"
for expr in all_exprs:
    result = eval(expr)
    assert result == expected, (
        f"`{expr.strip()[:80]}` returned '{result}' — "
        f"the real error message was silently lost!"
    )

print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_slurm_scheduler_reads_error_key():
    """slurm.py extracts actual error messages from server's {"error": "..."} responses."""
    r = _run_python(r"""
import re
from pathlib import Path

source = Path("areal/infra/scheduler/slurm.py").read_text()

class MockResponse:
    def json(self):
        return {"error": "Worker config failed: invalid rank"}

response = MockResponse()

sync_exprs = re.findall(
    r'response\.json\(\)\.get\(\s*"[^"]+"\s*,\s*"Unknown error"\s*\)',
    source
)

async_exprs_raw = re.findall(
    r'\(await response\.json\(\)\)\.get\(\s*"[^"]+"\s*,\s*"Unknown error"\s*\)',
    source
)
async_exprs = [e.replace("await ", "") for e in async_exprs_raw]

all_exprs = sync_exprs + async_exprs
assert len(all_exprs) >= 2, f"Expected >=2 error extraction calls, found {len(all_exprs)}"

expected = "Worker config failed: invalid rank"
for expr in all_exprs:
    result = eval(expr)
    assert result == expected, (
        f"`{expr.strip()[:80]}` returned '{result}' — "
        f"the real error message was silently lost!"
    )

print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_server_client_key_consistency():
    """Server configure() and scheduler clients agree on JSON error key."""
    r = _run_python(r"""
import ast, re
from pathlib import Path

# 1) Execute configure() to discover which key it actually uses
server_src = Path("areal/infra/rpc/rpc_server.py").read_text()
tree = ast.parse(server_src)
func_node = next(
    n for n in ast.walk(tree)
    if isinstance(n, ast.FunctionDef) and n.name == "configure"
)
func_code = "\n".join(server_src.splitlines()[func_node.lineno - 1 : func_node.end_lineno])

captured = {}
class MockRequest:
    def get_json(self):
        return None  # triggers first error path

def mock_jsonify(d, **kw):
    captured["resp"] = d
    return (d, 400)

ns = {"request": MockRequest(), "jsonify": mock_jsonify, "deserialize_value": lambda x: x}
exec(func_code, ns)
ns["configure"]()

server_key = [k for k in captured["resp"] if k in ("error", "detail")][0]

# configure() must use "error" — matching the other 42 server endpoints
assert server_key == "error", (
    f"configure() uses '{server_key}' but the other 42 endpoints use 'error'"
)

# 2) Verify clients also use "error" — round-trip with mock response
class MockResponse:
    def json(self):
        return captured["resp"]

response = MockResponse()

for path in ["areal/infra/scheduler/local.py", "areal/infra/scheduler/slurm.py"]:
    src = Path(path).read_text()
    exprs = re.findall(
        r'(?:response\.json\(\)|(?:\(await response\.json\(\)\)))\.get\(\s*"[^"]+"\s*,\s*"Unknown error"\s*\)',
        src
    )
    assert len(exprs) >= 2, f"{path}: expected >=2 error extraction points"

    for expr in exprs:
        cleaned = expr.replace("await ", "")
        result = eval(cleaned)
        assert result != "Unknown error", (
            f"Round-trip broken in {path}: server sends {captured['resp']}, "
            f"client expr `{cleaned[:60]}...` returns 'Unknown error'"
        )

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


# ---------------------------------------------------------------------------
# Repo CI/CD pass_to_pass gates
# ---------------------------------------------------------------------------

# [repo_ci] pass_to_pass — from .github/workflows/pre-commit.yml
def test_repo_ruff_check():
    """Repo's ruff linter passes on modified files (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "-q", "ruff"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Failed to install ruff: {r.stderr}"

    r = subprocess.run(
        ["ruff", "check"] + MODIFIED_FILES,
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout}\n{r.stderr}"


# [repo_ci] pass_to_pass — from .github/workflows/pre-commit.yml
def test_repo_precommit_hooks():
    """Repo's pre-commit hooks pass on modified files (pass_to_pass).

    Skips network-dependent hooks (generate-cli-docs).
    """
    r = subprocess.run(
        ["pip", "install", "-q", "pre-commit"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Failed to install pre-commit: {r.stderr}"

    # Run pre-commit on just the modified files, skipping network-dependent hooks
    files_str = " ".join(MODIFIED_FILES)
    r = subprocess.run(
        ["bash", "-c", f"SKIP=generate-cli-docs pre-commit run --files {files_str}"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Pre-commit hooks failed:\n{r.stdout}\n{r.stderr}"
