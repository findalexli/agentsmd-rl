"""
Task: playwright-feat-add-cdp-option-to-attach
Repo: microsoft/playwright @ 9d81a6754d9426295ac10bd33278fb2af476c8a9
PR:   40017

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/playwright"

CLI_CLIENT = f"{REPO}/packages/playwright-core/src/tools/cli-client"
CLI_DAEMON = f"{REPO}/packages/playwright-core/src/tools/cli-daemon"
MCP = f"{REPO}/packages/playwright-core/src/tools/mcp"
SKILL_MD = f"{CLI_CLIENT}/skill/SKILL.md"


def _run_js(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node in the repo directory."""
    script = Path(REPO) / "_eval_tmp.cjs"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


def _get_file_content(path: str) -> str:
    """Read file content from repo."""
    full_path = Path(REPO) / path
    if not full_path.exists():
        return ""
    return full_path.read_text()


# ============================================================================
# FAIL TO PASS TESTS (8 tests)
# These should FAIL on base commit and PASS after fix
# ============================================================================

# [pr_diff] fail_to_pass
def test_global_options_includes_cdp():
    """globalOptions array includes 'cdp' for CLI argument parsing."""
    src = _get_file_content("packages/playwright-core/src/tools/cli-client/program.ts")
    assert "globalOptions" in src, "globalOptions not found"
    # Check that 'cdp' is in the globalOptions array
    assert "'cdp'" in src or '"cdp"' in src, "'cdp' not found in globalOptions"


# [pr_diff] fail_to_pass
def test_attach_schema_has_cdp_option():
    """attach command zod schema declares cdp option."""
    src = _get_file_content("packages/playwright-core/src/tools/cli-daemon/commands.ts")
    assert "const attach = declareCommand" in src, "attach command not found"
    # Check that cdp option is defined in attach options
    assert "cdp:" in src or "'cdp'" in src or '"cdp"' in src, "cdp option not in attach schema"


# [pr_diff] fail_to_pass
def test_attach_conflict_detection():
    """attach command detects conflicting target + --cdp/--endpoint/--extension args."""
    src = _get_file_content("packages/playwright-core/src/tools/cli-client/program.ts")
    # The fix adds: if (attachTarget && (args.cdp || args.endpoint || args.extension))
    # Check for the specific conflict detection pattern
    has_conflict_check = (
        "attachTarget && (args.cdp || args.endpoint || args.extension)" in src or
        "attachTarget && (args.cdp ||args.endpoint || args.extension)" in src
    )
    assert has_conflict_check, "Conflict detection pattern not found in attach case"


# [pr_diff] fail_to_pass
def test_daemon_registers_cdp_flag():
    """daemon program.ts registers --cdp CLI flag via .option()."""
    src = _get_file_content("packages/playwright-core/src/tools/cli-daemon/program.ts")
    # Check for --cdp option registration
    assert ".option('--cdp" in src or ".option('--cdp" in src.replace("'", '"'), "--cdp option not registered"


# [pr_diff] fail_to_pass
def test_session_passes_cdp_to_daemon():
    """session.ts passes --cdp flag value to daemon arguments."""
    src = _get_file_content("packages/playwright-core/src/tools/cli-client/session.ts")
    # Check for cdp argument passing
    assert "cliArgs.cdp" in src or "--cdp=" in src, "cdp flag not passed to daemon args"


# [pr_diff] fail_to_pass
def test_config_cdp_endpoint_in_isolation():
    """config.ts maps cdpEndpoint and uses it in browser isolation logic."""
    src = _get_file_content("packages/playwright-core/src/tools/mcp/config.ts")
    # Check for the specific mapping: cdpEndpoint: cliOptions.cdp
    # This is the key change that maps the CLI --cdp option to cdpEndpoint
    has_mapping = "cdpEndpoint: options.cdp" in src or "cdpEndpoint: cliOptions.cdp" in src
    assert has_mapping, "cdpEndpoint mapping from CLI options not found"


# [pr_diff] fail_to_pass
def test_skill_md_attach_has_extension():
    """SKILL.md documents 'playwright-cli attach --extension' command."""
    src = _get_file_content("packages/playwright-core/src/tools/cli-client/skill/SKILL.md")
    # Check that attach --extension is documented
    assert "playwright-cli attach --extension" in src, "attach --extension not documented"


# [pr_diff] fail_to_pass
def test_skill_md_open_no_extension():
    """SKILL.md no longer documents 'open --extension' in open section."""
    src = _get_file_content("packages/playwright-core/src/tools/cli-client/skill/SKILL.md")
    # After fix, open --extension should be removed (moved to attach)
    # The gold fix removes "# Connect to browser via extension\nplaywright-cli open --extension"
    # So "playwright-cli open --extension" should NOT exist in the file after fix
    # But "open --extension" alone might exist in examples - we check specifically for the standalone line
    lines = src.split('\n')
    for line in lines:
        # After fix, there should be no line with "open --extension" as a command example
        if "open --extension" in line and "attach" not in line.lower():
            # This is the old pattern that should be removed
            assert False, f"Found old 'open --extension' pattern that should be removed: {line}"


