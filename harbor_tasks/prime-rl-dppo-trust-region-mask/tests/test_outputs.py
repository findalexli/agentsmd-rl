"""
Task: prime-rl-dppo-trust-region-mask
Repo: prime-rl @ 09293f3e3eb8bd0fc643bac2d2b80014f0529641
PR:   2187

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import textwrap
from pathlib import Path

REPO = "/workspace/prime-rl"

# Stub wandb before any prime_rl import (avoids heavy transitive dep)
_PREAMBLE = "import sys, types; sys.modules['wandb'] = types.ModuleType('wandb')\n"


def _run_script(script: str, timeout: int = 60) -> subprocess.CompletedProcess:
    """Run a Python script in the repo with wandb stubbed out."""
    return subprocess.run(
        ["python3", "-c", _PREAMBLE + textwrap.dedent(script)],
        cwd=REPO, capture_output=True, text=True, timeout=timeout,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

def test_syntax_check():
    """Modified files must parse without errors."""
    for relpath in [
        "src/prime_rl/configs/trainer.py",
        "src/prime_rl/trainer/rl/loss.py",
        "tests/unit/train/rl/test_loss.py",
    ]:
        r = subprocess.run(
            ["python3", "-m", "py_compile", relpath],
            cwd=REPO, capture_output=True, text=True, timeout=30,
        )
        assert r.returncode == 0, f"Syntax error in {relpath}:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) - Repo CI/CD checks
# ---------------------------------------------------------------------------

def test_repo_ruff_check():
    """Repo's ruff lint check passes on modified files (pass_to_pass)."""
    # Install ruff if not available
    subprocess.run(["pip", "install", "ruff", "-q"], capture_output=True, timeout=60)
    r = subprocess.run(
        ["ruff", "check", "src/prime_rl/configs/trainer.py", "src/prime_rl/trainer/rl/loss.py", "--config=pyproject.toml"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_ruff_format():
    """Repo's ruff format check passes on modified files (pass_to_pass)."""
    # Install ruff if not available
    subprocess.run(["pip", "install", "ruff", "-q"], capture_output=True, timeout=60)
    r = subprocess.run(
        ["ruff", "format", "--check", "src/prime_rl/configs/trainer.py", "src/prime_rl/trainer/rl/loss.py", "--config=pyproject.toml"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_ruff_check_test_file():
    """Repo's ruff lint check passes on modified test file (pass_to_pass)."""
    subprocess.run(["pip", "install", "ruff", "-q"], capture_output=True, timeout=60)
    r = subprocess.run(
        ["ruff", "check", "tests/unit/train/rl/test_loss.py", "--config=pyproject.toml"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed on test file:\n{r.stdout}\n{r.stderr}"


def test_repo_ruff_format_test_file():
    """Repo's ruff format check passes on modified test file (pass_to_pass)."""
    subprocess.run(["pip", "install", "ruff", "-q"], capture_output=True, timeout=60)
    r = subprocess.run(
        ["ruff", "format", "--check", "tests/unit/train/rl/test_loss.py", "--config=pyproject.toml"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed on test file:\n{r.stdout}\n{r.stderr}"


def test_repo_pyproject_toml_valid():
    """Repo's pyproject.toml is valid TOML (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", "import tomllib; f=open('pyproject.toml', 'rb'); tomllib.load(f); f.close()"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"pyproject.toml is invalid TOML:\n{r.stderr}"


def test_repo_ruff_check_all():
    """Repo's ruff lint check passes on entire project (pass_to_pass)."""
    subprocess.run(["pip", "install", "ruff", "-q"], capture_output=True, timeout=60)
    r = subprocess.run(
        ["ruff", "check", ".", "--config=pyproject.toml"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check on entire repo failed:\n{r.stdout}\n{r.stderr}"


def test_repo_ruff_format_all():
    """Repo's ruff format check passes on entire project (pass_to_pass)."""
    subprocess.run(["pip", "install", "ruff", "-q"], capture_output=True, timeout=60)
    r = subprocess.run(
        ["ruff", "format", "--check", ".", "--config=pyproject.toml"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check on entire repo failed:\n{r.stdout}\n{r.stderr}"


def test_repo_imports_work():
    """Modified modules can be imported and used at base commit (pass_to_pass)."""
    r = _run_script("""
        import torch
        from prime_rl.configs.trainer import DefaultLossConfig
        from prime_rl.trainer.rl.loss import default_loss_fn, LossInputs

        # Test that config and loss function work at base commit
        config = DefaultLossConfig()
        trainer_logprobs = torch.tensor([-0.5, -0.3, -0.7, -0.4])
        inference_logprobs = torch.tensor([-2.0, -1.8, -2.5, -2.2])
        advantages = torch.tensor([1.0, 2.0, 0.5, 1.5])

        inputs = LossInputs(
            trainer_logprobs=trainer_logprobs,
            inference_logprobs=inference_logprobs,
            teacher_logprobs=None,
            advantages=advantages,
            loss_mask=torch.ones(4, dtype=torch.bool),
        )

        result = default_loss_fn(inputs, config)
        assert hasattr(result, 'loss'), 'Result should have loss attribute'
        assert hasattr(result, 'metrics'), 'Result should have metrics attribute'
        print("PASS")
    """)
    assert r.returncode == 0, f"Import test failed:\n{r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — config field renaming
# ---------------------------------------------------------------------------

def test_dppo_config_fields():
    """DefaultLossConfig must have dppo_mask_low and dppo_mask_high fields."""
    r = _run_script("""
        from prime_rl.configs.trainer import DefaultLossConfig
        for low, high in [(0.1, 0.3), (0.05, 0.5), (0.2, 0.2)]:
            c = DefaultLossConfig(dppo_mask_low=low, dppo_mask_high=high)
            assert c.dppo_mask_low == low, f"Expected dppo_mask_low={low}, got {c.dppo_mask_low}"
            assert c.dppo_mask_high == high, f"Expected dppo_mask_high={high}, got {c.dppo_mask_high}"
        c = DefaultLossConfig()
        assert hasattr(c, 'dppo_mask_low'), "Missing dppo_mask_low field"
        assert hasattr(c, 'dppo_mask_high'), "Missing dppo_mask_high field"
        print("PASS")
    """)
    assert r.returncode == 0, f"Failed:\n{r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


def test_old_ipo_config_removed():
    """DefaultLossConfig must NOT have ipo_mask_low or ipo_mask_high fields."""
    r = _run_script("""
        from prime_rl.configs.trainer import DefaultLossConfig
        fields = set(DefaultLossConfig.model_fields.keys())
        assert 'ipo_mask_low' not in fields, f"ipo_mask_low should be removed, found: {fields}"
        assert 'ipo_mask_high' not in fields, f"ipo_mask_high should be removed, found: {fields}"
        print("PASS")
    """)
    assert r.returncode == 0, f"Failed:\n{r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral: advantage-conditioned masking
# ---------------------------------------------------------------------------

def test_mask_positive_adv_ignores_low_violation():
    """With positive advantages, low-side trust region violations must NOT cause masking."""
    r = _run_script("""
        import torch
        from prime_rl.configs.trainer import DefaultLossConfig
        from prime_rl.trainer.rl.loss import default_loss_fn, LossInputs

        config = DefaultLossConfig(dppo_mask_low=0.1, dppo_mask_high=0.1)

        # trainer probs << inference probs -> probs_diff < -0.1 (low violation only)
        inputs = LossInputs(
            trainer_logprobs=torch.tensor([-2.0, -1.8, -2.5, -2.2]),
            inference_logprobs=torch.tensor([-0.5, -0.3, -0.7, -0.4]),
            teacher_logprobs=None,
            advantages=torch.tensor([1.0, 2.0, 0.5, 1.5]),
            loss_mask=torch.ones(4, dtype=torch.bool),
        )

        result = default_loss_fn(inputs, config)
        is_masked = result.metrics["is_masked"].item()
        assert is_masked == 0.0, (
            f"Expected 0 masking (positive adv + low-only violation), got {is_masked}"
        )
        print("PASS")
    """)
    assert r.returncode == 0, f"Failed:\n{r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


def test_mask_negative_adv_ignores_high_violation():
    """With negative advantages, high-side trust region violations must NOT cause masking."""
    r = _run_script("""
        import torch
        from prime_rl.configs.trainer import DefaultLossConfig
        from prime_rl.trainer.rl.loss import default_loss_fn, LossInputs

        config = DefaultLossConfig(dppo_mask_low=0.1, dppo_mask_high=0.1)

        # trainer probs >> inference probs -> probs_diff > 0.1 (high violation only)
        inputs = LossInputs(
            trainer_logprobs=torch.tensor([-0.5, -0.3, -0.7, -0.4]),
            inference_logprobs=torch.tensor([-2.0, -1.8, -2.5, -2.2]),
            teacher_logprobs=None,
            advantages=torch.tensor([-1.0, -2.0, -0.5, -1.5]),
            loss_mask=torch.ones(4, dtype=torch.bool),
        )

        result = default_loss_fn(inputs, config)
        is_masked = result.metrics["is_masked"].item()
        assert is_masked == 0.0, (
            f"Expected 0 masking (negative adv + high-only violation), got {is_masked}"
        )
        print("PASS")
    """)
    assert r.returncode == 0, f"Failed:\n{r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


def test_mask_mixed_advantages_selective():
    """With mixed advantages, masking must be applied selectively by advantage sign."""
    r = _run_script("""
        import torch
        from prime_rl.configs.trainer import DefaultLossConfig
        from prime_rl.trainer.rl.loss import default_loss_fn, LossInputs

        config = DefaultLossConfig(dppo_mask_low=0.1, dppo_mask_high=0.1)

        # Token 0: positive adv + high violation -> MASKED
        # Token 1: positive adv + low violation  -> NOT masked
        # Token 2: negative adv + high violation -> NOT masked
        # Token 3: negative adv + low violation  -> MASKED
        inputs = LossInputs(
            trainer_logprobs=torch.tensor([-0.5, -2.0, -0.5, -2.0]),
            inference_logprobs=torch.tensor([-2.0, -0.5, -2.0, -0.5]),
            teacher_logprobs=None,
            advantages=torch.tensor([1.0, 1.0, -1.0, -1.0]),
            loss_mask=torch.ones(4, dtype=torch.bool),
        )

        result = default_loss_fn(inputs, config)
        is_masked = result.metrics["is_masked"].item()
        assert abs(is_masked - 0.5) < 1e-6, (
            f"Expected is_masked=0.5 (2/4 tokens masked selectively), got {is_masked}"
        )
        print("PASS")
    """)
    assert r.returncode == 0, f"Failed:\n{r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — masking still works when it should
# ---------------------------------------------------------------------------

def test_mask_positive_adv_applies_high_violation():
    """Positive advantages with high-side violations must still be masked."""
    r = _run_script("""
        import torch
        from prime_rl.configs.trainer import DefaultLossConfig
        from prime_rl.trainer.rl.loss import default_loss_fn, LossInputs

        config = DefaultLossConfig(dppo_mask_low=0.1, dppo_mask_high=0.1)

        # trainer probs >> inference probs -> high violation + positive advantage
        inputs = LossInputs(
            trainer_logprobs=torch.tensor([-0.5, -0.3, -0.7, -0.4]),
            inference_logprobs=torch.tensor([-2.0, -1.8, -2.5, -2.2]),
            teacher_logprobs=None,
            advantages=torch.tensor([1.0, 2.0, 0.5, 1.5]),
            loss_mask=torch.ones(4, dtype=torch.bool),
        )

        result = default_loss_fn(inputs, config)
        is_masked = result.metrics["is_masked"].item()
        assert is_masked > 0.0, (
            f"Expected masking (positive adv + high violation), got {is_masked}"
        )
        print("PASS")
    """)
    assert r.returncode == 0, f"Failed:\n{r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


def test_mask_negative_adv_applies_low_violation():
    """Negative advantages with low-side violations must still be masked."""
    r = _run_script("""
        import torch
        from prime_rl.configs.trainer import DefaultLossConfig
        from prime_rl.trainer.rl.loss import default_loss_fn, LossInputs

        config = DefaultLossConfig(dppo_mask_low=0.1, dppo_mask_high=0.1)

        # trainer probs << inference probs -> low violation + negative advantage
        inputs = LossInputs(
            trainer_logprobs=torch.tensor([-2.0, -1.8, -2.5, -2.2]),
            inference_logprobs=torch.tensor([-0.5, -0.3, -0.7, -0.4]),
            teacher_logprobs=None,
            advantages=torch.tensor([-1.0, -2.0, -0.5, -1.5]),
            loss_mask=torch.ones(4, dtype=torch.bool),
        )

        result = default_loss_fn(inputs, config)
        is_masked = result.metrics["is_masked"].item()
        assert is_masked > 0.0, (
            f"Expected masking (negative adv + low violation), got {is_masked}"
        )
        print("PASS")
    """)
    assert r.returncode == 0, f"Failed:\n{r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout
