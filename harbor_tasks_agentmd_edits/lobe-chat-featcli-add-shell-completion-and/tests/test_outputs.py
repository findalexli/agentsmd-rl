"""
Task: lobe-chat-featcli-add-shell-completion-and
Repo: lobehub/lobe-chat @ 12280badbdf288b7018a9d5b907898780cd31a96
PR:   13164

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import json
from pathlib import Path

REPO = "/workspace/lobe-chat"
CLI_DIR = f"{REPO}/apps/cli"


def _run_in_cli(cmd: list[str], timeout: int = 60, env: dict | None = None) -> subprocess.CompletedProcess:
    """Run a command in the CLI directory."""
    full_env = {"PATH": "/usr/local/bin:/usr/bin:/bin"}
    if env:
        full_env.update(env)
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=CLI_DIR,
        env=full_env,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_typescript_compiles():
    """TypeScript source files compile without errors."""
    # Check that tsc can parse the modified files
    r = _run_in_cli(["npx", "tsc", "--noEmit"], timeout=120)
    assert r.returncode == 0, f"TypeScript compilation failed:\n{r.stdout}\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_completion_command_exists():
    """The completion command outputs a valid shell completion script."""
    # The fix adds a 'completion [shell]' command that outputs a shell script
    # Before the fix, this command doesn't exist
    r = _run_in_cli(
        ["bun", "run", "--silent", "src/index.ts", "completion", "zsh"],
        timeout=30,
    )
    assert r.returncode == 0, f"completion command failed: {r.stderr}"
    output = r.stdout.strip()
    # Should contain zsh-specific completion syntax
    assert "compdef _lobehub_completion" in output, f"Missing compdef in zsh output: {output[:200]}"
    assert "lh lobe lobehub" in output, f"Missing CLI names in output: {output[:200]}"


# [pr_diff] fail_to_pass
def test_completion_bash_output():
    """The completion command outputs valid bash completion script."""
    r = _run_in_cli(
        ["bun", "run", "--silent", "src/index.ts", "completion", "bash"],
        timeout=30,
    )
    assert r.returncode == 0, f"completion bash command failed: {r.stderr}"
    output = r.stdout.strip()
    # Should contain bash-specific completion syntax
    assert "complete -o nosort" in output, f"Missing complete command in bash output: {output[:200]}"
    assert "_lobehub_completion" in output, f"Missing function name in bash output: {output[:200]}"


# [pr_diff] fail_to_pass
def test_complete_internal_command_suggests_commands():
    """The __complete internal command suggests subcommands."""
    # The __complete command is used by shell completion to get candidates
    # LOBEHUB_COMP_CWORD=0 means we're completing the first word (commands)
    r = _run_in_cli(
        ["bun", "run", "--silent", "src/index.ts", "__complete"],
        timeout=30,
        env={"LOBEHUB_COMP_CWORD": "0"},
    )
    assert r.returncode == 0, f"__complete command failed: {r.stderr}"
    output = r.stdout.strip()
    # Should list some visible commands
    lines = [l for l in output.split("\n") if l.strip()]
    # Common commands should be present: agent, login, logout, config, etc.
    commands_found = [l for l in lines if l in ["agent", "login", "logout", "config", "status"]]
    assert len(commands_found) >= 3, f"Expected visible commands, got: {lines[:20]}"


# [pr_diff] fail_to_pass
def test_complete_internal_nested_subcommands():
    """The __complete command suggests nested subcommands in context."""
    # When completing "agent " (with trailing space), should suggest agent subcommands
    r = _run_in_cli(
        ["bun", "run", "--silent", "src/index.ts", "__complete", "agent"],
        timeout=30,
        env={"LOBEHUB_COMP_CWORD": "1"},  # Completing second word
    )
    assert r.returncode == 0, f"__complete command failed: {r.stderr}"
    output = r.stdout.strip()
    lines = [l for l in output.split("\n") if l.strip()]
    # Should suggest agent subcommands like "list"
    assert any("list" in l for l in lines), f"Expected 'list' in agent subcommands, got: {lines}"


# [pr_diff] fail_to_pass
def test_tsdown_build_config_exists():
    """The tsdown.config.ts exists and is valid."""
    # The fix migrates from tsup to tsdown
    config_path = Path(f"{CLI_DIR}/tsdown.config.ts")
    assert config_path.exists(), f"tsdown.config.ts does not exist at {config_path}"
    content = config_path.read_text()
    # Should have the tsdown config structure
    assert "defineConfig" in content, "Missing defineConfig in tsdown.config.ts"
    assert "banner" in content, "Missing banner config"
    assert "entry: ['src/index.ts']" in content or 'entry: ["src/index.ts"]' in content, "Missing entry point"


# [pr_diff] fail_to_pass
def test_tsup_config_removed():
    """The old tsup.config.ts is removed."""
    # Migration from tsup to tsdown means tsup.config.ts should be gone
    config_path = Path(f"{CLI_DIR}/tsup.config.ts")
    assert not config_path.exists(), f"Old tsup.config.ts still exists (should be removed)"


# [pr_diff] fail_to_pass
def test_package_json_uses_tsdown():
    """package.json uses tsdown instead of tsup for build."""
    pkg_path = Path(f"{CLI_DIR}/package.json")
    pkg = json.loads(pkg_path.read_text())
    # The build script should use tsdown, not tsup
    build_script = pkg.get("scripts", {}).get("build", "")
    assert "tsdown" in build_script, f"Expected build script to use tsdown, got: {build_script}"
    assert "tsup" not in build_script, f"Build script still references tsup: {build_script}"


# [pr_diff] fail_to_pass
def test_completion_utils_exists():
    """The completion utility module exists with required exports."""
    utils_path = Path(f"{CLI_DIR}/src/utils/completion.ts")
    assert utils_path.exists(), f"completion.ts utils does not exist"
    content = utils_path.read_text()
    # Should export the required functions
    assert "getCompletionCandidates" in content, "Missing getCompletionCandidates export"
    assert "renderCompletionScript" in content, "Missing renderCompletionScript export"
    assert "resolveCompletionShell" in content, "Missing resolveCompletionShell export"


# [pr_diff] fail_to_pass
def test_completion_command_module_exists():
    """The completion command module exists and exports register function."""
    cmd_path = Path(f"{CLI_DIR}/src/commands/completion.ts")
    assert cmd_path.exists(), f"completion.ts command does not exist"
    content = cmd_path.read_text()
    assert "registerCompletionCommand" in content, "Missing registerCompletionCommand export"
    assert 'program.command("completion [shell]")' in content, "Missing completion command registration"
    assert 'program.command("__complete")' in content, "Missing __complete command registration"


# [pr_diff] fail_to_pass
def test_index_imports_completion():
    """The CLI index imports and registers the completion command."""
    index_path = Path(f"{CLI_DIR}/src/index.ts")
    content = index_path.read_text()
    assert "registerCompletionCommand" in content, "Missing registerCompletionCommand import/usage in index.ts"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_upstream_completion_tests_pass():
    """The upstream completion.test.ts unit tests pass."""
    # Run the completion-specific tests that came with the PR
    r = _run_in_cli(
        ["bun", "test", "src/commands/completion.test.ts"],
        timeout=60,
    )
    # Bun returns 0 on success, or 1 if tests fail
    assert r.returncode == 0, f"Upstream completion tests failed:\n{r.stdout}\n{r.stderr}"


# [static] pass_to_pass
def test_not_stub_completion_utils():
    """The completion utils have meaningful implementation, not stubs."""
    utils_path = Path(f"{CLI_DIR}/src/utils/completion.ts")
    content = utils_path.read_text()
    # Should have substantial implementation (not just function signatures)
    lines = [l for l in content.split("\n") if l.strip() and not l.strip().startswith("//")]
    assert len(lines) > 30, f"completion.ts is too short to be a real implementation: {len(lines)} lines"
    # Should have actual logic, not just returns
    assert "return" in content, "Missing return statements in implementation"
    # Should handle multiple shells
    assert "bash" in content and "zsh" in content, "Missing shell implementations"
