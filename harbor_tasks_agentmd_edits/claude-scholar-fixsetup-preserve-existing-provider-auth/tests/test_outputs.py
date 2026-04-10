"""
Task: claude-scholar-fixsetup-preserve-existing-provider-auth
Repo: Galaxy-Dawn/claude-scholar @ d6fa24e0597692c21e16f976ec159a1482adcc2d
PR:   14

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

REPO = "/workspace/claude-scholar"
SETUP_SH = f"{REPO}/scripts/setup.sh"


def _source_and_run(code, env_extra=None):
    """Source setup.sh functions (without running main) and execute code."""
    env = {
        "HOME": "/tmp",
        "PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
        "TERM": "dumb",
    }
    if env_extra:
        env.update(env_extra)
    # Remove main invocation and relax error handling for testability
    script = f"""
source <(sed '/^main "\\$@"$/d; s/^set -euo pipefail$/set +e/' '{SETUP_SH}')
{code}
"""
    return subprocess.run(
        ["bash", "-c", script],
        capture_output=True, text=True, timeout=30, env=env,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """setup.sh must parse without bash syntax errors."""
    r = subprocess.run(
        ["bash", "-n", SETUP_SH],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"Bash syntax error: {r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_mask_secret_hides_long_keys():
    """mask_secret must show first 8 and last 4 chars of long secrets."""
    r = _source_and_run(
        'mask_secret "sk-abcdefgh_MIDDLE_wxyz"'
    )
    out = r.stdout.strip()
    assert "..." in out, f"mask_secret should contain '...', got: {out}"
    assert out.startswith("sk-abcde"), f"Should start with first 8 chars, got: {out}"
    assert out.endswith("wxyz"), f"Should end with last 4 chars, got: {out}"


# [pr_diff] fail_to_pass
def test_mask_secret_preserves_short():
    """mask_secret must return short secrets (<=12 chars) unchanged."""
    r = _source_and_run('mask_secret "short_key"')
    out = r.stdout.strip()
    assert out == "short_key", f"Short secret should be unchanged, got: {out}"


# [pr_diff] fail_to_pass
def test_normalize_env_prefix():
    """normalize_env_prefix must uppercase and replace separators."""
    r = _source_and_run('normalize_env_prefix "my-custom.provider"')
    out = r.stdout.strip()
    assert out == "MY_CUSTOM_PROVIDER", f"Expected MY_CUSTOM_PROVIDER, got: {out}"


# [pr_diff] fail_to_pass
def test_collect_api_key_candidates_provider_first():
    """collect_api_key_candidates with a provider puts its key first."""
    r = _source_and_run('collect_api_key_candidates "deepseek"')
    lines = r.stdout.strip().splitlines()
    assert len(lines) >= 2, f"Expected multiple candidates, got: {lines}"
    assert lines[0] == "DEEPSEEK_API_KEY", \
        f"Provider-specific key should be first, got: {lines[0]}"
    assert "OPENAI_API_KEY" in lines, "OPENAI_API_KEY should be in candidates"
    assert "ANTHROPIC_API_KEY" in lines, "ANTHROPIC_API_KEY should be in candidates"


# [pr_diff] fail_to_pass
def test_detect_existing_preserves_silently():
    """detect_existing must preserve config without interactive prompts (no read -rp)."""
    r = _source_and_run("""
        export CODEX_HOME=$(mktemp -d)
        echo 'model = "gpt-4"' > "$CODEX_HOME/config.toml"
        echo 'model_provider = "openai"' >> "$CODEX_HOME/config.toml"
        detect_existing < /dev/null
        echo "RESULT_SKIP_PROVIDER=$SKIP_PROVIDER"
        rm -rf "$CODEX_HOME"
    """)
    combined = r.stdout + r.stderr
    assert "RESULT_SKIP_PROVIDER=true" in r.stdout, \
        f"detect_existing should set SKIP_PROVIDER=true, got: {r.stdout}"
    # The fixed version says "without prompting"; the base version says "Keep existing"
    assert "without prompting" in combined or "keeping it without" in combined.lower(), \
        f"detect_existing should report silent preservation, got: {combined}"
    # Must NOT contain interactive prompt text
    assert "Keep existing provider/model config? [Y/n]" not in combined, \
        "detect_existing should not prompt user to keep config"


# [pr_diff] fail_to_pass
def test_check_deps_requires_node():
    """check_deps must require node (not python3) as a dependency."""
    # Create a PATH with git + node only (no python3)
    r = _source_and_run("""
        TBIN=$(mktemp -d)
        ln -s "$(which git)" "$TBIN/git"
        ln -s "$(which node)" "$TBIN/node"
        export PATH="$TBIN"
        check_deps 2>&1
        echo "CHECK_DEPS_RC=$?"
        rm -rf "$TBIN"
    """)
    assert "CHECK_DEPS_RC=0" in r.stdout, \
        f"check_deps should pass with git+node (no python3 needed): {r.stdout} {r.stderr}"


# [pr_diff] fail_to_pass
def test_write_auth_custom_env_creates_dual_keys():
    """write_auth with a custom env var name must write both custom and OPENAI_API_KEY."""
    with tempfile.TemporaryDirectory() as tmpdir:
        target = Path(tmpdir) / "auth.json"
        r = _source_and_run(f"""
            export CODEX_HOME="{tmpdir}"
            PERSIST_AUTH=true
            AUTH_ENV_VAR_NAME="DEEPSEEK_API_KEY"
            API_KEY="sk-test-12345"
            write_auth
        """)
        assert target.exists(), f"write_auth should create auth.json, got: {r.stdout} {r.stderr}"
        data = json.loads(target.read_text())
        assert "DEEPSEEK_API_KEY" in data, "auth.json should contain DEEPSEEK_API_KEY"
        assert "OPENAI_API_KEY" in data, "auth.json should also contain OPENAI_API_KEY for compat"
        assert data["DEEPSEEK_API_KEY"] == "sk-test-12345"
        assert data["OPENAI_API_KEY"] == "sk-test-12345"


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — README documentation updates
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — Repo CI/CD checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_bash_syntax():
    """All shell scripts must have valid bash syntax (pass_to_pass)."""
    scripts = [
        f"{REPO}/scripts/setup.sh",
        f"{REPO}/skills/hook-development/scripts/hook-linter.sh",
        f"{REPO}/skills/hook-development/scripts/test-hook.sh",
        f"{REPO}/skills/hook-development/scripts/validate-hook-schema.sh",
        f"{REPO}/skills/hook-development/examples/validate-bash.sh",
        f"{REPO}/skills/hook-development/examples/validate-write.sh",
        f"{REPO}/skills/hook-development/examples/load-context.sh",
        f"{REPO}/skills/agent-identifier/scripts/validate-agent.sh",
        f"{REPO}/skills/skill-improver/scripts/backup-skill.sh",
        f"{REPO}/skills/skill-improver/scripts/verify-update.sh",
        f"{REPO}/skills/skill-quality-reviewer/scripts/extract-yaml.sh",
    ]
    for script in scripts:
        r = subprocess.run(
            ["bash", "-n", script],
            capture_output=True, text=True, timeout=30,
        )
        assert r.returncode == 0, f"Bash syntax error in {script}:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_hook_linter():
    """setup.sh must pass hook-linter checks (pass_to_pass)."""
    r = subprocess.run(
        ["bash", f"{REPO}/skills/hook-development/scripts/hook-linter.sh", SETUP_SH],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Hook linter failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_node_syntax():
    """All JavaScript files must have valid Node.js syntax (pass_to_pass)."""
    scripts = [
        f"{REPO}/scripts/lib/package-manager.js",
        f"{REPO}/scripts/lib/utils.js",
        f"{REPO}/scripts/setup-package-manager.js",
    ]
    for script in scripts:
        r = subprocess.run(
            ["node", "--check", script],
            capture_output=True, text=True, timeout=30,
        )
        assert r.returncode == 0, f"Node.js syntax error in {script}:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_js_modules():
    """All JavaScript modules must load without errors (pass_to_pass)."""
    modules = [
        f"{REPO}/scripts/lib/package-manager.js",
        f"{REPO}/scripts/lib/utils.js",
    ]
    for module in modules:
        r = subprocess.run(
            ["node", "-e", f"require('{module}'); console.log('OK')"],
            capture_output=True, text=True, timeout=30,
        )
        assert r.returncode == 0, f"Node.js module load failed for {module}:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_skill_backup():
    """Skill backup script must work with actual skill (pass_to_pass)."""
    r = subprocess.run(
        ["bash", f"{REPO}/skills/skill-improver/scripts/backup-skill.sh", f"{REPO}/skills/git-workflow"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Skill backup failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_extract_yaml():
    """Skill YAML extraction script must work with actual skill (pass_to_pass)."""
    r = subprocess.run(
        ["bash", f"{REPO}/skills/skill-quality-reviewer/scripts/extract-yaml.sh", f"{REPO}/skills/git-workflow"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"YAML extraction failed:\n{r.stdout}\n{r.stderr}"
    # Verify it extracted expected fields
    assert "name:" in r.stdout, f"Expected 'name:' field in output:\n{r.stdout}"
    assert "description:" in r.stdout, f"Expected 'description:' field in output:\n{r.stdout}"


# [repo_tests] pass_to_pass
def test_repo_python_syntax():
    """All Python files must have valid syntax (pass_to_pass)."""
    scripts = [
        f"{REPO}/utils/platform_utils.py",
        f"{REPO}/scripts/codex_hook_emulation.py",
    ]
    for script in scripts:
        r = subprocess.run(
            ["python3", "-m", "py_compile", script],
            capture_output=True, text=True, timeout=30,
        )
        assert r.returncode == 0, f"Python syntax error in {script}:\n{r.stderr}"
