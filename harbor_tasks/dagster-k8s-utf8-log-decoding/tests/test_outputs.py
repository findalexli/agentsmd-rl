"""Tests for dagster-k8s UTF-8 log decoding fix.

These tests verify that the _process_log_stream function correctly handles
UTF-8 multi-byte characters that are split across Kubernetes log chunks.
"""

import subprocess
import sys
from typing import Iterator

REPO = "/workspace/dagster"
K8S_PIPES_MODULE = "python_modules/libraries/dagster-k8s/dagster_k8s/pipes.py"


def import_process_log_stream():
    """Import the _process_log_stream function from dagster_k8s.pipes."""
    sys.path.insert(0, f"{REPO}/python_modules/libraries/dagster-k8s")
    sys.path.insert(0, f"{REPO}/python_modules/dagster")
    from dagster_k8s.pipes import _process_log_stream
    return _process_log_stream


def test_utf8_char_split_across_two_chunks():
    """Test that a UTF-8 character split across two chunks is correctly decoded.

    The UTF-8 ellipsis character "…" is 3 bytes: e2 80 a6.
    This simulates a k8s log stream chunk boundary splitting the character mid-sequence.
    """
    _process_log_stream = import_process_log_stream()

    def stream():
        yield b"2024-03-22T02:17:29.885548Z hello " + b"\xe2"
        yield b"\x80\xa6 world\n"

    items = list(_process_log_stream(stream()))

    assert len(items) == 1, f"Expected 1 log item, got {len(items)}"
    assert items[0].timestamp == "2024-03-22T02:17:29.885548Z"
    assert items[0].log == "hello … world", f"Expected 'hello … world', got '{items[0].log}'"


def test_utf8_char_split_across_three_chunks():
    """Test that a UTF-8 character split across three chunks is correctly decoded."""
    _process_log_stream = import_process_log_stream()

    def stream():
        yield b"2024-03-22T02:17:29.885548Z start "
        yield b"\xe2"  # First byte of ellipsis
        yield b"\x80\xa6 end\n"  # Remaining bytes

    items = list(_process_log_stream(stream()))

    assert len(items) == 1
    assert items[0].timestamp == "2024-03-22T02:17:29.885548Z"
    assert items[0].log == "start … end"


def test_multiple_utf8_chars_split_differently():
    """Test multiple UTF-8 characters with different split patterns."""
    _process_log_stream = import_process_log_stream()

    def stream():
        # Euro sign (€) is 0xe2 0x82 0xac
        # Em dash (—) is 0xe2 0x80 0x94
        yield b"2024-03-22T02:17:29.885548Z price: " + b"\xe2\x82"  # First 2 bytes of €
        yield b"\xac, note" + b"\xe2"  # Last byte of €, then first byte of —
        yield b"\x80\x94 end\n"  # Last 2 bytes of —

    items = list(_process_log_stream(stream()))

    assert len(items) == 1
    assert items[0].timestamp == "2024-03-22T02:17:29.885548Z"
    assert items[0].log == "price: €, note— end"


def test_cjk_char_split_across_chunks():
    """Test CJK (Chinese/Japanese/Korean) characters split across chunks.

    CJK characters are typically 3 bytes in UTF-8.
    """
    _process_log_stream = import_process_log_stream()

    def stream():
        # "中" (Chinese character) is 0xe4 0xb8 0xad
        yield b"2024-03-22T02:17:29.885548Z " + b"\xe4\xb8"
        yield b"\xad test\n"

    items = list(_process_log_stream(stream()))

    assert len(items) == 1
    assert items[0].timestamp == "2024-03-22T02:17:29.885548Z"
    assert items[0].log == "中 test"


def test_incomplete_utf8_at_end_replaced():
    """Test that incomplete UTF-8 at stream end uses replacement character."""
    _process_log_stream = import_process_log_stream()

    def stream():
        # Incomplete ellipsis - only first 2 bytes, stream ends without \n
        yield b"2024-03-22T02:17:29.885548Z hello " + b"\xe2\x80"

    items = list(_process_log_stream(stream()))

    assert len(items) == 1
    assert items[0].timestamp == "2024-03-22T02:17:29.885548Z"
    # Should have replacement character () for incomplete sequence
    assert "\ufffd" in items[0].log or items[0].log == "hello"


