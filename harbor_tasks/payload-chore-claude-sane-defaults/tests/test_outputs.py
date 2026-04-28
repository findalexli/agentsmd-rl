"""
Task: payload-chore-claude-sane-defaults
Repo: payloadcms/payload @ 80d7781b4f2fc2e874323532a0a8a8da65c8fc22
PR:   14445

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
from pathlib import Path

REPO = "/workspace/payload"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / validation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_post_edit_hook_syntax():
    """post-edit.sh must be valid bash."""
    hook = Path(REPO) / ".claude" / "hooks" / "post-edit.sh"
    assert hook.exists(), ".claude/hooks/post-edit.sh must exist"
    r = subprocess.run(
        ["bash", "-n", str(hook)],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"Bash syntax error: {r.stderr}"


# [static] pass_to_pass
def test_settings_json_valid():
    """settings.json must be valid JSON."""
    settings = Path(REPO) / ".claude" / "settings.json"
    assert settings.exists(), ".claude/settings.json must exist"
    data = json.loads(settings.read_text())
    assert isinstance(data, dict), "settings.json root must be an object"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — post-edit hook behavior tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_post_edit_hook_extracts_filepath():
    """Hook script reads file_path from JSON stdin and processes matching files."""
    hook = Path(REPO) / ".claude" / "hooks" / "post-edit.sh"
    assert hook.exists(), ".claude/hooks/post-edit.sh must exist"

    # Create a temp .ts file so the script reaches the case/esac block
    tmp = Path(REPO) / "_eval_test_hook.ts"
    tmp.write_text("const x = 1;\n")
    try:
        r = subprocess.run(
            ["bash", str(hook)],
            input=json.dumps({"tool_input": {"file_path": str(tmp)}}),
            capture_output=True, text=True, timeout=15,
        )
        # Script should exit 0 (npx commands may fail silently, that's fine)
        assert r.returncode == 0, f"Hook failed with rc={r.returncode}: {r.stderr}"
    finally:
        tmp.unlink(missing_ok=True)


# [pr_diff] fail_to_pass
def test_post_edit_hook_handles_null_input():
    """Hook script exits 0 gracefully when file_path is null or missing."""
    hook = Path(REPO) / ".claude" / "hooks" / "post-edit.sh"
    assert hook.exists(), ".claude/hooks/post-edit.sh must exist"

    # Test with null file_path
    r = subprocess.run(
        ["bash", str(hook)],
        input=json.dumps({"tool_input": {"file_path": None}}),
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"Hook should exit 0 on null input, got rc={r.returncode}"

    # Test with empty JSON
    r2 = subprocess.run(
        ["bash", str(hook)],
        input="{}",
        capture_output=True, text=True, timeout=10,
    )
    assert r2.returncode == 0, f"Hook should exit 0 on empty JSON, got rc={r2.returncode}"


# [pr_diff] fail_to_pass
def test_post_edit_hook_case_matching():
    """Hook script has case/esac matching for different file extensions."""
    hook = Path(REPO) / ".claude" / "hooks" / "post-edit.sh"
    assert hook.exists(), ".claude/hooks/post-edit.sh must exist"
    content = hook.read_text()

    # Verify the script handles multiple file type patterns
    assert "case" in content and "esac" in content, \
        "Hook must use case/esac for file type matching"
    assert "*.ts" in content, \
        "Hook must handle TypeScript files"
    assert "*.md" in content, \
        "Hook must handle Markdown files"
    assert "package.json" in content, \
        "Hook must handle package.json"
    assert "prettier" in content, \
        "Hook must invoke prettier for formatting"
    assert "eslint" in content, \
        "Hook must invoke eslint for JS/TS files"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — settings.json config tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_settings_json_hooks_configured():
    """settings.json must configure PostToolUse hooks for Edit|Write."""
    settings = Path(REPO) / ".claude" / "settings.json"
    assert settings.exists(), ".claude/settings.json must exist"
    data = json.loads(settings.read_text())

    hooks = data.get("hooks", {})
    assert "PostToolUse" in hooks, "Must have PostToolUse hook section"

    post_hooks = hooks["PostToolUse"]
    assert isinstance(post_hooks, list) and len(post_hooks) > 0, \
        "PostToolUse must have at least one entry"

    # Find the Edit|Write matcher
    matchers = [h.get("matcher", "") for h in post_hooks]
    has_edit_write = any("Edit" in m and "Write" in m for m in matchers)
    assert has_edit_write, \
        f"Must have a matcher covering Edit and Write, got: {matchers}"

    # Verify it points to the hook script
    for entry in post_hooks:
        if "Edit" in entry.get("matcher", "") and "Write" in entry.get("matcher", ""):
            inner_hooks = entry.get("hooks", [])
            commands = [h.get("command", "") for h in inner_hooks]
            has_post_edit = any("post-edit" in c for c in commands)
            assert has_post_edit, \
                f"Hook must reference post-edit script, got commands: {commands}"


# [pr_diff] fail_to_pass
def test_settings_json_permissions():
    """settings.json must have a permissions allowlist with pnpm run and git commands."""
    settings = Path(REPO) / ".claude" / "settings.json"
    assert settings.exists(), ".claude/settings.json must exist"
    data = json.loads(settings.read_text())

    perms = data.get("permissions", {})
    allow = perms.get("allow", [])
    assert isinstance(allow, list) and len(allow) >= 10, \
        f"Permissions allowlist too small: {len(allow)} entries"

    allow_str = "\n".join(allow)
    assert "pnpm run" in allow_str, "Must allow pnpm run commands"
    assert "git log" in allow_str or "git diff" in allow_str, \
        "Must allow git read commands"
    assert "pnpm turbo" in allow_str, "Must allow pnpm turbo commands"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — CLAUDE.md documentation update tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_claude_md_documents_kv_redis():
    """CLAUDE.md must list kv-redis in the key directories section."""
    claude_md = Path(REPO) / "CLAUDE.md"
    content = claude_md.read_text()
    assert "kv-redis" in content, \
        "CLAUDE.md must document the kv-redis package"


# [pr_diff] fail_to_pass
def test_claude_md_documents_r2_storage():
    """CLAUDE.md must list R2 in storage adapters."""
    claude_md = Path(REPO) / "CLAUDE.md"
    content = claude_md.read_text()
    # R2 should be in the storage adapters line
    storage_lines = [l for l in content.splitlines() if "storage-*" in l.lower() or "Storage adapters" in l]
    assert len(storage_lines) > 0, "CLAUDE.md must mention storage adapters"
    storage_text = " ".join(storage_lines)
    assert "R2" in storage_text, \
        f"Storage adapters line must include R2, got: {storage_text}"


# [pr_diff] fail_to_pass
def test_claude_md_has_quick_start():
    """CLAUDE.md must have a Quick Start section."""
    claude_md = Path(REPO) / "CLAUDE.md"
    content = claude_md.read_text()
    assert "## Quick Start" in content or "### Quick Start" in content, \
        "CLAUDE.md must have a Quick Start section"
    # Verify it has actual steps (not just a heading)
    qs_match = re.search(r"##+ Quick Start\s*\n(.*?)\n(?=##|\Z)", content, re.DOTALL)
    assert qs_match, "Quick Start section must have content"
    qs_content = qs_match.group(1)
    assert "pnpm" in qs_content, "Quick Start must include pnpm commands"


# [pr_diff] fail_to_pass
def test_claude_md_pnpm_run_prefix():
    """Build/dev/test commands in CLAUDE.md must use 'pnpm run' prefix."""
    claude_md = Path(REPO) / "CLAUDE.md"
    content = claude_md.read_text()

    # Extract backtick-wrapped pnpm commands
    cmd_lines = re.findall(r'`(pnpm\s+\S+[^`]*)`', content)

    # Filter to build/dev/test/lint commands (not install, turbo, docker)
    actionable = [c for c in cmd_lines if any(
        c.startswith(f"pnpm {verb}") or c.startswith(f"pnpm run {verb}")
        for verb in ["build", "dev", "test", "lint"]
    )]

    # At least some commands should use 'pnpm run' prefix
    with_run = [c for c in actionable if "pnpm run " in c]
    without_run = [c for c in actionable if "pnpm run " not in c and not c.startswith("pnpm turbo")]

    assert len(with_run) >= 3, \
        f"Expected at least 3 commands with 'pnpm run' prefix, found {len(with_run)}: {with_run}"
    assert len(without_run) == 0, \
        f"Found commands without 'pnpm run' prefix: {without_run}"


# [pr_diff] fail_to_pass
def test_claude_md_pnpm_turbo_note():
    """CLAUDE.md must note that turbo should be run via pnpm, not directly."""
    claude_md = Path(REPO) / "CLAUDE.md"
    content = claude_md.read_text()
    assert "pnpm turbo" in content, \
        "CLAUDE.md must mention 'pnpm turbo'"
    # Should warn against using turbo directly
    turbo_context = [l for l in content.splitlines() if "turbo" in l.lower() and "pnpm" in l.lower()]
    has_warning = any("not" in l.lower() or "directly" in l.lower() or "should" in l.lower()
                      for l in turbo_context)
    assert has_warning, \
        "CLAUDE.md should warn that turbo must not be run directly"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI command tests that verify repo tooling works
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_prettier_claude_md():
    """CLAUDE.md passes prettier formatting check (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "prettier", "--check", f"{REPO}/CLAUDE.md"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed for CLAUDE.md:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_prettier_package_json():
    """package.json passes prettier formatting check (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "prettier", "--check", f"{REPO}/package.json"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed for package.json:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_claude_md_exists():
    """CLAUDE.md documentation file exists (pass_to_pass)."""
    claude_md = Path(REPO) / "CLAUDE.md"
    assert claude_md.exists(), "CLAUDE.md must exist"


# [static] pass_to_pass - file read check
def test_repo_prettier_rc_files():
    """Prettier config files are valid JSON (pass_to_pass)."""
    prettierrc = Path(REPO) / ".prettierrc.json"
    assert prettierrc.exists(), ".prettierrc.json must exist"
    # Validate JSON
    data = json.loads(prettierrc.read_text())
    assert isinstance(data, dict), ".prettierrc.json must be valid JSON"


# [repo_tests] pass_to_pass
def test_repo_prettier_turbo_json():
    """turbo.json passes prettier formatting check (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "prettier", "--check", f"{REPO}/turbo.json"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed for turbo.json:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_prettier_prettierrc():
    """.prettierrc.json passes prettier formatting check (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "prettier", "--check", f"{REPO}/.prettierrc.json"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed for .prettierrc.json:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_prettier_pnpm_workspace():
    """pnpm-workspace.yaml passes prettier formatting check (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "prettier", "--check", f"{REPO}/pnpm-workspace.yaml"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed for pnpm-workspace.yaml:\n{r.stderr[-500:]}"


# [static] pass_to_pass - file read check
def test_repo_package_json_valid():
    """package.json is valid JSON (pass_to_pass)."""
    package_json = Path(REPO) / "package.json"
    assert package_json.exists(), "package.json must exist"
    data = json.loads(package_json.read_text())
    assert isinstance(data, dict), "package.json must be an object"
    assert "name" in data, "package.json must have name field"


# [static] pass_to_pass - file read check
def test_repo_turbo_json_valid():
    """turbo.json is valid JSON with expected structure (pass_to_pass)."""
    turbo_json = Path(REPO) / "turbo.json"
    assert turbo_json.exists(), "turbo.json must exist"
    data = json.loads(turbo_json.read_text())
    assert isinstance(data, dict), "turbo.json must be an object"
    assert "tasks" in data or "pipeline" in data, "turbo.json must have tasks or pipeline"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_lint_lint():
    """pass_to_pass | CI job 'lint' → step 'Lint'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm lint -- --quiet'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Lint' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")