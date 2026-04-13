"""
Task: areal-eval-distributed-sampler-padding
Repo: inclusionAI/AReaL @ fdca82dc09e76052fd6ee2fe22afcdc5ff044743
PR:   1100

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import re
import subprocess
from pathlib import Path

REPO = "/repo"
FILE = Path(f"{REPO}/areal/utils/dataloader.py")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code in the repo environment via subprocess."""
    script = Path(f"{REPO}/_eval_tmp.py")
    script.write_text(code)
    try:
        return subprocess.run(
            ["python3", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# Shared preamble: loads the dataloader module with mocked internal imports
_PREAMBLE = """
from pathlib import Path

source = Path("/repo/areal/utils/dataloader.py").read_text()
for old in [
    "from areal.api.cli_args import ValidDatasetConfig, _DatasetConfig",
    "from areal.api.cli_args import _DatasetConfig",
]:
    source = source.replace(old, "")

class _DatasetConfig:
    batch_size = 4
    shuffle = False
    drop_last = True
    num_workers = 0

class ValidDatasetConfig(_DatasetConfig):
    drop_last = False

ns = {"__builtins__": __builtins__, "_DatasetConfig": _DatasetConfig, "ValidDatasetConfig": ValidDatasetConfig}
exec(compile(source, "<dataloader>", "exec"), ns)
EvalDistributedSampler = ns.get("EvalDistributedSampler")
create_dataloader = ns["create_dataloader"]
"""


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """dataloader.py must parse as valid Python."""
    ast.parse(FILE.read_text())


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests via subprocess
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_eval_sampler_no_padding():
    """EvalDistributedSampler covers every index exactly once without padding."""
    r = _run_py(_PREAMBLE + """
for ds_size, nrep in [(10, 3), (7, 4), (13, 5), (100, 7)]:
    dataset = list(range(ds_size))
    all_indices = []
    for rank in range(nrep):
        sampler = EvalDistributedSampler(
            dataset, num_replicas=nrep, rank=rank, shuffle=False, drop_last=False
        )
        all_indices.extend(list(sampler))
    assert sorted(all_indices) == list(range(ds_size)), (
        f"ds={ds_size}, replicas={nrep}: got {sorted(all_indices)}"
    )
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_create_dataloader_dispatches_eval_sampler():
    """create_dataloader uses EvalDistributedSampler for ValidDatasetConfig."""
    r = _run_py(_PREAMBLE + """
valid_config = ValidDatasetConfig()
valid_config.batch_size = 4
loader = create_dataloader(
    list(range(12)), rank=0, world_size=2, dataset_config=valid_config
)
sampler = loader.sampler
assert type(sampler).__name__ == "EvalDistributedSampler", (
    f"Expected EvalDistributedSampler, got {type(sampler).__name__}"
)
assert not sampler.drop_last, "Sampler drop_last should be False for validation"
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_edge_case_small_dataset():
    """Sampler handles dataset_size < num_replicas and exact division correctly."""
    r = _run_py(_PREAMBLE + """
for ds_size, nrep in [(2, 4), (6, 3), (1, 5)]:
    dataset = list(range(ds_size))
    all_indices = []
    for rank in range(nrep):
        sampler = EvalDistributedSampler(
            dataset, num_replicas=nrep, rank=rank, shuffle=False, drop_last=False
        )
        all_indices.extend(list(sampler))
    assert sorted(all_indices) == list(range(ds_size)), (
        f"ds={ds_size}, replicas={nrep}: got {sorted(all_indices)}"
    )
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_no_duplicate_indices():
    """No duplicate indices across ranks for various dataset sizes."""
    r = _run_py(_PREAMBLE + """
for ds_size, nrep in [(10, 3), (7, 4), (13, 5), (100, 7), (3, 8)]:
    dataset = list(range(ds_size))
    all_indices = []
    for rank in range(nrep):
        sampler = EvalDistributedSampler(
            dataset, num_replicas=nrep, rank=rank, shuffle=False, drop_last=False
        )
        all_indices.extend(list(sampler))
    assert len(all_indices) == len(set(all_indices)), (
        f"ds={ds_size}, replicas={nrep}: found duplicates"
    )
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_training_config_unchanged():
    """Training config still uses standard DistributedSampler with drop_last=True."""
    r = _run_py(_PREAMBLE + """
train_config = _DatasetConfig()
train_config.batch_size = 4
loader = create_dataloader(
    list(range(12)), rank=0, world_size=2, dataset_config=train_config
)
sampler = loader.sampler
assert type(sampler).__name__ == "DistributedSampler", (
    f"Expected DistributedSampler for training, got {type(sampler).__name__}"
)
assert sampler.drop_last, "Sampler drop_last should be True for training"
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks from the repository
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_ruff_lint():
    """Repo's ruff linting passes on dataloader.py (pass_to_pass)."""
    r = subprocess.run(
        ["ruff", "check", str(FILE)],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff lint failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_ruff_format():
    """Repo's ruff formatting passes on dataloader.py (pass_to_pass)."""
    r = subprocess.run(
        ["ruff", "format", "--check", str(FILE)],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_py_compile():
    """dataloader.py compiles as valid Python bytecode (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-m", "py_compile", str(FILE)],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Python compile failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_bandit():
    """Bandit security checks pass on dataloader.py (pass_to_pass)."""
    # Install bandit if not already available
    subprocess.run(
        ["pip", "install", "bandit", "-q"],
        capture_output=True, text=True, timeout=60,
    )
    r = subprocess.run(
        ["bandit", str(FILE)],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Bandit security check failed:\n{r.stdout}\n{r.stderr}"


# [static] pass_to_pass
def test_no_trailing_whitespace():
    """dataloader.py has no trailing whitespace (pass_to_pass)."""
    source = FILE.read_text()
    lines = source.split('\n')
    for i, line in enumerate(lines, 1):
        if line != line.rstrip():
            assert False, f"Trailing whitespace found at line {i}"


# [static] pass_to_pass
def test_eof_newline():
    """dataloader.py ends with a newline (pass_to_pass)."""
    source = FILE.read_text()
    assert source.endswith('\n'), "File must end with a newline"


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:30 @ fdca82dc
def test_no_wildcard_imports():
    """No wildcard imports in dataloader.py (AGENTS.md hard rule)."""
    source = FILE.read_text()
    assert not re.search(r"from\s+\S+\s+import\s+\*", source), (
        "Wildcard import found in dataloader.py"
    )


# [agent_config] pass_to_pass — AGENTS.md:100-101 @ fdca82dc
def test_explicit_type_hints_in_eval_sampler():
    """EvalDistributedSampler.__init__ must have explicit type annotations on all parameters."""
    tree = ast.parse(FILE.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "EvalDistributedSampler":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                    for arg in item.args.args:
                        if arg.arg == "self":
                            continue
                        assert arg.annotation is not None, (
                            f"EvalDistributedSampler.__init__ parameter '{arg.arg}' missing type annotation"
                        )
                    return  # found and checked
    assert False, "EvalDistributedSampler.__init__ not found in dataloader.py"


# [agent_config] pass_to_pass — AGENTS.md:90-92 @ fdca82dc
def test_no_print_statements():
    """No print() calls in dataloader.py — use areal.utils.logging.getLogger()."""
    tree = ast.parse(FILE.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id == "print":
                assert False, (
                    f"print() found at line {node.lineno} — use areal.utils.logging.getLogger()"
                )
