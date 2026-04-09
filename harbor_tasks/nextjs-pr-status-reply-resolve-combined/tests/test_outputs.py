"""
Task: nextjs-pr-status-reply-resolve-combined
Repo: next.js @ fea754747872122d167dd8bf1fc5581044e50521
PR:   92450

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import re
from pathlib import Path

REPO = "/workspace/next.js"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_reply_and_resolve_subcommand_no_args():
    """reply-and-resolve-thread subcommand exists and prints specific usage when called without args."""
    r = subprocess.run(
        ["node", "scripts/pr-status.js", "reply-and-resolve-thread"],
        cwd=REPO,
        capture_output=True,
        timeout=30,
    )
    stderr = r.stderr.decode()
    stdout = r.stdout.decode()
    combined = stderr + stdout
    # Must exit non-zero (usage error)
    assert r.returncode != 0, (
        f"Expected non-zero exit for missing args, got {r.returncode}"
    )
    # Must show the specific usage message for this subcommand
    assert "Usage:" in combined and "reply-and-resolve-thread" in combined and "<threadNodeId>" in combined, (
        f"Expected usage message with 'reply-and-resolve-thread <threadNodeId>', got:\n{combined}"
    )


# [pr_diff] fail_to_pass
def test_reply_and_resolve_subcommand_missing_body():
    """reply-and-resolve-thread requires both threadId AND body."""
    r = subprocess.run(
        ["node", "scripts/pr-status.js", "reply-and-resolve-thread", "FAKE_THREAD_ID"],
        cwd=REPO,
        capture_output=True,
        timeout=30,
    )
    stderr = r.stderr.decode()
    stdout = r.stdout.decode()
    combined = stderr + stdout
    # Must exit non-zero when body is missing
    assert r.returncode != 0, (
        f"Expected non-zero exit for missing body, got {r.returncode}"
    )
    # Must show usage message mentioning both required args
    assert "Usage:" in combined and "reply-and-resolve-thread" in combined and "<body>" in combined.replace("&lt;body&gt;", "<body>"), (
        f"Expected usage message with 'reply-and-resolve-thread ... <body>', got:\n{combined}"
    )


# [pr_diff] fail_to_pass
def test_generate_thread_md_includes_combined_command():
    """generateThreadMd outputs the reply-and-resolve-thread command for unresolved threads."""
    src = Path(f"{REPO}/scripts/pr-status.js").read_text()

    # Find the generateThreadMd function body
    match = re.search(r"function\s+generateThreadMd\s*\(", src)
    assert match, "generateThreadMd function not found in scripts/pr-status.js"

    # Extract from the function start to a reasonable endpoint
    func_start = match.start()
    func_body = src[func_start:func_start + 5000]

    # The function must include the combined command template for unresolved threads
    assert "reply-and-resolve-thread" in func_body, (
        "generateThreadMd must include 'reply-and-resolve-thread' command for unresolved threads"
    )


# [pr_diff] fail_to_pass
def test_reply_to_thread_uses_rest_api():
    """replyToThread uses the REST API endpoint instead of GraphQL mutation."""
    src = Path(f"{REPO}/scripts/pr-status.js").read_text()

    # Find the replyToThread function
    match = re.search(r"function\s+replyToThread\s*\(", src)
    assert match, "replyToThread function not found in scripts/pr-status.js"

    func_start = match.start()
    # Find the next top-level function to delimit
    next_func = re.search(r"\nfunction\s+\w+\s*\(", src[func_start + 1:])
    if next_func:
        func_body = src[func_start:func_start + 1 + next_func.start()]
    else:
        func_body = src[func_start:func_start + 5000]

    # Must NOT use the GraphQL addPullRequestReviewThreadReply mutation invocation
    # (a comment mentioning it is fine — check for the actual mutation call pattern)
    assert "addPullRequestReviewThreadReply(input" not in func_body, (
        "replyToThread should use REST API, not GraphQL addPullRequestReviewThreadReply mutation"
    )

    # Must use the REST endpoint for posting replies
    assert re.search(r"/pulls/.*/(comments|replies)", func_body), (
        "replyToThread should use the REST /pulls/.../comments/.../replies endpoint"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression tests
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """scripts/pr-status.js must parse without syntax errors."""
    r = subprocess.run(
        ["node", "--check", "scripts/pr-status.js"],
        cwd=REPO,
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, (
        f"Syntax error in pr-status.js:\n{r.stderr.decode()}"
    )


# [static] pass_to_pass
def test_reply_thread_usage_error():
    """Existing reply-thread subcommand still validates args correctly."""
    r = subprocess.run(
        ["node", "scripts/pr-status.js", "reply-thread"],
        cwd=REPO,
        capture_output=True,
        timeout=30,
    )
    stderr = r.stderr.decode()
    stdout = r.stdout.decode()
    combined = stderr + stdout
    assert r.returncode != 0, (
        f"Expected non-zero exit for reply-thread without args, got {r.returncode}"
    )
    assert "reply-thread" in combined.lower() or "usage" in combined.lower(), (
        f"reply-thread should show usage error, got:\n{combined}"
    )


# [static] pass_to_pass
def test_resolve_thread_usage_error():
    """Existing resolve-thread subcommand still validates args correctly."""
    r = subprocess.run(
        ["node", "scripts/pr-status.js", "resolve-thread"],
        cwd=REPO,
        capture_output=True,
        timeout=30,
    )
    stderr = r.stderr.decode()
    stdout = r.stdout.decode()
    combined = stderr + stdout
    assert r.returncode != 0, (
        f"Expected non-zero exit for resolve-thread without args, got {r.returncode}"
    )
    assert "resolve-thread" in combined.lower() or "usage" in combined.lower(), (
        f"resolve-thread should show usage error, got:\n{combined}"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from skill files
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — .agents/skills/pr-status-triage/SKILL.md:22 @ fea7547
def test_skill_md_thread_interaction_commands():
    """SKILL.md must document thread interaction commands including the combined command."""
    skill_path = Path(f"{REPO}/.agents/skills/pr-status-triage/SKILL.md")
    assert skill_path.exists(), "SKILL.md not found"
    content = skill_path.read_text()

    # Must have the combined command documented
    assert "reply-and-resolve-thread" in content, (
        "SKILL.md must document the reply-and-resolve-thread command"
    )

    # Should list all three thread commands for completeness
    assert "reply-thread" in content, "SKILL.md must list the reply-thread command"
    assert "resolve-thread" in content, "SKILL.md must list the resolve-thread command"


# [agent_config] fail_to_pass — .agents/skills/pr-status-triage/workflow.md:29 @ fea7547
def test_workflow_md_one_step_resolve():
    """workflow.md must document the one-step reply-and-resolve alternative."""
    workflow_path = Path(f"{REPO}/.agents/skills/pr-status-triage/workflow.md")
    assert workflow_path.exists(), "workflow.md not found"
    content = workflow_path.read_text()

    # Must mention the combined command
    assert "reply-and-resolve-thread" in content, (
        "workflow.md must document the reply-and-resolve-thread command "
        "as a one-step alternative in the 'Resolving Review Threads' section"
    )
