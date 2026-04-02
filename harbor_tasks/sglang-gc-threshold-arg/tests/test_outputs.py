"""
Task: sglang-gc-threshold-arg
Repo: sgl-project/sglang @ 4e905febd2f9e96b4c114530a2379b084ad791af
PR:   21481

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import gc
import textwrap
from pathlib import Path

REPO = "/workspace/sglang"
SERVER_ARGS = f"{REPO}/python/sglang/srt/server_args.py"
ENGINE = f"{REPO}/python/sglang/srt/entrypoints/engine.py"


# ---------------------------------------------------------------------------
# Helper: extract a named function's source from a file's AST
# ---------------------------------------------------------------------------

def _extract_func_source(filepath, func_name):
    """Return source text of `func_name` from `filepath`, or None."""
    source = Path(filepath).read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == func_name:
            return ast.get_source_segment(source, node)
    return None


def _find_gc_setter_func(filepath):
    """Find the function in engine.py that calls gc.set_threshold and return (name, source)."""
    source = Path(filepath).read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            func_src = ast.get_source_segment(source, node)
            if func_src and "set_threshold" in func_src:
                return node.name, func_src
    return None, None


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Both modified files must parse without syntax errors."""
    for f in [SERVER_ARGS, ENGINE]:
        source = Path(f).read_text()
        ast.parse(source)  # raises SyntaxError on failure


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_gc_function_sets_thresholds():
    """GC-setting function calls gc.set_threshold correctly for 1, 2, and 3 args."""
    func_name, func_src = _find_gc_setter_func(ENGINE)
    assert func_src is not None, "No function calling gc.set_threshold found in engine.py"

    # ServerArgs type annotation must be resolvable during exec (Python 3.12
    # evaluates annotations eagerly).  A placeholder type is sufficient.
    exec_ns = {"gc": gc, "__builtins__": __builtins__, "ServerArgs": type("ServerArgs", (), {})}
    exec(textwrap.dedent(func_src), exec_ns)
    fn = exec_ns[func_name]

    original = gc.get_threshold()

    # 3-arg
    class Args3:
        gc_threshold = [500, 5, 5]
    fn(Args3())
    assert gc.get_threshold() == (500, 5, 5), f"3-arg: expected (500,5,5), got {gc.get_threshold()}"

    # 1-arg
    gc.set_threshold(*original)
    class Args1:
        gc_threshold = [50000]
    fn(Args1())
    assert gc.get_threshold()[0] == 50000, f"1-arg: expected gen0=50000, got {gc.get_threshold()}"

    # 2-arg
    gc.set_threshold(*original)
    class Args2:
        gc_threshold = [700, 10]
    fn(Args2())
    assert gc.get_threshold()[0] == 700 and gc.get_threshold()[1] == 10, (
        f"2-arg: expected (700,10,...), got {gc.get_threshold()}"
    )

    # None → no-op
    gc.set_threshold(*original)
    class ArgsNone:
        gc_threshold = None
    fn(ArgsNone())
    assert gc.get_threshold() == original, "gc_threshold=None should be no-op"

    # Restore
    gc.set_threshold(*original)


# [pr_diff] fail_to_pass
def test_cli_parser_accepts_gc_threshold():
    """CLI parser accepts --gc-threshold with varying numbers of int arguments."""
    import argparse

    add_cli_src = _extract_func_source(SERVER_ARGS, "add_cli_args")
    assert add_cli_src is not None, "add_cli_args function not found"
    assert "--gc-threshold" in add_cli_src, "--gc-threshold not registered in add_cli_args"

    # Extract the parser.add_argument(...) block for --gc-threshold.
    # The argument string may appear on a line AFTER the opening paren,
    # so we backtrack to include the add_argument( line.
    lines = add_cli_src.split("\n")
    gc_line_idx = None
    for i, line in enumerate(lines):
        if "--gc-threshold" in line:
            gc_line_idx = i
            break
    assert gc_line_idx is not None, "Could not find --gc-threshold in add_cli_args"

    # Backtrack to the line containing add_argument(
    start = gc_line_idx
    for j in range(gc_line_idx, -1, -1):
        if "add_argument" in lines[j]:
            start = j
            break

    # Now capture from start until parens balance
    block_lines = []
    paren_depth = 0
    for line in lines[start:]:
        block_lines.append(line)
        paren_depth += line.count("(") - line.count(")")
        if paren_depth <= 0 and len(block_lines) > 0:
            break

    assert block_lines, "Could not extract --gc-threshold add_argument call"
    block_src = textwrap.dedent("\n".join(block_lines))
    parser = argparse.ArgumentParser()
    exec(block_src, {"parser": parser, "int": int, "str": str, "float": float, "bool": bool})

    # 3 ints
    args = parser.parse_args(["--gc-threshold", "700", "10", "10"])
    assert args.gc_threshold == [700, 10, 10]

    # 1 int
    args = parser.parse_args(["--gc-threshold", "50000"])
    assert args.gc_threshold == [50000]

    # Default is None
    args = parser.parse_args([])
    assert args.gc_threshold is None

    # Values are int, not str
    args = parser.parse_args(["--gc-threshold", "100", "20"])
    assert all(isinstance(v, int) for v in args.gc_threshold)


