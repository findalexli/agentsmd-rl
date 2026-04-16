"""
Task: areal-testing-add-sftgrpo-integration-test
Repo: inclusionAI/AReaL @ d64f8688833cd73648a1b06932f1fbec542694e3
PR:   726

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import json
import os
import subprocess
import sys

REPO = "/workspace/AReaL"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - core behavioral tests
# ---------------------------------------------------------------------------

def test_grpo_parametrized_with_megatron():
    """test_grpo is parametrized with @pytest.mark.parametrize for backends."""
    r = subprocess.run(
        ["python3", "-c", """
import ast

source = open('areal/tests/grpo/test_grpo.py').read()
tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'test_grpo':
        has_parametrize = False
        for dec in node.decorator_list:
            if isinstance(dec, ast.Call):
                func = dec.func
                if hasattr(func, 'attr') and func.attr == 'parametrize':
                    if dec.args and len(dec.args) >= 2:
                        arg = dec.args[1]
                        if isinstance(arg, (ast.List, ast.Tuple)):
                            if len(arg.elts) >= 2:
                                has_parametrize = True
        assert has_parametrize, "test_grpo missing @pytest.mark.parametrize with multiple backends"
        print("PASS")
        break
else:
    raise AssertionError("test_grpo function not found")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


def test_sft_parametrized_with_megatron():
    """test_sft is parametrized with @pytest.mark.parametrize for backends."""
    r = subprocess.run(
        ["python3", "-c", """
import ast

source = open('areal/tests/sft/test_sft.py').read()
tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'test_sft':
        has_parametrize = False
        for dec in node.decorator_list:
            if isinstance(dec, ast.Call):
                func = dec.func
                if hasattr(func, 'attr') and func.attr == 'parametrize':
                    if dec.args and len(dec.args) >= 2:
                        arg = dec.args[1]
                        if isinstance(arg, (ast.List, ast.Tuple)):
                            if len(arg.elts) >= 2:
                                has_parametrize = True
        assert has_parametrize, "test_sft missing @pytest.mark.parametrize with multiple backends"
        print("PASS")
        break
else:
    raise AssertionError("test_sft function not found")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


def test_megatron_grpo_config_exists():
    """config_megatron.yaml exists for GRPO with megatron allocation_mode."""
    r = subprocess.run(
        ["python3", "-c", """
import os
import yaml

config_path = 'areal/tests/grpo/config_megatron.yaml'
assert os.path.isfile(config_path), f"{config_path} does not exist"

with open(config_path) as f:
    config = yaml.safe_load(f)

assert "allocation_mode" in config
assert "megatron" in config["allocation_mode"].lower()
assert config.get("experiment_name") == "tests-grpo"
print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


def test_megatron_sft_config_exists():
    """config_megatron.yaml exists for SFT with megatron allocation_mode."""
    r = subprocess.run(
        ["python3", "-c", """
import os
import yaml

config_path = 'areal/tests/sft/config_megatron.yaml'
assert os.path.isfile(config_path), f"{config_path} does not exist"

with open(config_path) as f:
    config = yaml.safe_load(f)

assert "allocation_mode" in config
assert "megatron" in config["allocation_mode"].lower()
assert config.get("experiment_name") == "tests-sft"
print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


def test_megatron_sft_ref_losses():
    """ref_losses_megatron.json exists with 16 float loss values."""
    r = subprocess.run(
        ["python3", "-c", """
import json
import os

ref_path = 'areal/tests/sft/ref_losses_megatron.json'
assert os.path.isfile(ref_path)
with open(ref_path) as f:
    losses = json.load(f)
assert isinstance(losses, list)
assert len(losses) == 16
assert all(isinstance(v, (int, float)) for v in losses)
for i, v in enumerate(losses):
    assert 0.0 < v < 10.0, f"loss[{i}]={v} outside (0, 10)"
print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


def test_grpo_uses_backend_config_path():
    """test_grpo.py loads config via backend-dependent path pattern."""
    r = subprocess.run(
        ["python3", "-c", """
import ast

source = open('areal/tests/grpo/test_grpo.py').read()
tree = ast.parse(source)

found = False
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'test_grpo':
        if 'config_{backend}' in source or 'config_" + "backend' in source or 'f"config_{backend}' in source:
            found = True
if not found:
    raise AssertionError("test_grpo.py does not use backend-dependent config path")
print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


def test_config_uses_parametrize():
    """AGENTS.md L261: Prefer pytest.mark.parametrize over ad-hoc loops for test variants."""
    r = subprocess.run(
        ["python3", "-c", """
import ast

for test_file in ['areal/tests/grpo/test_grpo.py', 'areal/tests/sft/test_sft.py']:
    source = open(test_file).read()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        if not node.name.startswith('test_'):
            continue

        has_parametrize = False
        for dec in node.decorator_list:
            if isinstance(dec, ast.Call):
                func = dec.func
                if hasattr(func, 'attr') and func.attr == 'parametrize':
                    if dec.args and len(dec.args) >= 2:
                        arg = dec.args[1]
                        if isinstance(arg, (ast.List, ast.Tuple)):
                            if len(arg.elts) >= 2:
                                has_parametrize = True

        assert has_parametrize, f"{test_file}:{node.name} does not use parametrize"

print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (static) - syntax / structural checks
# ---------------------------------------------------------------------------

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
# Pass-to-pass (repo_tests) - repo CI/CD checks
# ---------------------------------------------------------------------------

def test_repo_ruff_lint():
    """Repo's Python linting passes on modified files (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True, text=True, timeout=60,
    )
    r = subprocess.run(
        ["ruff", "check", "areal/tests/grpo/test_grpo.py", "areal/tests/sft/test_sft.py",
         "--select", "E,W,F", "--ignore", "E501"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff lint failed:\n{r.stdout}\n{r.stderr}"


def test_repo_python_syntax():
    """Modified Python files have valid syntax (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "py_compile", "areal/tests/grpo/test_grpo.py", "areal/tests/sft/test_sft.py"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Python syntax check failed:\n{r.stderr}"


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

config_dir = os.path.join(os.getcwd(), 'areal/tests')
for subdir in ['grpo', 'sft']:
    subdir_path = os.path.join(config_dir, subdir)
    if os.path.isdir(subdir_path):
        for fname in os.listdir(subdir_path):
            if fname.endswith('.yaml') or fname.endswith('.yml'):
                fpath = os.path.join(subdir_path, fname)
                with open(fpath) as f:
                    yaml.safe_load(f.read())
                print(f"OK: {fpath}")
print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"YAML validation failed:\n{r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


def test_precommit_check_yaml():
    """Pre-commit check-yaml hook passes on config files (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "pre-commit", "pyyaml", "-q"],
        capture_output=True, text=True, timeout=120,
    )
    subprocess.run(
        ["git", "init", "-q"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    r = subprocess.run(
        ["pre-commit", "run", "check-yaml", "--files",
         "areal/tests/grpo/config.yaml", "areal/tests/sft/config.yaml"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"check-yaml hook failed:\n{r.stdout}\n{r.stderr}"


def test_precommit_check_json():
    """Pre-commit check-json hook passes on JSON files (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "pre-commit", "-q"],
        capture_output=True, text=True, timeout=120,
    )
    subprocess.run(
        ["git", "init", "-q"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    r = subprocess.run(
        ["pre-commit", "run", "check-json", "--files",
         "areal/tests/sft/ref_losses.json"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"check-json hook failed:\n{r.stdout}\n{r.stderr}"


def test_precommit_trailing_whitespace():
    """Pre-commit trailing-whitespace hook passes on modified files (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "pre-commit", "-q"],
        capture_output=True, text=True, timeout=120,
    )
    subprocess.run(
        ["git", "init", "-q"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    r = subprocess.run(
        ["pre-commit", "run", "trailing-whitespace", "--files",
         "areal/tests/grpo/test_grpo.py", "areal/tests/sft/test_sft.py"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"trailing-whitespace hook failed:\n{r.stdout}\n{r.stderr}"


def test_precommit_end_of_file():
    """Pre-commit end-of-file-fixer hook passes on modified files (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "pre-commit", "-q"],
        capture_output=True, text=True, timeout=120,
    )
    subprocess.run(
        ["git", "init", "-q"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    r = subprocess.run(
        ["pre-commit", "run", "end-of-file-fixer", "--files",
         "areal/tests/grpo/test_grpo.py", "areal/tests/sft/test_sft.py"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"end-of-file-fixer hook failed:\n{r.stdout}\n{r.stderr}"


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


def test_repo_clang_format():
    """C++ source files are properly formatted (pass_to_pass)."""
    r = subprocess.run(
        ["apt-get", "update"],
        capture_output=True, text=True, timeout=60,
    )
    r = subprocess.run(
        ["apt-get", "install", "-y", "--no-install-recommends", "clang-format"],
        capture_output=True, text=True, timeout=120,
    )
    r = subprocess.run(
        ["bash", "-c",
         r"find csrc -type f \( -name '*.c' -o -name '*.h' -o -name '*.cpp' -o -name '*.hpp' -o -name '*.cu' -o -name '*.cuh' \) -exec clang-format --dry-run --Werror {} +"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"clang-format check failed:\n{r.stderr}"


def test_repo_json_valid():
    """JSON reference files are syntactically valid (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
import json
import os

json_dir = os.path.join(os.getcwd(), 'areal/tests/sft')
found_any = False
if os.path.isdir(json_dir):
    for fname in os.listdir(json_dir):
        if fname.startswith('ref_losses') and fname.endswith('.json'):
            fpath = os.path.join(json_dir, fname)
            with open(fpath) as f:
                json.load(f)
            print(f"OK: {fpath}")
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


def test_repo_imports():
    """Modified test files can be imported without errors (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
import ast
import sys

files = [
    "areal/tests/grpo/test_grpo.py",
    "areal/tests/sft/test_sft.py",
]
for path in files:
    with open(path) as f:
        source = f.read()
    tree = ast.parse(source, filename=path)
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
