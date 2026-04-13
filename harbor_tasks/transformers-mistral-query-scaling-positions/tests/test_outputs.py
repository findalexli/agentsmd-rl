"""
Task: transformers-mistral-query-scaling-positions
Repo: huggingface/transformers @ e94695e574f969ba5eeb8e442a7fb1e9f72ff37f
PR:   44860

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
from pathlib import Path

REPO = "/workspace/transformers"

AFFECTED_FILES = [
    "src/transformers/models/ministral3/modeling_ministral3.py",
    "src/transformers/models/ministral3/modular_ministral3.py",
    "src/transformers/models/mistral4/modeling_mistral4.py",
    "src/transformers/models/mistral4/modular_mistral4.py",
]

MODELING_FILES = {
    "ministral3": "src/transformers/models/ministral3/modeling_ministral3.py",
    "mistral4": "src/transformers/models/mistral4/modeling_mistral4.py",
}

MODULAR_FILES = {
    "ministral3": "src/transformers/models/ministral3/modular_ministral3.py",
    "mistral4": "src/transformers/models/mistral4/modular_mistral4.py",
}


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Write code to a temp file and execute via python3 in the repo directory."""
    script = Path(f"{REPO}/_eval_tmp.py")
    script.write_text(code)
    try:
        return subprocess.run(
            ["python3", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# -----------------------------------------------------------------------------
# Pass-to-pass (static) — syntax / compilation checks
# -----------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """All four affected files parse without syntax errors."""
    for f in AFFECTED_FILES:
        src = Path(f"{REPO}/{f}").read_text()
        ast.parse(src)


# [static] pass_to_pass
def test_not_stub():
    """get_llama_4_attn_scale in both modeling files has real computation (not a stub)."""
    for model, f in MODELING_FILES.items():
        src = Path(f"{REPO}/{f}").read_text()
        tree = ast.parse(src)
        found = False
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "get_llama_4_attn_scale":
                found = True
                real_stmts = [
                    s for s in node.body
                    if not (isinstance(s, ast.Expr) and isinstance(getattr(s, "value", None), ast.Constant))
                ]
                assert len(real_stmts) >= 2, (
                    f"{model}: get_llama_4_attn_scale appears stubbed ({len(real_stmts)} statements)"
                )
                break
        assert found, f"{model}: get_llama_4_attn_scale not found in {f}"


# [repo_tests] pass_to_pass
def test_repo_imports():
    """Repo modeling modules import without errors (pass_to_pass)."""
    r = _run_py(f"""
import sys
sys.path.insert(0, "{REPO}/src")
from transformers.models.ministral3.modeling_ministral3 import get_llama_4_attn_scale
from transformers.models.ministral3.modular_ministral3 import get_llama_4_attn_scale as _
from transformers.models.mistral4.modeling_mistral4 import get_llama_4_attn_scale as __
from transformers.models.mistral4.modular_mistral4 import get_llama_4_attn_scale as ___
print("PASS")
""")
    assert r.returncode == 0, f"Repo imports failed: {r.stderr}"
    assert "PASS" in r.stdout


# [repo_tests] pass_to_pass - CI-style imports check for all affected modules
def test_repo_ci_imports():
    """CI-style import check: verify all affected modeling modules can be imported (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-c",
         f"import sys; sys.path.insert(0, '{REPO}/src'); "
         "from transformers.models.ministral3.modeling_ministral3 import get_llama_4_attn_scale; "
         "from transformers.models.ministral3.modular_ministral3 import get_llama_4_attn_scale as _; "
         "from transformers.models.mistral4.modeling_mistral4 import get_llama_4_attn_scale as __; "
         "from transformers.models.mistral4.modular_mistral4 import get_llama_4_attn_scale as ___; "
         "print('IMPORTS_OK')"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"CI import check failed: {r.stderr}"
    assert "IMPORTS_OK" in r.stdout


# [repo_tests] pass_to_pass - AST verification that function exists in all files
def test_repo_function_existence():
    """AST check: get_llama_4_attn_scale exists in all expected files (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-c",
         f"""
import ast
import sys
from pathlib import Path

files = [
    "{REPO}/src/transformers/models/ministral3/modeling_ministral3.py",
    "{REPO}/src/transformers/models/ministral3/modular_ministral3.py",
    "{REPO}/src/transformers/models/mistral4/modeling_mistral4.py",
]

missing = []
for f in files:
    src = Path(f).read_text()
    tree = ast.parse(src)
    found = any(node.name == "get_llama_4_attn_scale" for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))
    if not found:
        missing.append(f)

if missing:
    print(f"MISSING: {{missing}}")
    sys.exit(1)
print("ALL_FUNCTIONS_FOUND")
"""],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Function existence check failed: {r.stderr}"
    assert "ALL_FUNCTIONS_FOUND" in r.stdout


# [repo_tests] pass_to_pass - Modular file imports the function correctly
def test_repo_mistral4_modular_import():
    """Verify modular_mistral4.py correctly imports get_llama_4_attn_scale from ministral3 (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-c",
         f"""
import ast
from pathlib import Path

src = Path("{REPO}/src/transformers/models/mistral4/modular_mistral4.py").read_text()
tree = ast.parse(src)

# Check for 'from ..ministral3.modeling_ministral3 import get_llama_4_attn_scale'
# AST stores this as module='ministral3.modeling_ministral3'
found_import = False
for node in ast.walk(tree):
    if isinstance(node, ast.ImportFrom):
        if node.module and "modeling_ministral3" in node.module:
            for alias in node.names:
                if alias.name == "get_llama_4_attn_scale":
                    found_import = True
                    break

if not found_import:
    print("IMPORT_NOT_FOUND")
else:
    print("IMPORT_OK")
"""],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Modular import check failed: {r.stderr}"
    assert "IMPORT_OK" in r.stdout


# -----------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests via subprocess
# -----------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_ministral3_modeling_scale_shape():
    """get_llama_4_attn_scale in ministral3/modeling returns 4D tensor (B,1,S,1) for varied input shapes."""
    code = f"""
import torch
import sys
sys.path.insert(0, "{REPO}/src")
from transformers.models.ministral3.modeling_ministral3 import get_llama_4_attn_scale

for B, S in [(1, 3), (2, 4), (3, 1)]:
    pos = torch.randint(0, 128, (B, S))
    result = get_llama_4_attn_scale(pos, beta=0.1, max_position_embeddings=4)
    assert result.ndim == 4, f"Expected 4D, got {{result.ndim}}D with shape {{result.shape}}"
    assert result.shape == (B, 1, S, 1), f"Expected ({{B}},1,{{S}},1), got {{result.shape}}"

print("PASS")
"""
    r = _run_py(code)
    assert r.returncode == 0, f"ministral3 scale shape test failed: {{r.stderr}}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_mistral4_modeling_scale_shape():
    """get_llama_4_attn_scale in mistral4/modeling returns 4D tensor (B,1,S,1) for varied input shapes."""
    code = f"""
import torch
import sys
sys.path.insert(0, "{REPO}/src")
from transformers.models.mistral4.modeling_mistral4 import get_llama_4_attn_scale

for B, S in [(1, 3), (2, 3), (2, 1)]:
    pos = torch.randint(0, 256, (B, S))
    result = get_llama_4_attn_scale(pos, beta=0.1, max_position_embeddings=64)
    assert result.ndim == 4, f"Expected 4D, got {{result.ndim}}D with shape {{result.shape}}"
    assert result.shape == (B, 1, S, 1), f"Expected ({{B}},1,{{S}},1), got {{result.shape}}"

print("PASS")
"""
    r = _run_py(code)
    assert r.returncode == 0, f"mistral4 scale shape test failed: {{r.stderr}}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_scaling_formula_values():
    """Scaling formula 1+beta*log(1+floor(pos/max_pos)) matches expected values at 5 diverse positions."""
    code = f"""
import torch
import math
import sys
sys.path.insert(0, "{REPO}/src")
from transformers.models.ministral3.modeling_ministral3 import get_llama_4_attn_scale

beta = 0.1
max_pos = 64
pos = torch.tensor([[0, 64, 128, 256, 384]])

result = get_llama_4_attn_scale(pos, beta=beta, max_position_embeddings=max_pos)

assert result.shape == (1, 1, 5, 1), f"Expected (1,1,5,1), got {{result.shape}}"

expected = [
    1.0,                          # floor(0/64)=0,   log(1+0)=0
    1.0 + 0.1 * math.log(2),     # floor(64/64)=1,  log(1+1)=ln(2)
    1.0 + 0.1 * math.log(3),     # floor(128/64)=2, log(1+2)=ln(3)
    1.0 + 0.1 * math.log(5),     # floor(256/64)=4, log(1+4)=ln(5)
    1.0 + 0.1 * math.log(7),     # floor(384/64)=6, log(1+6)=ln(7)
]
for i, exp in enumerate(expected):
    got = result[0, 0, i, 0].item()
    assert abs(got - exp) < 1e-4, f"pos={{pos[0, i].item()}}: expected {{exp:.4f}}, got {{got:.4f}}"

print("PASS")
"""
    r = _run_py(code)
    assert r.returncode == 0, f"Scaling formula test failed: {{r.stderr}}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_per_batch_scaling_differs():
    """Different position_ids per batch item produce different scaling values and correct 4D shape."""
    code = f"""
import torch
import sys
sys.path.insert(0, "{REPO}/src")
from transformers.models.mistral4.modeling_mistral4 import get_llama_4_attn_scale

pos = torch.tensor([[0, 1, 2, 3], [100, 101, 102, 103]])
result = get_llama_4_attn_scale(pos, beta=0.1, max_position_embeddings=64)

assert result.ndim == 4, f"Expected 4D, got {{result.ndim}}D"
assert result.shape == (2, 1, 4, 1), f"Expected (2,1,4,1), got {{result.shape}}"

batch0 = result[0, 0, :, 0]
batch1 = result[1, 0, :, 0]

assert (batch0 - 1.0).abs().max() < 1e-5, f"Batch 0 (pos 0-3) should all be 1.0, got {{batch0}}"
assert (batch1 > 1.0).all(), f"Batch 1 (pos 100-103) should all be >1.0, got {{batch1}}"
assert not torch.allclose(batch0, batch1), "Batches must produce different scaling values"

print("PASS")
"""
    r = _run_py(code)
    assert r.returncode == 0, f"Per-batch scaling test failed: {{r.stderr}}"
    assert "PASS" in r.stdout


# -----------------------------------------------------------------------------
# Fail-to-pass (agent_config) — modular file requirements from .ai/AGENTS.md
# -----------------------------------------------------------------------------

# [agent_config] fail_to_pass — .ai/AGENTS.md:66 @ e94695e574f969ba5eeb8e442a7fb1e9f72ff37f
def test_ministral3_modular_scale_shape():
    """get_llama_4_attn_scale in modular_ministral3.py is also fixed to return 4D tensor."""
    code = f"""
import torch
import sys
sys.path.insert(0, "{REPO}/src")
from transformers.models.ministral3.modular_ministral3 import get_llama_4_attn_scale

for B, S in [(1, 3), (2, 2), (1, 5)]:
    pos = torch.randint(0, 32, (B, S))
    result = get_llama_4_attn_scale(pos, beta=0.1, max_position_embeddings=4)
    assert result.ndim == 4, f"Expected 4D, got {{result.ndim}}D ({{result.shape}})"
    assert result.shape == (B, 1, S, 1), f"Expected ({{B}},1,{{S}},1), got {{result.shape}}"

print("PASS")
"""
    r = _run_py(code)
    assert r.returncode == 0, f"Ministral3 modular scale shape test failed: {{r.stderr}}"
    assert "PASS" in r.stdout


# [agent_config] fail_to_pass — .ai/AGENTS.md:66 @ e94695e574f969ba5eeb8e442a7fb1e9f72ff37f
def test_mistral4_modular_scale_shape():
    """get_llama_4_attn_scale in modular_mistral4.py is also fixed to return 4D tensor."""
    code = f"""
import torch
import sys
sys.path.insert(0, "{REPO}/src")
from transformers.models.mistral4.modular_mistral4 import get_llama_4_attn_scale

for B, S in [(1, 3), (2, 2), (1, 5)]:
    pos = torch.randint(0, 32, (B, S))
    result = get_llama_4_attn_scale(pos, beta=0.1, max_position_embeddings=4)
    assert result.ndim == 4, f"Expected 4D, got {{result.ndim}}D ({{result.shape}})"
    assert result.shape == (B, 1, S, 1), f"Expected ({{B}},1,{{S}},1), got {{result.shape}}"

print("PASS")
"""
    r = _run_py(code)
    assert r.returncode == 0, f"Mistral4 modular scale shape test failed: {{r.stderr}}"
    assert "PASS" in r.stdout


# [agent_config] fail_to_pass — .ai/AGENTS.md:66 @ e94695e574f969ba5eeb8e442a7fb1e9f72ff37f
def test_ministral3_modular_no_absolute_positions():
    """Ministral3 modular forward() no longer computes absolute_positions from cache; uses position_ids directly."""
    code = f"""
import ast
import sys
from pathlib import Path

src = Path("{REPO}/src/transformers/models/ministral3/modular_ministral3.py").read_text()
tree = ast.parse(src)

# Find Ministral3Attention.forward method
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "Ministral3Attention":
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "forward":
                forward_src = "\\n".join(src.splitlines()[item.lineno-1:item.end_lineno])
                if "absolute_positions" in forward_src:
                    print("FAIL: modular_ministral3.py forward() still uses absolute_positions")
                    sys.exit(1)
                if "position_ids" not in forward_src:
                    print("FAIL: modular_ministral3.py forward() does not accept position_ids parameter")
                    sys.exit(1)
                print("PASS")
                sys.exit(0)

print("FAIL: Could not find Ministral3Attention.forward")
sys.exit(1)
"""
    r = _run_py(code)
    assert r.returncode == 0, f"Ministral3 modular absolute_positions check failed: {{r.stderr}}"
    assert "PASS" in r.stdout


# [agent_config] fail_to_pass — .ai/AGENTS.md:66 @ e94695e574f969ba5eeb8e442a7fb1e9f72ff37f
def test_mistral4_modular_no_absolute_positions():
    """Mistral4 modular forward() no longer computes absolute_positions from cache; uses position_ids directly."""
    code = f"""
import ast
import sys
from pathlib import Path

src = Path("{REPO}/src/transformers/models/mistral4/modular_mistral4.py").read_text()
tree = ast.parse(src)

# Find Mistral4Attention.forward method
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "Mistral4Attention":
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "forward":
                forward_src = "\\n".join(src.splitlines()[item.lineno-1:item.end_lineno])
                if "absolute_positions" in forward_src:
                    print("FAIL: modular_mistral4.py forward() still uses absolute_positions")
                    sys.exit(1)
                if "position_ids" not in forward_src:
                    print("FAIL: modular_mistral4.py forward() does not accept position_ids parameter")
                    sys.exit(1)
                print("PASS")
                sys.exit(0)

print("FAIL: Could not find Mistral4Attention.forward")
sys.exit(1)
"""
    r = _run_py(code)
    assert r.returncode == 0, f"Mistral4 modular absolute_positions check failed: {{r.stderr}}"
    assert "PASS" in r.stdout


# -----------------------------------------------------------------------------
# Additional Pass-to-pass (repo_tests) — CI-style quality checks
# -----------------------------------------------------------------------------


# [repo_tests] pass_to_pass - Modeling structure check
def test_repo_modeling_structure():
    """Modeling structure check passes (pass_to_pass)."""
    r = subprocess.run(
        ["python", "utils/check_modeling_structure.py"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Modeling structure check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass - Doctest list check
def test_repo_doctest_list():
    """Doctest list check passes (pass_to_pass)."""
    r = subprocess.run(
        ["python", "utils/check_doctest_list.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Doctest list check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass - Dummies check
def test_repo_check_dummies():
    """Check dummies passes (pass_to_pass)."""
    r = subprocess.run(
        ["python", "utils/check_dummies.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Check dummies failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass - Ruff linter check on modified files
def test_repo_ruff_check():
    """Ruff linter passes on modified model files - installs ruff if needed (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "pip install ruff --quiet && ruff check src/transformers/models/ministral3/ src/transformers/models/mistral4/"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass - Ruff format check on modified files
def test_repo_ruff_format():
    """Ruff format check passes on modified model files - installs ruff if needed (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "pip install ruff --quiet && ruff format --check src/transformers/models/ministral3/ src/transformers/models/mistral4/"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass - All affected files are valid Python (AST check via subprocess)
def test_repo_all_files_syntax():
    """All affected files parse as valid Python via AST (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-c",
         f"""
import ast
import sys
from pathlib import Path

files = [
    "{REPO}/src/transformers/models/ministral3/modeling_ministral3.py",
    "{REPO}/src/transformers/models/ministral3/modular_ministral3.py",
    "{REPO}/src/transformers/models/mistral4/modeling_mistral4.py",
    "{REPO}/src/transformers/models/mistral4/modular_mistral4.py",
]

for f in files:
    try:
        src = Path(f).read_text()
        ast.parse(src)
    except SyntaxError as e:
        print(f"SYNTAX_ERROR: {{f}}: {{e}}")
        sys.exit(1)

print("ALL_SYNTAX_OK")
"""],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Syntax check failed: {r.stderr}"
    assert "ALL_SYNTAX_OK" in r.stdout


# [repo_tests] pass_to_pass - Ministral3 modeling module is importable with classes
def test_repo_ministral3_modeling_import():
    """Ministral3 modeling module imports without errors (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-c",
         f"""
import sys
sys.path.insert(0, "{REPO}/src")
from transformers.models.ministral3.modeling_ministral3 import Ministral3Attention, get_llama_4_attn_scale
print("MINISTRAL3_IMPORT_OK")
"""],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ministral3 import failed: {r.stderr}"
    assert "MINISTRAL3_IMPORT_OK" in r.stdout


# [repo_tests] pass_to_pass - Mistral4 modeling module is importable with classes
def test_repo_mistral4_modeling_import():
    """Mistral4 modeling module imports without errors (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-c",
         f"""
import sys
sys.path.insert(0, "{REPO}/src")
from transformers.models.mistral4.modeling_mistral4 import Mistral4Attention, get_llama_4_attn_scale
print("MISTRAL4_IMPORT_OK")
"""],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Mistral4 import failed: {r.stderr}"
    assert "MISTRAL4_IMPORT_OK" in r.stdout
