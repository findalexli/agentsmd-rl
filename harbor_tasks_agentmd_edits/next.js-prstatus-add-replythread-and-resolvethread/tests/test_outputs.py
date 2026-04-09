"""
Task: next.js-prstatus-add-replythread-and-resolvethread
Repo: vercel/next.js @ c300a63cc9e0b9eeea6632f0b2150114de8c5d23
PR:   90773

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path
import json
import re

REPO = "/workspace/next.js"
SCRIPT_PATH = f"{REPO}/scripts/pr-status.js"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without errors."""
    # Check that pr-status.js parses correctly
    r = subprocess.run(
        ["node", "--check", SCRIPT_PATH],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Syntax check failed: {r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_reply_thread_function_exists():
    """replyToThread function exists with correct GraphQL mutation."""
    src = Path(SCRIPT_PATH).read_text()

    # Check function exists
    assert "function replyToThread(threadId, body)" in src, \
        "replyToThread function not found"

    # Check GraphQL mutation for addPullRequestReviewThreadReply
    assert "addPullRequestReviewThreadReply" in src, \
        "addPullRequestReviewThreadReply mutation not found"

    # Check it uses execFileSync (safe argument passing, not shell)
    assert "execFileSync" in src, \
        "execFileSync not found (should be used for safe argument passing)"

    # Check the function uses correct parameter structure
    assert "pullRequestReviewThreadId: $threadId" in src or \
           'pullRequestReviewThreadId: $threadId' in src, \
        "GraphQL mutation must use pullRequestReviewThreadId parameter"


# [pr_diff] fail_to_pass
def test_resolve_thread_function_exists():
    """resolveThread function exists with correct GraphQL mutation."""
    src = Path(SCRIPT_PATH).read_text()

    # Check function exists
    assert "function resolveThread(threadId)" in src, \
        "resolveThread function not found"

    # Check GraphQL mutation for resolveReviewThread
    assert "resolveReviewThread" in src, \
        "resolveReviewThread mutation not found"

    # The fix commit changed from pullRequestReviewThreadId to threadId
    # Check that the mutation uses threadId (not pullRequestReviewThreadId)
    mutation_match = re.search(
        r'resolveReviewThread\(input:\s*\{([^}]+)\}\)',
        src
    )
    assert mutation_match, "Could not find resolveReviewThread mutation input"

    mutation_input = mutation_match.group(1)
    assert "threadId: $threadId" in mutation_input, \
        "resolveReviewThread must use threadId (not pullRequestReviewThreadId) in input"
    assert "pullRequestReviewThreadId" not in mutation_input, \
        "resolveReviewThread should NOT use pullRequestReviewThreadId (use threadId instead)"


# [pr_diff] fail_to_pass
def test_subcommand_dispatch():
    """Main function dispatches reply-thread and resolve-thread subcommands."""
    src = Path(SCRIPT_PATH).read_text()

    # Check subcommand dispatch exists
    assert "process.argv[2]" in src, \
        "Main should check process.argv[2] for subcommands"

    # Check reply-thread subcommand dispatch
    assert "subcommand === 'reply-thread'" in src or \
           "'reply-thread'" in src, \
        "reply-thread subcommand not handled"

    # Check resolve-thread subcommand dispatch
    assert "subcommand === 'resolve-thread'" in src or \
           "'resolve-thread'" in src, \
        "resolve-thread subcommand not handled"

    # Check that replyToThread is called for reply-thread
    assert "replyToThread(threadId, body)" in src, \
        "replyToThread should be called in subcommand handler"

    # Check that resolveThread is called for resolve-thread
    assert "resolveThread(threadId)" in src, \
        "resolveThread should be called in subcommand handler"


# [pr_diff] fail_to_pass
def test_thread_commands_section_in_output():
    """Thread markdown output includes Commands section with ready-to-use commands."""
    src = Path(SCRIPT_PATH).read_text()

    # Check that generateThreadMd includes Commands section
    assert "## Commands" in src, \
        "Thread markdown should include ## Commands section"

    # Check for reply-thread command template in output
    assert 'node scripts/pr-status.js reply-thread' in src, \
        "Reply command template should be in thread output"

    # Check for resolve-thread command template in output
    assert 'node scripts/pr-status.js resolve-thread' in src, \
        "Resolve command template should be in thread output"

    # Check that thread.id is used in command templates
    assert "thread.id" in src, \
        "Thread ID should be embedded in command templates"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """Modified functions have real logic, not just pass/return."""
    src = Path(SCRIPT_PATH).read_text()

    # Find replyToThread function and check it has meaningful body
    # Use a simpler approach: find the function and check the overall content
    reply_start = src.find("function replyToThread(threadId, body)")
    assert reply_start != -1, "Could not find replyToThread function"

    # Find the matching closing brace by counting braces
    brace_count = 0
    found_opening = False
    reply_end = reply_start
    for i, char in enumerate(src[reply_start:]):
        if char == "{":
            brace_count += 1
            found_opening = True
        elif char == "}":
            brace_count -= 1
        if found_opening and brace_count == 0:
            reply_end = reply_start + i + 1
            break

    reply_body = src[reply_start:reply_end]

    # Should have execFileSync call and mutation
    assert "execFileSync" in reply_body, \
        "replyToThread should call execFileSync"
    assert "mutation" in reply_body.lower(), \
        "replyToThread should define GraphQL mutation"

    # Find resolveThread function and check it has meaningful body
    resolve_start = src.find("function resolveThread(threadId)")
    assert resolve_start != -1, "Could not find resolveThread function"

    # Find the matching closing brace by counting braces
    brace_count = 0
    found_opening = False
    resolve_end = resolve_start
    for i, char in enumerate(src[resolve_start:]):
        if char == "{":
            brace_count += 1
            found_opening = True
        elif char == "}":
            brace_count -= 1
        if found_opening and brace_count == 0:
            resolve_end = resolve_start + i + 1
            break

    resolve_body = src[resolve_start:resolve_end]

    # Should have execFileSync call
    assert "execFileSync" in resolve_body, \
        "resolveThread should call execFileSync"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from .agents/skills/pr-status-triage/SKILL.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — .agents/skills/pr-status-triage/SKILL.md:22 @ c300a63cc9e0b9eeea6632f0b2150114de8c5d23
def test_skill_documentation_updated():
    """SKILL.md documents the new review thread workflow."""
    skill_path = f"{REPO}/.agents/skills/pr-status-triage/SKILL.md"

    # File should exist
    assert Path(skill_path).exists(), \
        f"SKILL.md not found at {skill_path}"

    content = Path(skill_path).read_text()

    # Should mention resolving review threads
    assert "resolve" in content.lower() or "thread" in content.lower(), \
        "SKILL.md should document review thread resolution workflow"

    # Should reference thread-N.md files
    assert "thread-" in content or "thread N" in content.lower(), \
        "SKILL.md should reference thread-N.md files"


# [agent_config] fail_to_pass — .agents/skills/pr-status-triage/workflow.md @ c300a63cc9e0b9eeea6632f0b2150114de8c5d23
def test_workflow_documentation_updated():
    """workflow.md includes Resolving Review Threads section."""
    workflow_path = f"{REPO}/.agents/skills/pr-status-triage/workflow.md"

    # File should exist
    assert Path(workflow_path).exists(), \
        f"workflow.md not found at {workflow_path}"

    content = Path(workflow_path).read_text()

    # Should have section about resolving review threads
    assert "Resolving Review Threads" in content or \
           "review thread" in content.lower(), \
        "workflow.md should have section on resolving review threads"

    # Should document reply-thread command
    assert "reply-thread" in content, \
        "workflow.md should document reply-thread command"

    # Should document resolve-thread command
    assert "resolve-thread" in content, \
        "workflow.md should document resolve-thread command"

    # Should remind to reply before resolving
    assert "reply" in content.lower(), \
        "workflow.md should remind to reply before resolving"


# [repo_tests] pass_to_pass — prettier check from CI pipeline (added by p2p enrichment)
def test_repo_prettier():
    """Repo's Prettier formatting check passes on modified file (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "prettier", "--check", "scripts/pr-status.js"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


