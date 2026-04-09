"""
Task: transformers-tokenizer-hub-class-missing
Repo: huggingface/transformers @ c55f65056becad6df5f7eef7ce74ac0811fdfac6
PR:   44801

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/transformers"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """tokenization_auto.py must parse without syntax errors."""
    import py_compile

    py_compile.compile(
        f"{REPO}/src/transformers/models/auto/tokenization_auto.py",
        doraise=True,
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_deepseek_v2_in_incorrect_hub_set():
    """deepseek_v2 must be in MODELS_WITH_INCORRECT_HUB_TOKENIZER_CLASS."""
    from transformers.models.auto.tokenization_auto import (
        MODELS_WITH_INCORRECT_HUB_TOKENIZER_CLASS,
    )

    assert "deepseek_v2" in MODELS_WITH_INCORRECT_HUB_TOKENIZER_CLASS


# [pr_diff] fail_to_pass
def test_deepseek_v3_in_incorrect_hub_set():
    """deepseek_v3 must be in MODELS_WITH_INCORRECT_HUB_TOKENIZER_CLASS."""
    from transformers.models.auto.tokenization_auto import (
        MODELS_WITH_INCORRECT_HUB_TOKENIZER_CLASS,
    )

    assert "deepseek_v3" in MODELS_WITH_INCORRECT_HUB_TOKENIZER_CLASS


# [pr_diff] fail_to_pass
def test_modernbert_in_incorrect_hub_set():
    """modernbert must be in MODELS_WITH_INCORRECT_HUB_TOKENIZER_CLASS."""
    from transformers.models.auto.tokenization_auto import (
        MODELS_WITH_INCORRECT_HUB_TOKENIZER_CLASS,
    )

    assert "modernbert" in MODELS_WITH_INCORRECT_HUB_TOKENIZER_CLASS


# [pr_diff] fail_to_pass
def test_new_models_resolve_in_tokenizer_mapping():
    """All three new model types must have entries in TOKENIZER_MAPPING_NAMES."""
    from transformers.models.auto.tokenization_auto import TOKENIZER_MAPPING_NAMES

    for model_type in ("deepseek_v2", "deepseek_v3", "modernbert"):
        entry = TOKENIZER_MAPPING_NAMES.get(model_type)
        assert entry is not None, f"{model_type} not in TOKENIZER_MAPPING_NAMES"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_incorrect_hub_entries_preserved():
    """Pre-existing entries in the override set must not be removed."""
    from transformers.models.auto.tokenization_auto import (
        MODELS_WITH_INCORRECT_HUB_TOKENIZER_CLASS,
    )

    existing = [
        "arctic",
        "chameleon",
        "deepseek_vl",
        "deepseek_vl_v2",
        "fuyu",
        "jamba",
        "llava",
        "phi3",
    ]
    for m in existing:
        assert m in MODELS_WITH_INCORRECT_HUB_TOKENIZER_CLASS, (
            f"Regression: {m} removed from set"
        )


# [repo_tests] pass_to_pass
def test_core_tokenizer_mapping_entries_intact():
    """Core model types (bert, gpt2, etc.) must still be in TOKENIZER_MAPPING_NAMES."""
    from transformers.models.auto.tokenization_auto import TOKENIZER_MAPPING_NAMES

    for model_type in ("bert", "gpt2", "roberta", "t5"):
        assert model_type in TOKENIZER_MAPPING_NAMES, (
            f"Regression: {model_type} missing from TOKENIZER_MAPPING_NAMES"
        )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from CLAUDE.md / copilot-instructions.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — CLAUDE.md:2 @ c55f65056becad6df5f7eef7ce74ac0811fdfac6
def test_ruff_format():
    """Code passes ruff format check (CLAUDE.md style rule)."""
    r = subprocess.run(
        [
            "python3",
            "-m",
            "ruff",
            "format",
            "--check",
            "--quiet",
            "src/transformers/models/auto/tokenization_auto.py",
        ],
        cwd=REPO,
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, f"ruff format failed:\n{r.stderr.decode()}"


# [agent_config] pass_to_pass — CLAUDE.md:2 @ c55f65056becad6df5f7eef7ce74ac0811fdfac6
def test_ruff_lint():
    """Code passes ruff lint check (make style runs linters per CLAUDE.md)."""
    r = subprocess.run(
        [
            "python3",
            "-m",
            "ruff",
            "check",
            "--quiet",
            "src/transformers/models/auto/tokenization_auto.py",
        ],
        cwd=REPO,
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, f"ruff check failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"


# [agent_config] pass_to_pass — CLAUDE.md:65 @ c55f65056becad6df5f7eef7ce74ac0811fdfac6
def test_no_copied_from_blocks_modified():
    """'# Copied from' blocks must not be edited (CLAUDE.md rule)."""
    r = subprocess.run(
        ["git", "diff", "HEAD"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=15,
    )
    for line in r.stdout.splitlines():
        if line.startswith(("+", "-")) and not line.startswith(("+++", "---")):
            assert "# Copied from" not in line, (
                "A '# Copied from' block was modified"
            )


# ---------------------------------------------------------------------------
# Additional pass_to_pass (repo_tests) — CI/CD gates discovered from Makefile
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass — auto mappings sorted
def test_repo_sort_auto_mappings():
    """Auto mappings must be sorted (make check-repo style gate)."""
    r = subprocess.run(
        ["python", "utils/sort_auto_mappings.py", "--check_only"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"sort_auto_mappings check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass — tokenization_auto imports work
def test_repo_tokenization_auto_imports():
    """Tokenization auto module imports must work (repo import check)."""
    r = subprocess.run(
        [
            "python",
            "-c",
            "from transformers.models.auto.tokenization_auto import "
            "TOKENIZER_MAPPING_NAMES, MODELS_WITH_INCORRECT_HUB_TOKENIZER_CLASS; "
            "assert len(TOKENIZER_MAPPING_NAMES) > 0; "
            "assert len(MODELS_WITH_INCORRECT_HUB_TOKENIZER_CLASS) > 0",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Tokenization auto imports failed:\n{r.stderr}"
