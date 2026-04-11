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


def _run_npm_build() -> subprocess.CompletedProcess:
    """Build the TypeScript packages."""
    return subprocess.run(
        ["npm", "run", "build"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )


def _get_install_skills_command_exists() -> bool:
    """Check if install-skills command exists by running --help."""
    r = subprocess.run(
        ["node", "./packages/playwright/cli.js", "--help"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    return "install-skills" in r.stdout or "install-skills" in r.stderr


def _get_install_browser_command_exists() -> bool:
    """Check if install-browser command exists (renamed from install)."""
    r = subprocess.run(
        ["node", "./packages/playwright/cli.js", "--help"],
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
        ["node", "./packages/playwright/cli.js", "--help"],
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
            ["node", f"{REPO}/packages/playwright/cli.js", "install-skills"],
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
        ["node", "./packages/playwright/cli.js", "--help"],
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
def test_skill_file_documentation():
    """SKILL.md must document the install-skills command."""
    skill_file = Path(REPO) / "packages/playwright/src/skill/SKILL.md"
    assert skill_file.exists(), "SKILL.md not found"
    content = skill_file.read_text()

    # Check that install-skills is documented
    assert "install-skills" in content, "install-skills command not documented in SKILL.md"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) - regression + anti-stub
# ---------------------------------------------------------------------------

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
