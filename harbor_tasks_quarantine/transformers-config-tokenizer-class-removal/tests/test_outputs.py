"""
Task: transformers-config-tokenizer-class-removal
Repo: huggingface/transformers @ 18f88de7f575410f3ad8a64418abf2572fecb259
PR:   44971

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
import sys
from pathlib import Path

REPO = "/workspace/transformers"
sys.path.insert(0, f"{REPO}/src")


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """All modified files must parse without syntax errors."""
    for rel in [
        "src/transformers/configuration_utils.py",
        "src/transformers/models/mt5/configuration_mt5.py",
        "src/transformers/models/umt5/configuration_umt5.py",
    ]:
        src = Path(f"{REPO}/{rel}").read_text()
        compile(src, rel, "exec")


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_pretrained_config_no_tokenizer_class():
    """PreTrainedConfig().to_dict() must not contain a default tokenizer_class key."""
    from transformers.configuration_utils import PreTrainedConfig

    for kwargs in [{}, {"hidden_size": 128}, {"num_attention_heads": 4}]:
        config = PreTrainedConfig(**kwargs)
        d = config.to_dict()
        assert "tokenizer_class" not in d, (
            f"tokenizer_class should not appear in default config dict, got: {d.get('tokenizer_class')}"
        )


# [pr_diff] fail_to_pass
def test_mt5_config_no_tokenizer_class():
    """MT5Config must not declare tokenizer_class as a class-level attribute."""
    # AST-only because: MT5Config @auto_docstring decorator requires PyTorch
    src = Path(f"{REPO}/src/transformers/models/mt5/configuration_mt5.py").read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "MT5Config":
            for item in node.body:
                # Check annotated assignments (e.g. tokenizer_class: str = "T5Tokenizer")
                if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                    assert item.target.id != "tokenizer_class", (
                        f"MT5Config still declares tokenizer_class as a class attribute (line {item.lineno})"
                    )
                # Check plain assignments (e.g. tokenizer_class = "T5Tokenizer")
                if isinstance(item, ast.Assign):
                    for target in item.targets:
                        if isinstance(target, ast.Name) and target.id == "tokenizer_class":
                            raise AssertionError(
                                f"MT5Config still declares tokenizer_class as a class attribute (line {item.lineno})"
                            )
            return
    raise AssertionError("MT5Config class not found")


# [pr_diff] fail_to_pass
def test_umt5_config_no_tokenizer_class():
    """UMT5Config must not declare tokenizer_class as a class-level attribute."""
    # AST-only because: UMT5Config @auto_docstring decorator requires PyTorch
    src = Path(f"{REPO}/src/transformers/models/umt5/configuration_umt5.py").read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "UMT5Config":
            for item in node.body:
                # Check annotated assignments (e.g. tokenizer_class: str = "T5Tokenizer")
                if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                    assert item.target.id != "tokenizer_class", (
                        f"UMT5Config still declares tokenizer_class as a class attribute (line {item.lineno})"
                    )
                # Check plain assignments (e.g. tokenizer_class = "T5Tokenizer")
                if isinstance(item, ast.Assign):
                    for target in item.targets:
                        if isinstance(target, ast.Name) and target.id == "tokenizer_class":
                            raise AssertionError(
                                f"UMT5Config still declares tokenizer_class as a class attribute (line {item.lineno})"
                            )
            return
    raise AssertionError("UMT5Config class not found")


# [pr_diff] fail_to_pass
def test_no_tokenizer_base_in_config_module():
    """configuration_utils must not import PreTrainedTokenizerBase at module level."""
    # AST-only because: module is already cached in sys.modules; importlib.reload
    # is fragile with transformers' circular imports, so we check the source directly.
    src = Path(f"{REPO}/src/transformers/configuration_utils.py").read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                assert alias.name != "PreTrainedTokenizerBase", (
                    f"configuration_utils still imports PreTrainedTokenizerBase "
                    f"(line {node.lineno}: from {node.module} import {alias.name})"
                )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / repo_tests) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_config_roundtrip():
    """Config creation, serialization, and round-trip must still work."""
    from transformers.configuration_utils import PreTrainedConfig

    # Basic creation
    c = PreTrainedConfig()
    d = c.to_dict()
    assert "model_type" in d, "model_type missing from dict"

    # Custom params — multiple input combos
    for hidden, heads in [(128, 2), (256, 4), (512, 8)]:
        c = PreTrainedConfig(hidden_size=hidden, num_attention_heads=heads)
        d = c.to_dict()
        assert d["hidden_size"] == hidden
        assert d["num_attention_heads"] == heads

        # from_dict round-trip
        c2 = PreTrainedConfig(**{k: v for k, v in d.items() if k != "transformers_version"})
        assert c2.hidden_size == hidden, "round-trip hidden_size mismatch"


# [pr_diff] pass_to_pass
def test_tokenizer_class_kwarg_passthrough():
    """Users can still pass tokenizer_class as a kwarg — it flows through **kwargs."""
    from transformers.configuration_utils import PreTrainedConfig

    # Multiple different values to prevent hardcoding
    for tc_val in ["MyTokenizer", "GPT2Tokenizer", "LlamaTokenizer"]:
        c = PreTrainedConfig(tokenizer_class=tc_val)
        d = c.to_dict()
        assert d.get("tokenizer_class") == tc_val, (
            f"tokenizer_class kwarg not preserved: expected {tc_val}, got {d.get('tokenizer_class')}"
        )


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — CLAUDE.md:2 @ 18f88de7f575410f3ad8a64418abf2572fecb259
def test_ruff_check_changed_files():
    """ruff check passes on all changed files (CLAUDE.md: make style runs ruff)."""
    changed_files = [
        "src/transformers/configuration_utils.py",
        "src/transformers/models/mt5/configuration_mt5.py",
        "src/transformers/models/umt5/configuration_umt5.py",
    ]
    for f in changed_files:
        r = subprocess.run(
            ["python3", "-m", "ruff", "check", f, "--select=F401,I", "--quiet"],
            cwd=REPO,
            capture_output=True,
            timeout=30,
        )
        assert r.returncode == 0, (
            f"ruff check failed on {f}:\n{r.stdout.decode()}\n{r.stderr.decode()}"
        )


# [agent_config] pass_to_pass — CLAUDE.md:64 @ 18f88de7f575410f3ad8a64418abf2572fecb259
def test_no_cross_model_inheritance():
    """Modified model configs must not directly inherit from other model-specific configs."""
    # AST-only because: checking class hierarchy structure, not runtime behavior
    for rel in [
        "src/transformers/models/mt5/configuration_mt5.py",
        "src/transformers/models/umt5/configuration_umt5.py",
    ]:
        src = Path(f"{REPO}/{rel}").read_text()
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name.endswith("Config"):
                for base in node.bases:
                    base_name = ""
                    if isinstance(base, ast.Name):
                        base_name = base.id
                    elif isinstance(base, ast.Attribute):
                        base_name = base.attr
                    if base_name.endswith("Config") and base_name != "PreTrainedConfig":
                        raise AssertionError(
                            f"{node.name} in {rel} inherits from {base_name}, "
                            f"not PreTrainedConfig (violates no cross-model inheritance)"
                        )


# ---------------------------------------------------------------------------
# Repo CI checks (pass_to_pass) — ensure fix doesn't break existing repo checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass — ruff check on changed files
def test_repo_ruff_changed_files():
    """Repo's ruff linter passes on all changed files (pass_to_pass)."""
    changed_files = [
        "src/transformers/configuration_utils.py",
        "src/transformers/models/mt5/configuration_mt5.py",
        "src/transformers/models/umt5/configuration_umt5.py",
    ]
    for f in changed_files:
        r = subprocess.run(
            ["python3", "-m", "ruff", "check", f],
            cwd=REPO,
            capture_output=True,
            timeout=30,
        )
        assert r.returncode == 0, (
            f"ruff check failed on {f}:\n{r.stdout.decode()}\n{r.stderr.decode()}"
        )


