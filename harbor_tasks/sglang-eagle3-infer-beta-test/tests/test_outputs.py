"""
Task: sglang-eagle3-infer-beta-test
Repo: sglang @ 6c2a759a04232ef4cb0c845528d75516ddbd9fe2
PR:   22303

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
from pathlib import Path

REPO = "/workspace/sglang"
TARGET_FILE = f"{REPO}/test/registered/spec/eagle/test_eagle_infer_beta.py"


def _parse_target_ast():
    """Parse the target file and return AST tree."""
    src = Path(TARGET_FILE).read_text()
    return ast.parse(src)


def _run_python_in_repo(code, timeout=60):
    """Run Python code in the repo environment."""
    r = subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )
    return r


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified test file must parse without errors."""
    src = Path(TARGET_FILE).read_text()
    ast.parse(src)  # Will raise SyntaxError if invalid


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_imports_use_eagle3():
    """Imports must use EAGLE3 constants instead of EAGLE - BEHAVIORAL via AST analysis."""
    tree = _parse_target_ast()

    # Behavioral analysis: Check that the import statements reference EAGLE3 constants
    # and that the class attributes use these imported names

    # Find imports
    imported_names = {}  # alias -> full_name
    eagle3_draft_imported = False
    eagle3_target_imported = False
    eagle_draft_imported = False
    eagle_target_imported = False

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module and 'test_utils' in node.module:
                for alias in node.names:
                    if alias.name == 'DEFAULT_DRAFT_MODEL_EAGLE3':
                        eagle3_draft_imported = True
                        imported_names[alias.asname or alias.name] = alias.name
                    if alias.name == 'DEFAULT_TARGET_MODEL_EAGLE3':
                        eagle3_target_imported = True
                        imported_names[alias.asname or alias.name] = alias.name
                    if alias.name == 'DEFAULT_DRAFT_MODEL_EAGLE':
                        eagle_draft_imported = True
                    if alias.name == 'DEFAULT_TARGET_MODEL_EAGLE':
                        eagle_target_imported = True

    # Must import EAGLE3 constants
    assert eagle3_draft_imported, "Must import DEFAULT_DRAFT_MODEL_EAGLE3"
    assert eagle3_target_imported, "Must import DEFAULT_TARGET_MODEL_EAGLE3"

    # Must NOT import old EAGLE constants
    assert not eagle_draft_imported, "Must not import old DEFAULT_DRAFT_MODEL_EAGLE"
    assert not eagle_target_imported, "Must not import old DEFAULT_TARGET_MODEL_EAGLE"

    # Now check that TestEagle3ServerBase uses the EAGLE3 constants
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "TestEagle3ServerBase":
            for item in node.body:
                if isinstance(item, ast.Assign):
                    for target in item.targets:
                        if isinstance(target, ast.Name):
                            if target.id == "model":
                                # Check that model uses EAGLE3 target
                                if isinstance(item.value, ast.Name):
                                    var_name = item.value.id
                                    assert "EAGLE3" in var_name or "EAGLE3" in imported_names.get(var_name, ""), \
                                        f"model must use DEFAULT_TARGET_MODEL_EAGLE3, got {var_name}"
                            if target.id == "draft_model":
                                # Check that draft_model uses EAGLE3
                                if isinstance(item.value, ast.Name):
                                    var_name = item.value.id
                                    assert "EAGLE3" in var_name or "EAGLE3" in imported_names.get(var_name, ""), \
                                        f"draft_model must use DEFAULT_DRAFT_MODEL_EAGLE3, got {var_name}"


