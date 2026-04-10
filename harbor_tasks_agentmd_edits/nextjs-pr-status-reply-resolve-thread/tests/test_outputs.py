"""
Task: nextjs-pr-status-reply-resolve-thread
Repo: vercel/next.js @ fea754747872122d167dd8bf1fc5581044e50521
PR:   92450

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
import tempfile
from pathlib import Path

REPO = "/workspace/next.js"


def _run_node(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run a Node.js script from a temp file in the repo directory."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".js", dir=REPO, delete=False
    ) as f:
        f.write(script)
        f.flush()
        path = f.name
    try:
        return subprocess.run(
            ["node", path],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=REPO,
        )
    finally:
        Path(path).unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------


def test_script_syntax_valid():
    """pr-status.js must parse without errors."""
    r = subprocess.run(
        ["node", "--check", "scripts/pr-status.js"],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Syntax error in pr-status.js:\n{r.stderr}"


def test_pr_status_script_exists():
    """pr-status.js script must exist (pass_to_pass)."""
    script_path = Path(f"{REPO}/scripts/pr-status.js")
    assert script_path.exists(), "scripts/pr-status.js must exist"
    assert script_path.stat().st_size > 0, "scripts/pr-status.js must not be empty"


def test_skill_files_exist():
    """Skill documentation files must exist (pass_to_pass)."""
    skill_md = Path(f"{REPO}/.agents/skills/pr-status-triage/SKILL.md")
    workflow_md = Path(f"{REPO}/.agents/skills/pr-status-triage/workflow.md")
    assert skill_md.exists(), "SKILL.md must exist"
    assert workflow_md.exists(), "workflow.md must exist"
    assert skill_md.stat().st_size > 0, "SKILL.md must not be empty"
    assert workflow_md.stat().st_size > 0, "workflow.md must not be empty"


def test_pr_status_has_core_functions():
    """pr-status.js must contain replyToThread and resolveThread functions (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-e",
         "const src = require('fs').readFileSync('/workspace/next.js/scripts/pr-status.js', 'utf8'); " +
         "if (!src.includes('function replyToThread')) { console.error('replyToThread not found'); process.exit(1); } " +
         "if (!src.includes('function resolveThread')) { console.error('resolveThread not found'); process.exit(1); } " +
         "console.log('OK');"],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    assert r.returncode == 0, f"pr-status.js missing required functions:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


