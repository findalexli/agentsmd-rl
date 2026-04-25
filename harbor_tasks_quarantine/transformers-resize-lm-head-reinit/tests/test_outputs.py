"""
Task: transformers-resize-lm-head-reinit
Repo: huggingface/transformers @ 57e84139542c8c297873f35fcd25f66ffcf132ae
PR:   45079

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import json
import subprocess
import sys
from pathlib import Path

REPO = "/workspace/transformers"

MODELING_UTILS = Path(REPO) / "src/transformers/modeling_utils.py"


# -----------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# -----------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_valid():
    """Modified modeling_utils.py must parse without syntax errors."""
    ast.parse(MODELING_UTILS.read_text())


# -----------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# -----------------------------------------------------------------------------

def _run_python_code(code: str, timeout: int = 60) -> subprocess.CompletedProcess:
    """Execute Python code in a subprocess within the repo environment."""
    return subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=REPO,
        env={"PYTHONPATH": REPO},
    )


# [pr_diff] fail_to_pass
def test_resize_embeddings_weights_preserved_after_post_init():
    """LM head weights are preserved through resize_token_embeddings() then post_init().

    Bug: When tie_word_embeddings=False, calling resize_token_embeddings() then
    post_init() overwrites LM head weights with random values because the new
    nn.Linear does not have _is_hf_initialized set.
    """
    code = """
import torch
import json
from transformers import AutoConfig, AutoModelForCausalLM

# Test with different vocab sizes to prevent hardcoding
for original_vocab, added_tokens in [(100, 10), (200, 20), (50, 5)]:
    config = AutoConfig.from_pretrained(
        "openai-community/gpt2",
        vocab_size=original_vocab,
        n_positions=64,
        n_embd=32,
        n_layer=2,
        n_head=2,
    )
    config.tie_word_embeddings = False

    model = AutoModelForCausalLM.from_config(config)

    # Get initial LM head weights
    lm_head = model.get_output_embeddings()
    weights_before = lm_head.weight.data.clone()
    bias_before = lm_head.bias.data.clone() if lm_head.bias is not None else None

    # Resize embeddings (creates new LM head without _is_hf_initialized)
    model.resize_token_embeddings(original_vocab + added_tokens)

    # Get weights after resize
    lm_head_after_resize = model.get_output_embeddings()
    weights_after_resize = lm_head_after_resize.weight.data.clone()

    # Call post_init() — this is where the bug manifests
    model.post_init()

    # Get weights after post_init
    lm_head_after_post_init = model.get_output_embeddings()
    weights_after_post_init = lm_head_after_post_init.weight.data.clone()

    # The bug: weights would be re-randomized after post_init
    # The fix: weights should be preserved (matching after-resize state)
    if not torch.equal(weights_after_resize, weights_after_post_init):
        max_diff = (weights_after_resize - weights_after_post_init).abs().max().item()
        print(json.dumps({
            "error": f"LM head weights were reinitialized by post_init() after resize. Max diff: {max_diff}",
            "vocab": original_vocab,
            "added": added_tokens
        }))
        exit(1)

    if bias_before is not None:
        bias_after_resize = lm_head_after_resize.bias.data.clone()
        bias_after_post_init = lm_head_after_post_init.bias.data.clone()
        if not torch.equal(bias_after_resize, bias_after_post_init):
            max_diff = (bias_after_resize - bias_after_post_init).abs().max().item()
            print(json.dumps({
                "error": f"LM head bias was reinitialized by post_init() after resize. Max diff: {max_diff}",
                "vocab": original_vocab,
                "added": added_tokens
            }))
            exit(1)

print(json.dumps({"status": "PASS"}))
"""
    result = _run_python_code(code, timeout=120)
    if result.returncode != 0:
        error_msg = result.stderr.strip() or result.stdout.strip()
        raise AssertionError(f"Test failed: {error_msg}")

    try:
        output = json.loads(result.stdout.strip())
        if output.get("status") != "PASS":
            raise AssertionError(f"Test failed: {output.get('error', 'Unknown error')}")
    except json.JSONDecodeError:
        # If no JSON output but returncode was 0, it is probably ok
        if "PASS" not in result.stdout:
            raise AssertionError(f"Unexpected output: {result.stdout[:500]}")


# [pr_diff] fail_to_pass
def test_resize_embeddings_expands_and_shrinks_correctly():
    """LM head weights preserved for both vocab expansion and shrinking."""
    code = """
import torch
import json
from transformers import AutoConfig, AutoModelForCausalLM

