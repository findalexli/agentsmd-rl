"""
Tests for the CommsDecoder thread safety fix.

This tests the fix for apache/airflow#64894 where _get_response() was called
outside the thread lock in CommsDecoder.send(), causing race conditions.
"""
import subprocess
import sys
import threading
import time
from pathlib import Path
from socket import socketpair

import pytest

REPO = Path("/workspace/airflow")


class TestConcurrentSendBehavior:
    """
    Verify that concurrent send() calls don't return crossed responses.

    The bug: _get_response() was called outside the thread lock, so concurrent
    threads could get each other's responses. Each _RequestFrame has a unique
    id that the server echoes back in _ResponseFrame.id for correlation.
    """

    def test_concurrent_sends_no_crossed_responses(self):
        """
        Verify that concurrent send() calls return correct responses.

        Two threads send requests concurrently with distinct keys.
        The responses must not get crossed - each thread must receive
        its own response (verified via the frame id correlation).
        """
        import msgspec
        import structlog
        from airflow.sdk.execution_time.comms import (
            CommsDecoder,
            VariableResult,
            _RequestFrame,
            _ResponseFrame,
        )

        r, w = socketpair()
        r.settimeout(10.0)

        decoder = CommsDecoder(socket=r, log=structlog.get_logger())

        num_threads = 2
        results = {}
        errors = []
        lock = threading.Lock()

        def feeder():
            """Send responses with unique IDs that match the requests."""
            for i in range(num_threads):
                time.sleep(0.05)  # Let both threads enter send() first
                resp = _ResponseFrame(
                    id=i,  # Echo back the request ID for correlation
                    body={"type": "VariableResult", "key": f"key_{i}", "value": f"value_{i}"},
                    error=None,
                )
                data = msgspec.msgpack.encode(resp)
                w.sendall(len(data).to_bytes(4, byteorder="big") + data)

        def sender(thread_id):
            """Send a request and record the response id and data."""
            try:
                key = f"key_{thread_id}"
                value = f"value_{thread_id}"
                resp = decoder.send(VariableResult(key=key, value=value, type="VariableResult"))
                with lock:
                    results[thread_id] = resp
            except Exception as e:
                with lock:
                    errors.append((thread_id, e))

        feeder_thread = threading.Thread(target=feeder)
        feeder_thread.start()

        threads = []
        for i in range(num_threads):
            t = threading.Thread(target=sender, args=(i,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join(timeout=10)

        feeder_thread.join(timeout=1)

        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == num_threads, f"Expected {num_threads} results, got {len(results)}"

        for i in range(num_threads):
            assert results[i] is not None, f"Thread {i} got None response"
            assert results[i].key == f"key_{i}", (
                f"Thread {i} got crossed response: expected key 'key_{i}', got '{results[i].key}'"
            )
            assert results[i].value == f"value_{i}", (
                f"Thread {i} got crossed response: expected value 'value_{i}', got '{results[i].value}'"
            )

        r.close()
        w.close()

    def test_multiple_concurrent_sends_no_errors(self):
        """
        Multiple concurrent sends should all complete without exceptions.
        """
        import structlog
        from socket import socketpair
        from airflow.sdk.execution_time.comms import CommsDecoder, VariableResult, _ResponseFrame
        import msgspec

        r, w = socketpair()
        r.settimeout(10.0)

        decoder = CommsDecoder(socket=r, log=structlog.get_logger())

        num_threads = 4
        results = {}
        errors = []
        lock = threading.Lock()

        def feeder():
            for i in range(num_threads):
                time.sleep(0.02)
                resp = _ResponseFrame(
                    id=i,
                    body={"type": "VariableResult", "key": f"key_{i}", "value": f"value_{i}"},
                    error=None,
                )
                data = msgspec.msgpack.encode(resp)
                w.sendall(len(data).to_bytes(4, byteorder="big") + data)

        def sender(thread_id):
            try:
                resp = decoder.send(VariableResult(key=f"key_{thread_id}", value=f"value_{thread_id}", type="VariableResult"))
                with lock:
                    results[thread_id] = resp
            except Exception as e:
                with lock:
                    errors.append((thread_id, e))

        feeder_thread = threading.Thread(target=feeder)
        feeder_thread.start()

        threads = []
        for i in range(num_threads):
            t = threading.Thread(target=sender, args=(i,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join(timeout=10)

        feeder_thread.join(timeout=1)

        assert len(errors) == 0, f"Errors occurred during concurrent sends: {errors}"
        assert len(results) == num_threads, f"Expected {num_threads} results, got {len(results)}"

        r.close()
        w.close()


class TestCommsDecoderBasic:
    """Basic tests for CommsDecoder functionality."""

    def test_single_send_receive(self):
        """A single send/receive operation works correctly."""
        import msgspec
        import structlog
        from airflow.sdk.execution_time.comms import (
            CommsDecoder,
            VariableResult,
            _ResponseFrame,
        )

        r, w = socketpair()
        # Set socket timeout to avoid hanging
        r.settimeout(5.0)

        decoder = CommsDecoder(socket=r, log=structlog.get_logger())

        def send_response():
            time.sleep(0.01)
            resp = {"type": "VariableResult", "key": "test_key", "value": "test_value"}
            frame = _ResponseFrame(0, resp, None)
            data = msgspec.msgpack.encode(frame)
            w.sendall(len(data).to_bytes(4, byteorder="big") + data)

        sender_thread = threading.Thread(target=send_response)
        sender_thread.start()

        msg = VariableResult(key="test_key", value="test_value", type="VariableResult")
        result = decoder.send(msg)

        sender_thread.join(timeout=2)

        assert result is not None, "No result received"
        assert result.key == "test_key", f"Wrong key: {result.key}"
        assert result.value == "test_value", f"Wrong value: {result.value}"

        r.close()
        w.close()

    def test_multiple_sequential_sends(self):
        """Multiple sequential sends work correctly with varying inputs."""
        import msgspec
        import structlog
        from airflow.sdk.execution_time.comms import (
            CommsDecoder,
            VariableResult,
            _ResponseFrame,
        )

        r, w = socketpair()
        r.settimeout(5.0)

        decoder = CommsDecoder(socket=r, log=structlog.get_logger())

        test_cases = [
            ("key_alpha", "value_alpha"),
            ("key_beta", "value_beta"),
            ("key_gamma", "value_gamma"),
        ]

        for i, (key, value) in enumerate(test_cases):
            def send_response(idx, k, v):
                time.sleep(0.01)
                resp = {"type": "VariableResult", "key": k, "value": v}
                frame = _ResponseFrame(idx, resp, None)
                data = msgspec.msgpack.encode(frame)
                w.sendall(len(data).to_bytes(4, byteorder="big") + data)

            sender_thread = threading.Thread(target=send_response, args=(i, key, value))
            sender_thread.start()

            msg = VariableResult(key=key, value=value, type="VariableResult")
            result = decoder.send(msg)

            sender_thread.join(timeout=2)

            assert result is not None, f"No result for {key}"
            assert result.key == key, f"Wrong key for {key}: got {result.key}"
            assert result.value == value, f"Wrong value for {key}: got {result.value}"

        r.close()
        w.close()


class TestRepoTests:
    """Run the repository's own tests as pass_to_pass checks."""

    def test_comms_module_imports(self):
        """Verify the comms module imports without errors."""
        from airflow.sdk.execution_time.comms import (
            CommsDecoder,
            _RequestFrame,
            _ResponseFrame,
        )
        assert CommsDecoder is not None
        assert _RequestFrame is not None
        assert _ResponseFrame is not None

    def test_comms_decoder_instantiation(self):
        """Verify CommsDecoder can be instantiated with basic attributes."""
        import structlog
        from socket import socketpair
        from airflow.sdk.execution_time.comms import CommsDecoder

        r, w = socketpair()
        decoder = CommsDecoder(socket=r, log=structlog.get_logger())

        # Verify basic attributes exist
        assert hasattr(decoder, '_thread_lock')
        assert hasattr(decoder, '_async_lock')
        assert hasattr(decoder, 'send')
        assert hasattr(decoder, 'asend')

        r.close()
        w.close()

    def test_repo_ruff_check(self):
        """Repo's ruff linter passes on comms.py (pass_to_pass)."""
        # Install ruff first
        install = subprocess.run(
            ["pip", "install", "--quiet", "ruff"],
            capture_output=True, text=True, timeout=120, cwd=REPO,
        )
        assert install.returncode == 0, f"Failed to install ruff: {install.stderr}"

        # Run ruff lint check
        r = subprocess.run(
            ["ruff", "check", "task-sdk/src/airflow/sdk/execution_time/comms.py"],
            capture_output=True, text=True, timeout=60, cwd=REPO,
        )
        assert r.returncode == 0, f"Ruff lint failed:\n{r.stdout}\n{r.stderr}"

    def test_repo_ruff_format_check(self):
        """Repo's ruff format check passes on comms.py (pass_to_pass)."""
        # Install ruff first
        install = subprocess.run(
            ["pip", "install", "--quiet", "ruff"],
            capture_output=True, text=True, timeout=120, cwd=REPO,
        )
        assert install.returncode == 0, f"Failed to install ruff: {install.stderr}"

        # Run ruff format check
        r = subprocess.run(
            ["ruff", "format", "--check", "task-sdk/src/airflow/sdk/execution_time/comms.py"],
            capture_output=True, text=True, timeout=60, cwd=REPO,
        )
        assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout}\n{r.stderr}"

    def test_repo_comms_models_tests(self):
        """Repo's own comms model tests pass (pass_to_pass)."""
        # Install pytest-asyncio first (needed by repo's tests)
        install = subprocess.run(
            ["pip", "install", "--quiet", "pytest-asyncio"],
            capture_output=True, text=True, timeout=120, cwd=REPO,
        )
        assert install.returncode == 0, f"Failed to install pytest-asyncio: {install.stderr}"

        # Run the repo's TestCommsModels tests (works without conftest fixtures)
        r = subprocess.run(
            ["python", "-m", "pytest",
             "task-sdk/tests/task_sdk/execution_time/test_comms.py::TestCommsModels",
             "--noconftest", "-v", "--tb=short"],
            capture_output=True, text=True, timeout=120, cwd=REPO,
        )
        assert r.returncode == 0, f"Repo comms model tests failed:\n{r.stdout}\n{r.stderr[-1000:]}"

    def test_repo_comms_decoder_huge_payload_test(self):
        """Repo's huge payload test passes (pass_to_pass)."""
        # Install pytest-asyncio first (needed by repo's tests)
        install = subprocess.run(
            ["pip", "install", "--quiet", "pytest-asyncio"],
            capture_output=True, text=True, timeout=120, cwd=REPO,
        )
        assert install.returncode == 0, f"Failed to install pytest-asyncio: {install.stderr}"

        # Run the repo's huge_payload test (works without conftest fixtures)
        r = subprocess.run(
            ["python", "-m", "pytest",
             "task-sdk/tests/task_sdk/execution_time/test_comms.py::TestCommsDecoder::test_huge_payload",
             "--noconftest", "-v", "--tb=short"],
            capture_output=True, text=True, timeout=120, cwd=REPO,
        )
        assert r.returncode == 0, f"Repo huge payload test failed:\n{r.stdout}\n{r.stderr[-1000:]}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])