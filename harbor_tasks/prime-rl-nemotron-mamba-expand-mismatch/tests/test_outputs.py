"""
Task: prime-rl-nemotron-mamba-expand-mismatch
Repo: PrimeIntellect-ai/prime-rl @ 8a6f4ef3bfe644c7fd1e33841aa66c6f3a4c26a4
PR:   2110

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
from pathlib import Path

REPO = "/workspace/prime-rl"
CONFIG_PY = f"{REPO}/src/prime_rl/trainer/models/nemotron_h/configuration_nemotron_h.py"
MODELING_PY = f"{REPO}/src/prime_rl/trainer/models/nemotron_h/modeling_nemotron_h.py"


def _run_py_direct(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code with direct config file loading (avoids torch dep)."""
    # Wrap the code to load config directly from file
    wrapped = f'''
import sys
import importlib.util
spec = importlib.util.spec_from_file_location("configuration_nemotron_h", "{CONFIG_PY}")
mod = importlib.util.module_from_spec(spec)
sys.path.insert(0, "{REPO}/src")
try:
    spec.loader.exec_module(mod)
    NemotronHConfig = mod.NemotronHConfig
except Exception as e:
    print(f"Import error: {{e}}")
    sys.exit(1)
{code}
'''
    return subprocess.run(
        ["python3", "-c", wrapped],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Both modified files must parse without syntax errors."""
    for fpath in [CONFIG_PY, MODELING_PY]:
        source = Path(fpath).read_text()
        ast.parse(source)  # raises SyntaxError on failure


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_nano_30b_dimension_invariant():
    """Config mamba_expand yields correct intermediate_size for Nano-30B."""
    r = _run_py_direct("""
config = NemotronHConfig(hidden_size=2688, mamba_num_heads=64, mamba_head_dim=64, mamba_expand=2)
expected = 64 * 64  # 4096
actual = int(config.mamba_expand * config.hidden_size)
assert actual == expected, f"intermediate_size={actual}, expected {expected}"
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_multiple_dimension_combos():
    """Config mamba_expand correct for varied hidden_size / head combos."""
    r = _run_py_direct("""
cases = [
    (1024, 32, 48, 3),   # expected 1536, raw gives 3072
    (512,  16, 48, 2),   # expected  768, raw gives 1024
    (2048, 64, 64, 1),   # expected 4096, raw gives 2048
]
for hs, nh, hd, me in cases:
    config = NemotronHConfig(hidden_size=hs, mamba_num_heads=nh, mamba_head_dim=hd, mamba_expand=me)
    expected = nh * hd
    actual = int(config.mamba_expand * config.hidden_size)
    assert actual == expected, f"hs={hs} nh={nh} hd={hd}: got {actual}, expected {expected}"
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_fractional_expand_precision():
    """No off-by-one from float truncation when expand is not a clean fraction."""
    r = _run_py_direct("""
# 3840 / 2688 = 1.42857142857... (repeating)
config = NemotronHConfig(hidden_size=2688, mamba_num_heads=80, mamba_head_dim=48, mamba_expand=2)
expected = 80 * 48  # 3840
actual = int(config.mamba_expand * config.hidden_size)
assert actual == expected, f"Fractional case: got {actual}, expected {expected}"

# 3072 / 1536 = 2.0 (clean fraction, should still work)
config2 = NemotronHConfig(hidden_size=1536, mamba_num_heads=48, mamba_head_dim=64, mamba_expand=4)
expected2 = 48 * 64  # 3072
actual2 = int(config2.mamba_expand * config2.hidden_size)
assert actual2 == expected2, f"Clean fraction case: got {actual2}, expected {expected2}"
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_120b_default_config():
    """120B default config still produces correct mamba_expand."""
    r = _run_py_direct("""
config = NemotronHConfig()
expected = 128 * 64  # 8192
actual = int(config.mamba_expand * config.hidden_size)
assert actual == expected, f"120B: got {actual}, expected {expected}"
assert config.mamba_expand > 0, "mamba_expand must be positive"
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [static] pass_to_pass
def test_not_stub():
    """NemotronHConfig.__init__ has real logic, not just pass/return."""
    tree = ast.parse(Path(CONFIG_PY).read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "NemotronHConfig":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                    real = [s for s in item.body if not isinstance(s, (ast.Pass, ast.Expr))]
                    assert len(real) >= 10, f"Stub detected: only {len(real)} statements"
                    return
    raise AssertionError("NemotronHConfig.__init__ not found")


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:5 @ 8a6f4ef
def test_no_silent_try_except():
    """No silent except/pass blocks (AGENTS.md: avoid try/except unless necessary)."""
    for fpath in [CONFIG_PY, MODELING_PY]:
        tree = ast.parse(Path(fpath).read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                for handler in node.handlers:
                    if len(handler.body) == 1 and isinstance(handler.body[0], ast.Pass):
                        raise AssertionError(
                            f"Silent except/pass in {fpath} at line {node.lineno}"
                        )


# [agent_config] pass_to_pass — AGENTS.md:7 @ 8a6f4ef
def test_no_work_process_comments():
    """No comments referring to old code or work process (AGENTS.md: no unnecessary comments)."""
    bad_patterns = ["used to", "previously", "old code", "was changed", "we changed", "refactored from"]
    for fpath in [CONFIG_PY, MODELING_PY]:
        for i, line in enumerate(Path(fpath).read_text().splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith("#"):
                lower = stripped.lower()
                for pat in bad_patterns:
                    if pat in lower:
                        raise AssertionError(
                            f"Work-process comment in {fpath}:{i}: {stripped}"
                        )


# ---------------------------------------------------------------------------
# Repo CI/CD checks (pass_to_pass) — repo_tests
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_ruff_check():
    """Repo's ruff lint check passes on modified files (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "-q", "ruff"],
        capture_output=True, text=True, timeout=60,
    )
    r = subprocess.run(
        ["python", "-m", "ruff", "check", "--config=pyproject.toml", "src/prime_rl/trainer/models/nemotron_h/"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_ruff_format():
    """Repo's ruff format check passes on modified files (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "-q", "ruff"],
        capture_output=True, text=True, timeout=60,
    )
    r = subprocess.run(
        ["python", "-m", "ruff", "format", "--check", "--config=pyproject.toml", "src/prime_rl/trainer/models/nemotron_h/"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_no_broken_syntax():
    """All modified Python files parse without syntax errors (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-c", f"import ast; ast.parse(open('{CONFIG_PY}').read())"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Syntax error in {CONFIG_PY}:\n{r.stderr[-500:]}"
    r = subprocess.run(
        ["python", "-c", f"import ast; ast.parse(open('{MODELING_PY}').read())"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Syntax error in {MODELING_PY}:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_ruff_full_lint():
    """Repo's full ruff lint check passes (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "-q", "ruff"],
        capture_output=True, text=True, timeout=60,
    )
    r = subprocess.run(
        ["python", "-m", "ruff", "check", "--config=pyproject.toml", "."],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Full ruff lint failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_imports_clean():
    """Modified config file parses and has NemotronHConfig class (pass_to_pass)."""
    # Parse the config file directly to verify structure (avoids torch dependency)
    r = subprocess.run(
        ["python", "-c", f"""
import ast
with open('{CONFIG_PY}') as f:
    tree = ast.parse(f.read())

# Check that NemotronHConfig class exists
classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
assert 'NemotronHConfig' in classes, f'NemotronHConfig not found, got: {{classes}}'
print('IMPORT_OK')
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Config import check failed:\n{r.stderr[-500:]}"
    assert "IMPORT_OK" in r.stdout


# [repo_tests] pass_to_pass
def test_repo_config_validates():
    """NemotronHConfig class has required attributes defined (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-c", f"""
import ast
with open('{CONFIG_PY}') as f:
    tree = ast.parse(f.read())

# Find NemotronHConfig class and check for required attributes
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'NemotronHConfig':
        # Check __init__ assigns required attributes
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == '__init__':
                assigns = [n.attr for n in ast.walk(item) if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id == 'self']
                required = ['mamba_expand', 'mamba_num_heads', 'mamba_head_dim', 'hidden_size']
                missing = [r for r in required if r not in assigns]
                assert not missing, f'Missing attributes in __init__: {{missing}}'
                print('CONFIG_VALID')
                break
        break
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Config validation failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"
    assert "CONFIG_VALID" in r.stdout
