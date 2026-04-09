"""Task: sglang-dump-metric-eval-paths
Repo: sgl-project/sglang @ cd2d45e22085045a5e9cd14666be7b0e96af601d
PR:   22147

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import sys
from pathlib import Path

REPO = Path("/workspace/sglang")


def find_function_calls(node: ast.AST, func_name: str):
    """Find all calls to a function by name in an AST subtree."""
    calls = []
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            # Handle direct name calls
            if isinstance(child.func, ast.Name) and child.func.id == func_name:
                calls.append(child)
            # Handle attribute calls (e.g., module.func)
            elif isinstance(child.func, ast.Attribute) and child.func.attr == func_name:
                calls.append(child)
    return calls


def get_call_keyword_arg(call: ast.Call, arg_name: str) -> ast.expr | None:
    """Get the value of a keyword argument from a call."""
    for kw in call.keywords:
        if kw.arg == arg_name:
            return kw.value
    return None


def parse_file(file_path: Path) -> ast.Module:
    """Parse a Python file and return its AST."""
    content = file_path.read_text()
    return ast.parse(content)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------


def test_accuracy_test_runner_syntax():
    """Modified accuracy_test_runner.py must parse without errors."""
    file_path = REPO / "python/sglang/test/accuracy_test_runner.py"
    src = file_path.read_text()
    ast.parse(src)  # Will raise SyntaxError if invalid


def test_lm_eval_kit_syntax():
    """Modified lm_eval_kit.py must parse without errors."""
    file_path = REPO / "python/sglang/test/kits/lm_eval_kit.py"
    src = file_path.read_text()
    ast.parse(src)  # Will raise SyntaxError if invalid


def test_mmmu_vlm_kit_syntax():
    """Modified mmmu_vlm_kit.py must parse without errors."""
    file_path = REPO / "python/sglang/test/kits/mmmu_vlm_kit.py"
    src = file_path.read_text()
    ast.parse(src)  # Will raise SyntaxError if invalid


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


def test_accuracy_test_runner_has_dump_metric_import():
    """Verify dump_metric is imported in accuracy_test_runner.py."""
    file_path = REPO / "python/sglang/test/accuracy_test_runner.py"
    tree = parse_file(file_path)

    found_import = False
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module == "sglang.test.test_utils":
                for alias in node.names:
                    if alias.name == "dump_metric":
                        found_import = True
                        break
        if found_import:
            break

    assert found_import, "dump_metric should be imported from test_utils"


def test_accuracy_test_runner_nemo_skills_has_dump_metric_call():
    """Verify _run_nemo_skills_eval calls dump_metric with correct args."""
    file_path = REPO / "python/sglang/test/accuracy_test_runner.py"
    tree = parse_file(file_path)

    func_node = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_run_nemo_skills_eval":
            func_node = node
            break

    assert func_node is not None, "_run_nemo_skills_eval function should exist"

    dump_calls = find_function_calls(func_node, "dump_metric")
    assert len(dump_calls) >= 1, "_run_nemo_skills_eval should call dump_metric"

    call = dump_calls[0]
    labels_arg = get_call_keyword_arg(call, "labels")
    assert labels_arg is not None, "dump_metric should have labels keyword arg"

    if isinstance(labels_arg, ast.Dict):
        keys = [k.value for k in labels_arg.keys if isinstance(k, ast.Constant)]
        assert "api" in keys, "labels should contain 'api' key"
        assert "nemo-skills" in str(ast.dump(labels_arg)), "api should be 'nemo-skills'"


def test_lm_eval_kit_has_dump_metric_import():
    """Verify dump_metric is imported in lm_eval_kit.py."""
    file_path = REPO / "python/sglang/test/kits/lm_eval_kit.py"
    tree = parse_file(file_path)

    found_import = False
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module == "sglang.test.test_utils":
                for alias in node.names:
                    if alias.name == "dump_metric":
                        found_import = True
                        break
        if found_import:
            break

    assert found_import, "dump_metric should be imported from test_utils"


def test_lm_eval_kit_test_lm_eval_has_dump_metric_call():
    """Verify test_lm_eval calls dump_metric with correct structure."""
    file_path = REPO / "python/sglang/test/kits/lm_eval_kit.py"
    tree = parse_file(file_path)

    func_node = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "test_lm_eval":
            func_node = node
            break

    assert func_node is not None, "test_lm_eval function should exist"

    dump_calls = find_function_calls(func_node, "dump_metric")
    assert len(dump_calls) >= 1, "test_lm_eval should call dump_metric"

    call = dump_calls[0]
    labels_arg = get_call_keyword_arg(call, "labels")
    assert labels_arg is not None, "dump_metric should have labels keyword arg"

    if isinstance(labels_arg, ast.Dict):
        keys = [k.value for k in labels_arg.keys if isinstance(k, ast.Constant)]
        assert "eval" in keys, "labels should contain 'eval' key"
        assert "lm-eval" in str(ast.dump(labels_arg)), "eval should be 'lm-eval'"


def test_mmmu_vlm_kit_has_dump_metric_import():
    """Verify dump_metric is imported in mmmu_vlm_kit.py."""
    file_path = REPO / "python/sglang/test/kits/mmmu_vlm_kit.py"
    tree = parse_file(file_path)

    found_import = False
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module == "sglang.test.test_utils":
                for alias in node.names:
                    if alias.name == "dump_metric":
                        found_import = True
                        break
        if found_import:
            break

    assert found_import, "dump_metric should be imported from test_utils"


def test_mmmu_vlm_kit_test_mmmu_has_dump_metric_call():
    """Verify test_mmmu function calls dump_metric."""
    file_path = REPO / "python/sglang/test/kits/mmmu_vlm_kit.py"
    tree = parse_file(file_path)

    func_node = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "test_mmmu":
            func_node = node
            break

    assert func_node is not None, "test_mmmu function should exist"

    dump_calls = find_function_calls(func_node, "dump_metric")
    assert len(dump_calls) >= 1, "test_mmmu should call dump_metric"

    call = dump_calls[0]
    labels_arg = get_call_keyword_arg(call, "labels")
    assert labels_arg is not None, "dump_metric should have labels keyword arg"

    if labels_arg and isinstance(labels_arg, ast.Dict):
        assert "lmms-eval" in str(ast.dump(labels_arg)), "api should be 'lmms-eval'"


def test_mmmu_vlm_kit_run_vlm_mmmu_test_has_dump_metric_call():
    """Verify _run_vlm_mmmu_test function calls dump_metric."""
    file_path = REPO / "python/sglang/test/kits/mmmu_vlm_kit.py"
    tree = parse_file(file_path)

    func_node = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_run_vlm_mmmu_test":
            func_node = node
            break

    assert func_node is not None, "_run_vlm_mmmu_test function should exist"

    dump_calls = find_function_calls(func_node, "dump_metric")
    assert len(dump_calls) >= 1, "_run_vlm_mmmu_test should call dump_metric"

    call = dump_calls[0]
    labels_arg = get_call_keyword_arg(call, "labels")
    assert labels_arg is not None, "dump_metric should have labels keyword arg"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------


def test_repo_ruff_lint():
    """Modified files pass ruff linting (pass_to_pass)."""
    import subprocess

    files = [
        "python/sglang/test/accuracy_test_runner.py",
        "python/sglang/test/kits/lm_eval_kit.py",
        "python/sglang/test/kits/mmmu_vlm_kit.py",
        "python/sglang/test/test_utils.py",
    ]

    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Failed to install ruff: {r.stderr[-500:]}"

    r = subprocess.run(
        ["ruff", "check", "--select=F401,F821"] + files,
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff linting failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


def test_repo_black_format():
    """Modified files pass black formatting check (pass_to_pass)."""
    import subprocess

    files = [
        "python/sglang/test/accuracy_test_runner.py",
        "python/sglang/test/kits/lm_eval_kit.py",
        "python/sglang/test/kits/mmmu_vlm_kit.py",
        "python/sglang/test/test_utils.py",
    ]

    r = subprocess.run(
        ["pip", "install", "black", "-q"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Failed to install black: {r.stderr[-500:]}"

    r = subprocess.run(
        ["black", "--check"] + files,
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Black format check failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


def test_repo_isort_check():
    """Modified files pass isort import sorting check (pass_to_pass)."""
    import subprocess

    files = [
        "python/sglang/test/accuracy_test_runner.py",
        "python/sglang/test/kits/lm_eval_kit.py",
        "python/sglang/test/kits/mmmu_vlm_kit.py",
        "python/sglang/test/test_utils.py",
    ]

    r = subprocess.run(
        ["pip", "install", "isort", "-q"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Failed to install isort: {r.stderr[-500:]}"

    r = subprocess.run(
        ["isort", "--check"] + files,
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Isort check failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


def test_test_utils_dump_metric_exists():
    """dump_metric function exists in test_utils module."""
    file_path = REPO / "python/sglang/test/test_utils.py"
    tree = parse_file(file_path)

    found_func = False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "dump_metric":
            found_func = True
            break

    assert found_func, "dump_metric function should exist in test_utils"


def test_repo_python_syntax():
    """All Python files in sglang/test compile without syntax errors (pass_to_pass)."""
    import py_compile

    test_dir = REPO / "python/sglang/test"
    py_files = list(test_dir.rglob("*.py"))

    errors = []
    for py_file in py_files:
        try:
            py_compile.compile(str(py_file), doraise=True)
        except py_compile.PyCompileError as e:
            errors.append(f"{py_file}: {e}")

    assert not errors, f"Syntax errors found:\n" + "\n".join(errors[:10])


def test_modified_files_compile():
    """Modified test files compile without errors (pass_to_pass)."""
    import py_compile

    files_to_check = [
        REPO / "python/sglang/test/accuracy_test_runner.py",
        REPO / "python/sglang/test/kits/lm_eval_kit.py",
        REPO / "python/sglang/test/kits/mmmu_vlm_kit.py",
        REPO / "python/sglang/test/test_utils.py",
    ]

    for file_path in files_to_check:
        try:
            py_compile.compile(str(file_path), doraise=True)
        except py_compile.PyCompileError as e:
            raise AssertionError(f"Syntax error in {file_path}: {e}")


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
