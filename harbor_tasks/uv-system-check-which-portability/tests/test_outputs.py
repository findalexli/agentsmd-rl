"""
Task: uv-system-check-which-portability
Repo: astral-sh/uv @ cedae1aa42c0f1ff59b4e4f988659c52d467d585
PR:   18588

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import importlib.util
from pathlib import Path

TARGET = "/repos/uv/scripts/check_system_python.py"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_valid():
    """Target script must be valid Python."""
    source = Path(TARGET).read_text()
    compile(source, TARGET, "exec")


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_no_platform_guard_on_path_check():
    """PATH verification must not be gated on os.name != 'nt'.

    The bug wraps the pylint path check in `if os.name != "nt":`,
    skipping it entirely on Windows. The fix removes this guard.
    Only checks for os.name guards that contain a `which` call or
    `"pylint"` PATH check inside their body — other os.name checks
    (e.g., choosing venv path) are legitimate.
    # AST-only because: install_package requires uv binary + network access
    """
    source = Path(TARGET).read_text()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if not isinstance(node, ast.If):
            continue
        test = node.test
        # Match: if os.name != "nt": or if os.name == "nt":
        is_os_name_nt = False
        if isinstance(test, ast.Compare):
            left = test.left
            if (isinstance(left, ast.Attribute)
                    and isinstance(left.value, ast.Name)
                    and left.value.id == "os"
                    and left.attr == "name"):
                for comparator in test.comparators:
                    if isinstance(comparator, ast.Constant) and comparator.value == "nt":
                        is_os_name_nt = True
        if not is_os_name_nt:
            continue
        # Check if the guarded body contains a `which` call or subprocess ["which", ...]
        body_source = ast.dump(node)
        if "which" in body_source.lower():
            assert False, (
                "Path check is still guarded by an os.name/'nt' comparison — "
                "Windows is never tested"
            )


# [pr_diff] fail_to_pass
def test_uses_cross_platform_which():
    """Must use shutil.which (cross-platform), not subprocess which.

    The buggy code calls subprocess.run(["which", "pylint"]) which only
    works on Unix. The fix should use shutil.which("pylint") which works
    on all platforms.
    # AST-only because: install_package requires uv binary + network access
    """
    source = Path(TARGET).read_text()
    tree = ast.parse(source)

    # Positive: shutil.which must be called somewhere in the module
    found_shutil_which_call = False
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "which"
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "shutil"):
            found_shutil_which_call = True
            break
    assert found_shutil_which_call, (
        "Expected shutil.which() call for cross-platform executable lookup"
    )

    # Negative: must not shell out to the `which` binary via subprocess
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            # Check for subprocess.run(["which", ...])
            if (isinstance(node.func, ast.Attribute)
                    and node.func.attr == "run"
                    and isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "subprocess"
                    and node.args):
                first_arg = node.args[0]
                if isinstance(first_arg, (ast.List, ast.Tuple)):
                    elts = first_arg.elts
                    if (elts
                            and isinstance(elts[0], ast.Constant)
                            and elts[0].value == "which"):
                        assert False, (
                            "Still shells out to Unix `which` command via subprocess"
                        )


# [pr_diff] fail_to_pass
def test_path_check_raises_when_not_found():
    """shutil.which result must be checked and raise Exception if None.

    Verifies the fix actually uses the shutil.which return value to decide
    whether to raise, not just calls it and ignores the result.
    # AST-only because: install_package requires uv binary + network access
    """
    source = Path(TARGET).read_text()
    tree = ast.parse(source)

    # Find: if shutil.which(...) is None: ... raise ...
    # or:   if not shutil.which(...): ... raise ...
    found = False
    for node in ast.walk(tree):
        if not isinstance(node, ast.If):
            continue
        test = node.test

        # Pattern 1: shutil.which(...) is None
        is_which_none = (
            isinstance(test, ast.Compare)
            and isinstance(test.left, ast.Call)
            and isinstance(test.left.func, ast.Attribute)
            and test.left.func.attr == "which"
            and isinstance(test.left.func.value, ast.Name)
            and test.left.func.value.id == "shutil"
            and any(isinstance(op, ast.Is) for op in test.ops)
        )

        # Pattern 2: not shutil.which(...)
        is_not_which = (
            isinstance(test, ast.UnaryOp)
            and isinstance(test.op, ast.Not)
            and isinstance(test.operand, ast.Call)
            and isinstance(test.operand.func, ast.Attribute)
            and test.operand.func.attr == "which"
            and isinstance(test.operand.func.value, ast.Name)
            and test.operand.func.value.id == "shutil"
        )

        if is_which_none or is_not_which:
            # Verify the body contains a raise
            for child in ast.walk(node):
                if isinstance(child, ast.Raise):
                    found = True
                    break
            if found:
                break

    assert found, (
        "Expected: if shutil.which(...) is None: raise Exception(...) — "
        "the which result must be checked and raise on failure"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_module_loads():
    """Module must load and install_package must be callable."""
    spec = importlib.util.spec_from_file_location("check_sp", TARGET)
    mod = importlib.util.module_from_spec(spec)
    mod.__name__ = "check_sp"
    spec.loader.exec_module(mod)
    assert hasattr(mod, "install_package"), "install_package function not found"
    assert callable(mod.install_package), "install_package is not callable"


# [static] pass_to_pass
def test_install_package_signature():
    """install_package must have correct function signature.

    Verifies the function accepts uv, package, and version parameters
    as required by the codebase.
    """
    source = Path(TARGET).read_text()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "install_package":
            # Check it has keyword-only arguments with proper defaults
            args = node.args
            # Should have keyword-only args: uv, package, version
            assert args.kwonlyargs, "install_package should have keyword-only args"
            arg_names = [a.arg for a in args.kwonlyargs]
            assert "uv" in arg_names, "install_package missing 'uv' parameter"
            assert "package" in arg_names, "install_package missing 'package' parameter"
            assert "version" in arg_names, "install_package missing 'version' parameter"
            return
    assert False, "install_package function not found"


# [static] pass_to_pass
def test_script_has_main_guard():
    """Script must have if __name__ == '__main__' guard for testability."""
    source = Path(TARGET).read_text()
    tree = ast.parse(source)

    found_main_guard = False
    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            # Check for if __name__ == "__main__": pattern
            if isinstance(node.test, ast.Compare):
                test = node.test
                if (isinstance(test.left, ast.Name) and test.left.id == "__name__"
                        and isinstance(test.comparators[0], ast.Constant)
                        and test.comparators[0].value == "__main__"):
                    found_main_guard = True
                    break
    assert found_main_guard, "Script missing if __name__ == '__main__' guard"


# [static] pass_to_pass
def test_not_stub():
    """install_package must have real implementation, not a stub.
    # AST-only because: install_package requires uv binary + network access
    """
    source = Path(TARGET).read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "install_package":
            meaningful = sum(
                1
                for child in ast.walk(node)
                if isinstance(
                    child,
                    (ast.Assign, ast.AugAssign, ast.If, ast.With, ast.For,
                     ast.While, ast.Try, ast.Raise, ast.Return),
                )
            )
            assert meaningful >= 5, (
                f"install_package has only {meaningful} statements — likely a stub"
            )
            return
    assert False, "install_package function not found in AST"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from CLAUDE.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — CLAUDE.md:16 @ cedae1aa42c0f1ff59b4e4f988659c52d467d585
def test_top_level_shutil_import():
    """shutil must be imported at the top level, not locally.

    CLAUDE.md line 16: PREFER top-level imports over local imports
    # AST-only because: checking import location requires AST inspection
    """
    source = Path(TARGET).read_text()
    tree = ast.parse(source)
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "shutil":
                    return  # Found at top level
        if isinstance(node, ast.ImportFrom) and node.module and "shutil" in node.module:
            return  # Found at top level
    assert False, "shutil not imported at top level (CLAUDE.md:16)"
