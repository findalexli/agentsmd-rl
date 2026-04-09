"""
Task: prime-rl-loguru-file
Repo: PrimeIntellect-ai/prime-rl @ 4526113207d008ee386330ad382badf8bb0fdaf8
PR:   556

This PR makes two types of changes:
1. Code changes: Update log file extensions from .log to .loguru, fix glob pattern bug, fix tail process tracking
2. README update: Document the new tmuxinator workflow and standalone inference server

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
from pathlib import Path

REPO = "/workspace/prime-rl"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified Python files must parse without errors."""
    files = [
        f"{REPO}/src/prime_rl/rl.py",
        f"{REPO}/src/prime_rl/trainer/logger.py",
        f"{REPO}/src/prime_rl/orchestrator/logger.py",
    ]
    for f in files:
        src = Path(f).read_text()
        ast.parse(src)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests using subprocess
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_loguru_extension_in_logger_files():
    """Logger setup functions construct paths with .loguru extension."""
    r = subprocess.run(
        ["python3", "-c", """
import ast, sys
from pathlib import Path

errors = []

# --- rl.py: expects `log_config.path / "rl.loguru"` (BinOp with / operator) ---
with open("src/prime_rl/rl.py") as f:
    tree = ast.parse(f.read())

rl_ok = False
for node in ast.walk(tree):
    # Match: something / "rl.loguru"  (Path division)
    if (isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div)
            and isinstance(node.right, ast.Constant)
            and isinstance(node.right.value, str)
            and node.right.value.endswith(".loguru")):
        # Actually construct the path to confirm extension
        result = Path("/tmp/logs") / node.right.value
        assert str(result).endswith(".loguru"), f"Bad extension: {result}"
        rl_ok = True
        break
if not rl_ok:
    errors.append("rl.py: setup_logger does not construct a .loguru path")

# --- trainer/logger.py and orchestrator/logger.py ---
# Both use: Path(log_config.path.as_posix() + ".loguru")
for fname, label in [
    ("src/prime_rl/trainer/logger.py", "trainer"),
    ("src/prime_rl/orchestrator/logger.py", "orchestrator"),
]:
    with open(fname) as f:
        tree = ast.parse(f.read())
    found = False
    for node in ast.walk(tree):
        if (isinstance(node, ast.Constant) and isinstance(node.value, str)
                and node.value == ".loguru"):
            # Verify the extension constructs a correct path
            test_path = Path(f"/tmp/logs/{label}" + node.value)
            assert str(test_path).endswith(".loguru"), f"Bad path: {test_path}"
            found = True
            break
    if not found:
        errors.append(f"{fname}: does not use .loguru extension")

if errors:
    print("FAIL: " + "; ".join(errors), file=sys.stderr)
    sys.exit(1)
print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_log_cleaning_glob_pattern():
    """The glob pattern in rl() no longer uses the old buggy *.stdout pattern."""
    r = subprocess.run(
        ["python3", "-c", """
import ast, sys

with open("src/prime_rl/rl.py") as f:
    tree = ast.parse(f.read())

# Extract all string arguments passed to .glob() calls
glob_patterns = []
for node in ast.walk(tree):
    if (isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "glob"
            and node.args
            and isinstance(node.args[0], ast.Constant)
            and isinstance(node.args[0].value, str)):
        glob_patterns.append(node.args[0].value)

if not glob_patterns:
    print("FAIL: No glob() calls found in rl.py", file=sys.stderr)
    sys.exit(1)

# The base commit has "*.log|*.stdout" — a buggy pattern referencing .stdout
for pat in glob_patterns:
    if ".stdout" in pat:
        print(f"FAIL: Found old buggy glob pattern: {pat}", file=sys.stderr)
        sys.exit(1)

print(f"OK: glob patterns={glob_patterns}")
print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_tail_process_tracked():
    """The tail Popen result is captured in a variable and appended to processes."""
    r = subprocess.run(
        ["python3", "-c", """
import ast, sys

with open("src/prime_rl/rl.py") as f:
    tree = ast.parse(f.read())

# Find Popen(["tail", ...]) calls that are ASSIGNED to a variable
popen_vars = set()
# Find processes.append(var) calls
append_vars = set()

for node in ast.walk(tree):
    # Pattern: var = Popen(["tail", ...])
    if isinstance(node, ast.Assign) and len(node.targets) == 1:
        target = node.targets[0]
        if isinstance(target, ast.Name) and isinstance(node.value, ast.Call):
            func = node.value.func
            if isinstance(func, ast.Name) and func.id == "Popen":
                if node.value.args and isinstance(node.value.args[0], ast.List):
                    for elt in node.value.args[0].elts:
                        if isinstance(elt, ast.Constant) and elt.value == "tail":
                            popen_vars.add(target.id)

    # Pattern: processes.append(var)
    if (isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Attribute)
            and node.value.func.attr == "append"
            and isinstance(node.value.func.value, ast.Name)
            and node.value.func.value.id == "processes"):
        if node.value.args and isinstance(node.value.args[0], ast.Name):
            append_vars.add(node.value.args[0].id)

# The tail Popen variable must exist AND be appended to processes
tracked = popen_vars & append_vars
if not tracked:
    print(f"FAIL: tail Popen vars={popen_vars}, appended to processes={append_vars}", file=sys.stderr)
    sys.exit(1)

print(f"OK: tracked tail process vars={tracked}")
print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks from the repo
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_ruff_lint():
    """Repo's ruff lint passes on all source files (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "-q", "ruff"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Failed to install ruff: {r.stderr}"

    r = subprocess.run(
        ["ruff", "check", "src/", "--config=pyproject.toml"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff lint failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_ruff_format():
    """Repo's ruff format check passes on modified files (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "-q", "ruff"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Failed to install ruff: {r.stderr}"

    files = [
        "src/prime_rl/rl.py",
        "src/prime_rl/trainer/logger.py",
        "src/prime_rl/orchestrator/logger.py",
    ]
    r = subprocess.run(
        ["ruff", "format", "--check"] + files + ["--config=pyproject.toml"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """Modified functions have real logic, not just pass/return."""
    rl_src = Path(f"{REPO}/src/prime_rl/rl.py").read_text()
    tree = ast.parse(rl_src)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "setup_logger":
            # Count non-pass statements
            stmts = [s for s in node.body if not isinstance(s, (ast.Pass, ast.Expr))]
            assert len(stmts) >= 3, "setup_logger is a stub or missing logic"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — README and config file updates
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass — README must document the new tmuxinator workflow
def test_readme_documents_tmuxinator_section():
    """README.md must have a Tmuxinator section documenting the new workflow."""
    readme = Path(f"{REPO}/README.md").read_text()
    assert "### Tmuxinator" in readme, "README should have a ### Tmuxinator section"
    assert "Trainer" in readme, "README should mention the Trainer pane"
    assert "Standalone Inference Server" in readme or "standalone" in readme.lower(), \
        "README should document the standalone inference server option"


# [pr_diff] fail_to_pass — tmuxinator.yaml must be updated
def test_tmuxinator_yaml_updated():
    """.tmuxinator.yaml must be updated with the new pane layout."""
    tmux_src = Path(f"{REPO}/.tmuxinator.yaml").read_text()
    assert "- RL:" in tmux_src, "tmuxinator.yaml should have 'RL:' window"
    assert "- Trainer:" in tmux_src, "tmuxinator.yaml should have 'Trainer:' pane"
    assert "orchestrator.loguru" in tmux_src, "tmuxinator.yaml should tail orchestrator.loguru"