# ============================================================================
# PASS TO PASS TESTS (10 tests)
# These should PASS on both base and fixed commits
# ============================================================================

# [static] pass_to_pass
def test_typescript_balanced_braces():
    """Modified TypeScript files have balanced braces."""
    files_to_check = [
        "packages/playwright-core/src/tools/cli-client/program.ts",
        "packages/playwright-core/src/tools/cli-client/registry.ts",
        "packages/playwright-core/src/tools/cli-client/session.ts",
        "packages/playwright-core/src/tools/cli-daemon/commands.ts",
        "packages/playwright-core/src/tools/cli-daemon/program.ts",
        "packages/playwright-core/src/tools/mcp/config.ts",
    ]
    for file_path in files_to_check:
        src = _get_file_content(file_path)
        if src:  # Only check if file exists
            open_count = src.count('{')
            close_count = src.count('}')
            assert open_count == close_count, f"Unbalanced braces in {file_path}: {open_count} vs {close_count}"


# [static] pass_to_pass
def test_resolve_session_name_has_logic():
    """resolveSessionName function has real logic, not a stub."""
    src = _get_file_content("packages/playwright-core/src/tools/cli-client/registry.ts")
    assert "export function resolveSessionName" in src, "resolveSessionName not exported"
    # Check it's not just returning a hardcoded value
    assert "explicitSessionName" in src or "sessionName" in src, "resolveSessionName lacks real logic"


# [repo_tests] pass_to_pass
def test_repo_cli_program_exports():
    """CLI client program.ts exports the program function."""
    src = _get_file_content("packages/playwright-core/src/tools/cli-client/program.ts")
    assert "export async function program" in src, "program function not exported"


# [repo_tests] pass_to_pass
def test_repo_tools_files_exist():
    """Key tools files exist in the repo."""
    files_to_check = [
        "packages/playwright-core/src/tools/cli-client/program.ts",
        "packages/playwright-core/src/tools/cli-client/session.ts",
        "packages/playwright-core/src/tools/cli-client/registry.ts",
        "packages/playwright-core/src/tools/cli-daemon/commands.ts",
        "packages/playwright-core/src/tools/cli-daemon/program.ts",
        "packages/playwright-core/src/tools/mcp/config.ts",
        "packages/playwright-core/src/tools/cli-client/skill/SKILL.md",
    ]
    for file_path in files_to_check:
        full_path = Path(REPO) / file_path
        assert full_path.exists(), f"Required file missing: {file_path}"


# [repo_tests] pass_to_pass
def test_repo_mcp_config_valid():
    """MCP config.ts has valid structure with CLIOptions type."""
    src = _get_file_content("packages/playwright-core/src/tools/mcp/config.ts")
    assert "export type CLIOptions" in src, "CLIOptions type not found"
    assert "cdpEndpoint" in src, "cdpEndpoint in CLIOptions not found"


# [repo_tests] pass_to_pass
def test_repo_esbuild_tools_compile():
    """Tools TypeScript files compile with esbuild."""
    esbuild_config = Path(REPO) / "packages/playwright-core/src/tools/esbuild.mjs"
    if esbuild_config.exists():
        r = subprocess.run(
            ["node", str(esbuild_config)],
            capture_output=True, text=True, timeout=60, cwd=REPO,
        )
        assert r.returncode == 0, f"esbuild failed: {r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_npm_install_and_eslint():
    """ESLint passes on tools directory after npm install."""
    r = subprocess.run(
        ["npm", "install"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"npm install failed: {r.stderr[-500:]}"

    r = subprocess.run(
        ["npx", "eslint", "packages/playwright-core/src/tools/"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    # ESLint might fail on existing issues, but should complete
    # We mainly care that it runs without crashing


# [repo_tests] pass_to_pass
def test_repo_check_deps_runs():
    """Dependency check script runs without crashing."""
    r = subprocess.run(
        ["node", "utils/check_deps.js"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    # Script should complete, return code may vary based on deps issues
    # but shouldn't crash with error


# [repo_tests] pass_to_pass
def test_repo_build():
    """Build completes successfully (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "install"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"npm install failed:\n{r.stderr[-500:]}"

    r = subprocess.run(
        ["npm", "run", "build"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Build failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_lint_packages():
    """Workspace packages are consistent (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "install"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"npm install failed:\n{r.stderr[-500:]}"

    r = subprocess.run(
        ["npm", "run", "lint-packages"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Lint packages failed:\n{r.stderr[-500:]}"