# [repo_tests] pass_to_pass — check_inits ensures __init__ structure is valid
def test_repo_check_inits():
    """Repo's check_inits passes (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "utils/check_inits.py"],
        cwd=REPO,
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, (
        f"check_inits failed:\n{r.stdout.decode()[-500:]}\n{r.stderr.decode()[-500:]}"
    )


# [repo_tests] pass_to_pass — check_copies ensures # Copied from blocks are valid
def test_repo_check_copies():
    """Repo's check_copies passes (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "utils/check_copies.py"],
        cwd=REPO,
        capture_output=True,
        timeout=60,
    )
    assert r.returncode == 0, (
        f"check_copies failed:\n{r.stdout.decode()[-500:]}\n{r.stderr.decode()[-500:]}"
    )


# [repo_tests] pass_to_pass — check_dummies validates dummy model generation
def test_repo_check_dummies():
    """Repo's check_dummies passes (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "utils/check_dummies.py"],
        cwd=REPO,
        capture_output=True,
        timeout=60,
    )
    assert r.returncode == 0, (
        f"check_dummies failed:\n{r.stdout.decode()[-500:]}\n{r.stderr.decode()[-500:]}"
    )


# [repo_tests] pass_to_pass — sort_auto_mappings validates auto mappings are sorted
def test_repo_sort_auto_mappings():
    """Repo's sort_auto_mappings passes (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "utils/sort_auto_mappings.py", "--check_only"],
        cwd=REPO,
        capture_output=True,
        timeout=60,
    )
    assert r.returncode == 0, (
        f"sort_auto_mappings failed:\n{r.stdout.decode()[-500:]}\n{r.stderr.decode()[-500:]}"
    )


# [repo_tests] pass_to_pass — custom_init_isort validates __init__ imports are sorted
def test_repo_custom_init_isort():
    """Repo's custom_init_isort passes (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "utils/custom_init_isort.py", "--check_only"],
        cwd=REPO,
        capture_output=True,
        timeout=60,
    )
    assert r.returncode == 0, (
        f"custom_init_isort failed:\n{r.stdout.decode()[-500:]}\n{r.stderr.decode()[-500:]}"
    )


# [repo_tests] pass_to_pass — check_doc_toc validates documentation TOC
def test_repo_check_doc_toc():
    """Repo's check_doc_toc passes (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "utils/check_doc_toc.py"],
        cwd=REPO,
        capture_output=True,
        timeout=60,
    )
    assert r.returncode == 0, (
        f"check_doc_toc failed:\n{r.stdout.decode()[-500:]}\n{r.stderr.decode()[-500:]}"
    )
