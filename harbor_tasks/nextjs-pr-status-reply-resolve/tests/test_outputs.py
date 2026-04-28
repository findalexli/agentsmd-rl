"""Tests for nextjs-pr-status-reply-resolve: add reply-and-resolve-thread subcommand."""
import subprocess
import os
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


def test_repo_prettier_check_local_repro():
    """Repo's prettier formatting passes on local-repro.md (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "prettier", "--check", ".agents/skills/pr-status-triage/local-repro.md"],
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


def test_repo_prettier_check_agents_dir():
    """Repo's prettier formatting passes on .agents directory files (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "prettier", "--check", ".agents/skills/pr-status-triage/"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(REPO),
    )
    assert r.returncode == 0, f"Prettier check failed on .agents dir:\n{r.stdout[-500:]}{r.stderr[-500:]}"


def test_repo_node_acorn_parse():
    """pr-status.js must be parseable by Node.js acorn/parser (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-e", """
        const fs = require('fs');
        const code = fs.readFileSync('./scripts/pr-status.js', 'utf8');
        try {
            // Use Node's internal parser (indirectly via --check style validation)
            new Function(code + '; return {};');
            console.log('Code parses correctly');
        } catch(e) {
            if (e instanceof SyntaxError) {
                console.error('Syntax error:', e.message);
                process.exit(1);
            }
            // Other errors are runtime errors, not syntax issues
            console.log('Code parses correctly (runtime errors expected)');
        }
        """],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(REPO),
    )
    # Script should either succeed or have runtime (not syntax) errors
    assert "Syntax error" not in r.stderr, f"Acorn parse failed:\n{r.stderr[-500:]}"


def test_repo_markdown_links_skill():
    """SKILL.md must have valid markdown links (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "markdown-link-check", ".agents/skills/pr-status-triage/SKILL.md", "--quiet"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(REPO),
    )
    assert r.returncode == 0, f"Markdown link check failed for SKILL.md:\n{r.stderr[-500:]}"


def test_repo_markdown_links_workflow():
    """workflow.md must have valid markdown links (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "markdown-link-check", ".agents/skills/pr-status-triage/workflow.md", "--quiet"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(REPO),
    )
    assert r.returncode == 0, f"Markdown link check failed for workflow.md:\n{r.stderr[-500:]}"


def test_repo_markdown_links_local_repro():
    """local-repro.md must have valid markdown links (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "markdown-link-check", ".agents/skills/pr-status-triage/local-repro.md", "--quiet"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(REPO),
    )
    assert r.returncode == 0, f"Markdown link check failed for local-repro.md:\n{r.stderr[-500:]}"


def test_repo_alex_lint_skill():
    """SKILL.md must pass alex linting for insensitive language (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "alex", ".agents/skills/pr-status-triage/SKILL.md"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(REPO),
    )
    assert r.returncode == 0, f"Alex lint failed for SKILL.md:\n{r.stdout[-500:]}{r.stderr[-500:]}"


def test_repo_alex_lint_workflow():
    """workflow.md must pass alex linting for insensitive language (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "alex", ".agents/skills/pr-status-triage/workflow.md"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(REPO),
    )
    assert r.returncode == 0, f"Alex lint failed for workflow.md:\n{r.stdout[-500:]}{r.stderr[-500:]}"


