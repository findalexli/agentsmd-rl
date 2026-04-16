"""
Task: wasp-refactor-build-commands-for-clarity
Repo: wasp-lang/wasp @ ed8f009c79766e66767307ea00fff365c9f12eae
PR:   3562

Rename build commands: build->build:hs, build:all->build, build:all:static->BUILD_STATIC env.
All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import re
import subprocess
from pathlib import Path

REPO = "/workspace/wasp"
RUN_CWD = f"{REPO}/waspc"


def _run_cmd(args, timeout=15, env=None):
    """Execute a command in the waspc directory and return the result."""
    return subprocess.run(
        args,
        cwd=RUN_CWD,
        capture_output=True, text=True, timeout=timeout,
        env=env,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / shell parse checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified shell scripts must parse without errors."""
    for script in ["waspc/run"]:
        r = subprocess.run(
            ["bash", "-n", script],
            cwd=REPO, capture_output=True, timeout=10,
        )
        assert r.returncode == 0, (
            f"{script} has syntax errors:\n{r.stderr.decode()}"
        )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests on waspc/run
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_build_dispatches_all():
    """'build' command must build everything (packages + haskell), not just haskell."""
    r = _run_cmd(["./run", "build"])
    output = r.stdout + r.stderr
    # echo_and_eval prints the dispatched command to stderr before executing it.
    # In the unfixed version, 'build' only runs 'cabal build all' (haskell-only).
    # After the fix, 'build' runs package compilation (npm) AND haskell (cabal).
    assert "npm" in output, (
        "'build' should compile TypeScript packages (npm), not just Haskell"
    )
    assert "cabal" in output, (
        "'build' should also build the Haskell project (cabal)"
    )


# [pr_diff] fail_to_pass
def test_build_hs_command_exists():
    """'build:hs' command must exist and dispatch to haskell-only build."""
    r = _run_cmd(["./run", "build:hs"])
    output = r.stdout + r.stderr
    # If recognized, echo_and_eval prints "Running:" before execution.
    # If unrecognized, the script prints USAGE instead.
    assert "Running:" in output, (
        "'build:hs' should be a recognized command in the run script"
    )
    assert "cabal" in output, (
        "'build:hs' should invoke a Haskell build"
    )


# [pr_diff] fail_to_pass
def test_old_build_all_removed():
    """'build:all' and 'build:all:static' must not be recognized commands."""
    for cmd in ["build:all", "build:all:static"]:
        r = _run_cmd(["./run", cmd])
        output = r.stdout + r.stderr
        # Unrecognized commands cause the script to show usage and exit non-zero
        assert "USAGE" in output, (
            f"'{cmd}' should no longer be a recognized command (should show usage)"
        )
        assert r.returncode != 0, (
            f"'{cmd}' should exit with non-zero when unrecognized"
        )


# [pr_diff] fail_to_pass
def test_static_via_env_var():
    """Static builds should be controlled via BUILD_STATIC env var."""
    env = os.environ.copy()
    env["BUILD_STATIC"] = "1"
    # Run build with BUILD_STATIC=1 — the echoed command should include the static flag
    r = _run_cmd(["./run", "build"], env=env)
    output = r.stdout + r.stderr
    assert "--enable-executable-static" in output, (
        "With BUILD_STATIC=1, the build should include --enable-executable-static"
    )

    # Without BUILD_STATIC, the static flag should not appear
    r2 = _run_cmd(["./run", "build"])
    output2 = r2.stdout + r2.stderr
    assert "--enable-executable-static" not in output2, (
        "Without BUILD_STATIC, --enable-executable-static should not appear"
    )


# [pr_diff] fail_to_pass
def test_ci_uses_new_build_command():
    """CI workflow must use './run build' (not './run build:all')."""
    ci_file = Path(REPO) / ".github" / "workflows" / "ci-waspc-build.yaml"
    # Use grep subprocess to find build command invocations
    r = subprocess.run(
        ["grep", "-n", r"./run build", str(ci_file)],
        capture_output=True, text=True, timeout=10,
    )
    lines = r.stdout.strip().split('\n') if r.stdout.strip() else []

    has_new_build = False
    has_old_build_all = False
    for line in lines:
        if "build:packages" in line or "build:hs" in line:
            continue
        if "build:all" in line:
            has_old_build_all = True
        elif "./run build" in line:
            has_new_build = True

    assert has_new_build, "CI should use './run build' as the build command"
    assert not has_old_build_all, "CI should not reference the old 'build:all' command"


