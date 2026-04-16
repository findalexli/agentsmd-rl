"""
Task: areal-ppo-token-stats-cp
Repo: inclusionAI/AReaL @ d1cdac3442585565f902f1e69b9d7399c50b9b34
PR:   990

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import re
import subprocess
from pathlib import Path

REPO = "/workspace/AReaL"

STATS_PATH = f"{REPO}/areal/trainer/ppo/stats.py"
ACTOR_PATH = f"{REPO}/areal/trainer/ppo/actor.py"
CRITIC_PATH = f"{REPO}/areal/trainer/ppo/critic.py"


def _run_python(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


def _compile_check(path: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["python3", "-m", "py_compile", path],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )


def test_syntax_check():
    """actor.py and critic.py must parse without errors."""
    for path in (ACTOR_PATH, CRITIC_PATH):
        ast.parse(Path(path).read_text())


def test_infer_token_denominator_behavior():
    """infer_token_denominator correctly derives token denominator from metadata."""
    # Dynamically discover the helper function to avoid binding to a specific name
    helper_code = f"""
import sys
sys.path.insert(0, '{REPO}')
import importlib.util, torch, inspect

spec = importlib.util.spec_from_file_location("stats", "{STATS_PATH}")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

# Discover the public function with >=2 parameters
found = None
for name in dir(mod):
    obj = getattr(mod, name)
    if not inspect.isfunction(obj) or name.startswith('_'):
        continue
    try:
        sig = inspect.signature(obj, eval_str=True)
        if len(list(sig.parameters.keys())) >= 2:
            found = obj
            break
    except (ValueError, TypeError):
        continue

if found is None:
    print("NO_CALLABLE")
    sys.exit(0)

infer = found

# Test 1: attention_mask takes priority
r = infer({{"attention_mask": torch.tensor([[1,1,0],[1,1,1]])}}, torch.zeros(5))
assert r.shape == torch.Size([2,3]), f"attention_mask 2D: expected [2,3] got {{r.shape}}"
assert r.dtype == torch.bool
assert torch.all(r)

# Test 2: 1-D attention_mask is preserved in shape
r = infer({{"attention_mask": torch.tensor([1,0,1,1])}}, torch.zeros(2))
assert r.shape == torch.Size([4]), f"attention_mask 1D: expected [4] got {{r.shape}}"
assert r.dtype == torch.bool

# Test 3: cu_seqlens fallback for packed sequences
r = infer({{"cu_seqlens": torch.tensor([0,4], dtype=torch.int32)}}, torch.zeros(2))
assert r.shape == torch.Size([4]), f"cu_seqlens [0,4]: expected [4] got {{r.shape}}"
assert r.dtype == torch.bool

# Test 4: cu_seqlens multi-segment
r = infer({{"cu_seqlens": torch.tensor([0,3,7], dtype=torch.int32)}}, torch.zeros(2))
assert r.shape == torch.Size([7]), f"cu_seqlens [0,3,7]: expected [7] got {{r.shape}}"
assert r.dtype == torch.bool

# Test 5: input_ids when shape matches fallback
r = infer({{"input_ids": torch.tensor([[11,12,13],[14,15,16]])}}, torch.zeros(2,3))
assert r.shape == torch.Size([2,3])
assert r.dtype == torch.bool

# Test 6: input_ids shape mismatch -> fallback used (shape of fallback)
r = infer({{"input_ids": torch.tensor([[11,12,13],[14,15,16]])}}, torch.zeros(5))
assert r.shape == torch.Size([5]), f"input_ids shape mismatch: expected fallback [5] got {{r.shape}}"

# Test 7: no recognized metadata -> fallback shape preserved
r = infer({{"logprobs": torch.zeros(3)}}, torch.zeros(4,8))
assert r.shape == torch.Size([4,8])
assert r.dtype == torch.bool
assert torch.all(r)

# Test 8: empty input_data -> fallback shape preserved
r = infer({{}}, torch.zeros(6))
assert r.shape == torch.Size([6])
assert torch.all(r)

# Test 9: cu_seqlens with zero elements -> fallback
r = infer({{"cu_seqlens": torch.tensor([], dtype=torch.int32)}}, torch.zeros(8))
assert r.shape == torch.Size([8])

