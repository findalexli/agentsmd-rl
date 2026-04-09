"""
Task: opencode-effectify-todowrite-tool
Repo: anomalyco/opencode @ ae7e2eb3fb32b12e0c45681950540df7379e021a
PR:   #20789

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import re
from pathlib import Path

REPO = "/workspace/opencode"
TODO_TS = Path(REPO) / "packages/opencode/src/tool/todo.ts"
REGISTRY_TS = Path(REPO) / "packages/opencode/src/tool/registry.ts"
SESSION_TODO_TS = Path(REPO) / "packages/opencode/src/session/todo.ts"
PKG_DIR = Path(REPO) / "packages/opencode"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified TypeScript files must exist and be non-empty."""
    for f in [TODO_TS, REGISTRY_TS, SESSION_TODO_TS]:
        assert f.exists(), f"{f.name} missing"
        assert f.stat().st_size > 100, f"{f.name} suspiciously small"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_todowrite_is_effect():
    """TodoWriteTool must be an Effect (built via Tool.defineEffect), not a plain object."""
    check = PKG_DIR / "_check_effect.ts"
    check.write_text(
        'import { Effect } from "effect"\n'
        'const { TodoWriteTool } = await import("./src/tool/todo")\n'
        'if (!Effect.isEffect(TodoWriteTool)) {\n'
        '  console.error("FAIL: TodoWriteTool is not an Effect")\n'
        '  process.exit(1)\n'
        '}\n'
        'console.log("OK")\n'
    )
    try:
        r = subprocess.run(
            ["bun", "run", str(check)],
            cwd=str(PKG_DIR),
            capture_output=True, text=True, timeout=30,
        )
        assert r.returncode == 0, (
            f"TodoWriteTool is not an Effect:\n{r.stdout}\n{r.stderr}"
        )
    finally:
        check.unlink(missing_ok=True)


# [pr_diff] fail_to_pass
def test_todo_default_layer_exported():
    """Todo.defaultLayer must be exported (public) from session/todo.ts."""
    src = SESSION_TODO_TS.read_text()
    assert re.search(r'\bexport\s+const\s+defaultLayer\b', src), (
        "Todo.defaultLayer is not exported from session/todo.ts"
    )


# [pr_diff] fail_to_pass
def test_registry_provides_todo_layer():
    """ToolRegistry.defaultLayer must provide Todo.defaultLayer."""
    src = REGISTRY_TS.read_text()
    assert "Todo.defaultLayer" in src, (
        "ToolRegistry.defaultLayer does not provide Todo.defaultLayer"
    )
    assert re.search(r'import\s.*Todo.*from', src), (
        "registry.ts does not import Todo"
    )


# [pr_diff] fail_to_pass
def test_todowrite_yields_service():
    """TodoWriteTool must yield Todo.Service inside an Effect (effectified pattern)."""
    src = TODO_TS.read_text()
    assert "yield* Todo.Service" in src, (
        "todo.ts does not yield Todo.Service — "
        "expected effectified pattern with `yield* Todo.Service`"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static)
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_typecheck():
    """bun typecheck must pass from packages/opencode."""
    r = subprocess.run(
        ["bun", "typecheck"],
        cwd=str(PKG_DIR),
        capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, (
        f"Typecheck failed:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — packages/opencode/AGENTS.md:20 @ ae7e2eb3
def test_effect_gen_composition():
    """todo.ts must use Effect.gen(function* () { ... }) for composition."""
    src = TODO_TS.read_text()
    assert re.search(r'Effect\.gen\s*\(\s*function\s*\*', src), (
        "todo.ts does not use Effect.gen(function* () { ... }) for composition "
        "(required by packages/opencode/AGENTS.md)"
    )


# [agent_config] pass_to_pass — AGENTS.md:13 @ ae7e2eb3
def test_no_any_type():
    """Modified tool files must not use the `any` type annotation."""
    for f in [TODO_TS]:
        src = f.read_text()
        lines = [l for l in src.splitlines()
                 if not l.strip().startswith("//") and not l.strip().startswith("*")]
        code = "\n".join(lines)
        matches = re.findall(r':\s*any\b', code)
        assert len(matches) == 0, (
            f"Found {len(matches)} `: any` type annotations in {f.name}"
        )
