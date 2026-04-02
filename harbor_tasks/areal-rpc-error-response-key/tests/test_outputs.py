"""
Task: areal-rpc-error-response-key
Repo: inclusionAI/AReaL @ a3e36d4af66ac6fa88e723675060cde591ca133e
PR:   1019

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import re
from pathlib import Path

REPO = "/workspace/AReaL"

SERVER = f"{REPO}/areal/infra/rpc/rpc_server.py"
LOCAL = f"{REPO}/areal/infra/scheduler/local.py"
SLURM = f"{REPO}/areal/infra/scheduler/slurm.py"
MODIFIED_FILES = [SERVER, LOCAL, SLURM]


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without errors."""
    for path in MODIFIED_FILES:
        source = Path(path).read_text()
        ast.parse(source)  # raises SyntaxError on failure


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
# AST-only because: rpc_server.py requires Flask, areal.*, and full infra stack
def test_server_configure_uses_error_key():
    """rpc_server /configure error responses use 'error' key, not 'detail'."""
    source = Path(SERVER).read_text()
    tree = ast.parse(source)

    # Find the configure function
    configure_src = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "configure":
            lines = source.splitlines(keepends=True)
            configure_src = "".join(lines[node.lineno - 1 : node.end_lineno])
            break

    assert configure_src is not None, "configure() function not found in rpc_server.py"

    # Extract keys from jsonify calls in configure
    jsonify_keys = re.findall(r'jsonify\(\s*\{\s*["\'](\w+)["\']', configure_src)
    assert len(jsonify_keys) >= 3, (
        f"Expected at least 3 jsonify error responses, found {len(jsonify_keys)}"
    )

    for key in jsonify_keys:
        if key in ("error", "detail"):
            assert key == "error", (
                f"configure() uses '{key}' instead of 'error' in jsonify call"
            )


# [pr_diff] fail_to_pass
# AST-only because: local.py requires aiohttp, requests, areal.* distributed infra
def test_local_scheduler_reads_error_key():
    """local.py scheduler reads 'error' key from RPC JSON responses, not 'detail'."""
    source = Path(LOCAL).read_text()

    # Find all .get("detail"|"error", "Unknown error") patterns in error-handling code
    detail_gets = re.findall(
        r'\.get\(\s*["\']detail["\'].*?Unknown error', source
    )
    error_gets = re.findall(
        r'\.get\(\s*["\']error["\'].*?Unknown error', source
    )

    assert len(detail_gets) == 0, (
        f"local.py still has {len(detail_gets)} .get('detail', 'Unknown error') calls"
    )
    assert len(error_gets) >= 2, (
        f"local.py should have at least 2 .get('error', 'Unknown error') calls, found {len(error_gets)}"
    )


# [pr_diff] fail_to_pass
# AST-only because: slurm.py requires aiohttp, requests, areal.* distributed infra
def test_slurm_scheduler_reads_error_key():
    """slurm.py scheduler reads 'error' key from RPC JSON responses, not 'detail'."""
    source = Path(SLURM).read_text()

    detail_gets = re.findall(
        r'\.get\(\s*["\']detail["\'].*?Unknown error', source
    )
    error_gets = re.findall(
        r'\.get\(\s*["\']error["\'].*?Unknown error', source
    )

    assert len(detail_gets) == 0, (
        f"slurm.py still has {len(detail_gets)} .get('detail', 'Unknown error') calls"
    )
    assert len(error_gets) >= 2, (
        f"slurm.py should have at least 2 .get('error', 'Unknown error') calls, found {len(error_gets)}"
    )


# [pr_diff] fail_to_pass
# AST-only because: files require Flask, aiohttp, requests, areal.* infra
def test_server_client_key_consistency():
    """Server and schedulers use the same JSON key for error responses."""
    server_src = Path(SERVER).read_text()
    local_src = Path(LOCAL).read_text()
    slurm_src = Path(SLURM).read_text()

    # Server: extract the key used in jsonify error responses in configure()
    tree = ast.parse(server_src)
    configure_src = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "configure":
            lines = server_src.splitlines(keepends=True)
            configure_src = "".join(lines[node.lineno - 1 : node.end_lineno])
            break
    assert configure_src is not None

    server_keys = set(re.findall(r'jsonify\(\s*\{\s*["\'](\w+)["\']', configure_src))
    # Filter to error-related keys only
    error_keys = server_keys & {"error", "detail"}
    assert len(error_keys) == 1, f"Server uses multiple error keys: {error_keys}"
    server_key = error_keys.pop()

    # Clients: check they read the same key
    for name, src in [("local.py", local_src), ("slurm.py", slurm_src)]:
        client_reads_server_key = re.search(
            rf'\.get\(\s*["\'{server_key}["\']', src
        )
        assert client_reads_server_key, (
            f"{name} does not read '{server_key}' key that server uses"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
# AST-only because: counting statements requires AST traversal by definition
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
# AST-only because: checking import style requires source inspection
def test_no_wildcard_imports():
    """No wildcard imports in modified files (AGENTS.md hard rule)."""
    for path in MODIFIED_FILES:
        source = Path(path).read_text()
        wildcards = re.findall(r"^from\s+\S+\s+import\s+\*", source, re.MULTILINE)
        assert len(wildcards) == 0, f"Wildcard import in {path}: {wildcards}"


# [agent_config] pass_to_pass — AGENTS.md:89-91 @ a3e36d4
# AST-only because: checking for print() calls requires source inspection
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