print("ALL_PASS")
"""
    r = _run_python(helper_code)
    assert r.returncode == 0, f"Script error: {r.stderr}"
    assert "NO_CALLABLE" not in r.stdout, "stats.py has no callable matching (dict, tensor) signature"
    assert "ALL_PASS" in r.stdout, f"Behavioral assertions failed: {r.stdout}"


def test_actor_critic_integration():
    """Actor and critic compile and use the new helper function."""
    for path in (ACTOR_PATH, CRITIC_PATH):
        r = _compile_check(path)
        assert r.returncode == 0, f"{path} compile failed:\n{r.stderr}"

    # Verify via source inspection that actor and critic reference the helper function.
    for path in (ACTOR_PATH, CRITIC_PATH):
        content = Path(path).read_text()

        # Must have the stats import (from areal.trainer.ppo.stats import ...)
        stats_import = re.search(r'from\s+(?:areal\.trainer\.ppo\.)?stats\s+import', content)
        assert stats_import, f"{path} does not import from stats module"

        # Must use the infer_token_denominator function
        used = re.search(r'infer_token_denominator\s*\(', content)
        assert used, f"{path} does not call infer_token_denominator"


def test_not_stub():
    """stats.py has a function with >=3 non-docstring statements and conditional logic."""
    stats_path = Path(STATS_PATH)
    assert stats_path.exists(), "stats.py not created"
    tree = ast.parse(stats_path.read_text())

    funcs = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
    assert funcs, "No functions found in stats.py"

    found = None
    for func in funcs:
        body = [n for n in func.body
                if not (isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant))]
        if len(body) < 3:
            continue
        if any(isinstance(n, ast.If) for n in ast.walk(func)):
            found = func
            break

    assert found is not None, (
        f"No function with >=3 statements and conditional logic in stats.py. "
        f"Functions: {[f.name for f in funcs]}"
    )


PPO_FILES = [Path(ACTOR_PATH), Path(CRITIC_PATH), Path(STATS_PATH)]


def test_no_wildcard_imports():
    """No wildcard imports in PPO files."""
    assert PPO_FILES[2].exists(), "stats.py not created"
    for fpath in PPO_FILES:
        tree = ast.parse(fpath.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    assert alias.name != "*", f"Wildcard import in {fpath.name}"


def test_no_print_in_ppo_files():
    """No bare print() calls in PPO files."""
    assert PPO_FILES[2].exists(), "stats.py not created"
    for fpath in PPO_FILES:
        tree = ast.parse(fpath.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == "print":
                    raise AssertionError(f"Bare print() in {fpath.name}:{node.lineno}")


def test_no_hardcoded_paths():
    """No hardcoded absolute paths in PPO files."""
    assert PPO_FILES[2].exists(), "stats.py not created"
    pattern = re.compile(r'(?:/home/|/tmp/|/workspace/|/usr/local/|https?://)')
    for fpath in PPO_FILES:
        for lineno, line in enumerate(fpath.read_text().splitlines(), 1):
            if line.lstrip().startswith('#'):
                continue
            assert not pattern.search(line), f"Hardcoded path in {fpath.name}:{lineno}"


def test_type_hints_on_helper():
    """Helper function has type annotations on all params and return."""
    stats_path = Path(STATS_PATH)
    assert stats_path.exists(), "stats.py not created"
    tree = ast.parse(stats_path.read_text())

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if node.returns is None:
                continue
            all_annotated = all(
                arg.annotation is not None
                for arg in node.args.args
                if arg.arg != "self"
            )
            if all_annotated:
                return

    raise AssertionError("No function with complete type annotations found in stats.py")


def test_repo_ruff_lint_ppo():
    r = subprocess.run(["pip", "install", "ruff==0.14.9", "-q"],
                       capture_output=True, text=True, timeout=120, cwd=REPO)
    r = subprocess.run(["ruff", "check", "areal/trainer/ppo/", "--ignore", "E501"],
                       capture_output=True, text=True, timeout=60, cwd=REPO)
    assert r.returncode == 0, f"Ruff lint failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


def test_repo_ruff_format_ppo():
    r = subprocess.run(["pip", "install", "ruff==0.14.9", "-q"],
                       capture_output=True, text=True, timeout=120, cwd=REPO)
    r = subprocess.run(["ruff", "format", "--check", "areal/trainer/ppo/"],
                       capture_output=True, text=True, timeout=60, cwd=REPO)
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


def test_repo_syntax_areal():
    r = subprocess.run(["python3", "-m", "compileall", "-q", "areal/"],
                       capture_output=True, text=True, timeout=120, cwd=REPO)
    assert r.returncode == 0, f"Syntax check failed:\n{r.stderr[-500:]}"


def test_repo_syntax_tests():
    r = subprocess.run(["python3", "-m", "compileall", "-q", "tests/"],
                       capture_output=True, text=True, timeout=120, cwd=REPO)
    assert r.returncode == 0, f"Test syntax check failed:\n{r.stderr[-500:]}"


def test_repo_actor_critic_compile():
    for path in (ACTOR_PATH, CRITIC_PATH):
        r = _compile_check(path)
        assert r.returncode == 0, f"{path} compile failed:\n{r.stderr}"
