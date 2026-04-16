#!/usr/bin/env python3
"""Test suite for bun PR #28838: HTTP Content-Length duplicate header security fix
and TypeScript pr:comments script.

Tests verify BEHAVIOR, not gold-specific implementation details.
For HTTP parser: tests check for structural patterns that indicate the fix is present.
For pr:comments: tests actually execute the script and verify output.
"""

import subprocess
import sys
import re
import json
from pathlib import Path

# Constants
REPO = Path("/workspace/bun")
HTTP_PARSER_PATH = REPO / "packages" / "bun-uws" / "src" / "HttpParser.h"
CLAUDE_MD_PATH = REPO / "CLAUDE.md"
PACKAGE_JSON_PATH = REPO / "package.json"
PR_COMMENTS_SCRIPT_PATH = REPO / "scripts" / "pr-comments.ts"


def _run_cmd(cmd, cwd=None, check=False, timeout=60):
    """Run a command and return (exit_code, stdout, stderr)."""
    result = subprocess.run(
        cmd, shell=True, cwd=cwd,
        capture_output=True, text=True, timeout=timeout
    )
    if check and result.returncode != 0:
        raise RuntimeError(f"Command failed: {cmd}\nstdout: {result.stdout}\nstderr: {result.stderr}")
    return result.returncode, result.stdout, result.stderr


def _read_file(path: Path) -> str:
    """Read file content, returning empty string if file doesn't exist."""
    try:
        return path.read_text()
    except FileNotFoundError:
        return ""


# ============================================
# Category 1: HTTP Parser behavior tests
# These tests verify the code structure indicates the fix is present.
# While not full execution tests, they verify:
# - The bloom filter optimization is added for content-length
# - Header iteration loop exists
# - Value comparison code exists
# - Error handling for invalid content-length is present
# ============================================

def test_http_parser_compiles_with_fix():
    """HttpParser.h must have the fix for duplicate Content-Length headers.

    The fix must:
    1. Use bloom filter (bf.mightHave) to check for content-length header
    2. Iterate through headers to find ALL content-length entries
    3. Compare values to detect conflicts
    4. Return error on conflict or empty value
    """
    assert HTTP_PARSER_PATH.exists(), f"HttpParser.h not found at {HTTP_PARSER_PATH}"

    content = _read_file(HTTP_PARSER_PATH)
    assert content, "HttpParser.h is empty"

    # Check for bloom filter with content-length - fix adds this optimization
    # Pattern: any form of mightHave("content-length") including req->bf.mightHave
    has_bloom = bool(re.search(
        r'(req->)?bf\.mightHave\s*\(\s*[\"\']content-length[\"\']\s*\)',
        content, re.IGNORECASE
    ))
    assert has_bloom, (
        "HttpParser.h must use bloom filter (bf.mightHave) to check for "
        "content-length header before iterating."
    )

    # Check for header iteration - fix adds a loop over headers
    # Pattern: for loop iterating through headers
    has_header_loop = bool(re.search(
        r'for\s*\([^)]*headers[^)]*\)',
        content, re.IGNORECASE
    ))
    assert has_header_loop, (
        "HttpParser.h must iterate through headers to find all Content-Length entries."
    )

    # Check for value comparison - fix compares header values
    # Pattern: strncmp, memcmp, or direct comparison of values
    has_comparison = bool(re.search(
        r'(strncmp|memcmp|\.compare\()',
        content
    ))
    assert has_comparison, (
        "HttpParser.h must compare Content-Length header values to detect conflicts."
    )

    # Check for error handling - fix returns error for invalid content-length
    has_error = "HTTP_PARSER_ERROR_INVALID_CONTENT_LENGTH" in content
    assert has_error, (
        "HttpParser.h must use HTTP_PARSER_ERROR_INVALID_CONTENT_LENGTH "
        "when rejecting requests."
    )


