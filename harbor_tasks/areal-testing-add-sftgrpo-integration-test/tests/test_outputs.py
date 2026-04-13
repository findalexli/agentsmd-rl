"""
Task: areal-testing-add-sftgrpo-integration-test
Repo: inclusionAI/AReaL @ d64f8688833cd73648a1b06932f1fbec542694e3
PR:   726

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/AReaL"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_grpo_parametrized_with_megatron():
    """test_grpo is parametrized with @pytest.mark.parametrize for fsdp and megatron."""
    r = subprocess.run(
        ["python3", "-c", """
import ast

source = open('areal/tests/grpo/test_grpo.py').read()
tree = ast.parse(source)

found = False
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'test_grpo':
        found = True
        # Check 'backend' is in function parameters
        param_names = [a.arg for a in node.args.args]
        assert 'backend' in param_names, (
            f"test_grpo missing 'backend' parameter, has: {param_names}"
        )
        # Check for @pytest.mark.parametrize decorator with both backends
        has_parametrize = False
        for dec in node.decorator_list:
            if not isinstance(dec, ast.Call):
                continue
            func = dec.func
            # Match pytest.mark.parametrize(...)
            if not (hasattr(func, 'attr') and func.attr == 'parametrize'):
                continue
            if not dec.args or not isinstance(dec.args[0], ast.Constant):
                continue
            if dec.args[0].value != 'backend':
                continue
            if len(dec.args) > 1 and isinstance(dec.args[1], ast.List):
                values = [e.value for e in dec.args[1].elts if isinstance(e, ast.Constant)]
                if 'fsdp' in values and 'megatron' in values:
                    has_parametrize = True
        assert has_parametrize, "test_grpo missing @pytest.mark.parametrize with fsdp+megatron"
        break

