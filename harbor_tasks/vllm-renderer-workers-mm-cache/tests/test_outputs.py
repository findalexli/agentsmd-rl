"""
Task: vllm-renderer-workers-mm-cache
Repo: vllm-project/vllm @ 2bf5b70ae86261431b4b92276828b40b9c0903b6
PR:   38418

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import textwrap
from pathlib import Path
from types import SimpleNamespace

REPO = "/workspace/vllm"
TARGET = Path(f"{REPO}/vllm/config/model.py")


def _find_validation_block():
    """Find the innermost if-block in ModelConfig.__post_init__ that validates
    renderer_num_workers with mm processor cache. Returns dedented source or None.
    # AST-only because: ModelConfig depends on torch, transformers, and dozens of vLLM internals
    """
    src = TARGET.read_text()
    tree = ast.parse(src)
    lines = src.splitlines()

    candidates = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "ModelConfig":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "__post_init__":
                    for stmt in ast.walk(item):
                        if isinstance(stmt, ast.If):
                            block = "\n".join(lines[stmt.lineno - 1 : stmt.end_lineno])
                            if "renderer_num_workers" in block:
                                size = stmt.end_lineno - stmt.lineno
                                candidates.append((size, block))
                    break
            break

    if not candidates:
        return None

    # Return the smallest (most specific) block
    candidates.sort(key=lambda x: x[0])
    return textwrap.dedent(candidates[0][1])


def _exec_validation(renderer_num_workers, mm_processor_cache_gb):
    """Execute the validation block with mock self.
    Returns (raised: bool, message: str|None).
    raised=True + message if ValueError raised.
    raised=False + None if no error.
    Returns (None, None) if validation block not found."""
    block = _find_validation_block()
    if block is None:
        return None, None

    mm_config = SimpleNamespace(mm_processor_cache_gb=mm_processor_cache_gb)
    mock_self = SimpleNamespace(
        renderer_num_workers=renderer_num_workers,
        multimodal_config=mm_config,
    )

    try:
        exec(compile(block, "<validation>", "exec"), {"self": mock_self})
        return False, None
    except ValueError as e:
        return True, str(e)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_model_config_syntax():
    """vllm/config/model.py must parse without syntax errors."""
    src = TARGET.read_text()
    ast.parse(src)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_raises_multi_worker_default_cache():
    """renderer_num_workers > 1 with default cache (4 GB) must raise ValueError."""
    for workers in (2, 4, 8):
        raised, _ = _exec_validation(renderer_num_workers=workers, mm_processor_cache_gb=4.0)
        assert raised is True, (
            f"Expected ValueError for renderer_num_workers={workers} with cache=4.0 GB"
        )


# [pr_diff] fail_to_pass
def test_raises_multi_worker_explicit_cache():
    """renderer_num_workers > 1 with various explicit cache sizes must raise ValueError."""
    cases = [
        (2, 1.0),
        (3, 0.5),
        (2, 0.001),
    ]
    for workers, cache_gb in cases:
        raised, _ = _exec_validation(renderer_num_workers=workers, mm_processor_cache_gb=cache_gb)
        assert raised is True, (
            f"Expected ValueError for renderer_num_workers={workers} with cache={cache_gb} GB"
        )


# [pr_diff] fail_to_pass
def test_error_message_content():
    """ValueError message must mention both relevant CLI flags for user guidance."""
    raised, msg = _exec_validation(renderer_num_workers=4, mm_processor_cache_gb=4.0)
    assert raised is True, "Expected ValueError to be raised"
    assert msg is not None
    msg_lower = msg.lower()
    assert "renderer" in msg_lower and "worker" in msg_lower, (
        f"Error message should mention renderer workers, got: {msg}"
    )
    assert "cache" in msg_lower, (
        f"Error message should mention the cache, got: {msg}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_allows_single_worker_with_cache():
    """renderer_num_workers=1 with various cache sizes must NOT raise."""
    for cache_gb in (0.5, 4.0, 10.0):
        raised, _ = _exec_validation(renderer_num_workers=1, mm_processor_cache_gb=cache_gb)
        assert raised is not True, (
            f"Single worker with cache={cache_gb} GB should be allowed"
        )


# [pr_diff] pass_to_pass
def test_allows_multi_worker_cache_disabled():
    """renderer_num_workers > 1 with cache disabled (0 GB) must NOT raise."""
    for workers in (2, 4, 8):
        raised, _ = _exec_validation(renderer_num_workers=workers, mm_processor_cache_gb=0)
        assert raised is not True, (
            f"renderer_num_workers={workers} with cache disabled should be allowed"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_post_init_not_stub():
    """ModelConfig.__post_init__ has substantial implementation, not a stub."""
    # AST-only because: ModelConfig depends on torch, transformers, and dozens of vLLM internals
    src = TARGET.read_text()
    tree = ast.parse(src)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "ModelConfig":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "__post_init__":
                    stmts = [
                        s
                        for s in item.body
                        if not isinstance(s, ast.Pass)
                        and not (
                            isinstance(s, ast.Expr)
                            and isinstance(getattr(s, "value", None), ast.Constant)
                        )
                    ]
                    assert len(stmts) >= 10, (
                        f"__post_init__ has only {len(stmts)} statements — likely a stub"
                    )
                    return

    assert False, "ModelConfig.__post_init__ not found"
