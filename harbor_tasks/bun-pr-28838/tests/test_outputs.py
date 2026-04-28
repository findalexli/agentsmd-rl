#!/usr/bin/env python3
"""Test suite for bun PR #28838: HTTP Content-Length duplicate header security fix
and TypeScript pr:comments script.

Tests verify BEHAVIOR: HTTP parser tests extract the validation code from HttpParser.h,
compile it with g++ using mock types, and run behavioral test cases.
pr:comments tests execute the script via subprocess.
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
# These tests verify the Content-Length duplicate detection security fix.
# The behavioral test extracts the validation code from HttpParser.h,
# compiles it with mock types using g++, and runs test cases.
# ============================================

def test_http_parser_has_security_fix():
    """HttpParser.h must have content-length duplicate detection with bloom filter and error code.

    Checks high-level structural properties required by the instruction:
    - Bloom filter usage for content-length (instruction requirement #6)
    - HTTP_PARSER_ERROR_INVALID_CONTENT_LENGTH error code (instruction requirement #7)
    """
    content = _read_file(HTTP_PARSER_PATH)
    assert content, "HttpParser.h not found or empty"

    # Must use bloom filter for content-length (instruction requirement #6)
    assert re.search(
        r'mightHave\s*\([^)]*content.length',
        content, re.IGNORECASE
    ), (
        "HttpParser.h must use bloom filter (mightHave) to check for "
        "content-length header before iterating."
    )

    # Must use the specific error code (instruction requirement #7)
    assert "HTTP_PARSER_ERROR_INVALID_CONTENT_LENGTH" in content, (
        "HttpParser.h must use HTTP_PARSER_ERROR_INVALID_CONTENT_LENGTH "
        "when rejecting requests with invalid Content-Length."
    )


def test_http_parser_content_length_behavior():
    """Extract CL validation from HttpParser.h, compile with mock types, test behavior.

    This test:
    1. Locates the content-length handling section using stable landmarks in the
       original code (the "request smuggling" comment and contentLengthStringLen)
    2. Extracts the validation code added by the fix
    3. Wraps it in a C++ test harness with mock types matching HttpParser.h's API
    4. Compiles with g++ and runs behavioral test cases:
       - No error when no Content-Length header is present
       - No error for a single valid Content-Length
       - No error for duplicate identical Content-Length values (RFC 9112 6.3)
       - Error 400 for conflicting Content-Length values
       - Error 400 for empty Content-Length value
    """
    content = _read_file(HTTP_PARSER_PATH)
    assert content, "HttpParser.h not found or empty"

    # Find the content-length handling section using stable landmarks.
    # "ought to be handled as an error" is in the ORIGINAL code's comment block
    # about request smuggling, right before the Content-Length handling code.
    start_marker = "ought to be handled as an error"
    start_idx = content.find(start_marker)
    assert start_idx != -1, (
        "Could not find 'ought to be handled as an error' comment in HttpParser.h. "
        "This landmark exists in the original code's request-smuggling comment."
    )

    # Find end of that comment block
    comment_end = content.find("*/", start_idx)
    assert comment_end != -1, "Malformed comment block in HttpParser.h"
    code_start = comment_end + 2

    # "contentLengthStringLen" is in the ORIGINAL code, right after the CL handling.
    end_marker = "contentLengthStringLen"
    end_idx = content.find(end_marker, code_start)
    assert end_idx != -1, (
        "Could not find 'contentLengthStringLen' after content-length handling. "
        "This landmark exists in the original code."
    )

    # Extract to the start of the line containing contentLengthStringLen
    line_start = content.rfind('\n', code_start, end_idx)
    if line_start == -1:
        line_start = code_start

    validation_code = content[code_start:line_start].strip()
    assert len(validation_code) > 30, (
        f"Extracted content-length validation code is too short "
        f"({len(validation_code)} chars). Expected duplicate Content-Length "
        f"detection logic between the request-smuggling comment and "
        f"contentLengthStringLen."
    )

    # Build C++ test harness with mock types matching HttpParser.h's API surface.
    cpp_header = r'''
#include <string_view>
#include <cstring>
#include <iostream>
#include <algorithm>

#ifndef HTTP_ERROR_400_BAD_REQUEST
#define HTTP_ERROR_400_BAD_REQUEST 400
#endif
#ifndef HTTP_PARSER_ERROR_INVALID_CONTENT_LENGTH
#define HTTP_PARSER_ERROR_INVALID_CONTENT_LENGTH 1
#endif

struct HttpParserResult {
    bool is_error;
    int code;
    int parser_error;
    static HttpParserResult error(int c, int pe) { return {true, c, pe}; }
};

struct Header {
    std::string_view key;
    std::string_view value;
};

struct BloomFilter {
    bool _has;
    bool mightHave(const char*) const { return _has; }
    bool mightHave(std::string_view) const { return _has; }
};

struct HttpRequest {
    using Header = ::Header;
    ::Header* headers;
    BloomFilter bf;

    std::string_view getHeader(const char* name) const {
        for (::Header* h = headers; (++h)->key.length(); ) {
            if (h->key == name) return h->value;
        }
        return {};
    }
};

HttpParserResult validate_cl(HttpRequest* req) {
    // --- BEGIN extracted from HttpParser.h ---
'''

    cpp_footer = r'''
    // --- END extracted ---
    return HttpParserResult{false, 0, 0};
}

bool run_test(const char* name, bool expect_error, ::Header* hdrs, bool bloom) {
    HttpRequest req;
    req.headers = hdrs;
    req.bf._has = bloom;
    auto r = validate_cl(&req);
    if (r.is_error != expect_error) {
        std::cerr << "FAIL: " << name
                  << " expected=" << (expect_error ? "error" : "ok")
                  << " got=" << (r.is_error ? "error" : "ok") << "\n";
        return false;
    }
    std::cerr << "PASS: " << name << "\n";
    return true;
}

int main() {
    bool ok = true;

    // 1: No content-length header (bloom says no) -> accept
    ::Header h1[] = {{}, {"host", "example.com"}, {}};
    ok &= run_test("no_cl", false, h1, false);

    // 2: Single valid content-length -> accept
    ::Header h2[] = {{}, {"content-length", "42"}, {}};
    ok &= run_test("single_cl", false, h2, true);

    // 3: Duplicate IDENTICAL content-length -> accept (RFC 9112 6.3)
    ::Header h3[] = {{}, {"content-length", "42"}, {"content-length", "42"}, {}};
    ok &= run_test("identical_dup_cl", false, h3, true);

    // 4: CONFLICTING content-length -> reject with error
    ::Header h4[] = {{}, {"content-length", "42"}, {"content-length", "99"}, {}};
    ok &= run_test("conflicting_cl", true, h4, true);

    // 5: EMPTY content-length -> reject with error (RFC 9112 6.3)
    ::Header h5[] = {{}, {"content-length", ""}, {}};
    ok &= run_test("empty_cl", true, h5, true);

    if (ok) {
        std::cout << "ALL_TESTS_PASSED" << std::endl;
        return 0;
    }
    return 1;
}
'''

    test_cpp = cpp_header + "\n" + validation_code + "\n" + cpp_footer
    test_file = REPO / "_cl_validation_test.cpp"
    test_binary = REPO / "_cl_validation_test"

    try:
        test_file.write_text(test_cpp)

        # Compile with g++ (C++17 for std::string_view)
        result = subprocess.run(
            ["g++", "-std=c++17", "-o", str(test_binary), str(test_file)],
            capture_output=True, text=True, timeout=30, cwd=str(REPO)
        )
        assert result.returncode == 0, (
            f"Content-length validation code failed to compile with g++:\n"
            f"{result.stderr}\n"
            f"The extracted code from HttpParser.h must compile with the "
            f"standard HttpParser types (HttpRequest, HttpParserResult, etc.)."
        )

        # Run the behavioral tests
        result = subprocess.run(
            [str(test_binary)],
            capture_output=True, text=True, timeout=10
        )
        assert result.returncode == 0, (
            f"Content-length behavioral tests failed:\n{result.stderr}"
        )
        assert "ALL_TESTS_PASSED" in result.stdout, (
            f"Not all behavioral tests passed:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
    finally:
        test_file.unlink(missing_ok=True)
        test_binary.unlink(missing_ok=True)


def test_http_parser_has_rfc_reference():
    """HttpParser.h must reference RFC 9110 or RFC 9112 in Content-Length handling code.

    Checks the extracted content-length validation section (between the
    original request-smuggling comment and contentLengthStringLen) for an
    RFC reference. This ensures the RFC mention is in the new code, not
    just in pre-existing comments elsewhere in the file.
    """
    content = _read_file(HTTP_PARSER_PATH)
    assert content, "HttpParser.h not found"

    # Extract the content-length handling section using the same landmarks
    # as test_http_parser_content_length_behavior.
    start_marker = "ought to be handled as an error"
    start_idx = content.find(start_marker)
    assert start_idx != -1, (
        "Could not find request-smuggling comment landmark in HttpParser.h."
    )

    comment_end = content.find("*/", start_idx)
    assert comment_end != -1, "Malformed comment block in HttpParser.h"
    code_start = comment_end + 2

    end_marker = "contentLengthStringLen"
    end_idx = content.find(end_marker, code_start)
    assert end_idx != -1, (
        "Could not find contentLengthStringLen landmark in HttpParser.h."
    )

    line_start = content.rfind('\n', code_start, end_idx)
    if line_start == -1:
        line_start = code_start

    validation_code = content[code_start:line_start].strip()

    assert "RFC" in validation_code, (
        "The Content-Length validation code must reference RFC 9110 or RFC 9112 "
        "in a comment. The new handling code should cite the relevant RFC "
        "per instruction requirement #8."
    )


# ============================================
# Category 2: TypeScript pr:comments script tests
# These tests verify the pr-comments.ts script exists, runs, and
# has the required features (pagination, endpoints, GraphQL, JSON).
# ============================================

def test_pr_comments_script_exists():
    """scripts/pr-comments.ts must exist and be a valid TypeScript/Bun script."""
    assert PR_COMMENTS_SCRIPT_PATH.exists(), (
        f"pr-comments.ts not found at {PR_COMMENTS_SCRIPT_PATH}"
    )

    content = _read_file(PR_COMMENTS_SCRIPT_PATH)
    assert content, "pr-comments.ts is empty"

    has_bun_shebang = (
        content.startswith("#!/usr/bin/env bun") or
        content.startswith("#!/usr/bin/bun")
    )
    has_imports = "import" in content
    assert has_bun_shebang or has_imports, (
        "pr-comments.ts must be a Bun/TypeScript script "
        "(missing shebang or imports)"
    )


def test_pr_comments_script_runs_without_crash():
    """pr-comments.ts must run without JavaScript traceback errors.

    Executes the script via subprocess. It may fail due to no GitHub auth
    in the test environment, but must not have syntax/type errors.
    """
    assert PR_COMMENTS_SCRIPT_PATH.exists(), "pr-comments.ts not found"

    result = subprocess.run(
        ["bash", "-c", f"cd {REPO} && timeout 30 bun run pr:comments 2>&1 || true"],
        capture_output=True, text=True, timeout=60, cwd=str(REPO)
    )
    combined = result.stdout + result.stderr

    has_traceback = any(err in combined for err in [
        "SyntaxError", "ReferenceError", "TypeError"
    ])
    assert not has_traceback, (
        f"pr-comments.ts has syntax/execution errors:\n{combined}"
    )


def test_pr_comments_script_has_pagination():
    """pr-comments.ts must use --paginate for gh api to handle large result sets."""
    content = _read_file(PR_COMMENTS_SCRIPT_PATH)
    assert content, "pr-comments.ts not found"

    assert "--paginate" in content, (
        "pr-comments.ts must use 'gh api --paginate' to handle large result sets."
    )


def test_pr_comments_script_fetches_all_endpoints():
    """pr-comments.ts must fetch all three GitHub REST endpoints."""
    content = _read_file(PR_COMMENTS_SCRIPT_PATH)
    assert content, "pr-comments.ts not found"

    assert "/issues/" in content and "/comments" in content, \
        "Must fetch from /issues/N/comments endpoint"
    assert "/pulls/" in content and "/reviews" in content, \
        "Must fetch from /pulls/N/reviews endpoint"
    assert "/pulls/" in content and "/comments" in content, \
        "Must fetch from /pulls/N/comments endpoint"


def test_pr_comments_script_uses_graphql():
    """pr-comments.ts must use GraphQL for thread state (resolved/outdated)."""
    content = _read_file(PR_COMMENTS_SCRIPT_PATH)
    assert content, "pr-comments.ts not found"

    has_graphql = "graphql" in content.lower()
    has_thread_state = "isResolved" in content or "isOutdated" in content

    assert has_graphql and has_thread_state, (
        "pr-comments.ts must use GraphQL to fetch thread state "
        "(isResolved, isOutdated)."
    )


def test_pr_comments_script_has_json_output():
    """pr-comments.ts must support --json flag and label entries with their kind.

    The instruction requires the script to label each entry with its kind
    (issue comment, review verdict, line comment, reply, + suggestion).
    """
    content = _read_file(PR_COMMENTS_SCRIPT_PATH)
    assert content, "pr-comments.ts not found"

    assert "--json" in content, "pr-comments.ts must support --json flag"
    assert "JSON.stringify" in content, "pr-comments.ts must stringify output as JSON"

    # Must label entries with different kind values (instruction requirement)
    for label in ["issue comment", "review", "line comment"]:
        assert label in content, (
            f"pr-comments.ts must label entries with kind '{label}'"
        )


# ============================================
# Category 3: Documentation and package.json tests
# These tests verify CLAUDE.md has the required "Reading PR Feedback"
# section and package.json has the pr:comments script entry.
# ============================================

def test_claude_md_has_pr_feedback_section():
    """CLAUDE.md must have a 'Reading PR Feedback' section."""
    content = _read_file(CLAUDE_MD_PATH)
    assert content, "CLAUDE.md not found"

    assert "Reading PR Feedback" in content, (
        "CLAUDE.md must have a 'Reading PR Feedback' section."
    )


def test_claude_md_explains_gh_pr_view_limitation():
    """CLAUDE.md must explain the limitation of 'gh pr view --comments'."""
    content = _read_file(CLAUDE_MD_PATH)
    assert content, "CLAUDE.md not found"

    assert "gh pr view --comments" in content, (
        "CLAUDE.md must mention 'gh pr view --comments'"
    )

    explains = (
        "only returns" in content.lower() or
        "silently omits" in content.lower() or
        "footgun" in content.lower() or
        "does not show" in content.lower() or
        "missing" in content.lower()
    )
    assert explains, (
        "CLAUDE.md must explain the limitation of 'gh pr view --comments' "
        "(e.g., that it silently omits review comments)."
    )


def test_claude_md_documents_pr_comments_command():
    """CLAUDE.md must document the 'bun run pr:comments' command."""
    content = _read_file(CLAUDE_MD_PATH)
    assert content, "CLAUDE.md not found"

    assert "pr:comments" in content, (
        "CLAUDE.md must document the 'pr:comments' command."
    )


def test_claude_md_has_json_output_documentation():
    """CLAUDE.md must document the --json output format and JSON fields."""
    content = _read_file(CLAUDE_MD_PATH)
    assert content, "CLAUDE.md not found"

    assert "--json" in content, "CLAUDE.md must document the --json flag"

    assert "user" in content and "kind" in content, (
        "CLAUDE.md must document JSON output fields (user, kind, etc.)"
    )


def test_claude_md_has_resolved_field_documentation():
    """CLAUDE.md must explain the resolved thread state field."""
    content = _read_file(CLAUDE_MD_PATH)
    assert content, "CLAUDE.md not found"

    assert "resolved" in content.lower(), (
        "CLAUDE.md must document the 'resolved' thread state field."
    )


def test_package_json_has_pr_comments_script():
    """package.json must have the 'pr:comments' script entry."""
    content = _read_file(PACKAGE_JSON_PATH)
    assert content, "package.json not found"

    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        assert False, "package.json is not valid JSON"

    scripts = data.get("scripts", {})
    assert "pr:comments" in scripts, (
        "package.json must have 'pr:comments' script entry"
    )

    script_value = scripts.get("pr:comments", "")
    assert "pr-comments" in script_value or "pr_comments" in script_value, (
        f"pr:comments script should reference pr-comments.ts, got: {script_value}"
    )


def test_existing_package_json_scripts_unchanged():
    """Regression: existing ci:* and watch scripts must remain intact in package.json.

    The gold fix adds a pr:comments entry but must not corrupt or remove
    any existing script entries. This passes on both base and gold.
    """
    content = _read_file(PACKAGE_JSON_PATH)
    assert content, "package.json not found"

    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        assert False, "package.json is not valid JSON"

    scripts = data.get("scripts", {})
    assert "ci:errors" in scripts, "Missing existing ci:errors script"
    assert "ci:logs" in scripts, "Missing existing ci:logs script"
    assert "ci:watch" in scripts, "Missing existing ci:watch script"
    assert "watch" in scripts, "Missing existing watch script"
    assert "bd" in scripts, "Missing existing bd script"
    assert "build" in scripts, "Missing existing build script"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
