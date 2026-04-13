"""
Task: goose-remove-clippy-lint-decompose-functions
Repo: block/goose @ 948cb91d5402b6175d4ff6386e8e02beea6b86cd
PR:   7064

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess

REPO = "/workspace/goose"


def _run(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute a Python script in the repo directory."""
    return subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


def test_build_session_decomposed():
    """build_session must be refactored into focused helper functions."""
    r = _run("""
import sys

with open("crates/goose-cli/src/session/builder.rs") as f:
    content = f.read()

# Helper functions must exist as standalone fn declarations
helpers = [
    "fn resolve_provider_and_model",
    "fn resolve_session_id",
    "fn handle_resumed_session_workdir",
    "fn resolve_and_load_extensions",
    "fn configure_session_prompts",
]

for sig in helpers:
    if sig not in content:
        print("FAIL: Missing " + sig)
        sys.exit(1)

# build_session must delegate to each helper
calls = [
    "resolve_provider_and_model(",
    "resolve_session_id(",
    "handle_resumed_session_workdir(",
    "resolve_and_load_extensions(",
    "configure_session_prompts(",
]

for call in calls:
    if call not in content:
        print("FAIL: build_session does not call " + call)
        sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


def test_clippy_toml_created():
    """clippy.toml must exist with valid too-many-lines-threshold setting."""
    r = _run("""
import re, sys

with open("clippy.toml") as f:
    content = f.read()

match = re.search(r"too-many-lines-threshold\\s*=\\s*(\\d+)", content)
if not match:
    print("FAIL: clippy.toml missing too-many-lines-threshold")
    sys.exit(1)

threshold = int(match.group(1))
if threshold <= 0:
    print("FAIL: threshold must be positive, got " + str(threshold))
    sys.exit(1)

print("PASS: too-many-lines-threshold = " + str(threshold))
""")
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


def test_old_infrastructure_removed():
    """Old custom clippy scripts and baseline files must be removed."""
    r = _run("""
import sys
from pathlib import Path

must_not_exist = [
    "scripts/clippy-lint.sh",
    "scripts/clippy-baseline.sh",
    "clippy-baselines/too_many_lines.txt",
]

for f in must_not_exist:
    if Path(f).exists():
        print("FAIL: " + f + " must be removed")
        sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (agent_config / pr_diff) — config file update tests
# ---------------------------------------------------------------------------


def test_agents_md_standard_clippy():
    """AGENTS.md must reference standard cargo clippy, not ./scripts/clippy-lint.sh."""
    r = _run("""
import sys

with open("AGENTS.md") as f:
    content = f.read()

if "./scripts/clippy-lint.sh" in content:
    print("FAIL: AGENTS.md still references ./scripts/clippy-lint.sh")
    sys.exit(1)
if "cargo clippy --all-targets" not in content:
    print("FAIL: AGENTS.md must reference cargo clippy --all-targets")
    sys.exit(1)
if "Merge without running clippy" not in content:
    print("FAIL: AGENTS.md Never rule should say Merge without running clippy")
    sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


def test_copilot_instructions_updated():
    """.github/copilot-instructions.md must use standard cargo clippy."""
    r = _run("""
import sys

with open(".github/copilot-instructions.md") as f:
    content = f.read()

if "./scripts/clippy-lint.sh" in content:
    print("FAIL: copilot-instructions.md still references ./scripts/clippy-lint.sh")
    sys.exit(1)
if "cargo clippy --all-targets" not in content:
    print("FAIL: copilot-instructions.md must reference cargo clippy --all-targets")
    sys.exit(1)
if "CI handles this (clippy)" not in content:
    print("FAIL: copilot-instructions.md should reference standard clippy")
    sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


def test_doc_files_consistent():
    """HOWTOAI.md, CONTRIBUTING.md, and Justfile must use standard clippy."""
    r = _run("""
import sys

with open("HOWTOAI.md") as f:
    c = f.read()
if "./scripts/clippy-lint.sh" in c:
    print("FAIL: HOWTOAI.md still references ./scripts/clippy-lint.sh"); sys.exit(1)
if "cargo clippy --all-targets" not in c:
    print("FAIL: HOWTOAI.md must reference standard clippy command"); sys.exit(1)
if "clippy.toml" not in c:
    print("FAIL: HOWTOAI.md should reference clippy.toml"); sys.exit(1)

with open("CONTRIBUTING.md") as f:
    c = f.read()
if "./scripts/clippy-lint.sh" in c:
    print("FAIL: CONTRIBUTING.md still references ./scripts/clippy-lint.sh"); sys.exit(1)
if "cargo clippy --all-targets" not in c:
    print("FAIL: CONTRIBUTING.md must reference standard clippy command"); sys.exit(1)

with open("Justfile") as f:
    c = f.read()
if "./scripts/clippy-lint.sh" in c:
    print("FAIL: Justfile still references ./scripts/clippy-lint.sh"); sys.exit(1)
if "cargo clippy --all-targets" not in c:
    print("FAIL: Justfile must reference standard clippy command"); sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks that must pass on base commit
# ---------------------------------------------------------------------------


def test_repo_cargo_fmt():
    """Repo's Rust code must be properly formatted (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "fmt", "--check"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"cargo fmt --check failed:\n{r.stderr[-500:]}"


def test_repo_cargo_check_goose_cli():
    """Repo's goose-cli crate must compile (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "check", "-p", "goose-cli"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"cargo check -p goose-cli failed:\n{r.stderr[-500:]}"



def test_repo_cargo_clippy_goose():
    """Repo's goose crate must pass clippy linting (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "clippy", "-p", "goose", "--", "-D", "warnings"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"cargo clippy -p goose failed:\n{r.stderr[-500:]}"


def test_repo_cargo_clippy_goose_cli():
    """Repo's goose-cli crate must pass clippy linting (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "clippy", "-p", "goose-cli", "--", "-D", "warnings"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"cargo clippy -p goose-cli failed:\n{r.stderr[-500:]}"


def test_repo_cargo_check_workspace_lib():
    """Repo's workspace library code must compile (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "check", "--workspace", "--lib"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"cargo check --workspace --lib failed:\n{r.stderr[-500:]}"


def test_repo_cargo_clippy_all_targets():
    """Repo must pass clippy on all targets (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "clippy", "--all-targets", "--", "-D", "warnings"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"cargo clippy --all-targets failed:\n{r.stderr[-500:]}"

# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + syntax checks
# ---------------------------------------------------------------------------


def test_rust_syntax_valid():
    """builder.rs must have valid Rust function syntax (balanced braces, fn declarations)."""
    r = _run("""
import re, sys

with open("crates/goose-cli/src/session/builder.rs") as f:
    content = f.read()

open_b = content.count("{")
close_b = content.count("}")
if open_b != close_b:
    print("FAIL: Unbalanced braces: " + str(open_b) + " open, " + str(close_b) + " close")
    sys.exit(1)

fn_pattern = r"(?:pub\\s+)?(?:async\\s+)?fn\\s+\\w+"
functions = re.findall(fn_pattern, content)
if len(functions) < 10:
    print("FAIL: Expected >= 10 functions, found " + str(len(functions)))
    sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout
