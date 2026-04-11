"""
Task: prime-rl-sft-vlm-dtype-validation
Repo: PrimeIntellect-ai/prime-rl @ 7ef29a76600d767e732c99c8eaaec768830a7bca
PR:   2079

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import sys

sys.path.insert(0, "/workspace/prime-rl/src")

REPO = "/workspace/prime-rl"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """trainer.py and sft.py must parse without errors."""
    import py_compile

    py_compile.compile(
        "/workspace/prime-rl/src/prime_rl/configs/trainer.py",
        doraise=True,
    )
    py_compile.compile(
        "/workspace/prime-rl/src/prime_rl/configs/sft.py",
        doraise=True,
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — repo CI/CD checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_ruff_lint_configs():
    """Repo's ruff lint check passes on configs directory (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "-q", "ruff==0.13.0"],
        capture_output=True, text=True, timeout=60,
    )
    r = subprocess.run(
        ["ruff", "check", "--config=pyproject.toml", "src/prime_rl/configs/"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff lint failed:{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_ruff_format_configs():
    """Repo's ruff format check passes on configs directory (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "-q", "ruff==0.13.0"],
        capture_output=True, text=True, timeout=60,
    )
    r = subprocess.run(
        ["ruff", "format", "--check", "--config=pyproject.toml", "src/prime_rl/configs/"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_ruff_lint_src():
    """Repo's ruff lint check passes on src/prime_rl directory (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "-q", "ruff==0.13.0"],
        capture_output=True, text=True, timeout=60,
    )
    r = subprocess.run(
        ["ruff", "check", "--config=pyproject.toml", "src/prime_rl/"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff lint failed on src:{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_ruff_format_src():
    """Repo's ruff format check passes on src/prime_rl directory (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "-q", "ruff==0.13.0"],
        capture_output=True, text=True, timeout=60,
    )
    r = subprocess.run(
        ["ruff", "format", "--check", "--config=pyproject.toml", "src/prime_rl/"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed on src:{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_configs_importable():
    """Configs module imports work without errors (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-c",
         "import sys; sys.path.insert(0, '/workspace/prime-rl/src'); "
         "from prime_rl.configs.trainer import ModelConfig, TrainerConfig; "
         "from prime_rl.configs.sft import SFTConfig; "
         "print('All config imports successful')"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Config imports failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_modelconfig_creation():
    """ModelConfig can be instantiated for various model types (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-c",
         "import sys; sys.path.insert(0, '/workspace/prime-rl/src'); "
         "from prime_rl.configs.trainer import ModelConfig; "
         "mc1 = ModelConfig(name='Qwen/Qwen3-0.6B'); "
         "mc2 = ModelConfig(name='meta-llama/Llama-3-8B'); "
         "mc3 = ModelConfig(name='mistralai/Mistral-7B'); "
         "print(f'Created {mc1.name}, {mc2.name}, {mc3.name}')"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"ModelConfig creation failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_modelconfig_vlm_default_dtypes():
    """ModelConfig with VLM names and default float32 dtypes does NOT raise."""
    from prime_rl.configs.trainer import ModelConfig

    # Test multiple VLM patterns — both Qwen3-VL and Qwen3.5 families
    for name in [
        "Qwen/Qwen3-VL-4B-Instruct",
        "Qwen/Qwen3-VL-72B",
        "Qwen/Qwen3.5-VL-7B",
    ]:
        mc = ModelConfig(name=name)
        assert mc.optimization_dtype == "float32", f"{name}: expected float32 optimization_dtype"
        assert mc.reduce_dtype == "float32", f"{name}: expected float32 reduce_dtype"


# [pr_diff] fail_to_pass
def test_sftconfig_vlm_default_dtypes():
    """SFTConfig with VLM model and default float32 dtypes does NOT raise."""
    from prime_rl.configs.sft import SFTConfig
    from prime_rl.configs.trainer import ModelConfig

    for name in [
        "Qwen/Qwen3-VL-4B-Instruct",
        "Qwen/Qwen3.5-VL-7B",
    ]:
        mc = ModelConfig(name=name)
        sc = SFTConfig(model=mc)
        assert sc.model.name == name


# [pr_diff] fail_to_pass
def test_trainerconfig_vlm_rejects_default_float32():
    """TrainerConfig with VLM name and default float32 dtypes raises ValueError."""
    import pytest

    from prime_rl.configs.trainer import ModelConfig, TrainerConfig

    for name in [
        "Qwen/Qwen3-VL-4B-Instruct",
        "Qwen/Qwen3-VL-72B",
        "Qwen/Qwen3.5-VL-7B",
    ]:
        mc = ModelConfig(name=name)
        with pytest.raises(ValueError, match="bfloat16"):
            TrainerConfig(model=mc)


# [pr_diff] fail_to_pass
def test_trainerconfig_vlm_rejects_partial_mismatch():
    """TrainerConfig rejects VLM with one float32 and one bfloat16 dtype."""
    import pytest

    from prime_rl.configs.trainer import ModelConfig, TrainerConfig

    # optimization=float32, reduce=bfloat16
    mc1 = ModelConfig(
        name="Qwen/Qwen3-VL-4B-Instruct",
        optimization_dtype="float32",
        reduce_dtype="bfloat16",
    )
    with pytest.raises(ValueError, match="bfloat16"):
        TrainerConfig(model=mc1)

    # optimization=bfloat16, reduce=float32
    mc2 = ModelConfig(
        name="Qwen/Qwen3.5-VL-7B",
        optimization_dtype="bfloat16",
        reduce_dtype="float32",
    )
    with pytest.raises(ValueError, match="bfloat16"):
        TrainerConfig(model=mc2)


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — preserved behavior
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_modelconfig_vlm_explicit_bfloat16():
    """ModelConfig accepts VLM with explicit bfloat16 (was always valid)."""
    from prime_rl.configs.trainer import ModelConfig

    mc = ModelConfig(
        name="Qwen/Qwen3-VL-4B-Instruct",
        optimization_dtype="bfloat16",
        reduce_dtype="bfloat16",
    )
    assert mc.optimization_dtype == "bfloat16"
    assert mc.reduce_dtype == "bfloat16"


# [pr_diff] pass_to_pass
def test_trainerconfig_vlm_accepts_bfloat16():
    """TrainerConfig accepts VLM with correct bfloat16 dtypes."""
    from prime_rl.configs.trainer import ModelConfig, TrainerConfig

    tc = TrainerConfig(
        model=ModelConfig(
            name="Qwen/Qwen3-VL-4B-Instruct",
            optimization_dtype="bfloat16",
            reduce_dtype="bfloat16",
        )
    )
    assert tc.model.optimization_dtype == "bfloat16"


# [pr_diff] pass_to_pass
def test_non_vlm_modelconfig():
    """Non-VLM ModelConfig with default dtypes still works."""
    from prime_rl.configs.trainer import ModelConfig

    for name in ["Qwen/Qwen3-0.6B", "meta-llama/Llama-3-8B", "mistralai/Mistral-7B"]:
        mc = ModelConfig(name=name)
        assert mc.optimization_dtype == "float32"
        assert mc.reduce_dtype == "float32"


# [pr_diff] pass_to_pass
def test_non_vlm_trainerconfig():
    """Non-VLM TrainerConfig with default dtypes still works."""
    from prime_rl.configs.trainer import ModelConfig, TrainerConfig

    tc = TrainerConfig(model=ModelConfig(name="Qwen/Qwen3-0.6B"))
    assert tc.model.name == "Qwen/Qwen3-0.6B"


# ---------------------------------------------------------------------------
# Anti-stub (static) — validator must have real logic
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_trainerconfig_validator_not_stub():
    """TrainerConfig.vlms_require_bfloat16 must exist with real validation logic."""
    import ast

    # AST-only because: we need to verify the method exists structurally,
    # behavioral testing alone can't distinguish "validator removed" from
    # "validator exists but has a bug"
    src = open("/workspace/prime-rl/src/prime_rl/configs/trainer.py").read()
    tree = ast.parse(src)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "TrainerConfig":
            methods = {
                n.name: n
                for n in node.body
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
            }
            assert "vlms_require_bfloat16" in methods, (
                "TrainerConfig must have vlms_require_bfloat16 validator"
            )
            body = methods["vlms_require_bfloat16"].body
            # Must have more than just  or
            non_trivial = [
                s for s in body
                if not isinstance(s, (ast.Pass, ast.Return, ast.Expr))
                or (isinstance(s, ast.Return) and s.value is not None
                    and not (isinstance(s.value, ast.Name) and s.value.id == "self"))
            ]
            assert len(non_trivial) >= 1, (
                "vlms_require_bfloat16 body is a stub — must contain validation logic"
            )
            return

    raise AssertionError("TrainerConfig class not found in trainer.py")


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:5 @ 7ef29a76600d767e732c99c8eaaec768830a7bca
def test_no_unnecessary_try_except_in_validator():
    """Validator must not wrap logic in try/except (AGENTS.md: avoid try/except unless necessary)."""
    import ast

    # AST-only because: checking for try/except is a structural property
    src = open("/workspace/prime-rl/src/prime_rl/configs/trainer.py").read()
    tree = ast.parse(src)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "TrainerConfig":
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if item.name == "vlms_require_bfloat16":
                        try_blocks = [
                            n for n in ast.walk(item)
                            if isinstance(n, ast.Try)
                        ]
                        assert len(try_blocks) == 0, (
                            "vlms_require_bfloat16 should not use try/except — "
                            "validators should raise directly (AGENTS.md line 5)"
                        )
                        return

    # If validator doesn't exist, test_trainerconfig_validator_not_stub catches it