def test_reply_and_resolve_subcommand_usage():
    """The reply-and-resolve-thread subcommand must be recognized and show usage."""
    r = subprocess.run(
        ["node", "scripts/pr-status.js", "reply-and-resolve-thread"],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    # Should exit non-zero (missing required args)
    assert r.returncode != 0, "Should exit with error when args are missing"
    # Should show usage message, not "unknown subcommand" or crash
    assert "Usage" in r.stderr or "Usage" in r.stdout, (
        f"Expected usage message, got:\nstdout: {r.stdout}\nstderr: {r.stderr}"
    )
    assert "reply-and-resolve-thread" in r.stderr or "reply-and-resolve-thread" in r.stdout, (
        "Usage message should mention reply-and-resolve-thread"
    )


def test_subcommand_calls_reply_and_resolve():
    """reply-and-resolve-thread handler must invoke both replyToThread and resolveThread."""
    # First create the mock gh script in Python to avoid shell escaping issues
    import tempfile, os
    mock_gh_dir = tempfile.mkdtemp(prefix='mock-gh-')
    mock_gh_path = os.path.join(mock_gh_dir, 'gh')
    calls_log_path = os.path.join(mock_gh_dir, 'calls.json')

    mock_script = f'''#!/bin/bash
echo "$@" >> "{calls_log_path}"
if [[ "$*" == *"graphql"* ]] && [[ "$*" != *"mutation"* ]]; then
  echo '{{"data":{{"node":{{"pullRequest":{{"number":1}},"comments":{{"nodes":[{{"databaseId":123}}]}}}}}}}}'
elif [[ "$*" == *"/replies"* ]]; then
  echo '{{"html_url":"https://github.com/vercel/next.js/pull/1#discussion_r1"}}'
else
  echo '{{"data":{{"resolveReviewThread":{{"thread":{{"isResolved":true}}}}}}}}'
fi
'''
    with open(mock_gh_path, 'w') as f:
        f.write(mock_script)
    os.chmod(mock_gh_path, 0o755)
    # Create empty calls file
    open(calls_log_path, 'w').close()

    # Now run Node test that references these paths
    result = _run_node(
        f'''
const fs = require('fs');
const path = require('path');

const ghPath = '{mock_gh_path}';
const callsPath = '{calls_log_path}';
const ghDir = '{mock_gh_dir}';

// Patch process.argv and PATH, then require the script
process.argv = ['node', 'scripts/pr-status.js', 'reply-and-resolve-thread', 'PRRT_test123', 'Done -- fixed'];
process.env.PATH = ghDir + ':' + process.env.PATH;

// Prevent actual process.exit from killing the test process
let exitCode = 0;
process.exit = (code) => {{ exitCode = code; }};

try {{
  require('./scripts/pr-status.js');
}} catch (e) {{
  // Script might throw after process.exit mock
}}

// Read the calls log
const calls = fs.readFileSync(callsPath, 'utf8').trim().split('\\n').filter(x => x);

// Verify both functions were called:
const hasGraphQLLookup = calls.some(c => c.includes('graphql') && c.includes('query'));
const hasRestReply = calls.some(c => c.includes('/replies'));
const hasResolve = calls.some(c => c.includes('resolve'));

console.log(JSON.stringify({{
  totalCalls: calls.length,
  hasGraphQLLookup,
  hasRestReply,
  hasResolve,
  calls: calls
}}));
'''
    )
    assert result.returncode == 0, f"Test script failed:\n{result.stderr}"

    data = json.loads(result.stdout.strip().split('\n')[-1])
    assert data["hasGraphQLLookup"], (
        f"replyToThread should call gh api graphql for thread lookup. Calls: {data['calls']}"
    )
    assert data["hasRestReply"], (
        f"replyToThread should POST to /replies REST endpoint. Calls: {data['calls']}"
    )
    assert data["hasResolve"], (
        f"resolveThread should be called. Calls: {data['calls']}"
    )
    assert data["totalCalls"] >= 2, (
        f"Expected at least 2 gh calls (reply + resolve), got {data['totalCalls']}"
    )


def test_reply_to_thread_uses_rest_not_graphql_mutation():
    """replyToThread must use REST API for replies, not the GraphQL mutation."""
    src = Path(f"{REPO}/scripts/pr-status.js").read_text()
    # Find replyToThread function body
    func_start = src.index("function replyToThread(")
    # Find next top-level function after replyToThread
    next_func = src.index("\nfunction ", func_start + 1)
    func_body = src[func_start:next_func]

    # Must use REST /replies endpoint
    assert "/repos/" in func_body and "/replies" in func_body, (
        "replyToThread should use REST API endpoint /repos/.../replies"
    )
    # Must NOT use the old GraphQL mutation (but it can be mentioned in comments)
    # Check the actual code by removing comments before checking
    import re
    # Remove single-line comments from func_body for mutation check
    func_body_no_comments = re.sub(r'//.*$', '', func_body, flags=re.MULTILINE)
    # Also remove multi-line comments
    func_body_no_comments = re.sub(r'/\*.*?\*/', '', func_body_no_comments, flags=re.DOTALL)
    assert "addPullRequestReviewThreadReply" not in func_body_no_comments, (
        "replyToThread should NOT use the old GraphQL mutation addPullRequestReviewThreadReply in code logic"
    )


# ---------------------------------------------------------------------------
# Config/documentation update tests (REQUIRED for agentmd-edit tasks)
# ---------------------------------------------------------------------------


def test_skill_md_documents_thread_interaction():
    """SKILL.md must have a Thread interaction section documenting all thread commands."""
    skill_md = Path(f"{REPO}/.agents/skills/pr-status-triage/SKILL.md").read_text()

    # Must have Thread interaction section
    assert "Thread interaction" in skill_md, (
        "SKILL.md should have a 'Thread interaction' section"
    )
    # Must document the combined command
    assert "reply-and-resolve-thread" in skill_md, (
        "SKILL.md should document the reply-and-resolve-thread command"
    )
    # Must also document the individual commands (they were not removed)
    assert "reply-thread" in skill_md, "SKILL.md should still document reply-thread"
    assert "resolve-thread" in skill_md, "SKILL.md should still document resolve-thread"


def test_skill_md_workflow_step_mentions_combined():
    """SKILL.md workflow step 6 must mention the combined command."""
    skill_md = Path(f"{REPO}/.agents/skills/pr-status-triage/SKILL.md").read_text()

    # Step 6 should mention the combined command as an option
    lines = skill_md.split('\n')
    step6_lines = [l for l in lines if l.strip().startswith('6.')]
    assert len(step6_lines) >= 1, "SKILL.md should have workflow step 6"
    step6 = step6_lines[0]
    assert "reply-and-resolve-thread" in step6, (
        f"Step 6 should mention reply-and-resolve-thread. Got: {step6}"
    )


def test_workflow_md_one_step_alternative():
    """workflow.md must show the one-step reply-and-resolve alternative."""
    workflow_md = Path(
        f"{REPO}/.agents/skills/pr-status-triage/workflow.md"
    ).read_text()

    assert "reply-and-resolve-thread" in workflow_md, (
        "workflow.md should mention the reply-and-resolve-thread command"
    )
    assert "one step" in workflow_md.lower(), (
        "workflow.md should describe the one-step alternative"
    )