# [pr_diff] fail_to_pass
def test_validation_rejects_invalid_gc_threshold():
    """check_server_args rejects gc_threshold with 0 or 4+ values."""
    check_src = _extract_func_source(SERVER_ARGS, "check_server_args")
    assert check_src is not None, "check_server_args function not found"
    assert "gc_threshold" in check_src, "gc_threshold not validated in check_server_args"

    # Extract ONLY the gc_threshold validation block from check_server_args
    # to avoid executing unrelated checks with missing dependencies.
    lines = check_src.split("\n")
    gc_block = []
    capturing = False
    base_indent = None
    for line in lines:
        if "gc_threshold" in line and not capturing:
            capturing = True
            base_indent = len(line) - len(line.lstrip())
        if capturing:
            stripped = line.strip()
            cur_indent = len(line) - len(line.lstrip()) if stripped else base_indent + 1
            if cur_indent >= base_indent or not stripped:
                gc_block.append(line)
            else:
                break

    assert gc_block, "Could not locate gc_threshold validation block"
    gc_code = textwrap.dedent("\n".join(gc_block))

    # Wrap the extracted block in a callable that sets self.gc_threshold
    wrapper = f"""\
def _validate(gc_threshold):
    class _self:
        pass
    _self.gc_threshold = gc_threshold
    self = _self
{textwrap.indent(gc_code, '    ')}
"""
    exec_ns = {"__builtins__": __builtins__}
    exec(wrapper, exec_ns)
    validate = exec_ns["_validate"]

    # Valid inputs — should NOT raise
    for valid in ([700, 10, 10], [50000], [100, 20]):
        validate(valid)

    # Invalid: 4 values — must raise
    import pytest
    with pytest.raises((ValueError, SystemExit, AssertionError)):
        validate([1, 2, 3, 4])

    # Invalid: 5 values
    with pytest.raises((ValueError, SystemExit, AssertionError)):
        validate([1, 2, 3, 4, 5])


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_server_args_structures_intact():
    """ServerArgs class and add_cli_args/check_server_args functions exist."""
    source = Path(SERVER_ARGS).read_text()
    tree = ast.parse(source)
    classes = {n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}
    funcs = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    assert "ServerArgs" in classes, "ServerArgs class missing"
    assert "add_cli_args" in funcs, "add_cli_args function missing"
    assert "check_server_args" in funcs, "check_server_args function missing"


# [static] pass_to_pass
def test_launch_subprocesses_intact():
    """_launch_subprocesses function exists in engine.py."""
    source = Path(ENGINE).read_text()
    tree = ast.parse(source)
    funcs = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    assert "_launch_subprocesses" in funcs, "_launch_subprocesses missing"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — integration
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_gc_invoked_in_launch_subprocesses():
    """GC threshold logic is invoked within _launch_subprocesses."""
    source = Path(ENGINE).read_text()
    tree = ast.parse(source)

    # Find functions that call gc.set_threshold
    gc_func_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            func_src = ast.get_source_segment(source, node)
            if func_src and "set_threshold" in func_src:
                gc_func_names.add(node.name)

    assert gc_func_names, "No function calls gc.set_threshold in engine.py"

    # If directly in _launch_subprocesses, that's fine
    if "_launch_subprocesses" in gc_func_names:
        return

    # Otherwise check that a gc-setting function is called from _launch_subprocesses
    launch_src = _extract_func_source(ENGINE, "_launch_subprocesses")
    assert launch_src is not None, "_launch_subprocesses not found"
    for gc_name in gc_func_names:
        if gc_name in launch_src:
            return

    raise AssertionError("GC threshold logic not invoked during subprocess launch")


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — python/sglang/srt/server_args.py:287-290 @ 4e905feb
def test_gc_threshold_in_class_and_cli():
    """gc_threshold appears in both ServerArgs class body and add_cli_args (ordering rule)."""
    source = Path(SERVER_ARGS).read_text()
    tree = ast.parse(source)

    in_class = False
    in_cli = False
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "ServerArgs":
            for item in node.body:
                targets = []
                if isinstance(item, ast.AnnAssign):
                    targets = [item.target]
                elif isinstance(item, ast.Assign):
                    targets = item.targets
                for t in targets:
                    if hasattr(t, "id") and t.id == "gc_threshold":
                        in_class = True
        if isinstance(node, ast.FunctionDef) and node.name == "add_cli_args":
            func_src = ast.get_source_segment(source, node)
            if func_src and "--gc-threshold" in func_src:
                in_cli = True

    assert in_class, "gc_threshold not found in ServerArgs class body"
    assert in_cli, "gc_threshold not found in add_cli_args"
