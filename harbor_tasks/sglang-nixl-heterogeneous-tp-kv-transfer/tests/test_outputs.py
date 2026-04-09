"""
Task: sglang-nixl-heterogeneous-tp-kv-transfer
Repo: sgl-project/sglang @ ba78f6e0efb925fbb0f99e7f060eb2cb410331df
PR:   22145

Tests for NIXL disaggregation heterogeneous TP KV transfer fix.
Bugs fixed:
1. Notification key collision: pp_rank -> engine_rank in RDMA notifications
2. Wrong head distribution: Using per-rank kv_head_num instead of total_kv_head_num
"""

import ast
import subprocess
import sys
from pathlib import Path

REPO = "/workspace/sglang"
CONN_FILE = f"{REPO}/python/sglang/srt/disaggregation/nixl/conn.py"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

def test_syntax_check():
    """Modified conn.py must parse without errors."""
    src = Path(CONN_FILE).read_text()
    ast.parse(src)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

def test_notification_key_uses_engine_rank():
    """
    Notification key must use engine_rank, not pp_rank.

    Bug: With PP=1, all prefill ranks share pp_rank=0, causing notification key
    collisions. The fix uses engine_rank to make keys unique per prefill rank.
    """
    src = Path(CONN_FILE).read_text()

    # Check that the KV notification uses engine_rank
    assert 'f"{req.room}_kv_{chunk_id}_{int(is_last)}_{self.kv_args.engine_rank}"' in src, \
        "KV notification must use engine_rank, not pp_rank"

    # Check that the state notification uses engine_rank
    assert 'f"{req.room}_state_{self.kv_args.engine_rank}"' in src, \
        "State notification must use engine_rank, not pp_rank"

    # Make sure pp_rank is NOT used in notifications anymore
    lines = src.split('\n')
    for i, line in enumerate(lines):
        if 'notif' in line and 'pp_rank' in line:
            # These should not exist after the fix
            raise AssertionError(
                f"Line {i+1} still uses pp_rank in notification: {line.strip()}"
            )


def test_head_distribution_calculation():
    """
    Head distribution must use total_kv_head_num, not per-rank kv_head_num.

    Bug: Using kv_head_num loses precision when total_kv_heads < tp_size (GQA).
    The fix derives head counts from total_kv_head_num.
    """
    src = Path(CONN_FILE).read_text()
    tree = ast.parse(src)

    # Find the send_kvcache_slice function
    send_kvcache_slice = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "send_kvcache_slice":
            send_kvcache_slice = node
            break

    assert send_kvcache_slice is not None, "send_kvcache_slice function must exist"

    func_src = ast.unparse(send_kvcache_slice)

    # Check that total_kv_head_num is used
    assert "total_kv_head_num" in func_src, \
        "send_kvcache_slice must use total_kv_head_num for correct head distribution"

    # Check that total_kv_heads is computed properly
    assert "total_kv_heads" in func_src, \
        "Must compute total_kv_heads from kv_args.total_kv_head_num or fallback"

    # Check for max(1, ...) guards on head calculations
    assert "max(1, total_kv_heads // prefill_tp_size)" in func_src or \
           "src_heads_per_rank = max(1" in func_src, \
        "src_heads_per_rank calculation must use max(1, ...) guard"

    assert "max(1, total_kv_heads // decode_tp_size)" in func_src or \
           "dst_heads_per_rank = max(1" in func_src, \
        "dst_heads_per_rank calculation must use max(1, ...) guard"


def test_gqa_replication_handling():
    """
    GQA replication handling must be present for heterogeneous TP.

    Bug: When multiple prefill ranks share the same KV heads (GQA),
    the dst_head_start_offset was calculated incorrectly.
    The fix adds src_replication and unique_head_idx handling.
    """
    src = Path(CONN_FILE).read_text()

    # Check for GQA replication calculation
    assert "src_replication" in src, \
        "Must calculate src_replication for GQA handling"

    # Check for unique_head_idx calculation
    assert "unique_head_idx" in src, \
        "Must calculate unique_head_idx for correct dst_head_start_offset"

    # Verify the replication formula
    assert "max(1, prefill_tp_size // total_kv_heads)" in src, \
        "src_replication must be calculated as max(1, prefill_tp_size // total_kv_heads)"

    # Verify the offset calculation includes modulo
    assert "% dst_heads_per_rank" in src, \
        "dst_head_start_offset must include modulo dst_heads_per_rank"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

