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
# (it may appear in comments, but not as the active config path)
lines = source.splitlines()
for line in lines:
    stripped = line.strip()
    if stripped.startswith('#'):
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
