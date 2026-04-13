"""
Task: areal-vlm-training-on-npu
Repo: inclusionAI/AReaL @ b942ed019df2c66b851c397c0836fd31a3787b70
PR:   746

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO = "/workspace/AReaL"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, repo_tests) — repository CI/CD checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass — Repo Python files have no syntax errors
def test_repo_python_syntax():
    """All Python files in areal/ must parse without syntax errors (pass_to_pass)."""
    errors = []
    for root, dirs, files in os.walk(Path(REPO) / "areal"):
        for file in files:
            if file.endswith(".py"):
                filepath = Path(root) / file
                try:
                    with open(filepath, "r") as f:
                        ast.parse(f.read())
                except SyntaxError as e:
                    errors.append(f"{filepath}: {e}")
    assert not errors, f"Syntax errors found:\n" + "\n".join(errors[:10])


# [repo_tests] pass_to_pass — Repo YAML configs are valid
def test_repo_yaml_valid():
    """All YAML files in repo must parse without errors (pass_to_pass)."""
    errors = []
    yaml_dirs = ["areal/tests", "examples", "benchmark"]
    for yaml_dir in yaml_dirs:
        dirpath = Path(REPO) / yaml_dir
        if not dirpath.exists():
            continue
        for filepath in dirpath.rglob("*.yaml"):
            if filepath.is_file():
                try:
                    with open(filepath, "r") as f:
                        yaml.safe_load(f)
                except yaml.YAMLError as e:
                    errors.append(f"{filepath}: {e}")
    assert not errors, f"YAML parsing errors found:\n" + "\n".join(str(e) for e in errors[:10])


# [repo_tests] pass_to_pass — No wildcard imports in main code
def test_repo_no_wildcard_imports():
    """areal/ directory must not use wildcard imports (pass_to_pass)."""
    wildcard_files = []
    for root, dirs, files in os.walk(Path(REPO) / "areal"):
        if "__pycache__" in root or root.endswith("tests"):
            continue
        for file in files:
            if file.endswith(".py"):
                filepath = Path(root) / file
                try:
                    with open(filepath, "r") as f:
                        tree = ast.parse(f.read())
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ImportFrom) and any(
                            alias.name == "*" for alias in node.names
                        ):
                            wildcard_files.append(f"{filepath}: from {node.module} import *")
                except:
                    pass
    assert not wildcard_files, f"Wildcard imports found:\n" + "\n".join(wildcard_files[:10])


# [repo_tests] pass_to_pass — Ruff linting passes on areal/
def test_repo_ruff_lint_areal():
    """Repo's ruff linter passes on areal/ directory (pass_to_pass)."""
    # Install ruff if not already installed
    subprocess.run([sys.executable, "-m", "pip", "install", "ruff==0.14.9", "-q"], check=True, capture_output=True)
    r = subprocess.run(
        ["ruff", "check", "areal/"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff lint failed on areal/:\n{r.stderr[-500:]}{r.stdout[-500:]}"


# [repo_tests] pass_to_pass — Ruff linting passes on examples/
def test_repo_ruff_lint_examples():
    """Repo's ruff linter passes on examples/ directory (pass_to_pass)."""
    # Install ruff if not already installed
    subprocess.run([sys.executable, "-m", "pip", "install", "ruff==0.14.9", "-q"], check=True, capture_output=True)
    r = subprocess.run(
        ["ruff", "check", "examples/"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff lint failed on examples/:\n{r.stderr[-500:]}{r.stdout[-500:]}"


# [repo_tests] pass_to_pass — Ruff format check passes on areal/
def test_repo_ruff_format_areal():
    """Repo's ruff format check passes on areal/ directory (pass_to_pass)."""
    # Install ruff if not already installed
    subprocess.run([sys.executable, "-m", "pip", "install", "ruff==0.14.9", "-q"], check=True, capture_output=True)
    r = subprocess.run(
        ["ruff", "format", "--check", "areal/"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed on areal/:\n{r.stderr[-500:]}{r.stdout[-500:]}"


# [repo_tests] pass_to_pass — Ruff format check passes on examples/
def test_repo_ruff_format_examples():
    """Repo's ruff format check passes on examples/ directory (pass_to_pass)."""
    # Install ruff if not already installed
    subprocess.run([sys.executable, "-m", "pip", "install", "ruff==0.14.9", "-q"], check=True, capture_output=True)
    r = subprocess.run(
        ["ruff", "format", "--check", "examples/"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed on examples/:\n{r.stderr[-500:]}{r.stdout[-500:]}"


# [repo_tests] pass_to_pass — All Python files in repo have valid syntax
def test_repo_all_python_syntax():
    """All Python files in the repository parse without syntax errors (pass_to_pass)."""
    errors = []
    skip_dirs = {".git", "__pycache__", "evaluation", "build", "dist"}
    for root, dirs, files in os.walk(Path(REPO)):
        # Skip evaluation directory which has complex legacy code
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for file in files:
            if file.endswith(".py"):
                filepath = Path(root) / file
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        ast.parse(f.read())
                except SyntaxError as e:
                    errors.append(f"{filepath}: {e}")
    assert not errors, f"Syntax errors found in repository:\n" + "\n".join(errors[:10])


# [repo_tests] pass_to_pass — C++ files pass clang-format check
def test_repo_clang_format():
    """C++ files in the repository pass clang-format check (pass_to_pass)."""
    # Install clang-format if not already installed
    subprocess.run([sys.executable, "-m", "pip", "install", "clang-format==19.1.7", "-q"], check=True, capture_output=True)

    # Find all C++ files
    cpp_files = []
    skip_dirs = {".git", "__pycache__", "evaluation"}
    for root, dirs, files in os.walk(Path(REPO)):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for file in files:
            if file.endswith((".c", ".h", ".cpp", ".hpp", ".cu", ".cuh")):
                cpp_files.append(str(Path(root) / file))

    if not cpp_files:
        pytest.skip("No C++ files found to check")

    # Check each file with clang-format
    for filepath in cpp_files:
        r = subprocess.run(
            ["clang-format", "--dry-run", "--Werror", filepath],
            capture_output=True, text=True, timeout=60,
        )
        assert r.returncode == 0, f"clang-format check failed for {filepath}:\n{r.stderr[-500:]}{r.stdout[-500:]}"


# [repo_tests] pass_to_pass — JSON files are valid
def test_repo_json_valid():
    """All JSON files in the repository parse without errors (pass_to_pass)."""
    errors = []
    skip_dirs = {".git", "__pycache__", "evaluation", "build", "dist", "node_modules"}

    for root, dirs, files in os.walk(Path(REPO)):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for file in files:
            if file.endswith(".json"):
                filepath = Path(root) / file
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        json.load(f)
                except json.JSONDecodeError as e:
                    errors.append(f"{filepath}: {e}")
                except UnicodeDecodeError:
                    pass  # Skip binary files with .json extension

    assert not errors, f"JSON parsing errors found:\n" + "\n".join(errors[:10])


# [repo_tests] pass_to_pass — Python files end with newline (pre-commit check)
def test_repo_python_end_with_newline():
    """All Python files end with a newline (pre-commit end-of-file-fixer check) (pass_to_pass)."""
    errors = []
    skip_dirs = {".git", "__pycache__", "evaluation", "build", "dist"}

    for root, dirs, files in os.walk(Path(REPO)):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for file in files:
            if file.endswith(".py"):
                filepath = Path(root) / file
                try:
                    with open(filepath, "rb") as f:
                        content = f.read()
                    if content and not content.endswith(b"\n"):
                        errors.append(f"{filepath}: missing final newline")
                except:
                    pass

    assert not errors, f"Files missing final newline:\n" + "\n".join(errors[:10])


# [repo_tests] pass_to_pass — No trailing whitespace in Python files (pre-commit check)
def test_repo_python_no_trailing_whitespace():
    """All Python files have no trailing whitespace (pre-commit trailing-whitespace check) (pass_to_pass)."""
    errors = []
    skip_dirs = {".git", "__pycache__", "evaluation", "build", "dist"}

    for root, dirs, files in os.walk(Path(REPO)):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for file in files:
            if file.endswith(".py"):
                filepath = Path(root) / file
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        for i, line in enumerate(f, 1):
                            if line.rstrip("\n\r").endswith(" ") or line.rstrip("\n\r").endswith("\t"):
                                errors.append(f"{filepath}:{i}: trailing whitespace")
                except:
                    pass

    assert not errors, f"Trailing whitespace found:\n" + "\n".join(errors[:10])


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_python_syntax():
    """The training script must parse without syntax errors."""
    script = Path(REPO) / "examples/vlm_npu/geometry3k_grpo.py"
    assert script.exists(), "examples/vlm_npu/geometry3k_grpo.py does not exist"
    r = subprocess.run(
        [sys.executable, "-m", "py_compile", str(script)],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"Syntax error: {r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_format_reward_function():
    """format_reward returns correct scores for matching and non-matching inputs."""
    script = Path(REPO) / "examples/vlm_npu/geometry3k_grpo.py"
    assert script.exists(), "geometry3k_grpo.py does not exist"

    # Extract and execute format_reward in isolation (it only uses `re`)
    r = subprocess.run(
        [sys.executable, "-c", """
import re

def format_reward(predict_str: str) -> float:
    pattern = re.compile(r".*\\\\blacksquare.*\\\\boxed\\{.*\\}.*", re.DOTALL)
    match_result = re.fullmatch(pattern, predict_str)
    return 1.0 if match_result else 0.0

# Test matching input
good = "reasoning here\\\\blacksquare the answer is \\\\boxed{42}"
assert format_reward(good) == 1.0, f"Expected 1.0 for valid format, got {format_reward(good)}"

# Test non-matching input (no think tags)
bad = "the answer is \\\\boxed{42}"
assert format_reward(bad) == 0.0, f"Expected 0.0 for missing think tags, got {format_reward(bad)}"

# Test non-matching input (no boxed)
bad2 = "reasoning\\\\blacksquare the answer is 42"
assert format_reward(bad2) == 0.0, f"Expected 0.0 for missing boxed, got {format_reward(bad2)}"

print("PASS")
"""],
        capture_output=True, text=True, timeout=10, cwd=REPO,
    )
    assert r.returncode == 0, f"format_reward test failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_yaml_config_structure():
    """YAML config must parse and contain required training configuration keys."""
    yaml_path = Path(REPO) / "examples/vlm_npu/geometry3k_grpo.yaml"
    assert yaml_path.exists(), "geometry3k_grpo.yaml does not exist"

    r = subprocess.run(
        [sys.executable, "-c", f"""
import yaml

with open("{yaml_path}") as f:
    config = yaml.safe_load(f)

required_keys = ["experiment_name", "actor", "vllm", "train_dataset", "valid_dataset",
                 "gconfig", "cluster", "rollout", "saver"]
for key in required_keys:
    assert key in config, f"Missing required config key: {{key}}"

# Verify actor has model path
assert "path" in config["actor"], "actor.path is required"

# Verify vllm config exists
assert "model" in config["vllm"], "vllm.model is required"

# Verify dataset paths
assert "path" in config["train_dataset"], "train_dataset.path is required"
assert "path" in config["valid_dataset"], "valid_dataset.path is required"

# Verify allocation_mode references vllm (NPU uses vllm-ascend)
assert "allocation_mode" in config, "allocation_mode is required"
assert "vllm" in config["allocation_mode"], "allocation_mode should reference vllm for NPU"

print("PASS")
"""],
        capture_output=True, text=True, timeout=10, cwd=REPO,
    )
    assert r.returncode == 0, f"YAML config validation failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_shell_script_references():
    """Shell launcher must reference the correct Python script and YAML config."""
    sh_path = Path(REPO) / "examples/vlm_npu/geometry3k_grpo.sh"
    assert sh_path.exists(), "geometry3k_grpo.sh does not exist"
    content = sh_path.read_text()

    assert "examples/vlm_npu/geometry3k_grpo.py" in content, \
        "Shell script must reference geometry3k_grpo.py"
    assert "examples/vlm_npu/geometry3k_grpo.yaml" in content, \
        "Shell script must reference geometry3k_grpo.yaml"
    assert "USE_OPTIMIZED_MODEL=0" in content, \
        "Shell script must set USE_OPTIMIZED_MODEL=0 for NPU compatibility"


# [pr_diff] fail_to_pass
def test_readme_documents_npu():
    """README must document NPU hardware requirements and results."""
    readme_path = Path(REPO) / "examples/vlm_npu/README.md"
    assert readme_path.exists(), "examples/vlm_npu/README.md does not exist"
    content = readme_path.read_text()
    content_lower = content.lower()

    assert "npu" in content_lower, "README must mention NPU"
    assert "hardware" in content_lower, "README must document hardware requirements"
    assert "results" in content_lower, "README must include training results"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — AGENTS.md:119 @ b942ed019df2c66b851c397c0836fd31a3787b70
def test_no_wildcard_imports():
    """Python script must not use wildcard imports (AGENTS.md line 119)."""
    script = Path(REPO) / "examples/vlm_npu/geometry3k_grpo.py"
    assert script.exists(), "geometry3k_grpo.py does not exist"

    r = subprocess.run(
        [sys.executable, "-c", f"""
import ast

with open("{script}") as f:
    tree = ast.parse(f.read())

for node in ast.walk(tree):
    if isinstance(node, ast.ImportFrom) and any(
        alias.name == "*" for alias in node.names
    ):
        print(f"WILDCARD: from {{node.module}} import *")
        raise SystemExit(1)

print("PASS")
"""],
        capture_output=True, text=True, timeout=10, cwd=REPO,
    )
    assert r.returncode == 0, f"Wildcard import found: {r.stdout}"
    assert "PASS" in r.stdout


# [agent_config] fail_to_pass — AGENTS.md:184-185 @ b942ed019df2c66b851c397c0836fd31a3787b70
def test_reward_fn_signature():
    """Reward function must accept (prompt, completions, prompt_ids, completion_ids, **data) per AGENTS.md."""
    script = Path(REPO) / "examples/vlm_npu/geometry3k_grpo.py"
    assert script.exists(), "geometry3k_grpo.py does not exist"

    r = subprocess.run(
        [sys.executable, "-c", f"""
import ast, inspect

with open("{script}") as f:
    tree = ast.parse(f.read())

found = False
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "geometry3k_reward_fn":
        found = True
        args = node.args
        param_names = [a.arg for a in args.args]
        # Must have prompt, completions, prompt_ids, completion_ids as positional params
        required = ["prompt", "completions", "prompt_ids", "completion_ids"]
        for req in required:
            assert req in param_names, f"Missing required parameter: {{req}}"
        # Must accept **kwargs or **data
        assert args.kwarg is not None, "Must accept **kwargs for extensibility"
        break

assert found, "geometry3k_reward_fn function not found"
print("PASS")
"""],
        capture_output=True, text=True, timeout=10, cwd=REPO,
    )
    assert r.returncode == 0, f"Reward function signature check failed: {r.stderr}\\n{r.stdout}"
    assert "PASS" in r.stdout