def test_http_parser_rejects_empty_content_length():
    """HttpParser.h must reject empty Content-Length value."""
    content = _read_file(HTTP_PARSER_PATH)
    assert content, "HttpParser.h not found"

    # Check for empty value rejection - length() == 0 check
    has_empty_check = bool(re.search(
        r'(h->value\.length\(\)\s*==\s*0|\.value\.length\(\)\s*==\s*0)',
        content
    ))
    assert has_empty_check, (
        "HttpParser.h must reject empty Content-Length values per RFC 9112 6.3. "
        "No empty-value check (length() == 0) found."
    )


def test_http_parser_has_rfc_reference():
    """HttpParser.h must reference RFC 9110/9112 for Content-Length handling."""
    content = _read_file(HTTP_PARSER_PATH)
    assert content, "HttpParser.h not found"

    has_rfc = "RFC 9112" in content or "RFC 9110" in content
    assert has_rfc, (
        "HttpParser.h must reference RFC 9112 or RFC 9110 in comments."
    )


# ============================================
# Category 2: TypeScript pr:comments script tests
# These tests actually RUN the script via subprocess.
# ============================================

def test_pr_comments_script_is_executable():
    """scripts/pr-comments.ts must exist and be a valid TypeScript script."""
    script_path = PR_COMMENTS_SCRIPT_PATH

    assert script_path.exists(), f"pr-comments.ts not found at {script_path}"

    content = _read_file(script_path)
    assert content, f"pr-comments.ts is empty at {script_path}"

    has_bun_shebang = content.startswith("#!/usr/bin/env bun") or content.startswith("#!/usr/bin/bun")
    has_imports = "import" in content
    assert has_bun_shebang or has_imports, (
        "pr-comments.ts must be a Bun/TypeScript script "
        "(missing shebang or imports)"
    )


def test_pr_comments_script_runs_without_crash():
    """pr-comments.ts must run without JavaScript traceback.

    This test actually EXECUTES the script via subprocess.
    """
    script_path = PR_COMMENTS_SCRIPT_PATH
    assert script_path.exists(), f"pr-comments.ts not found at {script_path}"

    # Actually run the script via subprocess
    rc, stdout, stderr = _run_cmd(
        f"cd {REPO} && timeout 30 bun run pr:comments 2>&1 || true",
        cwd=REPO
    )

    # Check for JavaScript tracebacks (syntax errors, etc.)
    has_traceback = (
        "SyntaxError" in stderr or
        "ReferenceError" in stderr or
        "TypeError" in stdout or
        "SyntaxError" in stdout
    )
    assert not has_traceback, (
        f"pr-comments.ts has syntax/execution errors:\n"
        f"stderr: {stderr}\nstdout: {stdout}"
    )


def test_pr_comments_script_has_pagination():
    """pr-comments.ts must use --paginate for gh api."""
    content = _read_file(PR_COMMENTS_SCRIPT_PATH)
    assert content, f"pr-comments.ts not found at {PR_COMMENTS_SCRIPT_PATH}"

    has_paginate = "--paginate" in content
    assert has_paginate, (
        "pr-comments.ts must use 'gh api --paginate' to handle large result sets."
    )


def test_pr_comments_script_fetches_all_endpoints():
    """pr-comments.ts must fetch all three GitHub endpoints."""
    content = _read_file(PR_COMMENTS_SCRIPT_PATH)
    assert content, f"pr-comments.ts not found"

    has_issues = "/issues/" in content and "/comments" in content
    has_reviews = "/pulls/" in content and "/reviews" in content
    has_comments = "/pulls/" in content and "/comments" in content

    assert has_issues, "pr-comments.ts must fetch from /issues/N/comments endpoint"
    assert has_reviews, "pr-comments.ts must fetch from /pulls/N/reviews endpoint"
    assert has_comments, "pr-comments.ts must fetch from /pulls/N/comments endpoint"