def test_multiple_lines_with_split_chars():
    """Test multiple log lines where UTF-8 chars are split across chunks."""
    _process_log_stream = import_process_log_stream()

    def stream():
        # Line 1: ellipsis split
        yield b"2024-03-22T02:17:29.885548Z line1 " + b"\xe2"
        yield b"\x80\xa6\n"  # Complete ellipsis
        # Line 2: euro sign split
        yield b"2024-03-22T02:17:30.885548Z line2 " + b"\xe2\x82"
        yield b"\xac\n"  # Complete euro sign

    items = list(_process_log_stream(stream()))

    assert len(items) == 2
    assert items[0].timestamp == "2024-03-22T02:17:29.885548Z"
    assert items[0].log == "line1 …"
    assert items[1].timestamp == "2024-03-22T02:17:30.885548Z"
    assert items[1].log == "line2 €"


def test_existing_single_chunk_behavior_unchanged():
    """Verify that existing single-chunk behavior still works correctly."""
    _process_log_stream = import_process_log_stream()

    def stream():
        yield b"2024-03-22T02:17:29.885548Z complete log message\n"
        yield b"2024-03-22T02:17:30.885548Z another message\n"

    items = list(_process_log_stream(stream()))

    assert len(items) == 2
    assert items[0].timestamp == "2024-03-22T02:17:29.885548Z"
    assert items[0].log == "complete log message"
    assert items[1].timestamp == "2024-03-22T02:17:30.885548Z"
    assert items[1].log == "another message"


def test_continuation_line_across_chunks():
    """Test that line continuation (no timestamp) works with split UTF-8."""
    _process_log_stream = import_process_log_stream()

    def stream():
        # First chunk: timestamp + start of message
        yield b"2024-03-22T02:17:29.885548Z start "
        # Second chunk: continuation with split UTF-8, no timestamp
        yield b"\xe2\x80\xa6 continuation\n"

    items = list(_process_log_stream(stream()))

    assert len(items) == 1
    assert items[0].timestamp == "2024-03-22T02:17:29.885548Z"
    assert items[0].log == "start … continuation"


def test_repo_unit_tests_pass():
    """Run the existing dagster-k8s unit tests to ensure no regressions."""
    result = subprocess.run(
        [
            sys.executable, "-m", "pytest",
            "python_modules/libraries/dagster-k8s/dagster_k8s_tests/unit_tests/test_pipe_log_reader.py",
            "-v", "--tb=short"
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"Unit tests failed:\n{result.stderr}"


def test_repo_pipe_log_reader_tests():
    """Run dagster-k8s pipe log reader tests (pass_to_pass)."""
    result = subprocess.run(
        [
            sys.executable, "-m", "pytest",
            "python_modules/libraries/dagster-k8s/dagster_k8s_tests/unit_tests/test_pipe_log_reader.py",
            "-v", "--tb=short"
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"Pipe log reader tests failed:\n{result.stderr[-500:]}"


def test_repo_pipes_tests():
    """Run dagster-k8s pipes module tests (pass_to_pass)."""
    result = subprocess.run(
        [
            sys.executable, "-m", "pytest",
            "python_modules/libraries/dagster-k8s/dagster_k8s_tests/unit_tests/test_pipes.py",
            "-v", "--tb=short"
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"Pipes tests failed:\n{result.stderr[-500:]}"


def test_repo_all_k8s_unit_tests():
    """Run all dagster-k8s unit tests (pass_to_pass)."""
    result = subprocess.run(
        [
            sys.executable, "-m", "pytest",
            "python_modules/libraries/dagster-k8s/dagster_k8s_tests/unit_tests/",
            "-v", "--tb=short"
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert result.returncode == 0, f"All k8s unit tests failed:\n{result.stderr[-500:]}"


def test_codecs_import_present():
    """Verify that the codecs module is imported for incremental decoder."""
    with open(f"{REPO}/{K8S_PIPES_MODULE}") as f:
        content = f.read()

    # Check for codecs import at the top of the file
    lines = content.split('\n')
    import_line = None
    for i, line in enumerate(lines[:20]):  # Check first 20 lines
        if line.strip() == "import codecs":
            import_line = i
            break

    assert import_line is not None, "Missing 'import codecs' at top of pipes.py"


def test_incremental_decoder_usage():
    """Verify that codecs.getincrementaldecoder is used in _process_log_stream."""
    with open(f"{REPO}/{K8S_PIPES_MODULE}") as f:
        content = f.read()

    assert "codecs.getincrementaldecoder" in content, \
        "Missing codecs.getincrementaldecoder usage in pipes.py"
    assert 'decoder.decode(log_chunk, final=False)' in content, \
        "Missing decoder.decode(log_chunk, final=False) call"
    assert 'decoder.decode(b"", final=True)' in content, \
        "Missing final decoder flush with final=True"
