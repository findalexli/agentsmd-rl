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


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code in a subprocess with the repo on PYTHONPATH."""
    return subprocess.run(
        ["python3", "-c", code],
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
    r = _run_py("""
from prime_rl.trainer.models.nemotron_h.configuration_nemotron_h import NemotronHConfig
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
    r = _run_py("""
from prime_rl.trainer.models.nemotron_h.configuration_nemotron_h import NemotronHConfig
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
    r = _run_py("""
from prime_rl.trainer.models.nemotron_h.configuration_nemotron_h import NemotronHConfig

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
    r = _run_py("""
from prime_rl.trainer.models.nemotron_h.configuration_nemotron_h import NemotronHConfig
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
        ["pip", "install", "-q", "ruff", "pytest"],
        capture_output=True, text=True, timeout=60,
    )
    r = subprocess.run(
        ["ruff", "check", "--config=pyproject.toml", "src/prime_rl/trainer/models/nemotron_h/"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_ruff_format():
    """Repo's ruff format check passes on modified files (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "-q", "ruff", "pytest"],
        capture_output=True, text=True, timeout=60,
    )
    r = subprocess.run(
        ["ruff", "format", "--check", "--config=pyproject.toml", "src/prime_rl/trainer/models/nemotron_h/"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_no_broken_syntax():
    """All modified Python files parse without syntax errors (pass_to_pass)."""
    for fpath in [CONFIG_PY, MODELING_PY]:
        source = Path(fpath).read_text()
        try:
            ast.parse(source)
        except SyntaxError as e:
            raise AssertionError(f"Syntax error in {fpath}: {e}")