for new_vocab_size in [150, 80]:  # expand and shrink
    config = AutoConfig.from_pretrained(
        "openai-community/gpt2",
        vocab_size=100,
        n_positions=64,
        n_embd=32,
        n_layer=2,
        n_head=2,
    )
    config.tie_word_embeddings = False

    model = AutoModelForCausalLM.from_config(config)

    # Resize to new vocab size
    model.resize_token_embeddings(new_vocab_size)

    # Capture weights immediately after resize
    lm_head = model.get_output_embeddings()
    weights_after_resize = lm_head.weight.data.clone()

    # Call post_init — this should NOT reinitialize
    model.post_init()

    # Verify weights unchanged
    weights_after_post_init = model.get_output_embeddings().weight.data.clone()
    if not torch.equal(weights_after_resize, weights_after_post_init):
        print(json.dumps({
            "error": f"Weights changed after post_init for vocab_size={new_vocab_size}",
            "vocab_size": new_vocab_size
        }))
        exit(1)

    # Verify vocab size is correct
    if lm_head.weight.shape[0] != new_vocab_size:
        print(json.dumps({
            "error": f"Expected vocab size {new_vocab_size}, got {lm_head.weight.shape[0]}",
            "expected": new_vocab_size,
            "actual": lm_head.weight.shape[0]
        }))
        exit(1)

print(json.dumps({"status": "PASS"}))
"""
    result = _run_python_code(code, timeout=120)
    if result.returncode != 0:
        error_msg = result.stderr.strip() or result.stdout.strip()
        raise AssertionError(f"Test failed: {error_msg}")

    try:
        output = json.loads(result.stdout.strip())
        if output.get("status") != "PASS":
            raise AssertionError(f"Test failed: {output.get('error', 'Unknown error')}")
    except json.JSONDecodeError:
        if "PASS" not in result.stdout:
            raise AssertionError(f"Unexpected output: {result.stdout[:500]}")


# -----------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# -----------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_import_transformers():
    """Transformers library can be imported without errors (pass_to_pass)."""
    code = """
from transformers import AutoConfig, AutoModelForCausalLM
from transformers.models.gpt2.configuration_gpt2 import GPT2Config
from transformers.models.gpt2.modeling_gpt2 import GPT2LMHeadModel
print("PASS")
"""
    result = _run_python_code(code, timeout=30)
    assert result.returncode == 0, f"Import failed: {result.stderr}"
    assert "PASS" in result.stdout, f"Unexpected output: {result.stdout}"


# [repo_tests] pass_to_pass - CI: check_dummies
def test_repo_check_dummies():
    """Repo dummy objects check passes (pass_to_pass)."""
    result = subprocess.run(
        ["python", "utils/checkers.py", "dummies"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Dummy check failed:\n{result.stdout[-500:]}"


# [repo_tests] pass_to_pass - CI: check_inits
def test_repo_check_inits():
    """Repo init files check passes (pass_to_pass)."""
    result = subprocess.run(
        ["python", "utils/checkers.py", "inits"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Inits check failed:\n{result.stdout[-500:]}"


# [repo_tests] pass_to_pass - CI: check_deps_table
def test_repo_check_deps_table():
    """Repo dependency table check passes (pass_to_pass)."""
    result = subprocess.run(
        ["python", "utils/checkers.py", "deps_table"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Deps table check failed:\n{result.stdout[-500:]}"


# [repo_tests] pass_to_pass - CI: check_pipeline_typing
def test_repo_check_pipeline_typing():
    """Repo pipeline typing check passes (pass_to_pass)."""
    result = subprocess.run(
        ["python", "utils/checkers.py", "pipeline_typing"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Pipeline typing check failed:\n{result.stdout[-500:]}"


# [static] pass_to_pass
def test_fix_is_not_stub():
    """The fix must actually set _is_hf_initialized, not be a no-op."""
    source = MODELING_UTILS.read_text()

    # Verify the fix line exists in _get_resized_lm_head
    # The fix is: new_lm_head._is_hf_initialized = True
    tree = ast.parse(source)

    found_fix = False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_get_resized_lm_head":
            # Check for the assignment in this function
            for stmt in ast.walk(node):
                if isinstance(stmt, ast.Assign):
                    for target in stmt.targets:
                        if isinstance(target, ast.Attribute):
                            if target.attr == "_is_hf_initialized":
                                found_fix = True
                                break

    assert found_fix, (
        "The fix (new_lm_head._is_hf_initialized = True) is not present in "
        "_get_resized_lm_head function"
    )


# [repo_tests] pass_to_pass
def test_tied_embeddings_unaffected():
    """Models with tie_word_embeddings=True still work correctly."""
    code = """
import torch
from transformers import AutoConfig, AutoModelForCausalLM

config = AutoConfig.from_pretrained(
    "openai-community/gpt2",
    vocab_size=100,
    n_positions=64,
    n_embd=32,
    n_layer=2,
    n_head=2,
)
# tie_word_embeddings defaults to True for GPT2

model = AutoModelForCausalLM.from_config(config)