# [pr_diff] fail_to_pass
def test_class_names_updated():
    """Class names must be updated from TestEagle* to TestEagle3* - BEHAVIORAL via AST analysis."""
    tree = _parse_target_ast()

    class_names = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            class_names.append(node.name)

    # Should have EAGLE3 class names
    assert "TestEagle3ServerBase" in class_names, "Must define TestEagle3ServerBase class"
    assert "TestEagle3ServerPage" in class_names, "Must define TestEagle3ServerPage class"

    # Should NOT have old EAGLE class names
    assert "TestEagleServerBase" not in class_names, "Must not have old TestEagleServerBase class"
    assert "TestEagleServerPage" not in class_names, "Must not have old TestEagleServerPage class"

    # Check inheritance - TestEagle3ServerPage should inherit from TestEagle3ServerBase
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "TestEagle3ServerPage":
            base_names = [base.id for base in node.bases if isinstance(base, ast.Name)]
            assert "TestEagle3ServerBase" in base_names, \
                "TestEagle3ServerPage must inherit from TestEagle3ServerBase"


# [pr_diff] fail_to_pass
def test_speculative_algorithm_eagle3():
    """Speculative algorithm must be set to EAGLE3 - BEHAVIORAL via AST check."""
    tree = _parse_target_ast()

    # Find the setUpClass method and check the launch_args list
    found_eagle3 = False
    found_eagle = False

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "TestEagle3ServerBase":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "setUpClass":
                    # Check all string literals in setUpClass
                    for subnode in ast.walk(item):
                        if isinstance(subnode, ast.Constant) and isinstance(subnode.value, str):
                            if subnode.value == "EAGLE3":
                                found_eagle3 = True
                            if subnode.value == "EAGLE":
                                found_eagle = True

    assert found_eagle3, "Must use 'EAGLE3' as speculative algorithm in setUpClass"
    assert not found_eagle, "Must not use old 'EAGLE' algorithm in setUpClass"


# [pr_diff] fail_to_pass
def test_new_args_added():
    """New arguments --dtype, --chunked-prefill-size must be added - BEHAVIORAL via AST check."""
    tree = _parse_target_ast()

    # Find the launch_args list in setUpClass and check for required args
    found_dtype = False
    found_chunked = False
    found_1024 = False

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "TestEagle3ServerBase":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "setUpClass":
                    # Look through all string constants in the method
                    all_strings = []
                    for subnode in ast.walk(item):
                        if isinstance(subnode, ast.Constant) and isinstance(subnode.value, str):
                            all_strings.append(subnode.value)

                    # Check for required arguments
                    for s in all_strings:
                        if "--dtype=float16" in s:
                            found_dtype = True
                        if "--chunked-prefill-size" in s:
                            found_chunked = True
                        if s == "1024":
                            found_1024 = True

    assert found_dtype, "Must add '--dtype=float16' argument to launch_args"
    assert found_chunked, "Must add '--chunked-prefill-size' argument to launch_args"
    assert found_1024, "Must add '1024' as chunked-prefill-size value"


# [pr_diff] fail_to_pass
def test_env_override_added():
    """SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN env override must be added - BEHAVIORAL via AST check."""
    tree = _parse_target_ast()

    # Check that the environment variable is used with override in the context manager
    found_env_var = False
    found_override_call = False

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "TestEagle3ServerBase":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "setUpClass":
                    for subnode in ast.walk(item):
                        # Check for attribute access to the env var
                        if isinstance(subnode, ast.Attribute):
                            if subnode.attr == "SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN":
                                found_env_var = True
                            if subnode.attr == "override":
                                found_override_call = True

    assert found_env_var, "Must use SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN env variable"
    assert found_override_call, "Must call override() on env variable"


# [pr_diff] fail_to_pass
def test_name_updated():
    """Test print statement must use TestEagle3LargeBS - BEHAVIORAL via AST check."""
    tree = _parse_target_ast()

    # Find the test_gsm8k method and check the print statement
    found_new_name = False
    found_old_name = False

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "test_gsm8k":
            for subnode in ast.walk(node):
                if isinstance(subnode, ast.Constant) and isinstance(subnode.value, str):
                    if "TestEagle3LargeBS" in subnode.value:
                        found_new_name = True
                    if "TestEagleLargeBS" in subnode.value:
                        found_old_name = True

    assert found_new_name, "Must use 'TestEagle3LargeBS' in print statement"
    assert not found_old_name, "Must not use old 'TestEagleLargeBS' name"


