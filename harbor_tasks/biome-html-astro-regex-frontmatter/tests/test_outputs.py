"""
Test suite for biomejs/biome#9728: fix(html): handle escaped regex literals in astro frontmatter

The bug: When parsing Astro files with frontmatter containing regex literals like `/\d{4}/`,
the lexer's quote tracking state incorrectly shows non-empty state after the regex should have closed.

The fix: Reorders escape sequence handling in the lexer so that a deferred `/` is resolved
before generic escape handling.
"""

import subprocess
import os
import tempfile
import glob

REPO = "/workspace/biome_repo"


def run(cmd, **kwargs):
    kwargs.setdefault("capture_output", True)
    kwargs.setdefault("text", True)
    kwargs.setdefault("timeout", 600)
    kwargs.setdefault("cwd", REPO)
    result = subprocess.run(cmd, **kwargs)
    return result


def parse_astro_file(content):
    """
    Parse Astro content and return (success, output).

    Creates a temp file, runs the parser test on it, and returns whether
    parsing succeeded along with any output.
    """
    # Use the spec_test infrastructure to parse Astro content
    # We create a temp file in the fixtures directory
    fixture_dir = os.path.join(REPO, "crates/biome_html_parser/tests/html_specs/ok/astro")
    os.makedirs(fixture_dir, exist_ok=True)

    # Create temp file with unique name to avoid collisions
    fd, temp_path = tempfile.mkstemp(suffix=".astro", dir=fixture_dir)
    temp_name = os.path.basename(temp_path)
    try:
        with os.fdopen(fd, "w") as f:
            f.write(content)

        # Run parser tests - the spec_test will discover and parse this file
        r = run([
            "cargo", "test", "-p", "biome_html_parser",
            "html_specs::ok::astro", "--", "--test-threads=1"
        ])

        return r.returncode == 0, r.stdout + r.stderr
    finally:
        # Cleanup - remove temp file and any snapshot files created for it
        if os.path.exists(temp_path):
            os.remove(temp_path)
        # Remove any snapshot files that may have been created
        snap_path = temp_path + ".snap"
        if os.path.exists(snap_path):
            os.remove(snap_path)
        # Also remove new snapshots that match the temp file pattern
        for snap_file in glob.glob(os.path.join(fixture_dir, temp_name + "*.snap")):
            os.remove(snap_file)


class TestQuoteTrackerBug:
    """
    Fail-to-pass tests that verify the QuotesSeen lexer behavior fix.

    The bug: when parsing `const test = /\d{4}/`, the lexer incorrectly
    leaves non-empty quote state after the regex should close.

    On base commit: QuotesSeen.is_empty() returns FALSE (bug)
    After fix: QuotesSeen.is_empty() returns TRUE (correct)
    """

    def test_regex_with_escape_and_quantifier_parses(self):
        """
        Test that Astro frontmatter with regex literal containing escaped
        characters followed by quantifiers parses successfully.

        The source contains `/\d{4}/` - an escaped regex literal.
        The fix ensures the regex closes properly.
        """
        astro_content = """---
const RE = /\\d{4}/
---

<div />
"""
        success, output = parse_astro_file(astro_content)

        assert success, (
            f"Astro frontmatter with regex literal /\\d{{4}}/ must parse successfully. "
            f"The lexer fix allows escaped regexes with quantifiers to close properly.\n"
            f"Output: {output[-1000:]}"
        )

    def test_regex_with_multiple_escapes_parses(self):
        """
        Test that regexes with multiple escaped characters parse.
        E.g., `/\d{2}-\d{2}-\d{4}/` for date patterns.
        """
        astro_content = """---
const DATE_RE = /\\d{2}-\\d{2}-\\d{4}/
---

<span />
"""
        success, output = parse_astro_file(astro_content)

        assert success, (
            f"Astro frontmatter with complex regex literal must parse successfully.\n"
            f"Output: {output[-1000:]}"
        )

    def test_regex_with_escaped_slashes_parses(self):
        """
        Test that regexes with escaped slashes parse correctly.
        E.g., `/\/path\//` - regex matching paths.
        """
        astro_content = """---
const PATH_RE = /\\/path\\//
---

<p>Test</p>
"""
        success, output = parse_astro_file(astro_content)

        assert success, (
            f"Astro frontmatter with escaped slashes in regex must parse successfully.\n"
            f"Output: {output[-1000:]}"
        )

    def test_simple_regex_without_escapes_still_works(self):
        """
        Regression test: ensure simple regexes without escapes still work.
        E.g., `/[a-z]+/` - basic character class.
        """
        astro_content = """---
const SIMPLE_RE = /[a-z]+/
---

<a />
"""
        success, output = parse_astro_file(astro_content)

        assert success, (
            f"Simple regex literals without escapes must continue to parse.\n"
            f"Output: {output[-1000:]}"
        )

    def test_lexer_unit_tests_pass(self):
        """
        Verify the lexer's QuotesSeen unit tests all pass.
        These tests directly exercise the regex/quote tracking logic.
        """
        r = run([
            "cargo", "test", "-p", "biome_html_parser",
            "lexer::quotes_seen", "--"
        ])

        assert r.returncode == 0, (
            f"Lexer quotes_seen unit tests must all pass. "
            f"These verify the core quote tracking behavior is correct.\n"
            f"stderr: {r.stderr[-1000:]}"
        )


class TestRepoCI:
    """Pass-to-pass: repo's own CI tests must continue to pass."""

    def test_html_parser_tests(self):
        """
        Pass-to-pass: All biome_html_parser tests must pass.
        This ensures no regressions in the broader HTML parser.
        """
        r = run(["cargo", "test", "-p", "biome_html_parser"])
        assert r.returncode == 0, (
            f"biome_html_parser tests failed.\n"
            f"stderr: {r.stderr[-1000:]}"
        )

    def test_cargo_check(self):
        """
        Pass-to-pass: cargo check must succeed (compiles without errors).
        """
        r = run(["cargo", "check", "-p", "biome_html_parser"])
        assert r.returncode == 0, (
            f"cargo check failed.\n"
            f"stderr: {r.stderr[-1000:]}"
        )

    def test_clippy_html_parser(self):
        """
        Pass-to-pass: clippy passes on biome_html_parser (CI lint step).
        This is the same lint check run by the PR workflow's lint job.
        """
        r = run(["cargo", "clippy", "-p", "biome_html_parser", "--", "-D", "warnings"])
        assert r.returncode == 0, (
            f"clippy failed on biome_html_parser.\n"
            f"stderr: {r.stderr[-1000:]}"
        )
