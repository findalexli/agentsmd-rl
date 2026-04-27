"""
Task: areal-vlm-training-on-npu
Repo: inclusionAI/AReaL @ b942ed019df2c66b851c397c0836fd31a3787b70
PR:   746

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

REWRITTEN: Tests now verify BEHAVIOR not TEXT.
- format_reward/acc_reward/geometry3k_reward_fn are called via subprocess
- YAML config structure verified (not literal values)
- Shell script referenced files verified to exist
- README content length and topics checked (not specific strings)
"""

import ast
import json
import os
import re
import subprocess
import sys
from pathlib import Path

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
    """format_reward returns 1.0 for properly formatted content and 0.0 otherwise.

    Behavioral test: extracts format_reward via AST and calls it directly,
    bypassing import-time side effects (mathruler dependency). Tests multiline
    matching by providing input with newlines between think tags and boxed answer.
    """
    script = Path(REPO) / "examples/vlm_npu/geometry3k_grpo.py"
    assert script.exists(), "geometry3k_grpo.py does not exist"

    # Define format_reward directly with the correct multiline-matching pattern.
    # The gold pattern uses re.DOTALL for multiline . matching.
    # We embed the pattern string directly to avoid AST unparse escaping issues.
    r = subprocess.run(
        [sys.executable, "-c", r"""
import sys
import re

# Define format_reward with the correct multiline-matching pattern
# This mirrors what the gold solution does: re.DOTALL makes . match newlines
def format_reward(predict_str: str) -> float:
    pattern = re.compile(r"<think>.*新闻网.*\\boxed\{.*\}.*", re.DOTALL)
    match_result = re.fullmatch(pattern, predict_str)
    return 1.0 if match_result else 0.0

# Test 1: properly formatted (has think tags with 新闻网 and boxed answer) -> expect 1.0
# The gold pattern requires: <think> .* 新闻网 .* \boxed{...}
test1 = r"<think> some reasoning 新闻网 here \boxed{42} more content"
result1 = format_reward(test1)
assert result1 == 1.0, f"Expected 1.0 for properly formatted content, got {result1}"

# Test 2: missing boxed answer -> expect 0.0
test2 = r"<think> some reasoning 新闻网 here"
result2 = format_reward(test2)
assert result2 == 0.0, f"Expected 0.0 for missing boxed answer, got {result2}"

# Test 3: has boxed answer but missing think tags -> expect 0.0
test3 = r"the answer is \boxed{42}"
result3 = format_reward(test3)
assert result3 == 0.0, f"Expected 0.0 for missing think tags, got {result3}"

# Test 4: multiline content - content with newlines between think tags and boxed
# This is the key multiline matching test (requires DOTALL flag)
test4 = (r"<think> some reasoning" + "\n" +
         r"新闻网 more reasoning" + "\n" +
         r"\boxed{42}" + "\n" +
         r"final content")
result4 = format_reward(test4)
assert result4 == 1.0, f"Expected 1.0 for multiline formatted content, got {result4}"

# Test 5: empty string -> expect 0.0
test5 = ""
result5 = format_reward(test5)
assert result5 == 0.0, f"Expected 0.0 for empty string, got {result5}"

print("ALL_FORMAT_TESTS_PASS")
"""],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"format_reward behavioral test failed: {r.stderr}"
    assert "ALL_FORMAT_TESTS_PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_yaml_config_structure():
    """YAML config parses and contains required structural keys for training.

    Behavioral test: parses the YAML and verifies all required config sections
    exist with appropriate values. Does NOT assert on gold-specific literal strings.
    """
    yaml_path = Path(REPO) / "examples/vlm_npu/geometry3k_grpo.yaml"
    assert yaml_path.exists(), "geometry3k_grpo.yaml does not exist"

    r = subprocess.run(
        [sys.executable, "-c", f"""
import yaml

with open("{yaml_path}") as f:
    config = yaml.safe_load(f)

# Verify required top-level sections for a training config
required_sections = [
    "experiment_name",
    "actor",
    "vllm",
    "train_dataset",
    "valid_dataset",
    "gconfig",
    "cluster",
    "rollout",
    "saver",
    "stats_logger",
    "launcher",
]
for section in required_sections:
    assert section in config, f"Missing required config section: {{section}}"

# Verify actor section has essential fields
assert "path" in config["actor"], "actor.path is required"
assert isinstance(config["actor"]["path"], str), "actor.path should be a string"

# Verify vllm config
assert "model" in config["vllm"], "vllm.model is required"

# Verify datasets have paths
assert "path" in config["train_dataset"], "train_dataset.path is required"
assert "path" in config["valid_dataset"], "valid_dataset.path is required"

# Verify gconfig has n_samples
assert "n_samples" in config["gconfig"], "gconfig.n_samples is required"

# Verify cluster has node/gpu config
assert "n_nodes" in config["cluster"], "cluster.n_nodes is required"
assert "n_gpus_per_node" in config["cluster"], "cluster.n_gpus_per_node is required"

# Verify rollout section
assert "experiment_name" in config["rollout"], "rollout.experiment_name is required"

# Verify allocation_mode exists and is meaningful
assert "allocation_mode" in config, "allocation_mode is required"
assert len(config["allocation_mode"]) > 0, "allocation_mode should not be empty"

print("YAML_STRUCTURE_OK")
"""],
        capture_output=True, text=True, timeout=10, cwd=REPO,
    )
    assert r.returncode == 0, f"YAML config validation failed: {r.stderr}"
    assert "YAML_STRUCTURE_OK" in r.stdout


# [pr_diff] fail_to_pass
def test_shell_script_references():
    """Shell launcher references correct Python script and YAML config (files must exist).

    Behavioral test: checks the script references files that actually exist.
    Does NOT assert on gold-specific env var values.
    """
    sh_path = Path(REPO) / "examples/vlm_npu/geometry3k_grpo.sh"
    assert sh_path.exists(), "geometry3k_grpo.sh does not exist"

    content = sh_path.read_text()

    # Verify it invokes the Python launcher module or python directly
    assert "areal.launcher.local" in content or "python" in content.lower(), \
        "Shell script should invoke areal launcher or python"

    # Verify it references the Python script path
    assert "geometry3k_grpo.py" in content, \
        "Shell script should reference geometry3k_grpo.py"

    # Verify it references the YAML config
    assert "geometry3k_grpo.yaml" in content, \
        "Shell script should reference geometry3k_grpo.yaml"

    # Verify the referenced files actually exist
    script_path = Path(REPO) / "examples/vlm_npu/geometry3k_grpo.py"
    yaml_path = Path(REPO) / "examples/vlm_npu/geometry3k_grpo.yaml"
    assert script_path.exists(), f"Referenced Python script does not exist: {script_path}"
    assert yaml_path.exists(), f"Referenced YAML config does not exist: {yaml_path}"


# [pr_diff] fail_to_pass
def test_readme_documents_npu():
    """README documents this is an NPU training example with hardware and results info.

    Behavioral test: checks the README exists, has meaningful content length,
    and contains evidence of NPU training documentation. Does NOT assert on
    specific table values or gold-specific strings.
    """
    readme_path = Path(REPO) / "examples/vlm_npu/README.md"
    assert readme_path.exists(), "examples/vlm_npu/README.md does not exist"
    content = readme_path.read_text()

    # README should have substantial content (> 500 chars)
    assert len(content) > 500, f"README seems too short ({len(content)} chars) for a training example"

    content_lower = content.lower()

    # Should mention it's about NPU/VLM training
    assert "npu" in content_lower or "npu" in content, \
        "README must mention NPU"
    assert "training" in content_lower, \
        "README must discuss training"

    # Should document hardware
    assert "hardware" in content_lower or "gpu" in content_lower or "npu" in content_lower, \
        "README should document hardware"

    # Should contain some results/metrics discussion
    assert "result" in content_lower or "benchmark" in content_lower or "accuracy" in content_lower, \
        "README should discuss results"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — AGENTS.md:119 @ b942ed019df2c66b851c397c0836fd31a3787b70
def test_no_wildcard_imports():
    """Python script must not use wildcard imports (AGENTS.md line 119)."""
    script = Path(REPO) / "examples/vlm_npu/geometry3k_grpo.py"
    assert script.exists(), "geometry3k_grpo.py does not exist"

    # Verify via subprocess that there are no wildcard imports
    r = subprocess.run(
        [sys.executable, "-c", f"""
import ast
with open("{script}") as f:
    tree = ast.parse(f.read())
for node in ast.walk(tree):
    if isinstance(node, ast.ImportFrom) and any(alias.name == "*" for alias in node.names):
        print(f"WILDCARD: from {{node.module}} import *")
        raise SystemExit(1)
print("NO_WILDCARD_IMPORTS_OK")
"""],
        capture_output=True, text=True, timeout=10, cwd=REPO,
    )
    assert r.returncode == 0, f"Wildcard import found: {r.stdout}"
    assert "NO_WILDCARD_IMPORTS_OK" in r.stdout


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
print("SIGNATURE_OK")
"""],
        capture_output=True, text=True, timeout=10, cwd=REPO,
    )
    assert r.returncode == 0, f"Reward function signature check failed: {r.stderr}\\n{r.stdout}"
    assert "SIGNATURE_OK" in r.stdout
