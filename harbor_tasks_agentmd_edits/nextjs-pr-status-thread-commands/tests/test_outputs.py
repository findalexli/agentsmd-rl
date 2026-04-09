import json
import subprocess
import textwrap
from pathlib import Path

REPO = "/workspace/next.js"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass) — repo CI checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_syntax_check():
    """Repo JavaScript files have no syntax errors (pass_to_pass)."""
    # Check the main pr-status.js script that this PR modifies
    r = subprocess.run(
        ["node", "--check", "scripts/pr-status.js"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Syntax error in scripts/pr-status.js:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_reply_thread_no_args_exits_with_usage():
    """reply-thread subcommand with no args exits 1 and prints usage."""
    r = subprocess.run(
        ["node", "scripts/pr-status.js", "reply-thread"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode != 0, (
        f"Expected non-zero exit code, got {r.returncode}"
    )
    # Must print the specific usage line (not just any gh error containing 'reply-thread')
    assert "Usage: node scripts/pr-status.js reply-thread" in r.stderr, (
        f"Expected usage message for reply-thread in stderr:\n{r.stderr}"
    )


# [pr_diff] fail_to_pass
def test_reply_thread_missing_body_exits_with_usage():
    """reply-thread with threadId but no body exits 1 and prints usage."""
    r = subprocess.run(
        ["node", "scripts/pr-status.js", "reply-thread", "PRT_test123"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode != 0, (
        f"Expected non-zero exit code, got {r.returncode}"
    )
    assert "Usage: node scripts/pr-status.js reply-thread" in r.stderr, (
        f"Expected usage message for reply-thread in stderr:\n{r.stderr}"
    )


# [pr_diff] fail_to_pass
def test_resolve_thread_no_args_exits_with_usage():
    """resolve-thread subcommand with no args exits 1 and prints usage."""
    r = subprocess.run(
        ["node", "scripts/pr-status.js", "resolve-thread"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode != 0, (
        f"Expected non-zero exit code, got {r.returncode}"
    )
    assert "Usage: node scripts/pr-status.js resolve-thread" in r.stderr, (
        f"Expected usage message for resolve-thread in stderr:\n{r.stderr}"
    )


# [pr_diff] fail_to_pass
def test_thread_md_includes_commands_section():
    """generateThreadMd produces a Commands section with reply and resolve commands."""
    test_script = textwrap.dedent("""\
        const fs = require('fs');
        const src = fs.readFileSync(process.argv[2], 'utf8');

        // Extract generateThreadMd function
        const funcStart = src.indexOf('function generateThreadMd(');
        if (funcStart === -1) {
            console.error('generateThreadMd not found');
            process.exit(1);
        }

        // Find matching closing brace
        let braceCount = 0;
        let funcEnd = -1;
        let started = false;
        for (let i = funcStart; i < src.length; i++) {
            if (src[i] === '{') { braceCount++; started = true; }
            if (src[i] === '}') {
                braceCount--;
                if (started && braceCount === 0) { funcEnd = i + 1; break; }
            }
        }
        if (funcEnd === -1) {
            console.error('Could not find end of generateThreadMd');
            process.exit(1);
        }

        const funcSrc = src.substring(funcStart, funcEnd);
        const fn = eval('(' + funcSrc + ')');

        const thread = {
            id: 'PRT_kwDOTestNode',
            isResolved: false,
            path: 'src/example.ts',
            line: 42,
            comments: { nodes: [{
                author: { login: 'reviewer' },
                body: 'Fix this please',
                createdAt: '2024-01-15T10:00:00Z',
                url: 'https://github.com/test/pull/1#r1'
            }] }
        };
        const md = fn(thread, 0);

        const result = {
            hasCommands: md.includes('## Commands'),
            hasReply: md.includes('reply-thread PRT_kwDOTestNode'),
            hasResolve: md.includes('resolve-thread PRT_kwDOTestNode'),
        };
        console.log(JSON.stringify(result));
    """)

    script_path = Path(REPO) / "_eval_test_thread_md.js"
    script_path.write_text(test_script)
    try:
        r = subprocess.run(
            ["node", str(script_path), str(Path(REPO) / "scripts" / "pr-status.js")],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert r.returncode == 0, f"Test script failed:\n{r.stderr}"
        data = json.loads(r.stdout.strip())
        assert data["hasCommands"], "generateThreadMd output missing '## Commands' section"
        assert data["hasReply"], "generateThreadMd output missing reply-thread command"
        assert data["hasResolve"], "generateThreadMd output missing resolve-thread command"
    finally:
        script_path.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Config/documentation update tests (pr_diff) — agentmd-edit
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_skill_md_thread_resolution_rule():
    """SKILL.md must include guidance on replying to and resolving review threads."""
    skill_md = Path(REPO) / ".agents" / "skills" / "pr-status-triage" / "SKILL.md"
    content = skill_md.read_text()
    assert "reply" in content.lower() or "respond" in content.lower(), (
        "SKILL.md should mention replying to review threads"
    )
    assert "resolve" in content.lower(), (
        "SKILL.md should mention resolving review threads"
    )
    assert "thread" in content.lower(), (
        "SKILL.md should reference review threads"
    )


# [pr_diff] fail_to_pass
def test_workflow_md_resolving_threads_section():
    """workflow.md must include a section on resolving review threads with commands."""
    workflow_md = (
        Path(REPO) / ".agents" / "skills" / "pr-status-triage" / "workflow.md"
    )
    content = workflow_md.read_text()
    assert "resolv" in content.lower(), (
        "workflow.md should document resolving review threads"
    )
    assert "reply-thread" in content, (
        "workflow.md should show the reply-thread command"
    )
    assert "resolve-thread" in content, (
        "workflow.md should show the resolve-thread command"
    )