# [pr_diff] fail_to_pass
def test_powershell_build_dispatches_all():
    """PowerShell 'build' must build everything, 'build:hs' must exist, 'build:all' must be gone."""
    ps_script = Path(REPO) / "waspc" / "run.ps1"
    # Parse the PowerShell switch block to validate command structure
    r = subprocess.run(
        ["python3", "-c", r"""
import re, sys

content = open(sys.argv[1]).read()

# Extract switch block
switch_match = re.search(r'switch\s*\(.*?\)\s*\{(.+?)^\}', content, re.DOTALL | re.MULTILINE)
if not switch_match:
    print("FAIL: No switch block found")
    sys.exit(1)

switch_body = switch_match.group(1)

# Extract all case labels from the switch block
cases = re.findall(r'"([^"]+)"\s*\{', switch_body)

if "build:hs" not in cases:
    print("FAIL: 'build:hs' is not a recognized command in the PowerShell script")
    sys.exit(1)

if "build:all" in cases:
    print("FAIL: 'build:all' should be removed from the PowerShell script")
    sys.exit(1)

if "build" not in cases:
    print("FAIL: 'build' is not a recognized command in the PowerShell script")
    sys.exit(1)

# 'build' and 'build:hs' should dispatch to different expressions
build_match = re.search(r'"build"\s*\{([^}]+)\}', switch_body)
build_hs_match = re.search(r'"build:hs"\s*\{([^}]+)\}', switch_body)
if build_match and build_hs_match:
    build_body = build_match.group(1).strip()
    build_hs_body = build_hs_match.group(1).strip()
    if build_body == build_hs_body:
        print("FAIL: 'build' and 'build:hs' dispatch to the same expression")
        sys.exit(1)

print("OK")
""", str(ps_script)],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"PowerShell check failed: {r.stdout.strip()}"


# ---------------------------------------------------------------------------
# Pass-to-pass — regression checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_build_packages_preserved():
    """'build:packages' command must still work in the run script."""
    r = _run_cmd(["./run", "build:packages"])
    output = r.stdout + r.stderr
    # build:packages should be recognized (prints "Running:", not USAGE)
    assert "Running:" in output, (
        "'build:packages' command should still be recognized"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — actual CI commands
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_ci_file_valid_yaml():
    """The CI workflow file must exist and have valid structure (pass_to_pass)."""
    ci_file = Path(REPO) / ".github" / "workflows" / "ci-waspc-build.yaml"
    assert ci_file.exists(), "CI workflow file must exist"
    content = ci_file.read_text()
    assert "name:" in content, "YAML must have a name field"
    assert "on:" in content or "true" in content.lower(), "YAML must have 'on' trigger section"
    assert "jobs:" in content, "YAML must have a jobs section"


# [repo_tests] pass_to_pass
def test_repo_run_script_bash_parse():
    """The waspc/run script must parse as valid bash (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-n", "waspc/run"],
        cwd=REPO, capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"waspc/run has bash syntax errors: {r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_run_script_version_cmd():
    """The waspc/run script get-waspc-version command executes (pass_to_pass)."""
    r = subprocess.run(
        ["./run", "get-waspc-version"],
        cwd=RUN_CWD,
        capture_output=True, text=True, timeout=30,
    )
    assert "cabal" in r.stderr or r.returncode == 0 or "waspc" in str(r.stdout), (
        f"get-waspc-version command should execute: stderr={r.stderr[:200]}"
    )


# [repo_tests] pass_to_pass
def test_repo_packages_compile_cmd_defined():
    """The WASP_PACKAGES_COMPILE command must be defined (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "grep -q 'WASP_PACKAGES_COMPILE=' waspc/run"],
        cwd=REPO, capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, "WASP_PACKAGES_COMPILE must be defined in run script"


# [repo_tests] pass_to_pass
def test_repo_run_ps1_exists():
    """PowerShell run script exists and is valid (pass_to_pass)."""
    ps_script = Path(REPO) / "waspc" / "run.ps1"
    assert ps_script.exists(), "PowerShell run script must exist"
    content = ps_script.read_text()
    assert "param(" in content or "$Command" in content, "PowerShell script must have expected structure"


# [repo_tests] pass_to_pass
def test_repo_build_all_cmd_defined():
    """The BUILD_ALL_CMD command must be defined in run script (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "grep -q 'BUILD_ALL_CMD=' waspc/run"],
        cwd=REPO, capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, "BUILD_ALL_CMD must be defined in run script"


# [repo_tests] pass_to_pass
def test_repo_build_hs_cmd_defined():
    """The BUILD_HS_CMD command must be defined in run script (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "grep -q 'BUILD_HS_CMD=' waspc/run"],
        cwd=REPO, capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, "BUILD_HS_CMD must be defined in run script"


# [repo_tests] pass_to_pass
def test_repo_run_script_help_works():
    """The waspc/run script help/usage command works (pass_to_pass)."""
    r = subprocess.run(
        ["./run", "invalid-command-that-shows-usage"],
        cwd=RUN_CWD,
        capture_output=True, text=True, timeout=10,
    )
    assert "USAGE" in r.stdout or "COMMANDS" in r.stdout, (
        "Run script should show usage help when given invalid command"
    )


# [repo_tests] pass_to_pass
def test_repo_ci_yaml_syntax():
    """CI workflow file must have valid YAML syntax (pass_to_pass)."""
    ci_file = Path(REPO) / ".github" / "workflows" / "ci-waspc-build.yaml"
    r = subprocess.run(
        ["python3", "-c", f"""
import re
with open('{ci_file}') as f:
    content = f.read()
if '\\t' in content:
    print("YAML contains tabs")
    exit(1)
if not re.search(r'^[^#\\s].*:', content, re.MULTILINE):
    print("No YAML keys found")
    exit(1)
print("Basic YAML validation passed")
"""],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"CI workflow file must be valid YAML: {r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_package_json_valid():
    """Root package.json must be valid JSON (pass_to_pass)."""
    pkg_file = Path(REPO) / "package.json"
    r = subprocess.run(
        ["python3", "-c", "import json; json.load(open('" + str(pkg_file) + "'))"],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"package.json must be valid JSON: {r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_tools_script_valid():
    """Tools directory scripts must be valid bash (pass_to_pass)."""
    script = Path(REPO) / "waspc" / "tools" / "make_binary_package.sh"
    r = subprocess.run(
        ["bash", "-n", str(script)],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"Tools script has bash syntax errors: {r.stderr}"
