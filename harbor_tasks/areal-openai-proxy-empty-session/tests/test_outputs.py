"""
Task: areal-openai-proxy-empty-session
Repo: inclusionAI/AReaL @ 84eaef1292b2a3184d4a565d4abb0758408be018
PR:   #971

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import json
import subprocess
import textwrap
from pathlib import Path

REPO = "/workspace/AReaL"
TARGET = f"{REPO}/areal/experimental/openai/proxy/workflow.py"


# ---------------------------------------------------------------------------
# Helpers: extract the interactions-handling tail using AST
# ---------------------------------------------------------------------------

def _find_arun_episode_ast(source: str):
    """Return the AST node for arun_episode."""
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "arun_episode":
            return node
    return None


def _find_online_mode_interactions_block(func_node: ast.AsyncFunctionDef, source_lines: list[str]):
    """
    Find the interactions-handling block in the online-mode branch of arun_episode.

    Extracts the code AFTER 'interactions = await proxy_client.export_interactions(...)'
    through the final 'return interactions' at the end of the online-mode branch.

    The test script provides 'interactions' via __INTERACTIONS__, so we skip the
    interactions assignment itself and extract the subsequent processing code.

    Uses AST traversal to be robust to comment changes, variable renaming, and
    refactoring.
    """
    # Find 'if self.mode == "online"' in the function body
    online_if = None
    for item in func_node.body:
        if isinstance(item, ast.If):
            test = item.test
            if isinstance(test, ast.Compare):
                for cmp in test.left, *test.comparators:
                    if isinstance(cmp, ast.Attribute) and cmp.attr == "mode":
                        online_if = item
                        break
        if online_if:
            break

    if not online_if:
        return None

    # Find the interactions assignment and return in the online if body
    interactions_end_lineno = None
    return_lineno = None
    for s in online_if.body:
        if isinstance(s, ast.Assign):
            for t in s.targets:
                if isinstance(t, ast.Name) and t.id == "interactions":
                    if isinstance(s.value, ast.Await):
                        call = s.value.value
                        if isinstance(call, ast.Call):
                            func_attr = call.func
                            if isinstance(func_attr, ast.Attribute) and func_attr.attr == "export_interactions":
                                # The interactions assignment spans multiple lines
                                interactions_end_lineno = s.end_lineno
        if isinstance(s, ast.Return):
            if isinstance(s.value, ast.Name) and s.value.id == "interactions":
                return_lineno = s.lineno

    if interactions_end_lineno and return_lineno:
        # Extract from AFTER the interactions assignment to the return
        block_lines = [
            l if l.strip() else " "
            for l in source_lines[interactions_end_lineno : return_lineno]
        ]
        return block_lines

    return None


# Subprocess script template
_SUBPROCESS_TEMPLATE = """\
import asyncio, json, logging
from unittest.mock import MagicMock

_log = []
async def __TEST_FUNC__():
    import logging as _lg
    from unittest.mock import MagicMock as _M
    class _H(_lg.Handler):
        def emit(s, r): _log.append(r)
    logger = _lg.getLogger("__LOGGER__")
    logger.handlers.clear()
    logger.addHandler(_H())
    logger.setLevel(_lg.DEBUG)
    session_info = _M()
    session_info.session_id = "test-session"
    workflow_context = _M()
    workflow_context.stat_scope.return_value = "scope"
    stats_tracker = _M()
    self = _M()
    __INTERACTIONS__
__TAIL__

