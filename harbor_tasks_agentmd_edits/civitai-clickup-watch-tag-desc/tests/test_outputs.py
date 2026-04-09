"""
Task: civitai-clickup-watch-tag-desc
Repo: civitai/civitai @ 76f8944088d812aaab4e6780fc742d1d213df287
PR:   1948

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/civitai"
SKILL_DIR = f"{REPO}/.claude/skills/clickup"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified .mjs files parse without errors."""
    for f in ["api/tasks.mjs", "query.mjs"]:
        r = subprocess.run(
            ["node", "--check", f],
            cwd=SKILL_DIR,
            capture_output=True,
            timeout=15,
        )
        assert r.returncode == 0, (
            f"{f} has syntax errors:\n{r.stderr.decode()}"
        )


# [repo_tests] pass_to_pass — repo CI equivalent
def test_repo_modified_files_parse():
    """Repo's modified .mjs files parse as valid JavaScript (pass_to_pass)."""
    # Check all modified .mjs files in the PR parse correctly
    modified_files = [
        ".claude/skills/clickup/api/tasks.mjs",
        ".claude/skills/clickup/query.mjs",
    ]
    for f in modified_files:
        r = subprocess.run(
            ["node", "--check", f],
            cwd=REPO,
            capture_output=True,
            timeout=15,
        )
        assert r.returncode == 0, (
            f"{f} has syntax errors:\n{r.stderr.decode()}"
        )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_help_lists_new_commands():
    """CLI help output includes watch, tag, and description commands."""
    r = subprocess.run(
        ["node", "query.mjs"],
        cwd=SKILL_DIR,
        capture_output=True,
        timeout=15,
    )
    output = r.stdout.decode() + r.stderr.decode()
    # Each new command should appear in the usage/help text
    assert "watch" in output and "tag" in output and "description" in output, (
        f"Help output missing new commands. Got:\n{output[:500]}"
    )
    # Verify they appear as command entries (not just in descriptions of other commands)
    lines = output.lower().split("\n")
    has_watch_cmd = any("watch" in l and "<task>" in l for l in lines)
    has_tag_cmd = any(l.strip().startswith("tag") or "tag <task>" in l for l in lines)
    has_desc_cmd = any("description" in l and "<task>" in l for l in lines)
    assert has_watch_cmd, "Help should list 'watch <task>' as a command"
    assert has_tag_cmd, "Help should list 'tag <task>' as a command"
    assert has_desc_cmd, "Help should list 'description <task>' as a command"


# [pr_diff] fail_to_pass
def test_add_watcher_api_limitation():
    """addWatcher signals that ClickUp API doesn't support watchers directly."""
    script = (
        "const m = await import('./.claude/skills/clickup/api/tasks.mjs');\n"
        "if (typeof m.addWatcher !== 'function') {\n"
        "    console.log('FAIL: addWatcher not exported');\n"
        "    process.exit(1);\n"
        "}\n"
        "try {\n"
        "    await m.addWatcher('test123', 'user456');\n"
        "    console.log('FAIL: no error thrown');\n"
        "    process.exit(1);\n"
        "} catch(e) {\n"
        "    if (e.message.toLowerCase().includes('watcher') ||\n"
        "        e.message.toLowerCase().includes('not support')) {\n"
        "        console.log('PASS');\n"
        "        process.exit(0);\n"
        "    }\n"
        "    console.log('FAIL: unexpected error: ' + e.message);\n"
        "    process.exit(1);\n"
        "}\n"
    )
    r = subprocess.run(
        ["node", "--input-type=module", "-e", script],
        cwd=REPO,
        capture_output=True,
        timeout=15,
    )
    assert "PASS" in r.stdout.decode(), (
        f"addWatcher should throw about API limitation.\n"
        f"stdout: {r.stdout.decode()}\nstderr: {r.stderr.decode()}"
    )


# [pr_diff] fail_to_pass
def test_add_tag_exported():
    """addTag is exported from tasks.mjs as a callable function."""
    script = (
        "const m = await import('./.claude/skills/clickup/api/tasks.mjs');\n"
        "if (typeof m.addTag === 'function') {\n"
        "    console.log('PASS');\n"
        "} else {\n"
        "    console.log('FAIL: addTag is ' + typeof m.addTag);\n"
        "}\n"
    )
    r = subprocess.run(
        ["node", "--input-type=module", "-e", script],
        cwd=REPO,
        capture_output=True,
        timeout=15,
    )
    assert "PASS" in r.stdout.decode(), (
        f"addTag should be exported as a function.\n"
        f"stdout: {r.stdout.decode()}\nstderr: {r.stderr.decode()}"
    )


# [pr_diff] fail_to_pass
def test_tag_command_missing_arg_error():
    """'tag' is a recognized command; with missing tag name it shows a specific error."""
    r = subprocess.run(
        ["node", "query.mjs", "tag", "test123"],
        cwd=SKILL_DIR,
        capture_output=True,
        timeout=15,
    )
    output = r.stdout.decode() + r.stderr.decode()
    output_lower = output.lower()
    # Should NOT say "Unknown command"
    assert "unknown command" not in output_lower, (
        f"'tag' should be a recognized command, got: {output[:300]}"
    )
    # Should ask for a tag name
    assert "tag" in output_lower and ("required" in output_lower or "usage" in output_lower), (
        f"Should show tag-specific error, got: {output[:300]}"
    )


# [pr_diff] fail_to_pass
def test_description_command_missing_arg_error():
    """'description' is a recognized command; with missing text it shows a specific error."""
    r = subprocess.run(
        ["node", "query.mjs", "description", "test123"],
        cwd=SKILL_DIR,
        capture_output=True,
        timeout=15,
    )
    output = r.stdout.decode() + r.stderr.decode()
    output_lower = output.lower()
    assert "unknown command" not in output_lower, (
        f"'description' should be a recognized command, got: {output[:300]}"
    )
    assert "description" in output_lower and ("required" in output_lower or "usage" in output_lower), (
        f"Should show description-specific error, got: {output[:300]}"
    )


# [pr_diff] fail_to_pass
def test_watch_command_missing_arg_error():
    """'watch' is a recognized command; with missing user it shows a specific error."""
    r = subprocess.run(
        ["node", "query.mjs", "watch", "test123"],
        cwd=SKILL_DIR,
        capture_output=True,
        timeout=15,
    )
    output = r.stdout.decode() + r.stderr.decode()
    output_lower = output.lower()
    assert "unknown command" not in output_lower, (
        f"'watch' should be a recognized command, got: {output[:300]}"
    )
    assert "user" in output_lower and ("required" in output_lower or "usage" in output_lower), (
        f"Should show watch-specific error, got: {output[:300]}"
    )


# ---------------------------------------------------------------------------
# Config edit (config_edit) — SKILL.md documentation tests
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass
