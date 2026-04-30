"""
Task: transformers-camembert-tied-weights
Repo: huggingface/transformers @ d81ad48109331f910fd81f699869855cbd50f681
PR:   45031

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import re
import subprocess
from pathlib import Path

REPO = "/workspace/transformers"

MODELING = Path(REPO) / "src/transformers/models/camembert/modeling_camembert.py"
MODULAR = Path(REPO) / "src/transformers/models/camembert/modular_camembert.py"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_valid():
    """Modified camembert files must parse without syntax errors."""
    for f in [MODELING, MODULAR]:
        if f.exists():
            ast.parse(f.read_text())


# [repo_tests] pass_to_pass
def test_ruff_check():
    """Camembert module passes ruff linting (pass_to_pass)."""
    r = subprocess.run(
        ["ruff", "check", str(MODELING.parent)],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_ruff_format():
    """Camembert module passes ruff format check (pass_to_pass)."""
    r = subprocess.run(
        ["ruff", "format", "--check", str(MODELING.parent)],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_check_copies():
    """Camembert modeling file passes check_copies validation (pass_to_pass)."""
    r = subprocess.run(
        ["python", "utils/check_copies.py", "--file", str(MODELING)],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Check copies failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_init_isort():
    """Init files have correct import ordering (pass_to_pass)."""
    r = subprocess.run(
        ["python", "utils/checkers.py", "init_isort"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Init isort check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_modeling_structure():
    """Modeling files have correct structure (pass_to_pass)."""
    r = subprocess.run(
        ["python", "utils/checkers.py", "modeling_structure"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Modeling structure check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_inits():
    """Init files are correctly structured (pass_to_pass)."""
    r = subprocess.run(
        ["python", "utils/checkers.py", "inits"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Inits check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_dummies():
    """Dummy objects are correctly generated (pass_to_pass)."""
    r = subprocess.run(
        ["python", "utils/checkers.py", "dummies"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Dummies check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_pipeline_typing():
    """Pipeline type hints are correct (pass_to_pass)."""
    r = subprocess.run(
        ["python", "utils/checkers.py", "pipeline_typing"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Pipeline typing check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_config_attributes():
    """Config attributes are correctly defined (pass_to_pass)."""
    r = subprocess.run(
        ["python", "utils/checkers.py", "config_attributes"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Config attributes check failed:\n{r.stdout}\n{r.stderr}"


# [static] pass_to_pass
def test_modeling_file_structure():
    """Camembert modeling files have valid structure and imports (pass_to_pass)."""
    # Verify both modeling files can be parsed and have key components
    for f in [MODELING, MODULAR]:
        content = f.read_text()
        tree = ast.parse(content)

        # Find class definitions
        classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

        # Verify CamembertForCausalLM exists in both files
        assert "CamembertForCausalLM" in classes, f"CamembertForCausalLM not found in {f}"


# [static] pass_to_pass
def test_tied_weights_keys_exists():
    """CamembertForCausalLM has _tied_weights_keys defined (pass_to_pass)."""
    modeling_content = MODELING.read_text()
    modular_content = MODULAR.read_text()

    # Verify _tied_weights_keys exists in modeling file
    assert "_tied_weights_keys" in modeling_content, (
        "_tied_weights_keys not found in modeling_camembert.py"
    )

    # Verify _tied_weights_keys exists in modular file
    assert "_tied_weights_keys" in modular_content, (
        "_tied_weights_keys not found in modular_camembert.py"
    )




# [repo_tests] pass_to_pass
def test_syntax_valid_ast():
    """Modified camembert files must parse without syntax errors via AST (pass_to_pass)."""
    r = subprocess.run(
        [
            "python", "-c",
            "import ast; ast.parse(open('src/transformers/models/camembert/modeling_camembert.py').read()); ast.parse(open('src/transformers/models/camembert/modular_camembert.py').read()); print('Syntax OK')"
        ],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Syntax validation failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_camembert_importable():
    """CamembertForCausalLM can be imported without errors (pass_to_pass)."""
    r = subprocess.run(
        [
            "python", "-c",
            "from transformers.models.camembert.modeling_camembert import CamembertForCausalLM; from transformers.models.camembert.configuration_camembert import CamembertConfig; print('Import successful')"
        ],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Import test failed:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_model_instantiates():
    """CamembertForCausalLM can be created without ValueError on tied weights."""
    from transformers.models.camembert.configuration_camembert import CamembertConfig
    from transformers.models.camembert.modeling_camembert import CamembertForCausalLM

    # Test with multiple config sizes to prevent hardcoding
    for vocab_size, hidden_size in [(100, 32), (200, 64), (50, 16)]:
        config = CamembertConfig(
            vocab_size=vocab_size, hidden_size=hidden_size, num_hidden_layers=2,
            num_attention_heads=2, intermediate_size=hidden_size * 2,
            max_position_embeddings=128,
        )
        model = CamembertForCausalLM(config)
        assert hasattr(model, "lm_head"), "Model must have lm_head attribute"
        assert hasattr(model, "roberta"), "Model must have roberta attribute"


# [pr_diff] fail_to_pass
def test_weight_tying_shares_memory():
    """lm_head.decoder.weight must be the same tensor object as roberta embeddings."""
    from transformers.models.camembert.configuration_camembert import CamembertConfig
    from transformers.models.camembert.modeling_camembert import CamembertForCausalLM

    config = CamembertConfig(
        vocab_size=200, hidden_size=64, num_hidden_layers=2,
        num_attention_heads=2, intermediate_size=128, max_position_embeddings=64,
    )
    model = CamembertForCausalLM(config)

    lm_weight = model.lm_head.decoder.weight
    embed_weight = model.roberta.embeddings.word_embeddings.weight
    assert lm_weight.data_ptr() == embed_weight.data_ptr(), (
        "lm_head.decoder.weight must share memory with "
        "roberta.embeddings.word_embeddings.weight"
    )
    assert lm_weight.shape == embed_weight.shape, (
        f"Shape mismatch: lm_head={lm_weight.shape}, embed={embed_weight.shape}"
    )


# [pr_diff] fail_to_pass
def test_weight_mutation_propagates():
    """Mutating lm_head weight must propagate to embedding weight (proves tying)."""
    import torch
    from transformers.models.camembert.configuration_camembert import CamembertConfig
    from transformers.models.camembert.modeling_camembert import CamembertForCausalLM

    config = CamembertConfig(
        vocab_size=50, hidden_size=16, num_hidden_layers=1,
        num_attention_heads=1, intermediate_size=32, max_position_embeddings=32,
    )
    model = CamembertForCausalLM(config)

    with torch.no_grad():
        # Forward direction: lm_head -> embedding
        model.lm_head.decoder.weight[0, 0] = 12345.0
        assert model.roberta.embeddings.word_embeddings.weight[0, 0].item() == 12345.0, (
            "Weight mutation did not propagate lm_head -> embedding"
        )

        # Reverse direction: embedding -> lm_head
        model.roberta.embeddings.word_embeddings.weight[1, 0] = 99999.0
        assert model.lm_head.decoder.weight[1, 0].item() == 99999.0, (
            "Weight mutation did not propagate embedding -> lm_head"
        )

        # Third value to prevent single-value hardcoding
        model.lm_head.decoder.weight[2, 2] = -42.5
        assert model.roberta.embeddings.word_embeddings.weight[2, 2].item() == -42.5, (
            "Weight mutation did not propagate for third test value"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_other_camembert_models_unaffected():
    """Other Camembert model variants still instantiate and produce output."""
    from transformers.models.camembert.configuration_camembert import CamembertConfig
    from transformers.models.camembert.modeling_camembert import (
        CamembertForMaskedLM,
        CamembertForSequenceClassification,
        CamembertModel,
    )
    import torch

    config = CamembertConfig(
        vocab_size=100, hidden_size=32, num_hidden_layers=2,
        num_attention_heads=2, intermediate_size=64, max_position_embeddings=128,
    )

    # CamembertModel: verify it produces last_hidden_state with correct shape
    base = CamembertModel(config)
    input_ids = torch.randint(0, 100, (1, 10))
    out = base(input_ids)
    assert out.last_hidden_state.shape == (1, 10, 32), (
        f"CamembertModel output shape wrong: {out.last_hidden_state.shape}"
    )

    # CamembertForMaskedLM: verify logits shape
    mlm = CamembertForMaskedLM(config)
    out = mlm(input_ids)
    assert out.logits.shape == (1, 10, 100), (
        f"CamembertForMaskedLM logits shape wrong: {out.logits.shape}"
    )

    # CamembertForSequenceClassification: verify logits shape
    config.num_labels = 3
    cls = CamembertForSequenceClassification(config)
    out = cls(input_ids)
    assert out.logits.shape == (1, 3), (
        f"CamembertForSequenceClassification logits shape wrong: {out.logits.shape}"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — CLAUDE.md:67 @ d81ad48109331f910fd81f699869855cbd50f681
def test_modular_has_roberta_tied_key():
    """modular_camembert.py must override _tied_weights_keys with roberta path.

    CLAUDE.md:67 says modular files are source-of-truth; the fix must be there.
    # AST-only because: modular file is a source template processed by make fix-repo,
    # not directly importable as a standalone module.
    """
    source = MODULAR.read_text()
    # Verify CamembertForCausalLM class defines _tied_weights_keys with "roberta" path
    pattern = (
        r"class\s+CamembertForCausalLM\b.*?"
        r"_tied_weights_keys\s*=\s*\{[^}]*"
        r"roberta\.embeddings\.word_embeddings\.weight"
    )
    assert re.search(pattern, source, re.DOTALL), (
        "CamembertForCausalLM in modular_camembert.py must define "
        "_tied_weights_keys with roberta.embeddings.word_embeddings.weight"
    )