result = asyncio.run(__TEST_FUNC__())
warnings = [r for r in _log if r.levelno >= logging.WARNING]
print(json.dumps({
    "is_none": result is None,
    "is_dict": isinstance(result, dict),
    "len": len(result) if isinstance(result, dict) else 0,
    "warnings": len(warnings),
    "repr": repr(result),
}))
"""


def _run_tail_subprocess(interactions_code: str, test_id: str) -> dict:
    """Execute the interactions-handling block in a subprocess.

    Uses AST-based extraction (not text patterns) to find the online-mode
    interactions handling section, then runs it with mocked dependencies.
    """
    source = Path(TARGET).read_text()
    func_node = _find_arun_episode_ast(source)
    assert func_node is not None, "arun_episode not found in AST"

    lines = source.splitlines()
    block_lines = _find_online_mode_interactions_block(func_node, lines)

    # Fallback: if AST extraction fails, use structural line-based extraction
    if block_lines is None or len(block_lines) == 0:
        in_online = False
        interactions_end = None
        return_lineno = None
        for i, line in enumerate(lines):
            stripped = line.strip()
            if "mode" in stripped and "online" in stripped and "==" in stripped:
                in_online = True
            if in_online and "export_interactions" in stripped and "await" in stripped:
                # Found the interactions assignment - find its closing paren
                interactions_end = i + 1  # assume single line for fallback
            if in_online and interactions_end is not None:
                if stripped.startswith("return ") and "interactions" in stripped:
                    return_lineno = i
                    break
        if interactions_end and return_lineno:
            block_lines = [
                l if l.strip() else " "
                for l in lines[interactions_end:return_lineno]
            ]

    assert block_lines is not None and len(block_lines) > 0, (
        f"Could not extract interactions-handling block from arun_episode"
    )

    tail = "\n".join(block_lines)
    dedented = textwrap.dedent(tail)
    tail_indented = textwrap.indent(dedented, "    ")
    script = (
        _SUBPROCESS_TEMPLATE.replace("__TEST_FUNC__", f"_test_{test_id}")
        .replace("__LOGGER__", f"_eval_{test_id}")
        .replace("__INTERACTIONS__", interactions_code)
        .replace("__TAIL__", tail_indented)
    )

    r = subprocess.run(
        ["python3", "-c", script],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Subprocess failed: {r.stderr}\nstdout: {r.stdout}"
    return json.loads(r.stdout.strip().splitlines()[-1])


# ---------------------------------------------------------------------------
# Repo CI/CD Tests (pass_to_pass)
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass - from .github/workflows/format-check.yml
def test_repo_ruff_lint():
    """Repo's Python linting passes (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff==0.14.9", "-q"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Failed to install ruff: {r.stderr[-500:]}"

    r = subprocess.run(
        ["ruff", "check", "areal/"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff lint failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass - from .github/workflows/format-check.yml
def test_repo_ruff_format():
    """Repo's Python code formatting passes (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff==0.14.9", "-q"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Failed to install ruff: {r.stderr[-500:]}"

    r = subprocess.run(
        ["ruff", "format", "--check", "areal/"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass - syntax check for modified module
def test_repo_workflow_syntax():
    """Modified workflow.py compiles without syntax errors (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "py_compile", TARGET],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Syntax check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass - syntax check for proxy_gateway module
def test_repo_proxy_gateway_syntax():
    """Proxy gateway module compiles without syntax errors (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "py_compile", f"{REPO}/areal/experimental/openai/proxy/proxy_gateway.py"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"proxy_gateway.py syntax check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass - syntax check for online_agent module
def test_repo_online_agent_syntax():
    """Online agent module compiles without syntax errors (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "py_compile", f"{REPO}/areal/experimental/openai/proxy/online_agent.py"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"online_agent.py syntax check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass - verify pytest is available
def test_repo_pytest_available():
    """pytest is installed and functional (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "pytest", "--version"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"pytest check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass - from .github/workflows/format-check.yml (targeted)
def test_repo_ruff_lint_proxy():
    """Repo's Python linting passes for proxy module (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff==0.14.9", "-q"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Failed to install ruff: {r.stderr[-500:]}"

    r = subprocess.run(
        ["ruff", "check", "areal/experimental/openai/proxy/"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff lint failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass - from .github/workflows/format-check.yml (targeted)
def test_repo_ruff_format_proxy():
    """Repo's Python code formatting passes for proxy module (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff==0.14.9", "-q"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Failed to install ruff: {r.stderr[-500:]}"

    r = subprocess.run(
        ["ruff", "format", "--check", "areal/experimental/openai/proxy/"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass - syntax check for server module
def test_repo_server_syntax():
    """Proxy server module compiles without syntax errors (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "py_compile", f"{REPO}/areal/experimental/openai/proxy/server.py"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"server.py syntax check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass - from CI install-test (pyproject.toml validation)
def test_repo_pyproject_valid():
    """pyproject.toml is valid TOML and has required project section (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c",
         "import tomllib; f=open('pyproject.toml', 'rb'); d=tomllib.load(f); "
         "assert 'project' in d and 'name' in d['project'], 'Missing [project] name'"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"pyproject.toml validation failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """workflow.py must parse without syntax errors."""
    import py_compile
    py_compile.compile(TARGET, doraise=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests via subprocess
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_empty_interactions_returns_none():
    """Empty interactions dict returns None (rejected trajectory)."""
    result = _run_tail_subprocess("interactions = {}", "empty_none")
    assert result["is_none"], f"Expected None, got {result['repr']}"


# [pr_diff] fail_to_pass
def test_empty_interactions_logs_warning():
    """A warning is logged when session has no interactions."""
    result = _run_tail_subprocess("interactions = {}", "empty_warn")
    assert result["warnings"] >= 1, (
        f"Expected >=1 warning for empty session, got {result['warnings']}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_nonempty_interactions_returns_dict():
    """Non-empty interactions are returned as-is with stats recorded."""
    result = _run_tail_subprocess(
        "interactions = {'s1': _M(reward=0.75), 's2': _M(reward=0.9)}",
        "nonempty",
    )
    assert result["is_dict"], f"Expected dict, got {result['repr']}"
    assert result["len"] >= 2, f"Expected >=2 entries, got {result['len']}"


# [pr_diff] pass_to_pass
def test_single_interaction_returns_dict():
    """Single-interaction session still works correctly."""
    result = _run_tail_subprocess(
        "interactions = {'only': _M(reward=1.0)}",
        "single",
    )
    assert result["is_dict"] and result["len"] == 1, (
        f"Expected dict of len 1, got {result['repr']}"
    )


# [static] pass_to_pass
def test_not_stub():
    """arun_episode has a substantial body (not a stub)."""
    source = Path(TARGET).read_text()
    func_node = _find_arun_episode_ast(source)
    assert func_node is not None, "arun_episode not found"
    body = func_node.body
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
    func_node = _find_arun_episode_ast(source)
    assert func_node is not None, "arun_episode not found"
    for child in ast.walk(func_node):
        if (isinstance(child, ast.Call)
            and isinstance(child.func, ast.Name)
            and child.func.id == "print"):
            assert False, "print() call found in arun_episode — use logger"


# [agent_config] pass_to_pass — AGENTS.md:90 @ 84eaef12
def test_no_gpu_cpu_sync_in_arun_episode():
    """No GPU-CPU sync calls (.item(), .tolist()) in arun_episode hot path (AGENTS.md rule)."""
    source = Path(TARGET).read_text()
    func_node = _find_arun_episode_ast(source)
    assert func_node is not None, "arun_episode not found"
    for child in ast.walk(func_node):
        if (isinstance(child, ast.Call)
                and isinstance(child.func, ast.Attribute)
                and child.func.attr in ("item", "tolist")):
            assert False, (
                f"GPU-CPU sync call .{child.func.attr}() found in arun_episode — "
                "avoid sync ops in hot paths (AGENTS.md:90)"
            )
