'''
Task: wasp-rename-formatcheck-commands-from-toolaction
Repo: wasp @ 0ea59a851ef61e08184adc018e9b20801243ed8d
PR:   3853
'''

import subprocess
import json
import re

REPO = "/workspace/wasp"
WASPC_DIR = f"{REPO}/waspc"


def _run_script_usage():
    """Execute ./run with no args and return combined output (contains USAGE text)."""
    r = subprocess.run(
        ["./run"],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=WASPC_DIR,
    )
    return r.stdout + r.stderr


def _run_command(cmd):
    """Execute ./run <cmd> and return combined stdout+stderr."""
    r = subprocess.run(
        ["./run", cmd],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=WASPC_DIR,
    )
    return r.stdout + r.stderr


# ---- Pass-to-pass tests ----

def test_repo_git_index_valid():
    """Git index is valid and lists Haskell source files (pass_to_pass)."""
    r = subprocess.run(
        ["git", "ls-files", "*.hs", "*.hs-boot"],
        capture_output=True, text=True, timeout=30, cwd=WASPC_DIR,
    )
    assert r.returncode == 0, f"Git ls-files failed: {r.stderr[-500:]}"
    files = r.stdout.strip().split("\n")
    assert len(files) > 0 and files[0], "Should find at least one Haskell file"


def test_package_json_valid():
    """package.json is valid JSON with scripts section (pass_to_pass)."""
    with open(f"{REPO}/package.json") as f:
        data = json.load(f)
    assert "scripts" in data, "package.json should have a scripts section"


def test_package_lock_json_valid():
    """package-lock.json is valid JSON (pass_to_pass)."""
    with open(f"{REPO}/package-lock.json") as f:
        json.load(f)


def test_waspc_package_json_files_valid():
    """All waspc data package.json files are valid JSON (pass_to_pass)."""
    r = subprocess.run(
        [
            "bash", "-c",
            "find waspc/data/packages -name 'package.json' -exec python3 -c "
            "'import json,sys; json.load(open(sys.argv[1]))' {} \\; -print 2>&1 | head -20"
        ],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert "error" not in r.stderr.lower(), \
        f"Some package.json files invalid: {r.stderr[-500:]}"


def test_run_script_syntax_valid():
    """waspc/run script parses without bash syntax errors (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-n", "run"],
        capture_output=True, text=True, timeout=10, cwd=WASPC_DIR,
    )
    assert r.returncode == 0, f"run script syntax error: {r.stderr[-500:]}"


def test_run_script_executes():
    """waspc/run script executes and shows usage (pass_to_pass)."""
    r = subprocess.run(
        ["./run"], capture_output=True, text=True, timeout=10, cwd=WASPC_DIR,
    )
    output = r.stdout.lower() + r.stderr.lower()
    assert "usage" in output, "run script should show USAGE when run with no args"


def test_run_script_has_ormolu_commands():
    """waspc/run USAGE output mentions ormolu commands (pass_to_pass)."""
    usage = _run_script_usage()
    assert "ormolu" in usage.lower(), "run script usage should mention ormolu"


def test_run_script_has_prettier_commands():
    """waspc/run USAGE output mentions prettier commands (pass_to_pass)."""
    usage = _run_script_usage()
    assert "prettier" in usage.lower(), "run script usage should mention prettier"


def test_run_script_has_cabal_gild_commands():
    """waspc/run USAGE output mentions cabal formatting commands (pass_to_pass)."""
    usage = _run_script_usage()
    assert "cabal" in usage.lower(), "run script usage should mention cabal"


def test_package_json_has_prettier_scripts():
    """package.json has prettier npm scripts (pass_to_pass)."""
    with open(f"{REPO}/package.json") as f:
        data = json.load(f)
    scripts = data.get("scripts", {})
    assert any("prettier" in k for k in scripts), \
        "package.json should have prettier scripts"


def test_run_script_preserves_build_command():
    """waspc/run USAGE still lists build command (pass_to_pass)."""
    usage = _run_script_usage()
    assert "build" in usage, "run script usage should list build command"


def test_run_script_preserves_test_commands():
    """waspc/run USAGE still lists test commands (pass_to_pass)."""
    usage = _run_script_usage()
    assert "test:" in usage, "run script usage should list test commands"


# ---- Fail-to-pass tests ----

def test_run_script_case_branches_renamed():
    """Case branches renamed from tool:action to action:tool format (fail_to_pass).

    Executes the run script and verifies the USAGE output lists commands
    in the new action:tool naming convention.
    """
    usage = _run_script_usage()
    assert "check:ormolu" in usage, "run script usage should list check:ormolu"
    assert "format:ormolu" in usage, "run script usage should list format:ormolu"


def test_run_script_has_top_level_format_command():
    """New top-level 'format' command is recognized by the run script (fail_to_pass).

    Executes './run format' and verifies it does not fall through to USAGE
    output, meaning 'format' is handled as a valid command.
    """
    output = _run_command("format")
    assert "USAGE" not in output, \
        "'format' should be a recognized command (should not show USAGE)"


def test_run_script_has_top_level_check_command():
    """New top-level 'check' command is recognized by the run script (fail_to_pass).

    Executes './run check' and verifies it does not fall through to USAGE
    output, meaning 'check' is handled as a valid command.
    """
    output = _run_command("check")
    assert "USAGE" not in output, \
        "'check' should be a recognized command (should not show USAGE)"


def test_run_script_prettier_vars_use_new_npm_names():
    """Run script invokes check:prettier and format:prettier npm scripts (fail_to_pass).

    Executes './run check:prettier' and './run format:prettier' and verifies
    the echoed command output references the new npm script names.
    """
    check_output = _run_command("check:prettier")
    assert "check:prettier" in check_output, \
        "run script should invoke npm run check:prettier"

    format_output = _run_command("format:prettier")
    assert "format:prettier" in format_output, \
        "run script should invoke npm run format:prettier"


def test_package_json_scripts_renamed():
    """npm scripts use action:tool naming convention (fail_to_pass).

    Parses package.json and verifies the script keys use the new naming.
    """
    with open(f"{REPO}/package.json") as f:
        data = json.load(f)
    scripts = data.get("scripts", {})
    assert "check:prettier" in scripts, \
        "package.json should have check:prettier script"
    assert "format:prettier" in scripts, \
        "package.json should have format:prettier script"


def test_ci_formatting_uses_new_script_name():
    """CI workflow references the new check:prettier npm script (fail_to_pass).

    Parses the CI workflow file and extracts npm run commands to verify
    the new naming convention is used.
    """
    with open(f"{REPO}/.github/workflows/ci-formatting.yaml") as f:
        content = f.read()
    npm_commands = re.findall(r'npm\s+run\s+([\w:./-]+)', content)
    assert len(npm_commands) > 0, "CI workflow should contain npm run commands"
    assert any(cmd == "check:prettier" for cmd in npm_commands), \
        f"CI workflow should use 'npm run check:prettier', found: {npm_commands}"


def test_run_script_help_text_uses_new_names():
    """USAGE output documents all renamed commands in action:tool format (fail_to_pass).

    Executes the run script and verifies the help text lists all six
    renamed commands.
    """
    usage = _run_script_usage()
    for cmd in ["format:ormolu", "check:ormolu",
                "format:cabal", "check:cabal",
                "format:prettier", "check:prettier"]:
        assert cmd in usage, f"Usage should document {cmd}"