def test_module_imports():
    """The conn module should import without errors (given minimal deps)."""
    # We can't fully import without nixl, but we can at least check the syntax
    # and that the file structure is valid
    src = Path(CONN_FILE).read_text()
    tree = ast.parse(src)

    # Check that required classes exist
    classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
    assert "NixlKVManager" in classes, "NixlKVManager class must exist"
    assert "TransferStatus" in classes, "TransferStatus class must exist"


def test_send_kvcache_slice_not_stub():
    """send_kvcache_slice must have real implementation, not just pass/return."""
    src = Path(CONN_FILE).read_text()
    tree = ast.parse(src)

    # Find send_kvcache_slice function
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "send_kvcache_slice":
            # Count non-trivial statements (exclude pass, docstrings, simple returns)
            statements = []
            for stmt in node.body:
                if isinstance(stmt, ast.Pass):
                    continue
                if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
                    continue  # Docstring
                if isinstance(stmt, ast.Return) and stmt.value is None:
                    continue  # Bare return
                statements.append(stmt)

            # Should have substantial body (30+ lines indicates real logic)
            assert len(statements) >= 10, \
                f"send_kvcache_slice appears to be a stub (only {len(statements)} meaningful statements)"

            # Check for key operations
            func_src = ast.unparse(node)
            assert "get_mha_kv_ptrs_with_pp" in func_src, \
                "Must call get_mha_kv_ptrs_with_pp for KV pointer setup"

            return

    raise AssertionError("send_kvcache_slice function not found")


def test_add_transfer_request_not_stub():
    """add_transfer_request must have real implementation and use correct notification."""
    src = Path(CONN_FILE).read_text()
    tree = ast.parse(src)

    # Find add_transfer_request function
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "add_transfer_request":
            func_src = ast.unparse(node)

            # Should call send_kvcache or send_kvcache_slice
            assert "send_kvcache" in func_src, \
                "Must call send_kvcache or send_kvcache_slice"

            # Should call maybe_send_extra for state
            assert "maybe_send_extra" in func_src, \
                "Must call maybe_send_extra for state transfer"

            return

    raise AssertionError("add_transfer_request function not found")


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks from the repo
# ---------------------------------------------------------------------------

REPO_CONN_FILE = f"{REPO}/python/sglang/srt/disaggregation/nixl/conn.py"


def test_repo_conn_py_syntax():
    """Repo's conn.py must have valid Python syntax (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "py_compile", REPO_CONN_FILE],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Syntax check failed:\n{r.stderr}"


def test_repo_conn_py_ast_parse():
    """Repo's conn.py must parse into valid AST (pass_to_pass)."""
    src = Path(REPO_CONN_FILE).read_text()
    try:
        ast.parse(src)
    except SyntaxError as e:
        raise AssertionError(f"AST parse failed: {e}")


def test_repo_conn_py_no_undefined_names():
    """Repo's conn.py must not have undefined names (F821-like check) (pass_to_pass)."""
    # This is a simplified check - we verify the code compiles and key symbols are defined
    src = Path(REPO_CONN_FILE).read_text()
    tree = ast.parse(src)

    # Key symbols that should be defined in the conn.py file
    required_symbols = {
        "NixlKVManager": "class",
        "TransferStatus": "class",
        "TransferInfo": "class",
        "send_kvcache_slice": "function",
        "add_transfer_request": "function",
    }

    found = {"classes": set(), "functions": set()}

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            found["classes"].add(node.name)
        elif isinstance(node, ast.FunctionDef):
            found["functions"].add(node.name)

    for symbol, typ in required_symbols.items():
        if typ == "class":
            assert symbol in found["classes"], f"Required class {symbol} not found"
        elif typ == "function":
            assert symbol in found["functions"], f"Required function {symbol} not found"


def test_repo_conn_py_classes_exist():
    """Repo's conn.py must have required classes (pass_to_pass)."""
    src = Path(REPO_CONN_FILE).read_text()
    tree = ast.parse(src)

    classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
    assert "NixlKVManager" in classes, "NixlKVManager class must exist"
    assert "TransferStatus" in classes, "TransferStatus class must exist"
