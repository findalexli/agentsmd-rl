"""
Task: prime-rl-set-process-titles
Repo: PrimeIntellect-ai/prime-rl @ 8304f1e2acdd9a5264a323f15d132bb7f2015a9f
PR:   2159

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
import sys
from pathlib import Path

REPO = "/workspace/prime-rl"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, repo_tests) — CI linting / formatting checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_ruff_check():
    """Repo's ruff linter passes on modified files (pass_to_pass)."""
    files_to_check = [
        "src/prime_rl/utils/process.py",
        "src/prime_rl/entrypoints/inference.py",
        "src/prime_rl/entrypoints/rl.py",
        "src/prime_rl/entrypoints/sft.py",
        "src/prime_rl/orchestrator/env_server/env_server.py",
        "src/prime_rl/orchestrator/orchestrator.py",
        "src/prime_rl/trainer/rl/train.py",
        "src/prime_rl/trainer/sft/train.py",
    ]
    r = subprocess.run(
        ["ruff", "check", "--config=pyproject.toml"] + files_to_check,
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_ruff_format():
    """Repo's ruff format check passes on modified files (pass_to_pass)."""
    files_to_check = [
        "src/prime_rl/utils/process.py",
        "src/prime_rl/entrypoints/inference.py",
        "src/prime_rl/entrypoints/rl.py",
        "src/prime_rl/entrypoints/sft.py",
        "src/prime_rl/orchestrator/env_server/env_server.py",
        "src/prime_rl/orchestrator/orchestrator.py",
        "src/prime_rl/trainer/rl/train.py",
        "src/prime_rl/trainer/sft/train.py",
    ]
    r = subprocess.run(
        ["ruff", "format", "--check", "--config=pyproject.toml"] + files_to_check,
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout}\n{r.stderr}"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without errors."""
    files_to_check = [
        "src/prime_rl/utils/process.py",
        "src/prime_rl/entrypoints/inference.py",
        "src/prime_rl/entrypoints/rl.py",
        "src/prime_rl/entrypoints/sft.py",
        "src/prime_rl/orchestrator/env_server/env_server.py",
        "src/prime_rl/orchestrator/orchestrator.py",
        "src/prime_rl/trainer/rl/train.py",
        "src/prime_rl/trainer/sft/train.py",
    ]

    for file_path in files_to_check:
        full_path = Path(REPO) / file_path
        if full_path.exists():
            src = full_path.read_text()
            try:
                ast.parse(src)
            except SyntaxError as e:
                raise AssertionError(f"Syntax error in {file_path}: {e}")


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_set_proc_title_function_exists():
    """set_proc_title() function must be defined in process.py with correct implementation."""
    process_py = Path(REPO) / "src/prime_rl/utils/process.py"
    src = process_py.read_text()

    tree = ast.parse(src)

    # Find the set_proc_title function
    found_func = False
    found_prefix = False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "set_proc_title":
            found_func = True
            # Check it has the setproctitle call
            for child in ast.walk(node):
                if isinstance(child, ast.Call):
                    if isinstance(child.func, ast.Attribute) and child.func.attr == "setproctitle":
                        found_prefix = True

    assert found_func, "set_proc_title() function not found in process.py"
    assert found_prefix, "set_proc_title() must call setproctitle.setproctitle()"


# [pr_diff] fail_to_pass
def test_set_proc_title_sets_correct_title():
    """set_proc_title() actually sets the process title using setproctitle."""
    # Run a subprocess that calls set_proc_title and checks the result
    test_script = """
import sys
sys.path.insert(0, '/workspace/prime-rl/src')

from prime_rl.utils.process import set_proc_title
import setproctitle

# Get title before
before = setproctitle.getproctitle()

# Set title
set_proc_title("TestProcess")

# Get title after
after = setproctitle.getproctitle()

# Check it worked
assert "PRIME-RL::TestProcess" in after, f"Expected PRIME-RL::TestProcess in title, got: {after}"
print("SUCCESS: Process title set correctly")
"""
    result = subprocess.run(
        [sys.executable, "-c", test_script],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, f"Process title test failed: {result.stderr}"
    assert "SUCCESS" in result.stdout, f"Expected SUCCESS in output: {result.stdout}"


# [pr_diff] fail_to_pass
def test_entrypoints_call_set_proc_title():
    """All major entrypoints must call set_proc_title() in their main() function."""
    entrypoints = [
        ("src/prime_rl/entrypoints/inference.py", "Inference"),
        ("src/prime_rl/entrypoints/rl.py", "Launcher"),
        ("src/prime_rl/entrypoints/sft.py", "SFT"),
        ("src/prime_rl/orchestrator/env_server/env_server.py", "EnvServer"),
        ("src/prime_rl/orchestrator/orchestrator.py", "Orchestrator"),
        ("src/prime_rl/trainer/rl/train.py", "Trainer"),
        ("src/prime_rl/trainer/sft/train.py", "SFTTrainer"),
    ]

    for file_path, expected_name in entrypoints:
        full_path = Path(REPO) / file_path
        src = full_path.read_text()
        tree = ast.parse(src)

        found_in_main = False
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "main":
                # Check if set_proc_title is called with the right name
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        if isinstance(child.func, ast.Name) and child.func.id == "set_proc_title":
                            if child.args:
                                if isinstance(child.args[0], ast.Constant) and child.args[0].value == expected_name:
                                    found_in_main = True

        assert found_in_main, f"main() in {file_path} must call set_proc_title('{expected_name}')"


# [pr_diff] fail_to_pass
def test_setproctitle_dependency_added():
    """pyproject.toml must include setproctitle>=1.3.0 as a dependency."""
    pyproject = Path(REPO) / "pyproject.toml"
    content = pyproject.read_text()

    assert "setproctitle" in content, "pyproject.toml must include setproctitle dependency"
    assert "setproctitle>=1.3.0" in content or 'setproctitle = "1.3.0"' in content, \
        "pyproject.toml must specify setproctitle>=1.3.0"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — SKILL.md documentation update
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — AGENTS.md:73-78 @ 8304f1e2acdd9a5264a323f15d132bb7f2015a9f
# "When you make changes to the codebase, check if any skills need to be updated"
def test_skill_md_documents_process_titles():
    """skills/monitor-run/SKILL.md must document the new process tree titles."""
    skill_md = Path(REPO) / "skills/monitor-run/SKILL.md"
    content = skill_md.read_text()

    # Check for process title documentation
    assert "process title" in content.lower() or "setproctitle" in content.lower(), \
        "SKILL.md must document process titles (setproctitle)"

    # Check for the process title table or list
    assert "PRIME-RL::" in content, \
        "SKILL.md must list PRIME-RL:: process titles"

    # Check for key process titles
    expected_titles = [
        "Launcher",
        "Inference",
        "Orchestrator",
        "Trainer",
        "SFTTrainer",
        "EnvServer",
    ]
    for title in expected_titles:
        assert f"PRIME-RL::{title}" in content or title in content, \
            f"SKILL.md must document PRIME-RL::{title} process title"


# [agent_config] fail_to_pass — AGENTS.md:73-78 @ 8304f1e2acdd9a5264a323f15d132bb7f2015a9f
def test_skill_md_has_process_tree_inspection_commands():
    """SKILL.md must include commands for inspecting process trees."""
    skill_md = Path(REPO) / "skills/monitor-run/SKILL.md"
    content = skill_md.read_text()

    # Check for ps/pstree commands
    assert "ps " in content or "pstree" in content, \
        "SKILL.md must include ps or pstree commands for process inspection"

    # Check for example process tree output
    assert "Verifiers::EnvWorker" in content or "EnvWorker" in content, \
        "SKILL.md should document Verifiers::EnvWorker process titles"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_set_proc_title_not_stub():
    """set_proc_title() is not a stub - has real implementation logic."""
    process_py = Path(REPO) / "src/prime_rl/utils/process.py"
    src = process_py.read_text()
    tree = ast.parse(src)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "set_proc_title":
            # Count meaningful statements (not just docstring/pass)
            stmts = [
                s for s in node.body
                if not isinstance(s, (ast.Pass, ast.Expr))  # Expr includes docstrings
            ]
            # Filter out the docstring expression which is the first statement if it's a string
            if stmts and isinstance(stmts[0], ast.Expr) and isinstance(stmts[0].value, (ast.Constant, ast.Str)):
                stmts = stmts[1:]

            assert len(stmts) >= 1, "set_proc_title() must have meaningful implementation, not just pass/return"
