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
def test_attach_command_schema_via_build():
    """Build commands module and verify attach command schema includes cdp, endpoint, extension."""
    import json as _json

    # Install dependencies (esbuild + zod are devDependencies)
    r = subprocess.run(
        ["npm", "install", "--ignore-scripts"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"npm install failed: {r.stderr[-500:]}"

    # Use esbuild to compile the help generator and check attach command schema.
    # zodPlugin resolves the internal zodBundleImpl import to its actual location.
    script = Path(REPO) / "_eval_schema_check.cjs"
    script.write_text(
        "const esbuild = require('esbuild');\n"
        "const path = require('path');\n"
        "\n"
        "const zodPlugin = {\n"
        "  name: 'zodBundle-resolver',\n"
        "  setup(build) {\n"
        "    build.onResolve({ filter: /zodBundleImpl/ }, args => ({\n"
        "      path: path.resolve(process.cwd(), 'packages/playwright-core/bundles/zod/src/zodBundleImpl.ts')\n"
        "    }));\n"
        "  }\n"
        "};\n"
        "\n"
        "(async () => {\n"
        "  await esbuild.build({\n"
        "    entryPoints: [path.join(process.cwd(), 'packages/playwright-core/src/tools/cli-daemon/helpGenerator.ts')],\n"
        "    bundle: true, platform: 'node', format: 'cjs',\n"
        "    outfile: '/tmp/_eval_help_check.cjs',\n"
        "    plugins: [zodPlugin], logLevel: 'silent',\n"
        "  });\n"
        "  const { generateHelpJSON } = require('/tmp/_eval_help_check.cjs');\n"
        "  const helpJSON = generateHelpJSON();\n"
        "  const attachFlags = Object.keys(helpJSON.commands.attach?.flags || {});\n"
        "  console.log(JSON.stringify({ attachFlags }));\n"
        "})().catch(e => { console.error(e.message); process.exit(1); });\n"
    )
    try:
        r = subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=60, cwd=REPO,
        )
        assert r.returncode == 0, f"Schema build/check failed: {r.stderr}"
        data = _json.loads(r.stdout.strip().split('\n')[-1])
        assert "cdp" in data["attachFlags"], "cdp not in attach command flags"
        assert "endpoint" in data["attachFlags"], "endpoint not in attach command flags"
        assert "extension" in data["attachFlags"], "extension not in attach command flags"
    finally:
        script.unlink(missing_ok=True)
        Path("/tmp/_eval_help_check.cjs").unlink(missing_ok=True)


# [pr_diff] fail_to_pass
def test_attach_conflict_detection():
    """attach command detects conflicting target + --cdp/--endpoint/--extension args."""
    src = _get_file_content("packages/playwright-core/src/tools/cli-client/program.ts")
    # Find the attach case section
    attach_start = src.find("case 'attach'")
    if attach_start == -1:
        attach_start = src.find('case "attach"')
    assert attach_start >= 0, "attach case not found in program.ts"
    # Get the attach case section (until a reasonable boundary)
    attach_section = src[attach_start:attach_start + 2000]
    # The attach case must reference cdp, endpoint, extension for conflict detection
    assert "cdp" in attach_section, "cdp not referenced in attach case"
    assert "endpoint" in attach_section, "endpoint not referenced in attach case"
    assert "extension" in attach_section, "extension not referenced in attach case"
    # Must have error handling when conflicting args are provided
    has_error_handling = (
        "process.exit" in attach_section or
        "throw" in attach_section or
        "Error" in attach_section
    )
    assert has_error_handling, "No error handling found for conflicting options in attach case"


# [pr_diff] fail_to_pass
def test_daemon_registers_cdp_flag():
    """daemon program.ts registers --cdp CLI flag via .option()."""
    src = _get_file_content("packages/playwright-core/src/tools/cli-daemon/program.ts")
    # Check for --cdp option registration
    assert "'--cdp" in src or '"--cdp' in src, "--cdp option not registered"


# [pr_diff] fail_to_pass
def test_session_passes_cdp_to_daemon():
    """session.ts passes --cdp flag value to daemon arguments."""
    src = _get_file_content("packages/playwright-core/src/tools/cli-client/session.ts")
    # Check for cdp argument passing
    assert "cliArgs.cdp" in src or "--cdp=" in src, "cdp flag not passed to daemon args"


# [pr_diff] fail_to_pass
def test_config_cdp_endpoint_in_isolation():
    """config.ts maps cdpEndpoint from CLI options and uses it in browser isolation logic."""
    src = _get_file_content("packages/playwright-core/src/tools/mcp/config.ts")
    # Find the resolveCLIConfigForCLI function
    fn_start = src.find("resolveCLIConfigForCLI")
    assert fn_start >= 0, "resolveCLIConfigForCLI not found"
    fn_section = src[fn_start:fn_start + 3000]

    # Check 1: cdpEndpoint is passed in the configFromCLIOptions call within this function
    config_call_start = fn_section.find("configFromCLIOptions(")
    assert config_call_start >= 0, "configFromCLIOptions call not found in resolveCLIConfigForCLI"
    config_call = fn_section[config_call_start:config_call_start + 500]
    assert "cdpEndpoint" in config_call, "cdpEndpoint not passed in configFromCLIOptions call"

    # Check 2: cdpEndpoint is used in isolation logic
    isolated_lines = [line for line in fn_section.split('\n') if 'isolated' in line and '=' in line]
    has_cdp_in_isolation = any('cdpEndpoint' in line for line in isolated_lines)
    assert has_cdp_in_isolation, "cdpEndpoint not used in browser isolation logic"


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
def test_repo_npm_install_and_eslint():
    """ESLint passes on tools directory after npm install."""
    r = subprocess.run(
        ["npm", "install"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"npm install failed: {r.stderr[-500:]}"

    # Verify eslint is usable: check a single known-good file
    eslint_bin = Path(REPO, "node_modules/.bin/eslint")
    assert eslint_bin.exists(), "eslint binary not found after npm install"
    r = subprocess.run(
        [str(eslint_bin), "packages/playwright-core/src/tools/mcp/config.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"eslint could not run on config.ts:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_check_deps_runs():
    """Dependency check script runs without crashing."""
    r = subprocess.run(
        ["node", "utils/check_deps.js"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    # Verify the script actually executed (may have pre-existing warnings)
    assert "Checking DEPS" in (r.stdout + r.stderr), (
        f"check_deps.js did not execute properly. stdout: {r.stdout[:500]}, stderr: {r.stderr[:500]}")


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

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_build_playwright_driver_npm():
    """pass_to_pass | CI job 'build-playwright-driver' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'npm ci'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_playwright_driver_npm_2():
    """pass_to_pass | CI job 'build-playwright-driver' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'npm run build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")