assert found, "test_grpo function not found in test_grpo.py"
print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_sft_parametrized_with_megatron():
    """test_sft is parametrized with @pytest.mark.parametrize for fsdp and megatron."""
    r = subprocess.run(
        ["python3", "-c", """
import ast

source = open('areal/tests/sft/test_sft.py').read()
tree = ast.parse(source)

found = False
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'test_sft':
        found = True
        param_names = [a.arg for a in node.args.args]
        assert 'backend' in param_names, (
            f"test_sft missing 'backend' parameter, has: {param_names}"
        )
        has_parametrize = False
        for dec in node.decorator_list:
            if not isinstance(dec, ast.Call):
                continue
            func = dec.func
            if not (hasattr(func, 'attr') and func.attr == 'parametrize'):
                continue
            if not dec.args or not isinstance(dec.args[0], ast.Constant):
                continue
            if dec.args[0].value != 'backend':
                continue
            if len(dec.args) > 1 and isinstance(dec.args[1], ast.List):
                values = [e.value for e in dec.args[1].elts if isinstance(e, ast.Constant)]
                if 'fsdp' in values and 'megatron' in values:
                    has_parametrize = True
        assert has_parametrize, "test_sft missing @pytest.mark.parametrize with fsdp+megatron"
        break

assert found, "test_sft function not found in test_sft.py"
print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_megatron_grpo_config_exists():
    """config_megatron.yaml exists for GRPO with megatron in allocation_mode."""
    r = subprocess.run(
        ["python3", "-c", """
import os

config_path = 'areal/tests/grpo/config_megatron.yaml'
assert os.path.isfile(config_path), f"{config_path} does not exist"

content = open(config_path).read()
assert 'allocation_mode:' in content, "Missing allocation_mode key"
assert 'megatron' in content, "allocation_mode does not contain 'megatron'"
assert 'experiment_name: tests-grpo' in content, "experiment_name should be tests-grpo"
print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_megatron_sft_config_exists():
    """config_megatron.yaml exists for SFT with megatron allocation_mode."""
    r = subprocess.run(
        ["python3", "-c", """
import os

config_path = 'areal/tests/sft/config_megatron.yaml'
assert os.path.isfile(config_path), f"{config_path} does not exist"

content = open(config_path).read()
assert 'allocation_mode:' in content, "Missing allocation_mode key"
assert 'megatron' in content, "allocation_mode does not contain 'megatron'"
assert 'experiment_name: tests-sft' in content, "experiment_name should be tests-sft"
print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_megatron_sft_ref_losses():
    """ref_losses_megatron.json exists with 16 float loss values."""
    r = subprocess.run(
        ["python3", "-c", """
import json, os

ref_path = 'areal/tests/sft/ref_losses_megatron.json'
assert os.path.isfile(ref_path), f"{ref_path} does not exist"

with open(ref_path) as f:
    losses = json.load(f)

assert isinstance(losses, list), f"Expected list, got {type(losses).__name__}"
assert len(losses) == 16, f"Expected 16 entries, got {len(losses)}"
assert all(isinstance(v, float) for v in losses), "All entries must be floats"
assert all(0.0 < v < 10.0 for v in losses), "Loss values should be between 0 and 10"
print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_grpo_uses_backend_config_path():
    """test_grpo.py loads config via config_{backend}.yaml pattern, not config.yaml."""
    r = subprocess.run(
        ["python3", "-c", """
source = open('areal/tests/grpo/test_grpo.py').read()

# The fixed version should reference config_{backend}.yaml pattern
assert 'config_{backend}' in source or 'config_' + '{backend}' in source or 'f"config_{backend}.yaml"' in source, (
    "test_grpo.py should reference config_{backend}.yaml"
)

# The old hardcoded config.yaml reference should be gone from the load_expr_config call
# (it may appear in comments or test fixture code, but not as the active config path)
lines = source.splitlines()
for line in lines:
    stripped = line.strip()
    if stripped.startswith('#'):
        continue
    # Skip test fixture code (creating mock files in tmp_path)
    if 'tmp_path' in stripped and 'config.yaml' in stripped:
        continue
    if 'load_expr_config' in stripped or ('config.yaml' in stripped and 'config_' not in stripped):
        if '"config.yaml"' in stripped or "'config.yaml'" in stripped:
            assert False, f"test_grpo.py still loads hardcoded config.yaml: {stripped}"

print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — syntax / structural checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_python_files_parse():
    """Modified test Python files parse without syntax errors."""
    r = subprocess.run(
        ["python3", "-c", """
import ast

for path in [
    'areal/tests/grpo/test_grpo.py',
    'areal/tests/sft/test_sft.py',
]:
    with open(path) as f:
        source = f.read()
    ast.parse(source, filename=path)
    print(f"OK: {path}")
print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — repo CI/CD checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_ruff_lint():
    """Repo's Python linting passes on modified files (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True, text=True, timeout=60,
    )
    # Install may fail if already installed, ignore

    r = subprocess.run(
        ["ruff", "check", "areal/tests/grpo/test_grpo.py", "areal/tests/sft/test_sft.py",
         "--select", "E,W,F", "--ignore", "E501"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff lint failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_python_syntax():
    """Modified Python files have valid syntax (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "py_compile", "areal/tests/grpo/test_grpo.py", "areal/tests/sft/test_sft.py"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Python syntax check failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_yaml_valid():
    """YAML configs are syntactically valid (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "pyyaml", "-q"],
        capture_output=True, text=True, timeout=60,
    )

    r = subprocess.run(
        ["python3", "-c", """
import yaml
import os

# Check YAML configs - works on both base (config.yaml) and after fix (config_fsdp.yaml)
configs = [
    "areal/tests/grpo/config.yaml",  # base commit
    "areal/tests/grpo/config_fsdp.yaml",  # after fix
    "areal/tests/sft/config.yaml",  # base commit
    "areal/tests/sft/config_fsdp.yaml",  # after fix
]
found_any = False
for path in configs:
    if os.path.exists(path):
        with open(path) as f:
            yaml.safe_load(f.read())
        print(f"OK: {path}")
        found_any = True
if not found_any:
    print("ERROR: No config files found")
    exit(1)
print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"YAML validation failed:\n{r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — additional CI/CD checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_precommit_check_yaml():
    """Pre-commit check-yaml hook passes on config files (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "pre-commit", "pyyaml", "-q"],
        capture_output=True, text=True, timeout=120,
    )

    # Initialize git if needed
    subprocess.run(
        ["git", "init", "-q"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )

    # Check YAML files using pre-commit hook
    r = subprocess.run(
        ["pre-commit", "run", "check-yaml", "--files",
         "areal/tests/grpo/config.yaml", "areal/tests/sft/config.yaml"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"check-yaml hook failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_precommit_check_json():
    """Pre-commit check-json hook passes on JSON files (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "pre-commit", "-q"],
        capture_output=True, text=True, timeout=120,
    )

    # Initialize git if needed
    subprocess.run(
        ["git", "init", "-q"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )

    # Check JSON files using pre-commit hook
    r = subprocess.run(
        ["pre-commit", "run", "check-json", "--files",
         "areal/tests/sft/ref_losses.json"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"check-json hook failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_precommit_trailing_whitespace():
    """Pre-commit trailing-whitespace hook passes on modified files (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "pre-commit", "-q"],
        capture_output=True, text=True, timeout=120,
    )

    # Initialize git if needed
    subprocess.run(
        ["git", "init", "-q"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )

    # Check trailing whitespace using pre-commit hook
    r = subprocess.run(
        ["pre-commit", "run", "trailing-whitespace", "--files",
         "areal/tests/grpo/test_grpo.py", "areal/tests/sft/test_sft.py"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"trailing-whitespace hook failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_precommit_end_of_file():
    """Pre-commit end-of-file-fixer hook passes on modified files (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "pre-commit", "-q"],
        capture_output=True, text=True, timeout=120,
    )

    # Initialize git if needed
    subprocess.run(
        ["git", "init", "-q"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )

    # Check end-of-file using pre-commit hook
    r = subprocess.run(
        ["pre-commit", "run", "end-of-file-fixer", "--files",
         "areal/tests/grpo/test_grpo.py", "areal/tests/sft/test_sft.py"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"end-of-file-fixer hook failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_ruff_format():
    """Repo's Python formatting passes on modified files (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff==0.14.1", "-q"],
        capture_output=True, text=True, timeout=60,
    )

    r = subprocess.run(
        ["ruff", "format", "--check", "areal/tests/grpo/test_grpo.py", "areal/tests/sft/test_sft.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_clang_format():
    """C++ source files are properly formatted (pass_to_pass)."""
    # Install clang-format if not present
    r = subprocess.run(
        ["apt-get", "update"],
        capture_output=True, text=True, timeout=60,
    )
    r = subprocess.run(
        ["apt-get", "install", "-y", "--no-install-recommends", "clang-format"],
        capture_output=True, text=True, timeout=120,
    )

    # Find and check C++ files
    r = subprocess.run(
        ["bash", "-c", """
find csrc -type f \( -name '*.c' -o -name '*.h' -o -name '*.cpp' -o -name '*.hpp' -o -name '*.cu' -o -name '*.cuh' \) -exec clang-format --dry-run --Werror {} +
"""],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"clang-format check failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_json_valid():
    """JSON reference files are syntactically valid (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
import json
import os

# Check JSON reference files
json_files = [
    "areal/tests/sft/ref_losses.json",  # base commit
    "areal/tests/sft/ref_losses_fsdp.json",  # after fix
    "areal/tests/sft/ref_losses_megatron.json",  # after fix
]
found_any = False
for path in json_files:
    if os.path.exists(path):
        with open(path) as f:
            json.load(f)
        print(f"OK: {path}")
        found_any = True
if not found_any:
    print("ERROR: No JSON files found")
    exit(1)
print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"JSON validation failed:\n{r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [repo_tests] pass_to_pass
def test_repo_imports():
    """Modified test files can be imported without errors (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
import ast
import sys

# Check that the modified files can be parsed and basic imports work
files = [
    "areal/tests/grpo/test_grpo.py",
    "areal/tests/sft/test_sft.py",
]
for path in files:
    with open(path) as f:
        source = f.read()
    # Parse to AST
    tree = ast.parse(source, filename=path)
    # Check for test function definitions
    test_funcs = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name.startswith('test_')]
    print(f"{path}: found {len(test_funcs)} test functions")
    if not test_funcs:
        print(f"ERROR: No test functions found in {path}")
        sys.exit(1)
print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Import check failed:\n{r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — AGENTS.md:261 @ d64f8688833cd73648a1b06932f1fbec542694e3
def test_config_uses_parametrize():
    """AGENTS.md L261: Prefer pytest.mark.parametrize over ad-hoc loops for test variants."""
    r = subprocess.run(
        ["python3", "-c", """
import ast, re

for test_file in [
    'areal/tests/grpo/test_grpo.py',
    'areal/tests/sft/test_sft.py',
]:
    source = open(test_file).read()
    tree = ast.parse(source)

    # Find test functions
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        if not node.name.startswith('test_'):
            continue

        # If the function handles multiple backends, it must use parametrize
        # (not a for loop over backends inside the function body)
        has_for_over_backends = False
        for child in ast.walk(node):
            if isinstance(child, ast.For):
                # Check if iterating over a list of strings like ["fsdp", "megatron"]
                if isinstance(child.iter, ast.List):
                    vals = [e.value for e in child.iter.elts if isinstance(e, ast.Constant) and isinstance(e.value, str)]
                    if 'fsdp' in vals and 'megatron' in vals:
                        has_for_over_backends = True

        assert not has_for_over_backends, (
            f"{test_file}:{node.name} uses a for loop over backends instead of "
            f"@pytest.mark.parametrize as required by AGENTS.md"
        )

    # Verify parametrize is used for backend variation
    assert 'parametrize' in source, (
        f"{test_file} should use pytest.mark.parametrize per AGENTS.md:261"
    )

print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout
