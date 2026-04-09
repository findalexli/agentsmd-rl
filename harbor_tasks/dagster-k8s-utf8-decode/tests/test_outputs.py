"""Tests for dagster-k8s UTF-8 log stream decoding fix.

This verifies that the _process_log_stream function correctly handles:
1. UTF-8 multi-byte characters split across log chunks
2. Invalid byte sequences (replaced, not crashed)
3. Standard log streaming behavior
"""

import subprocess
import sys
import os

# Path to the cloned dagster repository
REPO = "/workspace/dagster"

# Add the dagster-k8s package to the path
sys.path.insert(0, "/workspace/dagster/python_modules/libraries/dagster-k8s")

from dagster_k8s.pipes import _process_log_stream, LogItem


class TestUtf8SplitAcrossChunks:
    """Test the core bug fix: UTF-8 characters split across k8s log chunks."""

    def test_ellipsis_split_across_two_chunks(self):
        """UTF-8 ellipsis '…' (e2 80 a6) split between chunks."""
        def stream():
            yield b"2024-03-22T02:17:29.885548Z hello " + b"\xe2"
            yield b"\x80\xa6 world\n"

        items = list(_process_log_stream(stream()))

        assert len(items) == 1
        assert items[0].timestamp == "2024-03-22T02:17:29.885548Z"
        assert items[0].log == "hello … world"

    def test_ellipsis_split_three_ways(self):
        """UTF-8 ellipsis split across three separate chunks."""
        def stream():
            yield b"2024-03-22T02:17:29.885548Z hello " + b"\xe2"
            yield b"\x80"
            yield b"\xa6 world\n"

        items = list(_process_log_stream(stream()))

        assert len(items) == 1
        assert items[0].log == "hello … world"

    def test_multiple_unicode_chars_split(self):
        """Multiple multi-byte chars (emoji) split across chunks."""
        # Emoji 😀 is f0 9f 98 80 (4 bytes)
        def stream():
            yield b"2024-03-22T02:17:29.885548Z " + b"\xf0"
            yield b"\x9f\x98\x80 smile\n"

        items = list(_process_log_stream(stream()))

        assert len(items) == 1
        assert items[0].log == "😀 smile"

    def test_split_character_at_chunk_boundary(self):
        """Character boundary exactly at the chunk split point."""
        # Japanese 日本語 - each char is 3 bytes in UTF-8
        # 日 = e6 97 a5, 本 = e6 9c ac, 語 = e8 aa 9e
        def stream():
            yield b"2024-03-22T02:17:29.885548Z " + b"\xe6\x97\xa5"  # 日
            yield b"\xe6\x9c\xac\xe8\xaa\x9e\n"  # 本語

        items = list(_process_log_stream(stream()))

        assert len(items) == 1
        assert items[0].log == "日本語"


class TestInvalidByteHandling:
    """Test that invalid bytes are handled gracefully with 'replace' error handling."""

    def test_invalid_bytes_replaced_not_crashed(self):
        """Invalid UTF-8 sequences should be replaced, not cause crashes."""
        def stream():
            # Invalid byte sequence (0xff is never valid in UTF-8)
            yield b"2024-03-22T02:17:29.885548Z hello " + b"\xff\xfe world\n"

        items = list(_process_log_stream(stream()))

        assert len(items) == 1
        assert items[0].timestamp == "2024-03-22T02:17:29.885548Z"
        # Should contain replacement characters () instead of crashing
        assert "" in items[0].log or "hello" in items[0].log

    def test_incomplete_sequence_at_end_replaced(self):
        """Incomplete UTF-8 sequence at stream end should be replaced/decoded."""
        def stream():
            # Start of 3-byte sequence (e2 80 ...) but never complete it
            yield b"2024-03-22T02:17:29.885548Z hello " + b"\xe2"
            yield b"\x80"  # Incomplete - missing third byte

        # Note: stream doesn't end with newline, but decoder should flush
        items = list(_process_log_stream(stream()))

        # Should handle gracefully without crashing - decoder flushes on final=True
        # Result should either have replacement chars or be a valid string
        assert isinstance(items, list)


class TestStandardLogStreaming:
    """Test that standard log streaming behavior still works correctly."""

    def test_single_complete_line(self):
        """A single complete log line parses correctly."""
        def stream():
            yield b"2024-03-22T02:17:29.885548Z hello world\n"

        items = list(_process_log_stream(stream()))

        assert len(items) == 1
        assert items[0].timestamp == "2024-03-22T02:17:29.885548Z"
        assert items[0].log == "hello world"

    def test_multiple_lines_in_one_chunk(self):
        """Multiple log lines in a single chunk parse correctly."""
        def stream():
            yield b"2024-03-22T02:17:29.885548Z first line\n2024-03-22T02:17:30.123456Z second line\n"

        items = list(_process_log_stream(stream()))

        assert len(items) == 2
        assert items[0].timestamp == "2024-03-22T02:17:29.885548Z"
        assert items[0].log == "first line"
        assert items[1].timestamp == "2024-03-22T02:17:30.123456Z"
        assert items[1].log == "second line"

    def test_continuation_line_no_timestamp(self):
        """Lines without timestamps are continuations of previous lines."""
        def stream():
            yield b"2024-03-22T02:17:29.885548Z first part\ncontinuation line\n"

        items = list(_process_log_stream(stream()))

        assert len(items) == 1
        assert items[0].log == "first part\ncontinuation line"

    def test_same_timestamp_multiple_lines(self):
        """Multiple lines with same timestamp are joined with newlines."""
        def stream():
            yield b"2024-03-22T02:17:29.885548Z first message\n"
            yield b"2024-03-22T02:17:29.885548Z second message\n"

        items = list(_process_log_stream(stream()))

        assert len(items) == 2
        assert items[0].log == "first message"
        assert items[1].log == "second message"

    def test_empty_stream(self):
        """Empty stream produces no items."""
        def stream():
            return
            yield  # Make it a generator

        items = list(_process_log_stream(stream()))
        assert len(items) == 0


class TestEdgeCases:
    """Edge cases and boundary conditions."""

    def test_line_split_without_newline_at_end(self):
        """Line split across chunks without final newline."""
        def stream():
            yield b"2024-03-22T02:17:29.885548Z part1"
            yield b" part2"  # No newline

        items = list(_process_log_stream(stream()))

        # Should still emit the final item
        assert len(items) == 1
        assert items[0].log == "part1 part2"

    def test_many_small_chunks(self):
        """Many small chunks don't break parsing."""
        def stream():
            yield b"2024-03-22T02:17:29.885548Z "
            yield b"h"
            yield b"e"
            yield b"l"
            yield b"l"
            yield b"o"
            yield b"\n"

        items = list(_process_log_stream(stream()))

        assert len(items) == 1
        assert items[0].log == "hello"

    def test_mixed_ascii_and_unicode_split(self):
        """Mix of ASCII and unicode split across chunks."""
        def stream():
            yield b"2024-03-22T02:17:29.885548Z ASCII " + b"\xc3\xa9"  # é
            yield b" more " + b"\xc3\xa0"  # à
            yield b"\n"

        items = list(_process_log_stream(stream()))

        assert len(items) == 1
        assert "ASCII" in items[0].log
        assert "more" in items[0].log


# =============================================================================
# PASS-TO-PASS TESTS - Verify existing repo CI checks pass on base and after fix
# =============================================================================

class TestRepoPassToPass:
    """Repo CI checks that should pass both on base commit and after the fix."""

    def test_dagster_k8s_unit_tests(self):
        """dagster-k8s unit tests pass (pass_to_pass)."""
        r = subprocess.run(
            ["python", "-m", "pytest", "dagster_k8s_tests/unit_tests/", "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=os.path.join(REPO, "python_modules/libraries/dagster-k8s"),
        )
        assert r.returncode == 0, f"Unit tests failed:\n{r.stdout[-2000:]}\n{r.stderr[-500:]}"

    def test_dagster_k8s_pipes_module_tests(self):
        """dagster-k8s pipes module unit tests pass (pass_to_pass)."""
        r = subprocess.run(
            ["python", "-m", "pytest", "dagster_k8s_tests/unit_tests/test_pipes.py", "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=os.path.join(REPO, "python_modules/libraries/dagster-k8s"),
        )
        assert r.returncode == 0, f"Pipes tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"

    def test_dagster_k8s_imports_cleanly(self):
        """dagster-k8s module imports without errors (pass_to_pass)."""
        r = subprocess.run(
            ["python", "-c", "import dagster_k8s; print('OK')"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=os.path.join(REPO, "python_modules/libraries/dagster-k8s"),
        )
        assert r.returncode == 0, f"Import failed:\n{r.stderr[-500:]}"
        assert "OK" in r.stdout, f"Import did not print OK: {r.stdout}"
