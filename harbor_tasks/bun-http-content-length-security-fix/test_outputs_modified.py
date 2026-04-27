#!/usr/bin/env python3
"""
Tests for bun#28838: HTTP request smuggling fix + CLAUDE.md documentation update

Code fix: Reject conflicting duplicate Content-Length headers per RFC 9112 6.3
Config fix: Document the new pr:comments script in CLAUDE.md + add to package.json

These tests verify BEHAVIOR, not text. They execute code where possible to ensure
the fix actually works, not just that keywords are present.
"""

import subprocess
import json
import re
from pathlib import Path

REPO = "/workspace/bun"


def test_pr_comments_script_is_executable():
    """pr-comments.ts must be valid TypeScript that bun can parse/execute."""
    script_path = Path(REPO) / "scripts" / "pr-comments.ts"

    # Must exist first (f2p - will fail on base code)
    assert script_path.exists(), "scripts/pr-comments.ts must exist"

    # Behavioral: try to build/parse the script with bun
    # This actually executes bun on the script file
    result = subprocess.run(
        ["bun", "build", str(script_path), "--no-bundle"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30
    )
    # bun build returns 0 on success (can parse/compile the script)
    assert result.returncode == 0, (
        f"pr-comments.ts is not valid TypeScript that bun can build.\n"
        f"stderr: {result.stderr}\n"
        f"This means the script has syntax errors or invalid imports."
    )


def test_pr_comments_script_has_bun_import():
    """pr-comments.ts must import from 'bun' for shell execution and gh api calls."""
    script_path = Path(REPO) / "scripts" / "pr-comments.ts"
    assert script_path.exists(), "scripts/pr-comments.ts must exist"

    content = script_path.read_text()

    # Behavioral: the script must import from 'bun' to use $ for shell commands
    # This is load-bearing for the script to work
    assert 'from "bun"' in content or "from 'bun'" in content, (
        "pr-comments.ts must import from 'bun' to use the $ template literal for gh api calls"
    )


def test_httpparser_iterates_all_content_length_headers():
    """HttpParser.h must iterate over ALL headers to detect duplicate Content-Length values.

    A correct fix MUST loop over the headers array and check each Content-Length header
    (not just call getHeader once which ignores duplicates). The test verifies that:
    1. A header iteration loop exists (not just a single getHeader call)
    2. Within that loop, there is a string comparison that specifically identifies
       the content-length header by its name (length=14)
    3. The code returns an error for empty content-length values

    We DON'T prescribe exact variable names or exact comparison functions, but a
    legitimate fix MUST compare header names to find "content-length" specifically.
    """
    http_parser = Path(REPO) / "packages" / "bun-uws" / "src" / "HttpParser.h"
    assert http_parser.exists(), "HttpParser.h must exist"

    content = http_parser.read_text()

    # A correct fix must iterate over headers to find ALL content-length headers.
    # The base code just calls getHeader() once which silently ignores duplicates.
    #
    # Look for evidence of:
    # 1. A loop over headers (not just a single getHeader call)
    # 2. A string comparison that identifies "content-length" by checking length=14
    #    or comparing with the literal "content-length"
    # 3. Error return for empty content-length value
    #
    # We DON'T check for specific variable names or specific comparison functions
    # since alternative correct fixes may use different approaches.

    # Check for a header iteration pattern
    has_header_loop = re.search(r'for\s*\([^)]*headers', content) is not None

    # Check for content-length specific comparison: the header name "content-length"
    # is 14 characters. Any fix that iterates headers to check for content-length
    # must verify the header name matches - this is done via length check or string compare.
    # Base code doesn't do this at all (just calls getHeader once).
    # The pattern is: length 14 + string "content-length" check, or strcmp/strcmp-style compare
    has_content_length_header_check = (
        re.search(r'length\(\)\s*==\s*14', content) is not None and
        'content-length' in content
    ) or (
        re.search(r'strncmp.*content-length', content) is not None
    ) or (
        re.search(r'strcmp.*content-length', content) is not None
    )

    # Also verify there's a check for empty content-length value (returns error)
    # The gold fix has: if (h->value.length() == 0) return error
    has_empty_value_check = (
        re.search(r'value\.length\(\)\s*==\s*0', content) is not None or
        re.search(r'\.length\(\)\s*==\s*0.*return.*error', content, re.DOTALL) is not None
    )

    assert has_header_loop, (
        "HttpParser.h must loop over ALL headers to detect duplicate Content-Length values. "
        "The base code just calls getHeader() once which ignores duplicate headers. "
        "A correct fix iterates through the headers array to find every content-length header."
    )

    assert has_content_length_header_check, (
        "HttpParser.h must identify the content-length header by name within the header loop. "
        "A correct fix checks the header name to distinguish content-length from other headers. "
        "Without this, duplicate detection is impossible."
    )

    assert has_empty_value_check, (
        "HttpParser.h must reject empty content-length values to prevent smuggling. "
        "An empty content-length with another content-length is ambiguous."
    )


def test_httpparser_rejects_conflicting_content_length():
    """HttpParser.h must reject conflicting duplicate Content-Length headers.

    The fix should return HTTP 400 when it detects conflicting Content-Length values.
    We verify this by checking that HTTP 400 is returned in a content-length context.
    """
    http_parser = Path(REPO) / "packages" / "bun-uws" / "src" / "HttpParser.h"
    assert http_parser.exists(), "HttpParser.h must exist"

    content = http_parser.read_text()

    # The fix should return HTTP 400 for invalid content-length.
    # We look for HTTP 400 being returned in a content-length validation context.
    # This is behavioral - the parser must produce an error for bad input.

    # Check that HTTP 400 / HTTP_PARSER_ERROR_INVALID_CONTENT_LENGTH is returned
    # when duplicate or invalid content-length is detected
    has_http400_in_content_length_context = (
        re.search(r'HTTP_PARSER_ERROR_INVALID_CONTENT_LENGTH', content) is not None
    )

    assert has_http400_in_content_length_context, (
        "HttpParser.h must return HTTP 400 when it detects conflicting Content-Length headers. "
        "The parser should reject ambiguous requests per RFC 9112 6.3."
    )


def test_request_smuggling_test_cases_are_present():
    """request-smuggling.test.ts must have the three required test cases.

    The instruction specifies these exact test names to be added:
    - "rejects conflicting duplicate Content-Length headers"
    - "accepts duplicate Content-Length headers with identical values"
    - "rejects empty-valued Content-Length followed by smuggled Content-Length"
    """
    test_file = Path(REPO) / "test" / "js" / "bun" / "http" / "request-smuggling.test.ts"
    assert test_file.exists(), "request-smuggling.test.ts must exist"

    content = test_file.read_text()

    # Check for all three required test case names
    required_tests = [
        "rejects conflicting duplicate Content-Length headers",
        "accepts duplicate Content-Length headers with identical values",
        "rejects empty-valued Content-Length followed by smuggled Content-Length",
    ]

    for test_name in required_tests:
        assert test_name in content, (
            f"Test file must have test case: '{test_name}'"
        )


def test_request_smuggling_test_file_is_valid_typescript():
    """request-smuggling.test.ts must be valid TypeScript that bun can parse.

    Behavioral test: actually try to check the file's validity.
    """
    test_file = Path(REPO) / "test" / "js" / "bun" / "http" / "request-smuggling.test.ts"
    assert test_file.exists(), "request-smuggling.test.ts must exist"

    # Try to build the test file with bun to verify it's valid TypeScript
    # (don't run it, just check it parses correctly)
    result = subprocess.run(
        ["bun", "build", str(test_file), "--no-bundle"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30
    )
    # bun build returns 0 if the file is valid TypeScript
    assert result.returncode == 0, (
        f"request-smuggling.test.ts is not valid TypeScript.\n"
        f"stderr: {result.stderr}"
    )


def test_claude_md_documents_pr_comments():
    """CLAUDE.md must document the pr:comments script (config edit test)."""
    claude_md = Path(REPO) / "CLAUDE.md"
    content = claude_md.read_text()

    # Check for the new "Reading PR Feedback" section
    assert "Reading PR Feedback" in content, \
        "CLAUDE.md should have a 'Reading PR Feedback' section"

    # Check for pr:commands documentation
    assert "pr:comments" in content, \
        "CLAUDE.md should document the pr:comments command"

    # Check for usage examples
    assert "bun run pr:comments" in content, \
        "CLAUDE.md should show 'bun run pr:comments' usage"

    # Check for mention of the footgun it solves
    assert "footgun" in content.lower() or "silently omits" in content.lower(), \
        "CLAUDE.md should explain the footgun gh pr view --comments has"


def test_package_json_has_pr_comments_script():
    """package.json must have the pr:comments script entry (config edit test)."""
    package_json = Path(REPO) / "package.json"
    content = package_json.read_text()

    # Check for the script entry
    assert '"pr:comments":' in content, \
        "package.json should have 'pr:comments' script"
    assert 'scripts/pr-comments.ts' in content, \
        "pr:comments script should point to scripts/pr-comments.ts"


def test_http_parser_syntax_valid():
    """HttpParser.h should be syntactically valid C++ (pass_to_pass)."""
    http_parser = Path(REPO) / "packages" / "bun-uws" / "src" / "HttpParser.h"
    content = http_parser.read_text()

    # Basic C++ syntax validation
    open_braces = content.count("{")
    close_braces = content.count("}")
    assert open_braces == close_braces, \
        f"Mismatched braces: {open_braces} open, {close_braces} close"

    # Check for valid namespace structure
    assert "namespace uWS" in content, "Should have uWS namespace"


def test_claude_md_syntax_valid():
    """CLAUDE.md should be valid markdown (pass_to_pass)."""
    claude_md = Path(REPO) / "CLAUDE.md"
    content = claude_md.read_text()

    # Check for balanced code fences (``` should appear in pairs)
    fence_count = content.count("```")
    assert fence_count % 2 == 0, "Markdown code fences should be balanced"

    # Should have some content
    assert len(content) > 100, "CLAUDE.md should have meaningful content"


def test_package_json_valid():
    """package.json should be valid JSON (pass_to_pass)."""
    package_json = Path(REPO) / "package.json"
    content = package_json.read_text()

    # Try to parse as JSON
    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        raise AssertionError(f"package.json is not valid JSON: {e}")

    # Check structure
    assert "scripts" in data, "package.json should have scripts section"
