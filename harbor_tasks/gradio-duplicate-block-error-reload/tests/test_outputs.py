"""
Task: gradio-duplicate-block-error-reload
Repo: gradio-app/gradio @ a17eb7888b48cbd98b1e0feb17e2614bf3853d66
PR:   13013

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import textwrap
import types
from pathlib import Path

REPO = "/workspace/gradio"
TARGET = f"{REPO}/gradio/utils.py"


def _extract_post_exec_region():
    """Extract code between exec(no_reload_source_code...) and sys.modules[/while."""
    source = Path(TARGET).read_text()
    lines = source.splitlines()

    exec_idx = None
    end_idx = None
    for i, line in enumerate(lines):
        if "exec(no_reload_source_code" in line:
            exec_idx = i
        if exec_idx is not None and i > exec_idx:
            stripped = line.strip()
            if stripped.startswith("sys.modules[") or stripped.startswith("while "):
                end_idx = i
                break

    assert exec_idx is not None, "exec(no_reload_source_code) not found in utils.py"
    if end_idx is None:
        end_idx = min(exec_idx + 30, len(lines))

    region = lines[exec_idx + 1 : end_idx]
    return textwrap.dedent("\n".join(region))


def _run_region(blocks, initial_context_id, demo_name="demo", demo_exists=True):
    """Run extracted post-exec region with mocks, return final Context.id."""
    code = _extract_post_exec_region()

    real_lines = [l for l in code.splitlines() if l.strip() and not l.strip().startswith("#")]
    assert len(real_lines) >= 1, "No executable code between exec() and sys.modules (bug not fixed)"

    class Context:
        id = initial_context_id

    class Demo:
        def __init__(self, blks):
            self.blocks = blks

    class Reloader:
        pass

    Reloader.demo_name = demo_name

    module = types.ModuleType("test_module")
    if demo_exists:
        module.demo = Demo(blocks) if blocks is not None else None
    reloader = Reloader()

    ns = {
        "Context": Context,
        "module": module,
        "reloader": reloader,
        "getattr": getattr,
        "hasattr": hasattr,
        "max": max,
        "len": len,
        "list": list,
        "set": set,
        "dict": dict,
        "int": int,
        "print": print,
        "type": type,
        "__builtins__": __builtins__,
    }

    exec(code, ns)
    return Context.id


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """gradio/utils.py must parse without syntax errors."""
    source = Path(TARGET).read_text()
    ast.parse(source)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_context_id_bumped_past_block_ids():
    """After module re-exec, Context.id must exceed max existing block ID."""
    result = _run_region(
        blocks={0: "b0", 1: "b1", 5: "b5", 10: "b10"},
        initial_context_id=3,
    )
    assert result >= 11, f"Context.id = {result}, expected >= 11 (max block key was 10)"


# [pr_diff] fail_to_pass
def test_context_id_varied_block_distributions():
    """Fix handles sequential, sparse, and single-block scenarios."""
    scenarios = [
        ({0: "x", 1: "x", 2: "x"}, 0, 3, "sequential 0-2"),
        ({0: "x", 5: "x", 100: "x"}, 2, 101, "sparse up to 100"),
        ({42: "x"}, 0, 43, "single block at 42"),
    ]
    for blocks, init_id, min_expected, desc in scenarios:
        result = _run_region(blocks=blocks, initial_context_id=init_id)
        assert result >= min_expected, f"[{desc}] Context.id={result}, expected >= {min_expected}"


# [pr_diff] fail_to_pass
def test_context_id_preserved_when_already_high():
    """If Context.id already exceeds max block ID, it must not decrease."""
    result = _run_region(
        blocks={0: "x", 5: "x", 10: "x"},
        initial_context_id=200,
    )
    assert result >= 200, f"Context.id={result}, expected >= 200 (was already high)"


# [pr_diff] fail_to_pass
def test_no_crash_when_demo_absent():
    """Fix must not crash when demo is missing, None, or has empty blocks."""
    # demo attribute not set on module
    cid = _run_region(blocks=None, initial_context_id=5, demo_exists=False)
    assert cid == 5, f"Context.id changed to {cid} when demo absent"

    # demo is None
    cid = _run_region(blocks=None, initial_context_id=7, demo_exists=True)
    assert cid == 7, f"Context.id changed to {cid} when demo is None"

    # demo has empty blocks dict
    cid = _run_region(blocks={}, initial_context_id=9)
    assert cid == 9, f"Context.id changed to {cid} when blocks empty"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_watchfn_structure_preserved():
    """Core watchfn landmarks must still be present."""
    source = Path(TARGET).read_text()
    assert "exec(no_reload_source_code" in source, "exec() call missing"
    assert "Context.id = 0" in source, "Context.id = 0 reset missing"
    assert "reloader.should_watch" in source, "reloader.should_watch loop missing"


# [pr_diff] pass_to_pass
def test_context_reset_precedes_exec():
    """Context.id = 0 must appear before exec(no_reload_source_code)."""
    lines = Path(TARGET).read_text().splitlines()
    reset_line = next((i for i, l in enumerate(lines) if "Context.id = 0" in l), None)
    exec_line = next((i for i, l in enumerate(lines) if "exec(no_reload_source_code" in l), None)
    assert reset_line is not None, "Context.id = 0 not found"
    assert exec_line is not None, "exec(no_reload_source_code) not found"
    assert reset_line < exec_line, (
        f"Context.id=0 (line {reset_line+1}) must precede exec() (line {exec_line+1})"
    )


# [static] pass_to_pass
def test_not_stub():
    """utils.py must not be a stub — needs substantial content."""
    source = Path(TARGET).read_text()
    assert len(source.splitlines()) >= 500, "File too short to be real"
    tree = ast.parse(source)
    funcs = sum(1 for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)))
    assert funcs >= 20, f"Only {funcs} functions — file appears to be a stub"
