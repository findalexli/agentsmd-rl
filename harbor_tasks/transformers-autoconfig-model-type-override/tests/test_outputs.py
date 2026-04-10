"""
Task: transformers-autoconfig-model-type-override
Repo: huggingface/transformers @ ce4a791c5277840c4c1d74eed03431b674869da5
PR:   45058

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import logging
import os
import subprocess
import tempfile
from pathlib import Path

REPO = "/workspace/transformers"


def _make_checkpoint(model_type: str, **extra) -> str:
    """Create a temporary directory with a minimal config.json."""
    tmpdir = tempfile.mkdtemp()
    config = {"model_type": model_type, **extra}
    with open(os.path.join(tmpdir, "config.json"), "w") as f:
        json.dump(config, f)
    return tmpdir


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """configuration_utils.py must parse without errors."""
    import py_compile
    py_compile.compile(
        f"{REPO}/src/transformers/configuration_utils.py",
        doraise=True,
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_override_model_type():
    """Passing model_type kwarg overrides config_dict value when they differ."""
    from transformers import PretrainedConfig

    for original, override in [
        ("wrong_type", "correct_type"),
        ("qwen2_vl", "qwen2_5_vl"),
        ("gpt2", "llama"),
    ]:
        ckpt = _make_checkpoint(original, architectures=["Dummy"])
        config_dict, _ = PretrainedConfig._get_config_dict(ckpt, model_type=override)
        assert config_dict["model_type"] == override, (
            f"Expected model_type='{override}', got '{config_dict['model_type']}' "
            f"(original was '{original}')"
        )


# [pr_diff] fail_to_pass
def test_warning_on_override():
    """A warning is logged when model_type is overridden."""
    from transformers import PretrainedConfig

    for orig, new in [("old_type", "new_type"), ("gpt2", "llama"), ("bert", "roberta")]:
        ckpt = _make_checkpoint(orig, architectures=["Dummy"])

        captured = []
        handler = logging.Handler()
        handler.emit = lambda record: captured.append(record.getMessage())
        logger = logging.getLogger("transformers.configuration_utils")
        logger.addHandler(handler)
        orig_level = logger.level
        logger.setLevel(logging.WARNING)

        try:
            PretrainedConfig._get_config_dict(ckpt, model_type=new)
        finally:
            logger.removeHandler(handler)
            logger.setLevel(orig_level)

        assert any(orig in msg and new in msg for msg in captured), (
            f"Expected warning mentioning both '{orig}' and '{new}', got: {captured}"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_no_warning_when_matching():
    """No warning is logged when model_type kwarg matches config."""
    from transformers import PretrainedConfig

    ckpt = _make_checkpoint("bert", architectures=["BertModel"])

    captured = []
    handler = logging.Handler()
    handler.emit = lambda record: captured.append(record.getMessage())
    logger = logging.getLogger("transformers.configuration_utils")
    logger.addHandler(handler)
    orig_level = logger.level
    logger.setLevel(logging.WARNING)

    try:
        config_dict, _ = PretrainedConfig._get_config_dict(ckpt, model_type="bert")
    finally:
        logger.removeHandler(handler)
        logger.setLevel(orig_level)

    assert config_dict["model_type"] == "bert"
    assert not any("bert" in msg and "override" in msg.lower() for msg in captured), (
        f"Unexpected override warning when types match: {captured}"
    )


# [pr_diff] pass_to_pass
def test_no_override_when_matching():
    """Passing model_type that matches config does not change anything."""
    from transformers import PretrainedConfig

    for model_type in ["bert", "gpt2", "llama"]:
        ckpt = _make_checkpoint(model_type, hidden_size=768)
        config_dict, _ = PretrainedConfig._get_config_dict(ckpt, model_type=model_type)
        assert config_dict["model_type"] == model_type
        assert config_dict["hidden_size"] == 768


# [pr_diff] pass_to_pass
def test_normal_load_without_model_type_kwarg():
    """Loading config without model_type kwarg works unchanged."""
    from transformers import PretrainedConfig

    ckpt = _make_checkpoint("bert", hidden_size=768)
    config_dict, _ = PretrainedConfig._get_config_dict(ckpt)
    assert config_dict["model_type"] == "bert"
    assert config_dict["hidden_size"] == 768


# [static] pass_to_pass
def test_not_stub():
    """configuration_utils.py is not stubbed out."""
    src = Path(f"{REPO}/src/transformers/configuration_utils.py").read_text()
    assert len(src.splitlines()) >= 800, (
        f"configuration_utils.py only has {len(src.splitlines())} lines, expected >= 800"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass — repo CI checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_import_configuration_utils():
    """Repo's configuration_utils module imports without errors (pass_to_pass)."""
    result = subprocess.run(
        ["python", "-c", "from transformers.configuration_utils import PretrainedConfig; print('OK')"],
        capture_output=True, text=True, cwd=REPO, timeout=30,
    )
    assert result.returncode == 0, f"Import failed: {result.stderr}"


# [repo_tests] pass_to_pass
def test_repo_pycompile_configuration_utils():
    """Repo's configuration_utils.py compiles without syntax errors (pass_to_pass)."""
    result = subprocess.run(
        ["python", "-m", "py_compile", "src/transformers/configuration_utils.py"],
        capture_output=True, text=True, cwd=REPO, timeout=30,
    )
    assert result.returncode == 0, f"Py_compile failed: {result.stderr}"


