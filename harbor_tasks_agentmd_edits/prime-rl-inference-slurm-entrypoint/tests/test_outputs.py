"""
Task: prime-rl-inference-slurm-entrypoint
Repo: PrimeIntellect-ai/prime-rl @ 6f6fa002a55a26ba1cc33aa9ac6b7301f59b82e0
PR:   1898

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import json
import subprocess
import sys
from pathlib import Path

REPO = "/workspace/prime-rl"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """New entrypoint file must parse without errors."""
    entrypoint_path = Path(f"{REPO}/src/prime_rl/entrypoints/inference.py")
    assert entrypoint_path.exists(), f"Entrypoint file not found: {entrypoint_path}"

    src = entrypoint_path.read_text()
    try:
        ast.parse(src)
    except SyntaxError as e:
        raise AssertionError(f"Syntax error in entrypoint: {e}")


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_entrypoint_file_exists_with_main():
    """New inference entrypoint file must exist with main() function."""
    entrypoint_path = Path(f"{REPO}/src/prime_rl/entrypoints/inference.py")
    assert entrypoint_path.exists(), "src/prime_rl/entrypoints/inference.py must be created"

    src = entrypoint_path.read_text()
    assert "def main():" in src, "Entrypoint must have main() function"
    assert "inference(cli(InferenceConfig))" in src, "main() must call inference(cli(InferenceConfig))"
    assert "def inference(" in src, "Entrypoint must have inference() function"
    assert "def inference_slurm(" in src, "Entrypoint must have inference_slurm() function"
    assert "def inference_local(" in src, "Entrypoint must have inference_local() function"


# [pr_diff] fail_to_pass
def test_pyproject_entrypoint_updated():
    """pyproject.toml must point to new entrypoint."""
    pyproject_path = Path(f"{REPO}/pyproject.toml")
    content = pyproject_path.read_text()

    # Should point to new entrypoint, not old one
    assert 'inference = "prime_rl.entrypoints.inference:main"' in content, \
        "pyproject.toml must point inference command to prime_rl.entrypoints.inference:main"
    assert 'inference = "prime_rl.inference.server:main"' not in content, \
        "pyproject.toml should not point to old inference.server entrypoint"


# [pr_diff] fail_to_pass
def test_config_has_slurm_and_deployment():
    """InferenceConfig must have slurm, deployment, output_dir, and dry_run fields."""
    sys.path.insert(0, REPO)
    try:
        from prime_rl.configs.inference import InferenceConfig

        # Check that the config class has the new fields
        import inspect
        sig = inspect.signature(InferenceConfig)
        params = list(sig.parameters.keys())

        assert "slurm" in params, "InferenceConfig must have 'slurm' parameter"
        assert "deployment" in params, "InferenceConfig must have 'deployment' parameter"
        assert "output_dir" in params, "InferenceConfig must have 'output_dir' parameter"
        assert "dry_run" in params, "InferenceConfig must have 'dry_run' parameter"
    finally:
        sys.path.pop(0)


# [pr_diff] fail_to_pass
def test_config_validators_exist():
    """InferenceConfig must have validators for multi_node + slurm and slurm template."""
    config_path = Path(f"{REPO}/src/prime_rl/configs/inference.py")
    content = config_path.read_text()

    assert "validate_multi_node_requires_slurm" in content, \
        "Must have validator ensuring multi_node requires slurm"
    assert "auto_setup_slurm_template" in content, \
        "Must have validator for auto-setting slurm template path"


# [pr_diff] fail_to_pass
def test_slurm_template_file_exists():
    """SLURM template file must exist."""
    template_path = Path(f"{REPO}/src/prime_rl/templates/inference.sbatch.j2")
    assert template_path.exists(), "src/prime_rl/templates/inference.sbatch.j2 must be created"

    content = template_path.read_text()
    assert "#!/bin/bash" in content, "Template must be a bash script"
    assert "#SBATCH" in content, "Template must have SBATCH directives"


# [pr_diff] fail_to_pass
def test_skill_md_updated_with_slurm_docs():
    """SKILL.md must be updated with SLURM inference documentation."""
    skill_path = Path(f"{REPO}/skills/inference-server/SKILL.md")
    content = skill_path.read_text()

    # Check for SLURM-specific documentation
    assert "## SLURM scheduling" in content, \
        "SKILL.md must have SLURM scheduling section header"
    assert "### Single-node SLURM" in content, \
        "SKILL.md must document single-node SLURM mode"
    assert "### Multi-node SLURM" in content, \
        "SKILL.md must document multi-node SLURM mode"
    assert "### Dry run" in content, \
        "SKILL.md must document dry_run mode"

    # Check for key SLURM config fields mentioned
    assert "[slurm]" in content, \
        "SKILL.md must show [slurm] section in examples"
    assert "[deployment]" in content, \
        "SKILL.md must show [deployment] section in examples"


# [pr_diff] fail_to_pass
def test_skill_md_key_files_updated():
    """SKILL.md key files section must reference new entrypoint."""
    skill_path = Path(f"{REPO}/skills/inference-server/SKILL.md")
    content = skill_path.read_text()

    # Check key files section was updated
    assert "src/prime_rl/entrypoints/inference.py" in content, \
        "SKILL.md key files must list the new entrypoint"
    assert "src/prime_rl/templates/inference.sbatch.j2" in content, \
        "SKILL.md key files must list the SLURM template"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_entrypoint_not_stub():
    """Entrypoint functions must have real logic, not just pass/return."""
    entrypoint_path = Path(f"{REPO}/src/prime_rl/entrypoints/inference.py")
    src = entrypoint_path.read_text()
    tree = ast.parse(src)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if node.name in ["inference", "inference_slurm", "inference_local", "main"]:
                # Count non-pass, non-docstring statements
                stmts = []
                for s in node.body:
                    if isinstance(s, ast.Pass):
                        continue
                    if isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant):
                        # Skip docstring (Constant string at start of function)
                        continue
                    stmts.append(s)

                assert len(stmts) >= 2, f"Function {node.name} appears to be a stub (too few statements)"


# [static] pass_to_pass
def test_config_classes_not_stub():
    """Deployment config classes must have real fields."""
    config_path = Path(f"{REPO}/src/prime_rl/configs/inference.py")
    src = config_path.read_text()
    tree = ast.parse(src)

    # Check that BaseInferenceDeploymentConfig has gpus_per_node field
    found_classes = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            if node.name in ["BaseInferenceDeploymentConfig", "SingleNodeInferenceDeploymentConfig", "MultiNodeInferenceDeploymentConfig"]:
                field_count = 0
                for item in node.body:
                    if isinstance(item, ast.AnnAssign):  # Annotated assignment = field
                        field_count += 1
                found_classes[node.name] = field_count

    assert found_classes.get("BaseInferenceDeploymentConfig", 0) >= 1, \
        "BaseInferenceDeploymentConfig must have at least 1 field"
    assert found_classes.get("MultiNodeInferenceDeploymentConfig", 0) >= 2, \
        "MultiNodeInferenceDeploymentConfig must have at least 2 fields (type, num_nodes)"
