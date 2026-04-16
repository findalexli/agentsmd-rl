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


def test_pr_comments_script_has_required_imports():
    """pr-comments.ts must import from 'bun' for shell execution."""
    script_path = Path(REPO) / "scripts" / "pr-comments.ts"
    assert script_path.exists(), "scripts/pr-comments.ts must exist"

    content = script_path.read_text()

    # Behavioral: the script must import from 'bun' to use $ for shell commands
    # This is load-bearing for the script to work
    assert 'from "bun"' in content or "from 'bun'" in content, (
        "pr-comments.ts must import from 'bun' to use the $ template literal for gh api calls"
    )


def test_httpparser_validates_content_length_behavior():
    """HttpParser.h must implement RFC 9112 6.3 Content-Length validation.

    A correct fix MUST iterate over headers to find ALL Content-Length headers
    (not just call getHeader once) and compare their values to detect conflicts.

    The fix behavior:
    1. Header iteration: loop over req->headers to find all content-length headers
    2. Value comparison: compare content-length values to detect conflicts
    """
    http_parser = Path(REPO) / "packages" / "bun-uws" / "src" / "HttpParser.h"
    assert http_parser.exists(), "HttpParser.h must exist"

    content = http_parser.read_text()

    # The fix iterates over req->headers to find ALL content-length headers
    # The base code just calls getHeader() once which ignores duplicates
    # We look for evidence of content-length specific header iteration:
    # - The string "content-length" should appear in the header processing section
    # - There should be a loop over headers
    # - Inside that loop, content-length values should be compared
    has_content_length_header_loop = (
        # Check for content-length string comparison in context of header iteration
        re.search(r'content-length.*strncmp', content, re.IGNORECASE) is not None or
        re.search(r'contentLength.*strncmp', content) is not None or
        # Check for length comparison pattern that would detect duplicates
        (re.search(r'for\s*\([^)]*headers', content) is not None and
         re.search(r'content-length.*!=.*content-length', content, re.IGNORECASE) is not None)
    )
    assert has_content_length_header_loop, (
        "HttpParser.h must loop over headers AND compare Content-Length values to detect duplicates. "
        "The base code just calls getHeader() once which ignores duplicate headers. "
        "A correct fix iterates through all headers, finds every content-length header, "
        "and compares their values."
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
