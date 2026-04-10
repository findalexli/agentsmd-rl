"""
Task: transformers-granite-config-int-multiplier
Repo: huggingface/transformers @ 7b00e3ba398d355d5f277a4896743b16f21049eb

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import tempfile

import pytest

REPO = "/repo"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """All three Granite config files must parse without errors."""
    import py_compile

    for f in [
        "src/transformers/models/granite/configuration_granite.py",
        "src/transformers/models/granitemoe/configuration_granitemoe.py",
        "src/transformers/models/granitemoeshared/configuration_granitemoeshared.py",
    ]:
        py_compile.compile(f"{REPO}/{f}", doraise=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("em,ls,rm,am", [
    (12, 8, 4, 2),
    (1, 100, 0, 50),
    (7, 3, 11, 99),
])
# [pr_diff] fail_to_pass
def test_granite_config_accepts_int_multipliers(em, ls, rm, am):
    """GraniteConfig must accept integer multiplier fields without error."""
    from transformers import GraniteConfig

    c = GraniteConfig(
        embedding_multiplier=em,
        logits_scaling=ls,
        residual_multiplier=rm,
        attention_multiplier=am,
    )
    assert c.embedding_multiplier == em
    assert c.logits_scaling == ls
    assert c.residual_multiplier == rm
    assert c.attention_multiplier == am


@pytest.mark.parametrize("em,ls", [
    (15, 9),
    (0, 1),
    (42, 7),
])
# [pr_diff] fail_to_pass
def test_granite_config_int_roundtrip(em, ls):
    """GraniteConfig with int values survives save_pretrained / from_pretrained."""
    from transformers import GraniteConfig

    c = GraniteConfig(embedding_multiplier=em, logits_scaling=ls)
    with tempfile.TemporaryDirectory() as d:
        c.save_pretrained(d)
        loaded = GraniteConfig.from_pretrained(d)
    assert loaded.embedding_multiplier == em
    assert loaded.logits_scaling == ls


@pytest.mark.parametrize("em,ls,rm,am", [
    (10, 5, 7, 3),
    (2, 20, 0, 8),
    (33, 1, 6, 14),
])
# [pr_diff] fail_to_pass
def test_granitemoe_config_accepts_int_multipliers(em, ls, rm, am):
    """GraniteMoeConfig must accept integer multiplier fields."""
    from transformers import GraniteMoeConfig

    c = GraniteMoeConfig(
        embedding_multiplier=em,
        logits_scaling=ls,
        residual_multiplier=rm,
        attention_multiplier=am,
    )
    assert c.embedding_multiplier == em
    assert c.logits_scaling == ls
    assert c.residual_multiplier == rm
    assert c.attention_multiplier == am


@pytest.mark.parametrize("em,ls", [
    (10, 6),
    (0, 4),
    (55, 12),
])
# [pr_diff] fail_to_pass
def test_granitemoe_config_int_roundtrip(em, ls):
    """GraniteMoeConfig int values survive save/load roundtrip."""
    from transformers import GraniteMoeConfig

    c = GraniteMoeConfig(embedding_multiplier=em, logits_scaling=ls)
    with tempfile.TemporaryDirectory() as d:
        c.save_pretrained(d)
        loaded = GraniteMoeConfig.from_pretrained(d)
    assert loaded.embedding_multiplier == em
    assert loaded.logits_scaling == ls


@pytest.mark.parametrize("em,ls,rm,am", [
    (11, 9, 5, 2),
    (3, 25, 0, 17),
    (8, 4, 16, 32),
])
# [pr_diff] fail_to_pass
def test_granitemoeshared_config_accepts_int_multipliers(em, ls, rm, am):
    """GraniteMoeSharedConfig must accept integer multiplier fields."""
    from transformers import GraniteMoeSharedConfig

    c = GraniteMoeSharedConfig(
        embedding_multiplier=em,
        logits_scaling=ls,
        residual_multiplier=rm,
        attention_multiplier=am,
    )
    assert c.embedding_multiplier == em
    assert c.logits_scaling == ls
    assert c.residual_multiplier == rm
    assert c.attention_multiplier == am


@pytest.mark.parametrize("em,ls", [
    (7, 3),
    (0, 5),
    (18, 9),
])
# [pr_diff] fail_to_pass
def test_granitemoeshared_config_int_roundtrip(em, ls):
    """GraniteMoeSharedConfig int values survive save/load roundtrip."""
    from transformers import GraniteMoeSharedConfig

    c = GraniteMoeSharedConfig(embedding_multiplier=em, logits_scaling=ls)
    with tempfile.TemporaryDirectory() as d:
        c.save_pretrained(d)
        loaded = GraniteMoeSharedConfig.from_pretrained(d)
    assert loaded.embedding_multiplier == em
    assert loaded.logits_scaling == ls


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression: float still works
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_granite_config_float_defaults():
    """Existing float-based configs must still load correctly."""
    from transformers import GraniteConfig

    c = GraniteConfig()
    assert c.embedding_multiplier == 1.0
    assert c.logits_scaling == 1.0
    assert c.residual_multiplier == 1.0
    assert c.attention_multiplier == 1.0


# [pr_diff] pass_to_pass
def test_granite_config_explicit_float_roundtrip():
    """Explicit float values still accepted and survive roundtrip."""
    from transformers import GraniteConfig

    c = GraniteConfig(embedding_multiplier=1.5, logits_scaling=2.0)
    with tempfile.TemporaryDirectory() as d:
        c.save_pretrained(d)
        loaded = GraniteConfig.from_pretrained(d)
    assert loaded.embedding_multiplier == 1.5
    assert loaded.logits_scaling == 2.0


# [pr_diff] pass_to_pass
def test_granitemoe_config_none_multipliers():
    """GraniteMoeConfig fields that allow None must still accept None after the fix."""
    from transformers import GraniteMoeConfig

    c = GraniteMoeConfig(
        embedding_multiplier=None,
        logits_scaling=None,
        residual_multiplier=None,
        attention_multiplier=None,
    )
    assert c.embedding_multiplier is None
    assert c.logits_scaling is None
    assert c.residual_multiplier is None
    assert c.attention_multiplier is None


# [pr_diff] pass_to_pass
def test_granitemoeshared_config_none_multipliers():
    """GraniteMoeSharedConfig fields that allow None must still accept None after the fix."""
    from transformers import GraniteMoeSharedConfig

    c = GraniteMoeSharedConfig(
        embedding_multiplier=None,
        logits_scaling=None,
    )
    assert c.embedding_multiplier is None
    assert c.logits_scaling is None


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from CLAUDE.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — CLAUDE.md:2 @ 7b00e3ba398d355d5f277a4896743b16f21049eb
def test_ruff_check_clean():
    """ruff check passes on all three modified config files."""
    r = subprocess.run(
        [
            "ruff", "check",
            "src/transformers/models/granite/configuration_granite.py",
            "src/transformers/models/granitemoe/configuration_granitemoe.py",
            "src/transformers/models/granitemoeshared/configuration_granitemoeshared.py",
        ],
        cwd=REPO,
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, f"ruff check failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Repo CI/CD pass_to_pass gates — ensure existing tests still pass
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass — Granite model tests
def test_repo_granite_config():
    """Granite base config test passes (pass_to_pass)."""
    r = subprocess.run(
        [
            "python", "-m", "pytest",
            "tests/models/granite/test_modeling_granite.py::GraniteModelTest::test_config",
            "-v", "--timeout=60",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Granite config test failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — GraniteMoe model tests
def test_repo_granitemoe_config():
    """GraniteMoe config test passes (pass_to_pass)."""
    r = subprocess.run(
        [
            "python", "-m", "pytest",
            "tests/models/granitemoe/test_modeling_granitemoe.py::GraniteMoeModelTest::test_config",
            "-v", "--timeout=60",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"GraniteMoe config test failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — GraniteMoeShared model tests
def test_repo_granitemoeshared_config():
    """GraniteMoeShared config test passes (pass_to_pass)."""
    r = subprocess.run(
        [
            "python", "-m", "pytest",
            "tests/models/granitemoeshared/test_modeling_granitemoeshared.py::GraniteMoeSharedModelTest::test_config",
            "-v", "--timeout=60",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"GraniteMoeShared config test failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — ruff format check
def test_repo_ruff_format():
    """Modified config files are properly formatted (pass_to_pass)."""
    r = subprocess.run(
        [
            "ruff", "format", "--check",
            "src/transformers/models/granite/configuration_granite.py",
            "src/transformers/models/granitemoe/configuration_granitemoe.py",
            "src/transformers/models/granitemoeshared/configuration_granitemoeshared.py",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"ruff format check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass — Config utils tests (lightweight, config-focused)
def test_repo_config_utils():
    """Configuration utils tests pass (pass_to_pass)."""
    r = subprocess.run(
        [
            "python", "-m", "pytest",
            "tests/utils/test_configuration_utils.py",
            "-v", "--timeout=60", "-x",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert r.returncode == 0, f"Config utils tests failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — Granite tensor registration test
def test_repo_granite_tensor_registration():
    """Granite model tensor registration test passes (pass_to_pass)."""
    r = subprocess.run(
        [
            "python", "-m", "pytest",
            "tests/models/granite/test_modeling_granite.py::GraniteModelTest::test_all_tensors_are_parameter_or_buffer",
            "-v", "--timeout=120",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=200,
    )
    assert r.returncode == 0, f"Granite tensor registration test failed:\n{r.stderr[-500:]}"
