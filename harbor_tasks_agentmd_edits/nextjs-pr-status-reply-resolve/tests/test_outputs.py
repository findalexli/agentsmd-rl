"""Tests for nextjs-pr-status-reply-resolve: add reply-and-resolve-thread subcommand."""
import subprocess
import shutil
from pathlib import Path

REPO = Path("/workspace/nextjs")


def _run_node(args: list[str], timeout: int = 15) -> subprocess.CompletedProcess:
    """Run node with given args in the repo directory."""
    return subprocess.run(
        ["node"] + args,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=str(REPO),
    )


# ---------- pass_to_pass: repo CI tests ----------


def test_repo_node_available():
    """Node.js must be available in the container (pass_to_pass)."""
    node_path = shutil.which("node")
    assert node_path is not None, "Node.js not found in PATH"


def test_repo_prettier_check():
    """Repo's prettier formatting passes on pr-status.js (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "prettier", "--check", "scripts/pr-status.js"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(REPO),
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


def test_repo_prettier_check_skill_md():
    """Repo's prettier formatting passes on SKILL.md (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "prettier", "--check", ".agents/skills/pr-status-triage/SKILL.md"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(REPO),
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


def test_repo_prettier_check_workflow_md():
    """Repo's prettier formatting passes on workflow.md (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "prettier", "--check", ".agents/skills/pr-status-triage/workflow.md"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(REPO),
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


def test_repo_node_syntax():
    """scripts/pr-status.js must have valid Node.js syntax (pass_to_pass)."""
    r = subprocess.run(
        ["node", "--check", "scripts/pr-status.js"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(REPO),
    )
    assert r.returncode == 0, f"Syntax check failed:\n{r.stderr[-500:]}"


def test_repo_module_loads():
    """scripts/pr-status.js must load as a module without syntax errors (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-e", "require('./scripts/pr-status.js')"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(REPO),
    )
    # Should not have syntax errors - runtime errors (gh not found) are expected
    assert "SyntaxError" not in r.stderr, f"Module loading failed with syntax error:\n{r.stderr[-500:]}"


# ---------- pass_to_pass: static checks ----------


def test_syntax_valid():
    """scripts/pr-status.js must parse without errors (static pass_to_pass)."""
    result = _run_node(["--check", "scripts/pr-status.js"])
    assert result.returncode == 0, f"Syntax error:\n{result.stderr}"


def test_skill_md_exists():
    """SKILL.md file must exist (static pass_to_pass)."""
    skill_md = REPO / ".agents/skills/pr-status-triage/SKILL.md"
    assert skill_md.exists(), "SKILL.md file should exist"


def test_workflow_md_exists():
    """workflow.md file must exist (static pass_to_pass)."""
    workflow_md = REPO / ".agents/skills/pr-status-triage/workflow.md"
    assert workflow_md.exists(), "workflow.md file should exist"


def test_pr_status_js_exists():
    """pr-status.js file must exist (static pass_to_pass)."""
    pr_status_js = REPO / "scripts/pr-status.js"
    assert pr_status_js.exists(), "pr-status.js file should exist"


# ---------- fail_to_pass: code behavior ----------


def test_reply_and_resolve_subcommand_exists():
    """The reply-and-resolve-thread subcommand must be handled in main()."""
    result = _run_node(["scripts/pr-status.js", "reply-and-resolve-thread"])
    # Without required args it should print usage and exit non-zero
    assert result.returncode != 0, "Should exit non-zero without args"
    assert "Usage:" in result.stderr or "reply-and-resolve-thread" in result.stderr, (
        f"Expected usage message, got: {result.stderr}"
    )


def test_reply_to_thread_uses_rest_api():
    """replyToThread must use REST API, not the old GraphQL mutation."""
    content = (REPO / "scripts/pr-status.js").read_text()

    # The old code used a GraphQL mutation with addPullRequestReviewThreadReply
    assert "addPullRequestReviewThreadReply(input:" not in content, (
        "replyToThread should no longer use the GraphQL addPullRequestReviewThreadReply mutation"
    )

    # The new code posts via REST to the replies endpoint
    assert "/comments/" in content and "/replies" in content, (
        "replyToThread should use the REST /comments/<id>/replies endpoint"
    )

    # Must look up comment databaseId via GraphQL query (not the old mutation)
    assert "databaseId" in content, (
        "replyToThread must resolve the comment databaseId for the REST endpoint"
    )


def test_generate_thread_md_includes_combined():
    """generateThreadMd must include the reply-and-resolve one-step option."""
    content = (REPO / "scripts/pr-status.js").read_text()
    assert "Reply and resolve in one step" in content, (
        "generateThreadMd should include the combined one-step command"
    )
    assert "reply-and-resolve-thread" in content, (
        "generateThreadMd should reference the reply-and-resolve-thread subcommand"
    )


def test_reply_to_thread_logs_html_url():
    """replyToThread should log html_url from REST response, not GraphQL comment.url."""
    content = (REPO / "scripts/pr-status.js").read_text()
    assert 'data.html_url' in content, (
        "replyToThread should log data.html_url from REST response"
    )


# ---------- fail_to_pass: config / documentation ----------


def test_skill_md_documents_combined_command():
    """SKILL.md must document the reply-and-resolve-thread command."""
    skill_md = REPO / ".agents/skills/pr-status-triage/SKILL.md"
    content = skill_md.read_text()

    assert "reply-and-resolve-thread" in content, (
        "SKILL.md should mention the reply-and-resolve-thread command"
    )

    assert "Thread interaction" in content, (
        "SKILL.md should have a 'Thread interaction' quick-command section"
    )


def test_skill_md_workflow_step_updated():
    """SKILL.md workflow step 6 must mention the combined command."""
    skill_md = REPO / ".agents/skills/pr-status-triage/SKILL.md"
    content = skill_md.read_text()

    # Step 6 should mention the one-step option
    assert "one step" in content.lower(), (
        "Step 6 should mention doing both in one step"
    )


def test_workflow_md_documents_one_step():
    """workflow.md must show the one-step reply-and-resolve alternative."""
    workflow_md = REPO / ".agents/skills/pr-status-triage/workflow.md"
    content = workflow_md.read_text()

    assert "reply-and-resolve-thread" in content, (
        "workflow.md should reference the reply-and-resolve-thread subcommand"
    )

    assert "one step" in content.lower(), (
        "workflow.md should describe the one-step alternative"
    )