# [pr_diff] fail_to_pass
def test_score_threshold_updated():
    """Score threshold must be updated from 0.22 to 0.7 - BEHAVIORAL via AST check."""
    tree = _parse_target_ast()

    # Find the assertGreater call in test_gsm8k
    found_07 = False
    found_022 = False

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "test_gsm8k":
            for subnode in ast.walk(node):
                if isinstance(subnode, ast.Constant):
                    if isinstance(subnode.value, (int, float)):
                        if abs(subnode.value - 0.7) < 0.01:
                            found_07 = True
                        if abs(subnode.value - 0.22) < 0.01:
                            found_022 = True

    assert found_07, "Must use score threshold 0.7 in assertGreater"
    assert not found_022, "Must not use old threshold 0.22"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub verification
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """Modified file is not a stub (has real test logic)."""
    src = Path(TARGET_FILE).read_text()
    tree = ast.parse(src)

    # Check that class has meaningful methods (not just pass)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "TestEagle3ServerBase":
            methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
            assert len(methods) >= 2, "TestEagle3ServerBase must have at least 2 methods"

            # Check setUpClass has meaningful content
            setup_methods = [m for m in methods if m.name == "setUpClass"]
            if setup_methods:
                body = [s for s in setup_methods[0].body if not isinstance(s, (ast.Pass, ast.Expr))]
                assert len(body) >= 3, "setUpClass must have meaningful implementation"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD verification
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_syntax_py_compile():
    """Target file compiles without syntax errors (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "py_compile", TARGET_FILE],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Python syntax check failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_test_directory_syntax():
    """All Python files in test/registered/spec/eagle compile (pass_to_pass)."""
    eagle_dir = Path(REPO) / "test" / "registered" / "spec" / "eagle"
    failed = []

    for pyfile in eagle_dir.glob("*.py"):
        r = subprocess.run(
            ["python3", "-m", "py_compile", str(pyfile)],
            capture_output=True, text=True, timeout=60, cwd=REPO,
        )
        if r.returncode != 0:
            failed.append(f"{pyfile.name}: {r.stderr[:200]}")

    assert not failed, f"Syntax errors found:\n" + "\n".join(failed[:5])


# [repo_tests] pass_to_pass
def test_repo_python_sglang_syntax():
    """Sample of Python files in python/sglang compile (pass_to_pass)."""
    # Check a representative sample of Python files
    sample_files = [
        "python/sglang/srt/utils.py",
        "python/sglang/srt/managers/io_struct.py",
        "python/sglang/srt/configs/model_config.py",
        "python/sglang/test/test_utils.py",
        "python/sglang/check_env.py",
    ]

    failed = []
    for rel_path in sample_files:
        full_path = Path(REPO) / rel_path
        if not full_path.exists():
            continue
        r = subprocess.run(
            ["python3", "-m", "py_compile", str(full_path)],
            capture_output=True, text=True, timeout=60, cwd=REPO,
        )
        if r.returncode != 0:
            failed.append(f"{rel_path}: {r.stderr[:200]}")

    assert not failed, f"Syntax errors found:\n" + "\n".join(failed)


# [repo_tests] pass_to_pass
def test_repo_related_eagle_tests_syntax():
    """Related EAGLE test files compile (pass_to_pass)."""
    # These files are related to the target and should all compile
    related_files = [
        "test/registered/spec/eagle/test_eagle3_basic.py",
        "test/registered/spec/eagle/test_eagle_infer_a.py",
        "test/registered/spec/eagle/test_eagle_infer_b.py",
        "test/registered/spec/eagle/test_eagle_constrained_decoding.py",
        "test/registered/spec/eagle/test_eagle_dp_attention.py",
    ]

    failed = []
    for rel_path in related_files:
        full_path = Path(REPO) / rel_path
        if not full_path.exists():
            continue
        r = subprocess.run(
            ["python3", "-m", "py_compile", str(full_path)],
            capture_output=True, text=True, timeout=60, cwd=REPO,
        )
        if r.returncode != 0:
            failed.append(f"{rel_path}: {r.stderr[:200]}")

    assert not failed, f"Syntax errors found:\n" + "\n".join(failed)


# [repo_tests] pass_to_pass
def test_repo_test_utils_syntax():
    """Test utilities module compiles (pass_to_pass)."""
    # The target file imports from test_utils, so this is a key dependency
    test_utils = Path(REPO) / "python" / "sglang" / "test" / "test_utils.py"
    if test_utils.exists():
        r = subprocess.run(
            ["python3", "-m", "py_compile", str(test_utils)],
            capture_output=True, text=True, timeout=60, cwd=REPO,
        )
        assert r.returncode == 0, f"test_utils.py syntax check failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_target_file_ast_parse():
    """Target file can be parsed for AST analysis (pass_to_pass)."""
    r = subprocess.run(
        [
            "python3", "-c",
            f"import ast; ast.parse(open('{TARGET_FILE}').read())"
        ],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"AST parse failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_workflow_job_names():
    """Workflow job names are unique across workflows (pass_to_pass)."""
    # Install pyyaml if needed and run the check
    r = subprocess.run(
        ["pip", "install", "pyyaml", "--quiet"],
        capture_output=True, text=True, timeout=60,
    )
    r = subprocess.run(
        ["python3", "scripts/ci/check_workflow_job_names.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Workflow job names check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_codespell():
    """Target file passes codespell check (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "codespell", "--quiet"],
        capture_output=True, text=True, timeout=60,
    )
    r = subprocess.run(
        ["codespell", "--config", ".codespellrc", TARGET_FILE],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Codespell check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_eagle_test_imports():
    """EAGLE test dependencies can be imported (pass_to_pass)."""
    # Check that key test dependencies are importable
    r = subprocess.run(
        [
            "python3", "-c",
            "from sglang.test.test_utils import ("
            "DEFAULT_DRAFT_MODEL_EAGLE, DEFAULT_TARGET_MODEL_EAGLE, "
            "DEFAULT_DRAFT_MODEL_EAGLE3, DEFAULT_TARGET_MODEL_EAGLE3, "
            "CustomTestCase, DEFAULT_TIMEOUT_FOR_SERVER_LAUNCH, "
            "DEFAULT_URL_FOR_TEST, popen_launch_server)"
        ],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"EAGLE test imports failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_test_kits_importable():
    """Test kits modules are importable (pass_to_pass)."""
    r = subprocess.run(
        [
            "python3", "-c",
            "from sglang.test.kits.matched_stop_kit import MatchedStopMixin; "
            "from sglang.test.kits.radix_cache_server_kit import run_radix_attention_test"
        ],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Test kits import failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_black_format():
    """Target file passes black format check (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "black", "--quiet"],
        capture_output=True, text=True, timeout=60,
    )
    r = subprocess.run(
        ["black", "--check", TARGET_FILE],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Black format check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_isort_check():
    """Target file passes isort import ordering check (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "isort", "--quiet"],
        capture_output=True, text=True, timeout=60,
    )
    r = subprocess.run(
        ["isort", "--check", TARGET_FILE],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"isort check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_precommit_hooks_yaml():
    """GitHub workflow YAML files pass pre-commit check-yaml (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "pyyaml", "--quiet"],
        capture_output=True, text=True, timeout=60,
    )
    # Use the check-yaml hook approach from pre-commit
    yaml_files = [
        ".github/workflows/lint.yml",
    ]
    failed = []
    for rel_path in yaml_files:
        full_path = Path(REPO) / rel_path
        if not full_path.exists():
            continue
        r = subprocess.run(
            ["python3", "-c", f"import yaml; yaml.safe_load(open('{full_path}'))"],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        if r.returncode != 0:
            failed.append(f"{rel_path}: {r.stderr[:200]}")
    assert not failed, f"YAML validation errors:\n" + "\n".join(failed)
