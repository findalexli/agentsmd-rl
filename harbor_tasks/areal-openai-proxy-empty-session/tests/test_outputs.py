"""
Task: areal-openai-proxy-empty-session
Repo: inclusionAI/AReaL @ 84eaef1292b2a3184d4a565d4abb0758408be018
PR:   #971

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import asyncio
import logging
import textwrap
from pathlib import Path
from unittest.mock import MagicMock

REPO = "/workspace/AReaL"
TARGET = f"{REPO}/areal/experimental/openai/proxy/workflow.py"


# ---------------------------------------------------------------------------
# Helper: extract the online-mode interactions-handling tail of arun_episode
# and run it with mocked dependencies.
# ---------------------------------------------------------------------------

def _find_arun_episode(source: str):
    """Return (AST node, source lines) for arun_episode, or (None, None)."""
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "arun_episode":
            return node, source.splitlines()
    return None, None


def _extract_tail(method_lines: list[str], func_node) -> str | None:
    """Extract the interactions-handling tail from the online-mode branch."""
    all_lines = method_lines[func_node.lineno - 1 : func_node.end_lineno]
    tail_start = None
    tail_end = None
    for i, line in enumerate(all_lines):
        s = line.strip().lower()
        if tail_start is None:
            if ("record stats" in s
                or ("interactions" in s and line.strip().startswith("if"))
                or "list(interactions" in s
                or ("empty" in s and "interact" in s)
                or ("no interactions" in s)):
                tail_start = i
        if tail_start is not None and line.strip().startswith("return interactions"):
            tail_end = i + 1
            # Look ahead for a 'return None' shortly after
            for j in range(i + 1, min(i + 5, len(all_lines))):
                sj = all_lines[j].strip()
                if sj.startswith("return None") or sj == "return None":
                    tail_end = j + 1
                    break
                if sj and not sj.startswith("#") and not sj.startswith("logger"):
                    break
            break
    if tail_start is None:
        return None
    end = tail_end if tail_end else len(all_lines)
    return textwrap.dedent("\n".join(all_lines[tail_start:end]))


def _run_tail(interactions_dict: str, func_name: str):
    """Execute the extracted tail with mocked dependencies.

    Returns (return_value, log_records) or raises on failure.
    """
    source = Path(TARGET).read_text()
    func_node, lines = _find_arun_episode(source)
    assert func_node is not None, "arun_episode not found"
    tail = _extract_tail(lines, func_node)
    assert tail is not None, "Could not extract interactions-handling tail"

    code_lines = [
        "_log = []",
        f"async def {func_name}():",
        "    import logging as _lg",
        "    from unittest.mock import MagicMock as _M",
        "    class _H(_lg.Handler):",
        "        def emit(s, r): _log.append(r)",
        f"    logger = _lg.getLogger('{func_name}')",
        "    logger.handlers.clear()",
        "    logger.addHandler(_H())",
        "    logger.setLevel(_lg.DEBUG)",
        "    session_info = _M()",
        "    session_info.session_id = 'test-session'",
        "    workflow_context = _M()",
        "    workflow_context.stat_scope.return_value = 'scope'",
        "    stats_tracker = _M()",
        "    self = _M()",
        f"    {interactions_dict}",
    ]
    for tl in tail.splitlines():
        code_lines.append("    " + tl)

    code = "\n".join(code_lines)
    ns = {}
    exec(compile(code, f"<{func_name}>", "exec"), ns)
    ret = asyncio.run(ns[func_name]())
    return ret, ns.get("_log", [])


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """workflow.py must parse without syntax errors."""
    import py_compile
    py_compile.compile(TARGET, doraise=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_empty_interactions_returns_none():
    """Empty interactions dict must return None (rejected trajectory)."""
    ret, _ = _run_tail("interactions = {}", "_t_empty_none")
    assert ret is None, f"Expected None for empty interactions, got {ret!r}"


# [pr_diff] fail_to_pass
def test_empty_interactions_logs_warning():
    """A warning must be logged when session has no interactions."""
    _, logs = _run_tail("interactions = {}", "_t_empty_warn")
    warnings = [r for r in logs if r.levelno >= logging.WARNING]
    assert len(warnings) >= 1, (
        f"Expected at least one WARNING log for empty session, "
        f"got levels: {[r.levelname for r in logs]}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_nonempty_interactions_returns_dict():
    """Non-empty interactions must be returned as-is with stats recorded."""
    ret, _ = _run_tail(
        "interactions = {'s1': _M(reward=0.75), 's2': _M(reward=0.9)}",
        "_t_nonempty",
    )
    assert isinstance(ret, dict), f"Expected dict, got {type(ret).__name__}"
    assert len(ret) >= 2, f"Expected at least 2 entries, got {len(ret)}"


# [pr_diff] pass_to_pass
def test_single_interaction_returns_dict():
    """Single-interaction session still works (boundary case)."""
    ret, _ = _run_tail(
        "interactions = {'only': _M(reward=1.0)}",
        "_t_single",
    )
    assert isinstance(ret, dict) and len(ret) == 1


# [static] pass_to_pass
def test_not_stub():
    """arun_episode must have a substantial body (not a stub)."""
    source = Path(TARGET).read_text()
    func_node, _ = _find_arun_episode(source)
    assert func_node is not None, "arun_episode not found"
    body = func_node.body
    # Skip docstring if present
    skip = 1 if (body and isinstance(body[0], ast.Expr)
                 and isinstance(getattr(body[0].value, 'value', None), str)) else 0
    assert len(body[skip:]) >= 5, "arun_episode body looks like a stub"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:25 @ 84eaef12
def test_no_wildcard_imports():
    """No wildcard imports in workflow.py (AGENTS.md rule)."""
    source = Path(TARGET).read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.names:
            assert not any(a.name == "*" for a in node.names), (
                f"Wildcard import found: from {node.module} import *"
            )


# [agent_config] pass_to_pass — AGENTS.md:84-86 @ 84eaef12
def test_no_print_in_arun_episode():
    """No print() calls in arun_episode — use logger instead (AGENTS.md rule)."""
    source = Path(TARGET).read_text()
    func_node, _ = _find_arun_episode(source)
    assert func_node is not None, "arun_episode not found"
    for child in ast.walk(func_node):
        if (isinstance(child, ast.Call)
            and isinstance(child.func, ast.Name)
            and child.func.id == "print"):
            assert False, "print() call found in arun_episode — use logger"