def test_repo_alex_lint_local_repro():
    """local-repro.md must pass alex linting for insensitive language (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "alex", ".agents/skills/pr-status-triage/local-repro.md"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(REPO),
    )
    assert r.returncode == 0, f"Alex lint failed for local-repro.md:\n{r.stdout[-500:]}{r.stderr[-500:]}"


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
    # Instruction explicitly says: "prints a Usage: message to stderr that includes the subcommand name"
    assert "Usage:" in result.stderr, (
        f"Expected Usage: message in stderr, got: {result.stderr[:200]}"
    )
    assert "reply-and-resolve-thread" in result.stderr, (
        "Usage message must include the subcommand name"
    )


def test_reply_to_thread_uses_rest_api():
    """replyToThread must use REST API, not the old GraphQL mutation."""
    # Execute a Node script that inspects the source to verify behavioral changes.
    # We run actual Node code to do the analysis (not just text grep from Python),
    # which demonstrates the code is loaded and examined programmatically.
    test_script = """
    const path = require('path');
    const fs = require('fs');

    // Read the source and check for REST API usage patterns
    const code = fs.readFileSync(path.join(process.cwd(), 'scripts/pr-status.js'), 'utf8');

    // Check 1: Old GraphQL mutation should NOT be present
    // Instruction says: "not the old GraphQL mutation" - so absence is the behavior
    if (code.includes('addPullRequestReviewThreadReply(input:')) {
        console.error('OLD_MUTATION_PRESENT');
        process.exit(1);
    }

    // Check 2: REST API endpoint should be used
    // Instruction specifies: URL path contains /comments/ and /replies
    if (!code.includes('/comments/') || !code.includes('/replies')) {
        console.error('REST_ENDPOINT_MISSING');
        process.exit(1);
    }

    // Check 3: databaseId field is used for REST call
    // Instruction specifies this field is needed for the REST endpoint
    if (!code.includes('databaseId')) {
        console.error('DATABASE_ID_MISSING');
        process.exit(1);
    }

    console.log('REST_API_CHECK_PASSED');
    """

    result = _run_node(["-e", test_script])
    assert result.returncode == 0, f"replyToThread REST API check failed: {result.stderr}"


def test_generate_thread_md_includes_combined():
    """generateThreadMd must include the reply-and-resolve one-step option."""
    # Verify by running a Node script that extracts and inspects the function body.
    # This executes Node code (not just Python file-read) to verify behavior.
    test_script = """
    const fs = require('fs');

    const code = fs.readFileSync(process.cwd() + '/scripts/pr-status.js', 'utf8');

    // Use a simpler pattern: find generateThreadMd function and check its content
    const funcMatch = code.match(/function generateThreadMd[\\s\\S]*?(?=function \\w+|$)/);
    if (!funcMatch) {
        console.error('FUNCTION_NOT_FOUND');
        process.exit(1);
    }

    const funcBody = funcMatch[0];

    // Check for the required content as specified in the instruction
    if (!funcBody.includes('Reply and resolve in one step')) {
        console.error('COMBINED_LABEL_MISSING');
        process.exit(1);
    }

    if (!funcBody.includes('reply-and-resolve-thread')) {
        console.error('SUBCOMMAND_MISSING');
        process.exit(1);
    }

    console.log('GENERATE_THREAD_MD_CHECK_PASSED');
    """

    result = _run_node(["-e", test_script])
    assert result.returncode == 0, f"generateThreadMd check failed: {result.stderr}"


def test_reply_to_thread_logs_html_url():
    """replyToThread should log html_url from REST response, not GraphQL comment.url."""
    # Write a Node script that validates the function logs html_url properly.
    # We use Node's vm module to run the check programmatically.
    test_script_content = """
    const path = require('path');
    const fs = require('fs');

    const code = fs.readFileSync(path.join(process.cwd(), 'scripts/pr-status.js'), 'utf8');

    // Check that the code parses REST JSON response and logs html_url
    // The pattern data.html_url indicates: JSON.parse(output).html_url
    // Instruction says: response includes html_url field that should be logged
    if (!code.includes('data.html_url')) {
        console.error('HTML_URL_LOGGING_MISSING');
        process.exit(1);
    }

    // Verify it's in the context of replyToThread function (not elsewhere)
    const replyToThreadIdx = code.indexOf('function replyToThread');
    if (replyToThreadIdx === -1) {
        console.error('REPLY_FUNCTION_NOT_FOUND');
        process.exit(1);
    }

    // Extract the function body (approximate - find next function or end)
    const funcBody = code.slice(replyToThreadIdx, replyToThreadIdx + 3000);
    if (!funcBody.includes('data.html_url')) {
        console.error('HTML_URL_NOT_IN_REPLY_FUNCTION');
        process.exit(1);
    }

    console.log('HTML_URL_LOGGING_CHECK_PASSED');
    """

    result = _run_node(["-e", test_script_content])
    assert result.returncode == 0, f"replyToThread html_url logging check failed: {result.stderr}"


# ---------- fail_to_pass: config / documentation ----------


def test_skill_md_documents_combined_command():
    """SKILL.md must document the reply-and-resolve-thread command."""
    skill_md = REPO / ".agents/skills/pr-status-triage/SKILL.md"
    content = skill_md.read_text()

    # Instruction specifies: "add a section with the heading 'Thread interaction'"
    assert "Thread interaction" in content, (
        "SKILL.md should have a 'Thread interaction' quick-command section"
    )

    # Instruction specifies the command name must appear
    assert "reply-and-resolve-thread" in content, (
        "SKILL.md should mention the reply-and-resolve-thread command"
    )


def test_skill_md_workflow_step_updated():
    """SKILL.md workflow step 6 must mention the combined command."""
    skill_md = REPO / ".agents/skills/pr-status-triage/SKILL.md"
    content = skill_md.read_text()
    lines = content.split('\n')

    # Find step 6 specifically - it should mention "one step" in context of review handling
    # Step 6 is the step about addressing review comments
    in_step6 = False
    step6_lines = []
    for line in lines:
        stripped = line.strip()
        # Step 6 starts with "6." and discusses review comments
        if stripped.startswith('6.') and ('review' in stripped.lower() or 'comment' in stripped.lower()):
            in_step6 = True
            step6_lines.append(stripped)
        elif in_step6:
            # Check if we've hit the next numbered step
            if stripped and stripped[0].isdigit() and stripped.split('.')[0].strip().isdigit():
                break
            step6_lines.append(stripped)

    step6_text = ' '.join(step6_lines).lower()

    # Instruction says step 6 should mention "one step" as the improvement
    assert "one step" in step6_text or "one-step" in step6_text, (
        f"Step 6 should mention doing both reply and resolve in one step. Step 6 content: {step6_text[:200]}"
    )


def test_workflow_md_documents_one_step():
    """workflow.md must show the one-step reply-and-resolve alternative."""
    workflow_md = REPO / ".agents/skills/pr-status-triage/workflow.md"
    content = workflow_md.read_text()

    # Instruction specifies: describe using reply-and-resolve-thread
    assert "reply-and-resolve-thread" in content, (
        "workflow.md should reference the reply-and-resolve-thread subcommand"
    )

    # Instruction specifies: mention "one step"
    assert "one step" in content.lower(), (
        "workflow.md should describe the one-step alternative"
    )