# Verify tied embeddings share memory
lm_head = model.get_output_embeddings()
embeddings = model.get_input_embeddings()
assert lm_head.weight.data_ptr() == embeddings.weight.data_ptr(), "Tied embeddings should share memory"

# Resize should work correctly
model.resize_token_embeddings(120)

# Verify model can still do a forward pass
input_ids = torch.randint(0, 120, (1, 10))
output = model(input_ids)
assert output.logits.shape == (1, 10, 120), f"Expected logits shape (1, 10, 120), got {output.logits.shape}"
print("PASS")
"""
    result = _run_python_code(code, timeout=60)
    assert result.returncode == 0, f"Test failed: {result.stderr}"
    assert "PASS" in result.stdout, f"Unexpected output: {result.stdout}"


# [repo_tests] pass_to_pass
def test_model_forward_pass_works():
    """Basic model inference still works after the fix."""
    code = """
import torch
from transformers import AutoConfig, AutoModelForCausalLM

config = AutoConfig.from_pretrained(
    "openai-community/gpt2",
    vocab_size=100,
    n_positions=64,
    n_embd=32,
    n_layer=2,
    n_head=2,
)
config.tie_word_embeddings = False

model = AutoModelForCausalLM.from_config(config)

# Test forward pass
input_ids = torch.randint(0, 100, (1, 10))
output = model(input_ids)

assert output.logits is not None, "Model output should have logits"
assert output.logits.shape == (1, 10, 100), f"Expected logits shape (1, 10, 100), got {output.logits.shape}"
print("PASS")
"""
    result = _run_python_code(code, timeout=60)
    assert result.returncode == 0, f"Test failed: {result.stderr}"


# [repo_tests] pass_to_pass - CI: check_imports
def test_repo_check_imports():
    """Repo public imports check passes (pass_to_pass)."""
    result = subprocess.run(
        ["python", "utils/checkers.py", "imports"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Imports check failed:\n{result.stdout[-500:]}"


# [repo_tests] pass_to_pass - CI: check_config_docstrings
def test_repo_check_config_docstrings():
    """Repo config docstrings check passes (pass_to_pass)."""
    result = subprocess.run(
        ["python", "utils/checkers.py", "config_docstrings"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Config docstrings check failed:\n{result.stdout[-500:]}"


# [repo_tests] pass_to_pass - CI: check_config_attributes
def test_repo_check_config_attributes():
    """Repo config attributes check passes (pass_to_pass)."""
    result = subprocess.run(
        ["python", "utils/checkers.py", "config_attributes"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Config attributes check failed:\n{result.stdout[-500:]}"


# [repo_tests] pass_to_pass - CI: check_modeling_structure
def test_repo_check_modeling_structure():
    """Repo modeling file structure check passes (pass_to_pass)."""
    result = subprocess.run(
        ["python", "utils/checkers.py", "modeling_structure"],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Modeling structure check failed:\n{result.stdout[-500:]}"


# [repo_tests] pass_to_pass - CI: check_import_complexity
def test_repo_check_import_complexity():
    """Repo import complexity check passes (pass_to_pass)."""
    result = subprocess.run(
        ["python", "utils/checkers.py", "import_complexity"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Import complexity check failed:\\n{result.stdout[-500:]}"


# [repo_tests] pass_to_pass - CI: check_doctest_list
def test_repo_check_doctest_list():
    """Repo doctest list check passes (pass_to_pass)."""
    result = subprocess.run(
        ["python", "utils/checkers.py", "doctest_list"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Doctest list check failed:\\n{result.stdout[-500:]}"


# [repo_tests] pass_to_pass - CI: check_auto_mappings
def test_repo_check_auto_mappings():
    """Repo auto mappings check passes (pass_to_pass)."""
    result = subprocess.run(
        ["python", "utils/checkers.py", "auto_mappings"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Auto mappings check failed:\\n{result.stdout[-500:]}"


# [repo_tests] pass_to_pass - CI: check_init_isort
def test_repo_check_init_isort():
    """Repo init isort check passes (pass_to_pass)."""
    result = subprocess.run(
        ["python", "utils/checkers.py", "init_isort"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Init isort check failed:\\n{result.stdout[-500:]}"


# [repo_tests] pass_to_pass - CI: check_add_dates
def test_repo_check_add_dates():
    """Repo add dates check passes (pass_to_pass)."""
    result = subprocess.run(
        ["python", "utils/checkers.py", "add_dates"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Add dates check failed:\\n{result.stdout[-500:]}"


# [repo_tests] pass_to_pass - CI: check_doc_toc
def test_repo_check_doc_toc():
    """Repo doc TOC check passes (pass_to_pass)."""
    result = subprocess.run(
        ["python", "utils/checkers.py", "doc_toc"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Doc TOC check failed:\\n{result.stdout[-500:]}"