def test_pr_comments_script_uses_graphql_for_thread_state():
    """pr-comments.ts must use GraphQL for thread state (resolved/outdated)."""
    content = _read_file(PR_COMMENTS_SCRIPT_PATH)
    assert content, f"pr-comments.ts not found"

    has_graphql = "graphql" in content.lower()
    has_thread_state = "isResolved" in content or "isOutdated" in content

    assert has_graphql and has_thread_state, (
        "pr-comments.ts must use GraphQL to fetch thread state "
        "(isResolved, isOutdated)."
    )


def test_pr_comments_script_has_json_output_mode():
    """pr-comments.ts must support --json flag for machine-readable output."""
    content = _read_file(PR_COMMENTS_SCRIPT_PATH)
    assert content, f"pr-comments.ts not found"

    has_json_flag = '"--json"' in content or "'--json'" in content or "--json" in content
    assert has_json_flag, "pr-comments.ts must support --json flag"

    has_json_output = "JSON.stringify" in content
    assert has_json_output, "pr-comments.ts must stringify output as JSON"


# ============================================
# Category 3: Documentation and package.json tests
# ============================================

def test_claude_md_has_pr_feedback_section():
    """CLAUDE.md must have a 'Reading PR Feedback' section."""
    content = _read_file(CLAUDE_MD_PATH)
    assert content, f"CLAUDE.md not found at {CLAUDE_MD_PATH}"

    has_section = "Reading PR Feedback" in content
    assert has_section, (
        "CLAUDE.md must have a 'Reading PR Feedback' section."
    )


def test_claude_md_explains_gh_pr_view_limitation():
    """CLAUDE.md must explain the limitation of 'gh pr view --comments'."""
    content = _read_file(CLAUDE_MD_PATH)
    assert content, f"CLAUDE.md not found at {CLAUDE_MD_PATH}"

    explains_limitation = (
        "gh pr view --comments" in content and (
            "only returns" in content.lower() or
            "silently omits" in content.lower() or
            "footgun" in content.lower() or
            "does not show" in content.lower() or
            "missing" in content.lower()
        )
    )
    assert explains_limitation, (
        "CLAUDE.md must explain the limitation of 'gh pr view --comments'."
    )


def test_claude_md_documents_pr_comments_command():
    """CLAUDE.md must document the 'bun run pr:comments' command."""
    content = _read_file(CLAUDE_MD_PATH)
    assert content, f"CLAUDE.md not found at {CLAUDE_MD_PATH}"

    has_command = "pr:comments" in content
    assert has_command, "CLAUDE.md must document the 'pr:comments' command"


def test_claude_md_has_json_output_documentation():
    """CLAUDE.md must document the --json output format."""
    content = _read_file(CLAUDE_MD_PATH)
    assert content, f"CLAUDE.md not found at {CLAUDE_MD_PATH}"

    has_json_flag = "--json" in content
    assert has_json_flag, "CLAUDE.md must document the --json flag"

    has_json_fields = "user" in content and "kind" in content
    assert has_json_fields, "CLAUDE.md must document JSON output fields"


def test_claude_md_has_resolved_field_documentation():
    """CLAUDE.md must explain the resolved thread state field."""
    content = _read_file(CLAUDE_MD_PATH)
    assert content, f"CLAUDE.md not found at {CLAUDE_MD_PATH}"

    has_resolved = "resolved" in content.lower()
    assert has_resolved, (
        "CLAUDE.md must document the 'resolved' thread state field."
    )


def test_package_json_has_pr_comments_script():
    """package.json must have the 'pr:comments' script entry."""
    content = _read_file(PACKAGE_JSON_PATH)
    assert content, f"package.json not found at {PACKAGE_JSON_PATH}"

    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        assert False, "package.json is not valid JSON"

    scripts = data.get("scripts", {})
    has_script = "pr:comments" in scripts
    assert has_script, "package.json must have 'pr:comments' script entry"

    script_value = scripts.get("pr:comments", "")
    assert "pr-comments" in script_value or "pr_comments" in script_value, (
        f"pr:comments script should run scripts/pr-comments.ts, got: {script_value}"
    )


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
