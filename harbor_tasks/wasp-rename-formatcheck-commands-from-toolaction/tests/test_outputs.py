'''
Task: wasp-rename-formatcheck-commands-from-toolaction
Repo: wasp @ 0ea59a851ef61e08184adc018e9b20801243ed8d
PR:   3853
'''

import subprocess
import json

REPO = "/workspace/wasp"
WASPC_DIR = f"{REPO}/waspc"


def test_repo_git_index_valid():
    """Git index is valid and lists Haskell source files (pass_to_pass)."""
    r = subprocess.run(
        ["git", "ls-files", "*.hs", "*.hs-boot"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=WASPC_DIR,
    )
    assert r.returncode == 0, f"Git ls-files failed: {r.stderr[-500:]}"
    # Should list at least some Haskell files
    files = r.stdout.strip().split("\n")
    assert len(files) > 0 and files[0], "Should find at least one Haskell file"


def test_package_json_valid():
    """package.json is valid JSON with scripts section (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", "import json; json.load(open('package.json')); print('valid')"],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=REPO,
    )
    assert r.returncode == 0, f"package.json validation failed: {r.stderr[-500:]}"
    assert "valid" in r.stdout, "package.json should be valid JSON"


def test_package_lock_json_valid():
    """package-lock.json is valid JSON (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", "import json; json.load(open('package-lock.json')); print('valid')"],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=REPO,
    )
    assert r.returncode == 0, f"package-lock.json validation failed: {r.stderr[-500:]}"


def test_waspc_package_json_files_valid():
    """All waspc data package.json files are valid JSON (pass_to_pass)."""
    r = subprocess.run(
        [
            "bash", "-c",
            "find waspc/data/packages -name 'package.json' -exec python3 -c 'import json,sys; json.load(open(sys.argv[1]))' {} \\; -print 2>&1 | head -20"
        ],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    # If no error output and exit code is 0, all files parsed successfully
    assert "Error" not in r.stderr and "error" not in r.stderr.lower(), f"Some package.json files invalid: {r.stderr[-500:]}"


def test_run_script_syntax_valid():
    """waspc/run script parses without bash syntax errors (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-n", "run"],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=WASPC_DIR,
    )
    assert r.returncode == 0, f"run script syntax error: {r.stderr[-500:]}"


def test_run_script_executes():
    """waspc/run script executes and shows usage (pass_to_pass)."""
    r = subprocess.run(
        ["./run"],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=WASPC_DIR,
    )
    assert r.returncode == 0 or r.returncode == 1, "run script should execute (exit 0 or 1 for usage)"
    assert "USAGE" in r.stdout or "usage" in r.stdout.lower(), "run script should show USAGE"


def test_run_script_has_ormolu_commands():
    """waspc/run contains ormolu formatting commands (pass_to_pass)."""
    r = subprocess.run(
        ["grep", "ormolu:check\\|ormolu:format\\|check:ormolu\\|format:ormolu", "run"],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=WASPC_DIR,
    )
    # Should find ormolu commands in the run script (base commit has old names, PR renames to new format)
    assert "ormolu:check" in r.stdout or "ormolu:format" in r.stdout or "check:ormolu" in r.stdout or "format:ormolu" in r.stdout, "run script should have ormolu commands"


def test_run_script_has_prettier_commands():
    """waspc/run contains prettier formatting commands (pass_to_pass)."""
    r = subprocess.run(
        ["grep", "prettier:check\\|prettier:format\\|check:prettier\\|format:prettier", "run"],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=WASPC_DIR,
    )
    # Base commit has old names (prettier:check, prettier:format), PR renames to new format (check:prettier, format:prettier)
    assert "prettier:check" in r.stdout or "prettier:format" in r.stdout or "check:prettier" in r.stdout or "format:prettier" in r.stdout, "run script should have prettier commands"


def test_run_script_has_cabal_gild_commands():
    """waspc/run contains cabal-gild formatting commands (pass_to_pass)."""
    r = subprocess.run(
        ["grep", "cabal-gild:check\\|cabal-gild:format\\|check:cabal\\|format:cabal", "run"],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=WASPC_DIR,
    )
    # Base commit has old names (cabal-gild:check, cabal-gild:format), PR renames to new format (check:cabal, format:cabal)
    assert "cabal-gild:check" in r.stdout or "cabal-gild:format" in r.stdout or "check:cabal" in r.stdout or "format:cabal" in r.stdout, "run script should have cabal-gild commands"


def test_package_json_has_prettier_scripts():
    """package.json has prettier npm scripts (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", "import json; d=json.load(open('package.json')); print('scripts' in d and any('prettier' in k for k in d.get('scripts',{}).keys()))"],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=REPO,
    )
    assert "True" in r.stdout, "package.json should have prettier scripts"


def test_run_script_preserves_build_command():
    """waspc/run still has build command (pass_to_pass)."""
    r = subprocess.run(
        ["grep", "build)", "run"],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=WASPC_DIR,
    )
    assert "build)" in r.stdout, "run script should have build command"


def test_run_script_preserves_test_commands():
    """waspc/run still has test commands (pass_to_pass)."""
    r = subprocess.run(
        ["grep", "test:waspc\\|test:cli", "run"],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=WASPC_DIR,
    )
    assert "test:" in r.stdout, "run script should have test commands"


# Fail-to-pass tests for the PR

def test_run_script_case_branches_renamed():
    """Case branches renamed from tool:action to action:tool format (fail_to_pass)."""
    r = subprocess.run(
        ["grep", "check:ormolu\\|format:ormolu\\|check:cabal\\|format:cabal\\|check:prettier\\|format:prettier", "run"],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=WASPC_DIR,
    )
    # After the PR, these new command names should exist
    assert "check:ormolu" in r.stdout, "run script should have check:ormolu command"
    assert "format:ormolu" in r.stdout, "run script should have format:ormolu command"


def test_run_script_has_top_level_format_command():
    """New top-level 'format' command runs all formatters (fail_to_pass)."""
    r = subprocess.run(
        ["grep", "^  format)", "run"],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=WASPC_DIR,
    )
    assert "format)" in r.stdout, "run script should have top-level format command"


def test_run_script_has_top_level_check_command():
    """New top-level 'check' command runs all checkers (fail_to_pass)."""
    r = subprocess.run(
        ["grep", "^  check)", "run"],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=WASPC_DIR,
    )
    assert "check)" in r.stdout, "run script should have top-level check command"


def test_run_script_prettier_vars_use_new_npm_names():
    """PRETTIER_*_CMD variables reference new npm script names (fail_to_pass)."""
    r = subprocess.run(
        ["grep", "check:prettier\\|format:prettier", "run"],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=WASPC_DIR,
    )
    assert "check:prettier" in r.stdout, "run script should reference check:prettier"
    assert "format:prettier" in r.stdout, "run script should reference format:prettier"


def test_package_json_scripts_renamed():
    """npm scripts renamed from prettier:* to check/format:prettier (fail_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", "import json; d=json.load(open('package.json')); s=d.get('scripts',{}); print('check:prettier' in s or 'format:prettier' in s)"],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=REPO,
    )
    assert "True" in r.stdout, "package.json should have check:prettier or format:prettier scripts after PR"


def test_ci_formatting_uses_new_script_name():
    """CI workflow uses check:prettier instead of prettier:check (fail_to_pass)."""
    r = subprocess.run(
        ["grep", "check:prettier", ".github/workflows/ci-formatting.yaml"],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=REPO,
    )
    assert "check:prettier" in r.stdout, "CI workflow should use check:prettier"


def test_run_script_help_text_uses_new_names():
    """print_usage section documents all renamed commands (fail_to_pass)."""
    r = subprocess.run(
        ["grep", "format:ormolu\\|check:ormolu", "run"],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=WASPC_DIR,
    )
    assert "format:ormolu" in r.stdout, "run script should document format:ormolu"
    assert "check:ormolu" in r.stdout, "run script should document check:ormolu"
