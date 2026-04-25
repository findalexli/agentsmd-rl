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


# [repo_tests] pass_to_pass — check_copies.py ensures Copied from blocks are consistent
def test_repo_check_copies():
    """Copied from blocks are consistent (repo consistency check)."""
    r = subprocess.run(
        ["python", "utils/check_copies.py"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"check_copies failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass — check_dummies.py ensures dummy objects are correctly defined
def test_repo_check_dummies():
    """Dummy objects are correctly defined (repo consistency check)."""
    r = subprocess.run(
        ["python", "utils/check_dummies.py"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"check_dummies failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass — check_inits.py ensures __init__ files are correctly set up
def test_repo_check_inits():
    """__init__ files are correctly set up (repo consistency check)."""
    r = subprocess.run(
        ["python", "utils/check_inits.py"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"check_inits failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass — ruff check on auto directory
def test_repo_ruff_auto_dir():
    """Ruff check passes on transformers/models/auto/ directory."""
    r = subprocess.run(
        ["python3", "-m", "ruff", "check", "src/transformers/models/auto/"],
        cwd=REPO,
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, f"ruff check on auto dir failed:\n{r.stderr.decode()}"


# [repo_tests] pass_to_pass — check_doc_toc.py ensures documentation TOC is valid
def test_repo_check_doc_toc():
    """Documentation TOC is valid (repo consistency check)."""
    r = subprocess.run(
        ["python", "utils/check_doc_toc.py"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"check_doc_toc failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass — tokenizer mapping structure unit test
def test_repo_tokenizer_mapping_structure():
    """Tokenizer mapping names structure is valid (unit test from test_tokenization_auto.py)."""
    r = subprocess.run(
        [
            "python",
            "-c",
            "from tests.models.auto.test_tokenization_auto import AutoTokenizerTest; "
            "t = AutoTokenizerTest(); "
            "t.test_tokenizer_mapping_names_use_single_entries(); "
            "print('PASS')",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0 and "PASS" in r.stdout, f"Test failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass — model name edge cases in mappings
def test_repo_model_name_edge_cases():
    """Model name edge cases in tokenizer mappings are handled correctly."""
    r = subprocess.run(
        [
            "python",
            "-c",
            "from tests.models.auto.test_tokenization_auto import AutoTokenizerTest; "
            "t = AutoTokenizerTest(); "
            "t.test_model_name_edge_cases_in_mappings(); "
            "print('PASS')",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0 and "PASS" in r.stdout, f"Test failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass — check_config_attributes.py
def test_repo_check_config_attributes():
    """Config attributes are correctly documented (repo consistency check)."""
    r = subprocess.run(
        ["python", "utils/check_config_attributes.py"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"check_config_attributes failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass — check_config_docstrings.py
def test_repo_check_config_docstrings():
    """Config docstrings are correctly formatted (repo consistency check)."""
    r = subprocess.run(
        ["python", "utils/check_config_docstrings.py"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"check_config_docstrings failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass — check_pipeline_typing.py
def test_repo_check_pipeline_typing():
    """Pipeline typing is correctly defined (repo consistency check)."""
    r = subprocess.run(
        ["python", "utils/check_pipeline_typing.py"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"check_pipeline_typing failed:\n{r.stdout}\n{r.stderr}"