# [repo_tests] pass_to_pass
def test_repo_check_config_docstrings():
    """Repo's config docstrings check passes (pass_to_pass)."""
    result = subprocess.run(
        ["python", "utils/check_config_docstrings.py"],
        capture_output=True, text=True, cwd=REPO, timeout=120,
    )
    err = result.stderr[-500:] if result.stderr else ""
    assert result.returncode == 0, f"check_config_docstrings failed: {err}"


# [repo_tests] pass_to_pass
def test_repo_check_config_attributes():
    """Repo's config attributes check passes (pass_to_pass)."""
    result = subprocess.run(
        ["python", "utils/check_config_attributes.py"],
        capture_output=True, text=True, cwd=REPO, timeout=120,
    )
    err = result.stderr[-500:] if result.stderr else ""
    assert result.returncode == 0, f"check_config_attributes failed: {err}"


# [repo_tests] pass_to_pass
def test_repo_check_inits():
    """Repo's init files check passes (pass_to_pass)."""
    result = subprocess.run(
        ["python", "utils/check_inits.py"],
        capture_output=True, text=True, cwd=REPO, timeout=120,
    )
    err = result.stderr[-500:] if result.stderr else ""
    assert result.returncode == 0, f"check_inits failed: {err}"


# [repo_tests] pass_to_pass
def test_repo_check_dummies():
    """Repo's dummy objects check passes (pass_to_pass)."""
    result = subprocess.run(
        ["python", "utils/check_dummies.py"],
        capture_output=True, text=True, cwd=REPO, timeout=120,
    )
    err = result.stderr[-500:] if result.stderr else ""
    assert result.returncode == 0, f"check_dummies failed: {err}"


# [repo_tests] pass_to_pass
def test_repo_check_modeling_structure():
    """Repo's modeling file structure check passes (pass_to_pass)."""
    result = subprocess.run(
        ["python", "utils/check_modeling_structure.py"],
        capture_output=True, text=True, cwd=REPO, timeout=120,
    )
    err = result.stderr[-500:] if result.stderr else ""
    assert result.returncode == 0, f"check_modeling_structure failed: {err}"


# [repo_tests] pass_to_pass
def test_repo_check_pipeline_typing():
    """Repo's pipeline type hints check passes (pass_to_pass)."""
    result = subprocess.run(
        ["python", "utils/check_pipeline_typing.py"],
        capture_output=True, text=True, cwd=REPO, timeout=120,
    )
    err = result.stderr[-500:] if result.stderr else ""
    assert result.returncode == 0, f"check_pipeline_typing failed: {err}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:2 @ ce4a791
def test_ruff_style_check():
    """configuration_utils.py must pass ruff style checks (AGENTS.md:2)."""
    import shutil
    import pytest
    if not shutil.which("ruff"):
        pytest.skip("ruff not installed")
    result = subprocess.run(
        ["ruff", "check", "src/transformers/configuration_utils.py"],
        capture_output=True, text=True, cwd=REPO,
    )
    assert result.returncode == 0, (
        f"ruff check failed: {result.stdout} {result.stderr}"
    )


# [agent_config] fail_to_pass — .github/copilot-instructions.md:15 @ ce4a791
def test_minimal_diff():
    """Fix should be brief — under 30 lines added (copilot-instructions.md:15)."""
    result = subprocess.run(
        ["git", "diff", "HEAD", "--numstat", "--",
         "src/transformers/configuration_utils.py"],
        capture_output=True, text=True, cwd=REPO,
    )
    numstat = result.stdout.strip()
    if not numstat:
        # Maybe committed
        result = subprocess.run(
            ["git", "diff", "HEAD~1", "--numstat", "--",
             "src/transformers/configuration_utils.py"],
            capture_output=True, text=True, cwd=REPO,
        )
        numstat = result.stdout.strip()

    assert numstat, "No changes detected to configuration_utils.py"
    added = int(numstat.split()[0])
    assert added <= 30, f"Too many lines added ({added}), expected <= 30"


# [repo_tests] pass_to_pass
def test_repo_check_doc_toc():
    """Repo's documentation table of contents check passes (pass_to_pass)."""
    result = subprocess.run(
        ["python", "utils/check_doc_toc.py"],
        capture_output=True, text=True, cwd=REPO, timeout=120,
    )
    err = result.stderr[-500:] if result.stderr else ""
    assert result.returncode == 0, f"check_doc_toc failed: {err}"


# [repo_tests] pass_to_pass
def test_repo_check_doctest_list():
    """Repo's doctest list check passes (pass_to_pass)."""
    result = subprocess.run(
        ["python", "utils/check_doctest_list.py"],
        capture_output=True, text=True, cwd=REPO, timeout=120,
    )
    err = result.stderr[-500:] if result.stderr else ""
    assert result.returncode == 0, f"check_doctest_list failed: {err}"


# [repo_tests] pass_to_pass
def test_repo_check_auto_mappings():
    """Repo's auto mappings sort check passes (pass_to_pass)."""
    result = subprocess.run(
        ["python", "utils/sort_auto_mappings.py", "--check_only"],
        capture_output=True, text=True, cwd=REPO, timeout=120,
    )
    err = result.stderr[-500:] if result.stderr else ""
    assert result.returncode == 0, f"sort_auto_mappings failed: {err}"


# [repo_tests] pass_to_pass
def test_repo_imports():
    """Repo's public imports work correctly (pass_to_pass)."""
    result = subprocess.run(
        ["python", "-c", "from transformers import *"],
        capture_output=True, text=True, cwd=REPO, timeout=60,
    )
    err = result.stderr[-500:] if result.stderr else ""
    assert result.returncode == 0, f"Public imports failed: {err}"
