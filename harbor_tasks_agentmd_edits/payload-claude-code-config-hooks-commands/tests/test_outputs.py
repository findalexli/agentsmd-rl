"""
Task: payload-claude-code-config-hooks-commands
Repo: payloadcms/payload @ 80d7781b4f2fc2e874323532a0a8a8da65c8fc22
PR:   14445

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import os
import stat
import subprocess
from pathlib import Path

REPO = "/workspace/payload"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / structural checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass


# [static] pass_to_pass
def test_settings_json_valid():
    """If .claude/settings.json exists it must be valid JSON."""
    settings = Path(REPO) / ".claude" / "settings.json"
    if settings.exists():
        data = json.loads(settings.read_text())
        assert isinstance(data, dict), "settings.json must be a JSON object"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — hook script behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_post_edit_hook_exists_and_executable():
    """Post-edit hook script must exist and be executable."""
    hook = Path(REPO) / ".claude" / "hooks" / "post-edit.sh"
    assert hook.exists(), ".claude/hooks/post-edit.sh must exist"
    mode = hook.stat().st_mode
    assert mode & stat.S_IXUSR, "post-edit.sh must be executable"


# [pr_diff] fail_to_pass
def test_hook_exits_zero_on_missing_file():
    """Hook must exit 0 gracefully when referenced file does not exist."""
    hook = Path(REPO) / ".claude" / "hooks" / "post-edit.sh"
    assert hook.exists(), "Hook script must exist first"
    result = subprocess.run(
        ["bash", str(hook)],
        input='{"tool_input": {"file_path": "/nonexistent/file.ts"}}',
        capture_output=True, text=True, timeout=10,
    )
    assert result.returncode == 0, (
        f"Hook should exit 0 for nonexistent file, got {result.returncode}: {result.stderr}"
    )


# [pr_diff] fail_to_pass
def test_hook_exits_zero_on_null_input():
    """Hook must exit 0 gracefully when file_path is null."""
    hook = Path(REPO) / ".claude" / "hooks" / "post-edit.sh"
    assert hook.exists(), "Hook script must exist first"
    result = subprocess.run(
        ["bash", str(hook)],
        input='{"tool_input": {"file_path": null}}',
        capture_output=True, text=True, timeout=10,
    )
    assert result.returncode == 0, (
        f"Hook should exit 0 for null file_path, got {result.returncode}: {result.stderr}"
    )


# [pr_diff] fail_to_pass
def test_hook_handles_multiple_file_types():
    """Hook must have formatting branches for ts/tsx, md, json, and package.json."""
    hook = Path(REPO) / ".claude" / "hooks" / "post-edit.sh"
    content = hook.read_text()
    # Must handle TypeScript files
    assert "*.ts" in content or "*.tsx" in content, "Hook should handle TypeScript files"
    # Must handle markdown
    assert "*.md" in content, "Hook should handle markdown files"
    # Must handle JSON
    assert "*.json" in content or "*.yml" in content, "Hook should handle JSON/YAML files"
    # Must handle package.json specially
    assert "package.json" in content, "Hook should have special handling for package.json"


# [pr_diff] fail_to_pass
def test_hook_uses_prettier_and_eslint():
    """Hook must invoke prettier for formatting and eslint for JS/TS linting."""
    hook = Path(REPO) / ".claude" / "hooks" / "post-edit.sh"
    content = hook.read_text()
    assert "prettier" in content, "Hook should use prettier for formatting"
    assert "eslint" in content, "Hook should use eslint for JS/TS linting"


# [pr_diff] fail_to_pass
def test_hook_sorts_package_json():
    """Hook must use sort-package-json for package.json files."""
    hook = Path(REPO) / ".claude" / "hooks" / "post-edit.sh"
    content = hook.read_text()
    assert "sort-package-json" in content, "Hook should use sort-package-json"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — settings.json tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_settings_configures_post_tool_use_hook():
    """Settings must configure a PostToolUse hook triggered on Edit or Write."""
    settings = Path(REPO) / ".claude" / "settings.json"
    assert settings.exists(), ".claude/settings.json must exist"
    data = json.loads(settings.read_text())
    hooks = data.get("hooks", {})
    assert "PostToolUse" in hooks, "Settings must have PostToolUse hook configuration"
    post_hooks = hooks["PostToolUse"]
    assert isinstance(post_hooks, list) and len(post_hooks) > 0, \
        "PostToolUse must have at least one hook entry"
    # At least one matcher must cover Edit and Write
    matchers = [h.get("matcher", "") for h in post_hooks]
    combined = " ".join(matchers)
    assert "Edit" in combined and "Write" in combined, \
        f"PostToolUse hooks must match both Edit and Write, got matchers: {matchers}"


# [pr_diff] fail_to_pass
def test_settings_has_pnpm_permissions():
    """Settings must pre-allow pnpm commands to reduce permission prompts."""
    settings = Path(REPO) / ".claude" / "settings.json"
    assert settings.exists(), ".claude/settings.json must exist"
    data = json.loads(settings.read_text())
    perms = data.get("permissions", {}).get("allow", [])
    pnpm_perms = [p for p in perms if "pnpm" in p]
    assert len(pnpm_perms) >= 3, \
        f"Settings should allow multiple pnpm commands, found {len(pnpm_perms)}"
    # Must allow pnpm run specifically
    assert any("pnpm run" in p for p in pnpm_perms), \
        "Settings must pre-allow 'pnpm run' commands"


# [pr_diff] fail_to_pass
def test_settings_has_git_permissions():
    """Settings must pre-allow common git readonly commands."""
    settings = Path(REPO) / ".claude" / "settings.json"
    data = json.loads(settings.read_text())
    perms = data.get("permissions", {}).get("allow", [])
    git_perms = [p for p in perms if "git " in p or "git)" in p]
    assert len(git_perms) >= 3, \
        f"Settings should allow multiple git commands, found {len(git_perms)}"


# ---------------------------------------------------------------------------
# Config file update checks (config_edit) — fail_to_pass
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass
