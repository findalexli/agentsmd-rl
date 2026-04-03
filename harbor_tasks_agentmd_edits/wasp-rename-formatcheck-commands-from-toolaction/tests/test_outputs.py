"""
Task: wasp-rename-formatcheck-commands-from-toolaction
Repo: wasp @ 0ea59a851ef61e08184adc018e9b20801243ed8d
PR:   3853

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

REPO = "/workspace/wasp"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

def test_run_script_syntax_valid():
    """The waspc/run script must be valid bash syntax."""
    result = subprocess.run(
        ["bash", "-n", f"{REPO}/waspc/run"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, f"Syntax error in waspc/run: {result.stderr}"


def test_package_json_valid():
    """package.json must be valid JSON."""
    pkg = Path(REPO) / "package.json"
    data = json.loads(pkg.read_text())
    assert "scripts" in data, "package.json must have a scripts section"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests: command renaming
# ---------------------------------------------------------------------------

def test_run_script_case_branches_renamed():
    """The run script case statement must use action:tool format (e.g., format:ormolu, not ormolu:format)."""
    content = Path(f"{REPO}/waspc/run").read_text()
    # New names must be present as case branches
    for cmd in ["format:ormolu)", "check:ormolu)", "format:cabal)", "check:cabal)",
                "format:prettier)", "check:prettier)"]:
        assert cmd in content, f"Case branch '{cmd}' not found in waspc/run"
    # Old names must NOT be present as case branches
    for old_cmd in ["ormolu:check)", "ormolu:format)", "cabal-gild:check)",
                    "cabal-gild:format)", "prettier:check)", "prettier:format)"]:
        assert old_cmd not in content, f"Old case branch '{old_cmd}' still present in waspc/run"


def test_run_script_has_top_level_format_command():
    """The run script must have a top-level 'format' command that runs all formatters."""
    content = Path(f"{REPO}/waspc/run").read_text()
    lines = content.split("\n")
    found_format = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped == "format)":
            found_format = True
            block = "\n".join(lines[i:i+6])
            assert "ORMOLU_FORMAT" in block, "format command should run ormolu formatter"
            assert "PRETTIER_FORMAT" in block or "CABAL_GILD_FORMAT" in block, \
                "format command should run multiple formatters"
            break
    assert found_format, "No top-level 'format)' case branch found"


def test_run_script_has_top_level_check_command():
    """The run script must have a top-level 'check' command that runs all checkers."""
    content = Path(f"{REPO}/waspc/run").read_text()
    lines = content.split("\n")
    found_check = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped == "check)":
            found_check = True
            block = "\n".join(lines[i:i+6])
            assert "ORMOLU_CHECK" in block, "check command should run ormolu checker"
            assert "PRETTIER_CHECK" in block or "CABAL_GILD_CHECK" in block, \
                "check command should run multiple checkers"
            break
    assert found_check, "No top-level 'check)' case branch found"


def test_run_script_prettier_vars_use_new_npm_names():
    """PRETTIER_CHECK_CMD and PRETTIER_FORMAT_CMD must reference the new npm script names."""
    content = Path(f"{REPO}/waspc/run").read_text()
    assert "npm run check:prettier" in content, \
        "PRETTIER_CHECK_CMD should use 'npm run check:prettier'"
    assert "npm run format:prettier" in content, \
        "PRETTIER_FORMAT_CMD should use 'npm run format:prettier'"
    assert "npm run prettier:check" not in content, \
        "Old npm script name 'prettier:check' still in run script"
    assert "npm run prettier:format" not in content, \
        "Old npm script name 'prettier:format' still in run script"


def test_package_json_scripts_renamed():
    """package.json npm scripts must use action:tool naming (check:prettier, format:prettier)."""
    data = json.loads(Path(f"{REPO}/package.json").read_text())
    scripts = data.get("scripts", {})
    assert "check:prettier" in scripts, "package.json must have 'check:prettier' script"
    assert "format:prettier" in scripts, "package.json must have 'format:prettier' script"
    assert "prettier:check" not in scripts, "Old 'prettier:check' script still in package.json"
    assert "prettier:format" not in scripts, "Old 'prettier:format' script still in package.json"


def test_ci_formatting_uses_new_script_name():
    """CI formatting workflow must use the new npm script name."""
    ci = Path(f"{REPO}/.github/workflows/ci-formatting.yaml").read_text()
    assert "check:prettier" in ci, "CI should reference 'check:prettier'"
    assert "prettier:check" not in ci, "CI still uses old 'prettier:check' name"


def test_run_script_help_text_uses_new_names():
    """The run script's print_usage section must document the new command names."""
    content = Path(f"{REPO}/waspc/run").read_text()
    for cmd_name in ["format:ormolu", "check:ormolu", "format:cabal", "check:cabal",
                     "format:prettier", "check:prettier"]:
        assert f'"{cmd_name}"' in content or f"'{cmd_name}'" in content, \
            f"Help text should document '{cmd_name}'"


# ---------------------------------------------------------------------------
# Config edit (config_edit) — README documentation update
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
# Pass-to-pass — regression: existing commands still work
# ---------------------------------------------------------------------------

def test_run_script_preserves_existing_commands():
    """Existing non-renamed commands (build, test, wasp-cli, etc.) must still be present."""
    content = Path(f"{REPO}/waspc/run").read_text()
    for cmd in ["build)", "test)", "wasp-cli)", "stan)", "hlint)", "code-check)"]:
        assert cmd in content, f"Existing command '{cmd}' missing from waspc/run"
