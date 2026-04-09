"""
Task: areal-ppo-token-stats-cp
Repo: inclusionAI/AReaL @ d1cdac3442585565f902f1e69b9d7399c50b9b34
PR:   990

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
from pathlib import Path

REPO = "/workspace/AReaL"

STATS_PATH = f"{REPO}/areal/trainer/ppo/stats.py"

LOAD_HELPER = """
import importlib.util
import torch

spec = importlib.util.spec_from_file_location("stats", "%s")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
infer = mod.infer_token_denominator
""" % STATS_PATH


def _run_python(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code in the repo directory."""
    return subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """actor.py and critic.py must parse without errors."""
    for name in ("areal/trainer/ppo/actor.py", "areal/trainer/ppo/critic.py"):
        src = Path(f"{REPO}/{name}").read_text()
        ast.parse(src)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests for infer_token_denominator
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_attention_mask_preferred():
    """infer_token_denominator prefers attention_mask over other metadata."""
    r = _run_python(LOAD_HELPER + """
# 2-D attention mask — shape comes from attention_mask, NOT fallback
input_data = {
    "attention_mask": torch.tensor([[1, 1, 0], [1, 1, 1]]),
    "input_ids": torch.tensor([[11, 12], [13, 14]]),
}
result = infer(input_data, fallback=torch.zeros(5))
assert result.shape == torch.Size([2, 3]), f"Expected [2,3], got {result.shape}"
assert result.dtype == torch.bool
assert torch.all(result)

# 1-D attention mask
input_data_1d = {"attention_mask": torch.tensor([1, 0, 1, 1])}
result_1d = infer(input_data_1d, fallback=torch.zeros(2))
assert result_1d.shape == torch.Size([4])
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_cu_seqlens_fallback():
    """cu_seqlens used for packed sequences when attention_mask absent."""
    r = _run_python(LOAD_HELPER + """
# cu_seqlens [0, 4] means 4 tokens total
input_data = {"cu_seqlens": torch.tensor([0, 4], dtype=torch.int32)}
result = infer(input_data, fallback=torch.zeros(2))
assert result.shape == torch.Size([4]), f"Expected [4], got {result.shape}"
assert result.dtype == torch.bool

# cu_seqlens [0, 3, 7] means 7 tokens total
input_data2 = {"cu_seqlens": torch.tensor([0, 3, 7], dtype=torch.int32)}
result2 = infer(input_data2, fallback=torch.zeros(2))
assert result2.shape == torch.Size([7])
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_input_ids_shape_match():
    """input_ids used when shape matches fallback; ignored otherwise."""
    r = _run_python(LOAD_HELPER + """
# Shapes match → use input_ids shape
input_data = {"input_ids": torch.tensor([[11, 12, 13], [14, 15, 16]])}
result = infer(input_data, fallback=torch.zeros(2, 3))
assert result.shape == torch.Size([2, 3])
assert result.dtype == torch.bool

# Shapes don't match → fall back to ones_like(fallback)
result_mismatch = infer(input_data, fallback=torch.zeros(5))
assert result_mismatch.shape == torch.Size([5])
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_final_fallback():
    """Falls back to ones_like(fallback) when no usable metadata."""
    r = _run_python(LOAD_HELPER + """
# No recognized metadata keys
fallback = torch.zeros(4, 8)
result = infer({"logprobs": torch.zeros(3)}, fallback)
assert result.shape == torch.Size([4, 8])
assert result.dtype == torch.bool
assert torch.all(result)

# Empty dict
result2 = infer({}, torch.zeros(6))
assert result2.shape == torch.Size([6])
assert torch.all(result2)
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — actor/critic integration
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_actor_critic_use_helper():
    """Actor and critic import infer_token_denominator, old buggy pattern removed."""
    r = _run_python(LOAD_HELPER + """
from pathlib import Path

actor_src = Path("areal/trainer/ppo/actor.py").read_text()
critic_src = Path("areal/trainer/ppo/critic.py").read_text()

# Old buggy patterns must be gone
assert "torch.ones_like(loss_mask, dtype=torch.bool)" not in actor_src, \\
    "Actor still has old buggy n_tokens pattern"
assert "torch.ones(value.shape[0], dtype=torch.bool" not in critic_src, \\
    "Critic still has old buggy n_tokens pattern"

# Both files must reference the helper
assert "infer_token_denominator" in actor_src, \\
    "Actor does not reference infer_token_denominator"
assert "infer_token_denominator" in critic_src, \\
    "Critic does not reference infer_token_denominator"
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] fail_to_pass
def test_not_stub():
    """stats.py infer_token_denominator has real conditional fallback logic."""
    stats_path = Path(STATS_PATH)
    assert stats_path.exists(), "stats.py not created"
    tree = ast.parse(stats_path.read_text())

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "infer_token_denominator":
            body = [n for n in node.body
                    if not (isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant))]
            assert len(body) >= 3, "Function body too small — likely a stub"
            has_if = any(isinstance(n, ast.If) for n in ast.walk(node))
            assert has_if, "No conditional logic — missing fallback chain"
            return

    raise AssertionError("infer_token_denominator function not found in stats.py")


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

PPO_FILES = [
    Path(f"{REPO}/areal/trainer/ppo/actor.py"),
    Path(f"{REPO}/areal/trainer/ppo/critic.py"),
    Path(f"{REPO}/areal/trainer/ppo/stats.py"),
]


# [agent_config] fail_to_pass — AGENTS.md:25 @ d1cdac3442585565f902f1e69b9d7399c50b9b34
def test_no_wildcard_imports():
    """No wildcard imports in modified PPO files."""
    assert PPO_FILES[2].exists(), "stats.py not created"
    for fpath in PPO_FILES:
        tree = ast.parse(fpath.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    assert alias.name != "*", \
                        f"Wildcard import in {fpath.name}: from {node.module} import *"


# [agent_config] fail_to_pass — AGENTS.md:84 @ d1cdac3442585565f902f1e69b9d7399c50b9b34
def test_no_print_in_ppo_files():
    """No bare print() calls in modified PPO files; use areal.utils.logging."""
    assert PPO_FILES[2].exists(), "stats.py not created"
    for fpath in PPO_FILES:
        tree = ast.parse(fpath.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Name) and func.id == "print":
                    raise AssertionError(
                        f"Bare print() in {fpath.name}:{node.lineno} — use areal.utils.logging"
                    )


# [agent_config] fail_to_pass — AGENTS.md:26 @ d1cdac3442585565f902f1e69b9d7399c50b9b34
def test_no_hardcoded_paths():
    """No hardcoded absolute paths or http(s) endpoints in modified PPO files."""
    import re
    assert PPO_FILES[2].exists(), "stats.py not created"
    pattern = re.compile(r'(?:/home/|/tmp/|/workspace/|/usr/local/|https?://\S)')
    for fpath in PPO_FILES:
        for lineno, line in enumerate(fpath.read_text().splitlines(), 1):
            stripped = line.lstrip()
            if stripped.startswith('#'):
                continue
            m = pattern.search(line)
            if m:
                raise AssertionError(
                    f"Hardcoded path/endpoint in {fpath.name}:{lineno}: {line.strip()!r}"
                )


# [agent_config] fail_to_pass — AGENTS.md:94 @ d1cdac3442585565f902f1e69b9d7399c50b9b34
def test_type_hints_on_helper():
    """infer_token_denominator has type annotations on parameters and return."""
    stats_path = Path(STATS_PATH)
    assert stats_path.exists(), "stats.py not created"
    tree = ast.parse(stats_path.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "infer_token_denominator":
            assert node.returns is not None, \
                "infer_token_denominator missing return type annotation"
            for arg in node.args.args:
                if arg.arg == "self":
                    continue
                assert arg.annotation is not None, \
                    f"Parameter '{arg.arg}' missing type annotation"
            return
    raise AssertionError("infer_token_denominator not found in stats.py")


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks from the repository
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass — ruff lint check on modified PPO files
def test_repo_ruff_lint_ppo():
    """Ruff linting passes on PPO files (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff==0.14.9", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    # Install may emit warnings; ignore them
    r = subprocess.run(
        ["ruff", "check", "areal/trainer/ppo/", "--ignore", "E501"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff lint failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — ruff format check on modified PPO files
def test_repo_ruff_format_ppo():
    """Ruff format check passes on PPO files (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff==0.14.9", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        ["ruff", "format", "--check", "areal/trainer/ppo/"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — syntax check on areal package
def test_repo_syntax_areal():
    """All areal Python files parse without syntax errors (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "compileall", "-q", "areal/"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Syntax check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — syntax check on tests directory
def test_repo_syntax_tests():
    """All test files parse without syntax errors (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "compileall", "-q", "tests/"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Test syntax check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — actor.py and critic.py compile
def test_repo_actor_critic_compile():
    """actor.py and critic.py compile without errors (pass_to_pass)."""
    for name in ("areal/trainer/ppo/actor.py", "areal/trainer/ppo/critic.py"):
        r = subprocess.run(
            ["python3", "-m", "py_compile", f"{REPO}/{name}"],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        assert r.returncode == 0, f"{name} failed to compile:\n{r.stderr}"
