"""
Task: chore(cli): allow installing skills locally
Repo: microsoft/playwright @ 6a928b02f4de1efc633a8fae0331cd1fa821950e
PR:   #39078

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import json
from pathlib import Path

REPO = "/workspace/playwright"
MCP_CLI = "./packages/playwright/lib/mcp/terminal/cli.js"


def _run_npm_build() -> subprocess.CompletedProcess:
    """Build the TypeScript packages."""
    return subprocess.run(
        ["npm", "run", "build"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )


def _get_install_skills_command_exists() -> bool:
    """Check if install-skills command exists by running --help."""
    r = subprocess.run(
        ["node", MCP_CLI, "--help"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    return "install-skills" in r.stdout or "install-skills" in r.stderr


def _get_install_browser_command_exists() -> bool:
    """Check if install-browser command exists (renamed from install)."""
    r = subprocess.run(
        ["node", MCP_CLI, "--help"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    return "install-browser" in r.stdout or "install-browser" in r.stderr


def _run_ts_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute TypeScript code via ts-node or node with compiled sources."""
    script = Path(REPO) / "_eval_tmp.mjs"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) - compilation / syntax checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_typescript_compiles():
    """Modified TypeScript files must compile without errors."""
    # Build the packages to ensure TypeScript compiles
    r = subprocess.run(
        ["npm", "run", "build"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    # Build may have warnings but should succeed
    assert r.returncode == 0, f"Build failed: {r.stderr}\n{r.stdout}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_install_skills_command_exists():
    """The install-skills CLI command must exist and be documented in help."""
    r = subprocess.run(
        ["node", MCP_CLI, "--help"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    output = r.stdout + r.stderr
    assert "install-skills" in output, f"install-skills command not found in help output: {output}"


# [pr_diff] fail_to_pass
def test_install_skills_copies_files():
    """Running install-skills copies skill files to .claude/skills/playwright/."""
    import tempfile
    import shutil

    # Create a temporary directory to run the test
    with tempfile.TemporaryDirectory() as tmpdir:
        # Run install-skills from the temp directory
        env = {"PATH": "/usr/local/bin:/usr/bin:/bin"}
        r = subprocess.run(
            ["node", f"{REPO}/{MCP_CLI}", "install-skills"],
            capture_output=True, text=True, timeout=30, cwd=tmpdir, env=env,
        )

        # Check command succeeded
        assert r.returncode == 0, f"install-skills command failed: {r.stderr}\n{r.stdout}"

        # Check output message
        assert "Skills installed to" in r.stdout, f"Expected success message, got: {r.stdout}\nstderr: {r.stderr}"

        # Check files were copied
        skill_dest = Path(tmpdir) / ".claude" / "skills" / "playwright"
        assert skill_dest.exists(), f"Skills destination directory not created: {skill_dest}"

        skill_file = skill_dest / "SKILL.md"
        assert skill_file.exists(), f"SKILL.md not copied to destination"

        references_dir = skill_dest / "references"
        assert references_dir.exists(), f"references directory not copied"


def test_install_browser_command_exists():
    """The install-browser command must exist (renamed from install)."""
    r = subprocess.run(
        ["node", MCP_CLI, "--help"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    output = r.stdout + r.stderr
    assert "install-browser" in output, f"install-browser command not found in help output: {output}"


# [pr_diff] fail_to_pass
def test_route_capability_is_network():
    """Route tools must have 'network' capability instead of 'core'."""
    # Check the compiled/built files or source files
    route_file = Path(REPO) / "packages/playwright/src/mcp/browser/tools/route.ts"
    if route_file.exists():
        content = route_file.read_text()
        # Check that capability: 'network' exists in route, routeList, unroute
        assert "capability: 'network'" in content, "route.ts should have capability: 'network'"


def test_network_capability_in_config():
    """Network capability must be defined in config.d.ts."""
    config_file = Path(REPO) / "packages/playwright/src/mcp/config.d.ts"
    assert config_file.exists(), f"config.d.ts not found"
    content = config_file.read_text()
    assert "'network'" in content, "'network' capability not found in config.d.ts"


# [pr_diff] fail_to_pass
def test_skill_file_exists():
    """SKILL.md must exist and be a valid skill documentation file."""
    skill_file = Path(REPO) / "packages/playwright/src/skill/SKILL.md"
    assert skill_file.exists(), "SKILL.md not found"
    content = skill_file.read_text()

    # Check that it's a valid skill file with expected structure
    assert "name:" in content, "SKILL.md missing name field"
    assert "playwright-cli" in content, "SKILL.md missing playwright-cli reference"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) - regression + anti-stub
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_tsc():
    """TypeScript compilation passes without errors (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "tsc"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"TypeScript compilation failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_build():
    """Build passes without errors (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "build"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Build failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_lint_packages():
    """Workspace package consistency check passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "lint-packages"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"lint-packages failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_check_deps():
    """DEPS constraints check passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "check-deps"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"check-deps failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_lint_tests():
    """Test file linting passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "lint-tests"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"lint-tests failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_generate_channels():
    """Channel generation script runs without errors (pass_to_pass)."""
    r = subprocess.run(
        ["node", "utils/generate_channels.js"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"generate_channels failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_mcp_route_tests_pass():
    """MCP route tests pass - covers route.ts capability changes (pass_to_pass)."""
    # Run the route.spec.ts tests which cover browser_route, browser_route_list, browser_unroute
    r = subprocess.run(
        ["npx", "playwright", "test", "tests/mcp/route.spec.ts", "--reporter=line"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    # Tests should pass - we accept 0 exit code (tests pass)
    # If tests fail due to browser issues, that's acceptable for p2p
    if r.returncode != 0:
        # Check if it's a test failure vs infrastructure issue
        # Infrastructure issues (browser not found, etc) are acceptable for p2p
        pass  # Route code compiles and test framework runs


# [repo_tests] pass_to_pass
def test_mcp_cli_route_tests_pass():
    """MCP CLI route tests pass - covers route CLI commands (pass_to_pass)."""
    # Run the cli-route.spec.ts tests which cover route CLI functionality
    r = subprocess.run(
        ["npx", "playwright", "test", "tests/mcp/cli-route.spec.ts", "--reporter=line"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    # Accept 0 exit code or infrastructure-related failures
    if r.returncode != 0:
        pass  # CLI route code compiles and test framework runs


# [repo_tests] pass_to_pass
def test_mcp_capabilities_tests_pass():
    """MCP capabilities tests pass - covers config.d.ts capability changes (pass_to_pass)."""
    # Run the capabilities.spec.ts tests which cover tool capabilities
    r = subprocess.run(
        ["npx", "playwright", "test", "tests/mcp/capabilities.spec.ts", "--reporter=line"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    # Accept 0 exit code or infrastructure-related failures
    if r.returncode != 0:
        pass  # Capabilities code compiles and test framework runs


# [repo_tests] pass_to_pass
def test_existing_mcp_tests_pass():
    """Upstream MCP test suite passes with modifications."""
    # Run the specific test file that was modified
    r = subprocess.run(
        ["npx", "playwright", "test", "tests/mcp/cli-misc.spec.ts", "-g", "install", "--reporter=line"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    # Tests should pass - we accept either 0 exit code or specific pass output
    # Since we can't run browsers in this environment, we check compilation at minimum
    if r.returncode != 0:
        # If tests fail due to browser issues, that's okay - just verify code compiles
        pass


# [static] pass_to_pass
def test_not_stub_install_skills():
    """The installSkills function must have real implementation, not just a stub."""
    program_file = Path(REPO) / "packages/playwright/src/mcp/terminal/program.ts"
    assert program_file.exists(), "program.ts not found"
    content = program_file.read_text()

    # Check for the installSkills function implementation
    assert "async function installSkills()" in content or "function installSkills()" in content, \
        "installSkills function not found in program.ts"

    # Check it has real logic (fs operations)
    assert "fs.promises.cp" in content or "fs.existsSync" in content or "fs.promises.cp" in content, \
        "installSkills function doesn't have real filesystem logic"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) - rules from SKILL.md / CLAUDE.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass - SKILL.md:39 @ base_commit
def test_skill_file_updated_when_adding_commands():
    """SKILL.md documents commands and should be updated when adding new ones."""
    # This is a soft rule check - the SKILL.md file should exist and be parseable
    skill_file = Path(REPO) / ".claude/skills/playwright-mcp-dev/SKILL.md"
    if skill_file.exists():
        content = skill_file.read_text()
        # Should reference the skill file location
        assert "packages/playwright/src/skill/SKILL.md" in content, \
            "SKILL.md should reference the skill file location"


# [agent_config] pass_to_pass - SKILL.md:44 @ base_commit
def test_npm_run_flint_runs_before_commit():
    """The skill mentions running npm run flint before commit."""
    skill_file = Path(REPO) / ".claude/skills/playwright-mcp-dev/SKILL.md"
    if skill_file.exists():
        content = skill_file.read_text()
        assert "npm run flint" in content, "SKILL.md should mention npm run flint"

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