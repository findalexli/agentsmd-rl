"""
Test suite for Airflow CommsDecoder thread-safety fix.

This tests that the send() method in CommsDecoder properly holds the thread lock
when calling _get_response(), preventing race conditions where responses can be
read out of order.
"""

import sys
import threading
from socket import socketpair

sys.path.insert(0, "/workspace/airflow/task-sdk/src")

import msgspec
import structlog

from airflow.sdk.execution_time.comms import CommsDecoder, VariableResult, _ResponseFrame


def test_send_thread_safety_race_condition():
    """
    Test that concurrent sends from multiple threads receive correct responses.

    This is a fail-to-pass test: on the buggy code, _get_response() is called
    outside the thread_lock, causing a race where responses can be swapped
    between threads. On the fixed code, the lock ensures proper ordering.
    """
    r, w = socketpair()
    decoder = CommsDecoder(socket=r, log=structlog.get_logger())

    num_threads = 5
    results = [None] * num_threads
    errors = [None] * num_threads
    request_sent = [threading.Event() for _ in range(num_threads)]

    def send_and_store(idx):
        """Send a message with unique key/value and store the response."""
        request_sent[idx].set()
        try:
            msg = VariableResult(key=f"key{idx}", value=f"value{idx}", type="VariableResult")
            results[idx] = decoder.send(msg)
        except Exception as e:
            errors[idx] = e

    # Create and start threads
    threads = [threading.Thread(target=send_and_store, args=(i,)) for i in range(num_threads)]
    for t in threads:
        t.start()

    # For each thread, wait until it signals it's ready, then send the matching response
    for idx in range(num_threads):
        request_sent[idx].wait()
        resp = {"type": "VariableResult", "key": f"key{idx}", "value": f"value{idx}"}
        frame = _ResponseFrame(idx, resp, None)
        data = msgspec.msgpack.encode(frame)
        w.sendall(len(data).to_bytes(4, byteorder="big") + data)

    # Wait for all threads to complete
    for t in threads:
        t.join(timeout=5)

    # Verify no threads are still running (deadlock check)
    for idx, t in enumerate(threads):
        assert not t.is_alive(), f"Thread {idx} did not finish (possible deadlock in send method)"

    # Verify no errors occurred
    for idx in range(num_threads):
        assert errors[idx] is None, f"Thread {idx} raised an error: {errors[idx]}"

    # Verify each thread got its CORRECT response (anti-stub: checking actual values)
    # On buggy code, responses can be swapped due to race condition
    for idx in range(num_threads):
        assert results[idx] is not None, f"Thread {idx} received no response"
        assert results[idx].key == f"key{idx}", (
            f"Thread {idx} got wrong key: expected 'key{idx}', got '{results[idx].key}'. "
            f"This indicates a race condition where responses were read out of order."
        )
        assert results[idx].value == f"value{idx}", (
            f"Thread {idx} got wrong value: expected 'value{idx}', got '{results[idx].value}'"
        )


def test_send_thread_safety_multiple_iterations():
    """
    Run the thread-safety test multiple times to increase chance of catching race conditions.

    Race conditions may not trigger 100% of the time, so we run multiple iterations
    with varying numbers of threads to stress-test the locking behavior.
    """
    for num_threads in [3, 5, 7]:
        r, w = socketpair()
        decoder = CommsDecoder(socket=r, log=structlog.get_logger())

        results = [None] * num_threads
        errors = [None] * num_threads
        request_sent = [threading.Event() for _ in range(num_threads)]

        def send_and_store(idx):
            request_sent[idx].set()
            try:
                # Vary the message content across iterations
                msg = VariableResult(
                    key=f"thread{idx}_iter{num_threads}",
                    value=f"value{idx}_{num_threads}",
                    type="VariableResult"
                )
                results[idx] = decoder.send(msg)
            except Exception as e:
                errors[idx] = e

        threads = [threading.Thread(target=send_and_store, args=(i,)) for i in range(num_threads)]
        for t in threads:
            t.start()

        for idx in range(num_threads):
            request_sent[idx].wait()
            resp = {
                "type": "VariableResult",
                "key": f"thread{idx}_iter{num_threads}",
                "value": f"value{idx}_{num_threads}"
            }
            frame = _ResponseFrame(idx, resp, None)
            data = msgspec.msgpack.encode(frame)
            w.sendall(len(data).to_bytes(4, byteorder="big") + data)

        for t in threads:
            t.join(timeout=5)

        for idx, t in enumerate(threads):
            assert not t.is_alive(), f"Thread {idx} did not finish with {num_threads} threads"

        for idx in range(num_threads):
            assert errors[idx] is None, f"Error in thread {idx} with {num_threads} threads: {errors[idx]}"
            assert results[idx] is not None, f"No response in thread {idx} with {num_threads} threads"
            expected_key = f"thread{idx}_iter{num_threads}"
            expected_value = f"value{idx}_{num_threads}"
            assert results[idx].key == expected_key, (
                f"Key mismatch in thread {idx} with {num_threads} threads: "
                f"expected '{expected_key}', got '{results[idx].key}'"
            )
            assert results[idx].value == expected_value, (
                f"Value mismatch in thread {idx} with {num_threads} threads: "
                f"expected '{expected_value}', got '{results[idx].value}'"
            )


def test_send_single_thread_still_works():
    """
    Verify that single-threaded usage still works correctly after the fix.
    This is a pass-to-pass test to ensure we didn't break normal operation.
    """
    r, w = socketpair()
    decoder = CommsDecoder(socket=r, log=structlog.get_logger())

    # Send multiple messages sequentially from the same thread
    for i in range(3):
        msg = VariableResult(key=f"single{i}", value=f"val{i}", type="VariableResult")

        # Send response in a separate thread to avoid blocking
        def send_response():
            resp = {"type": "VariableResult", "key": f"single{i}", "value": f"val{i}"}
            frame = _ResponseFrame(i, resp, None)
            data = msgspec.msgpack.encode(frame)
            w.sendall(len(data).to_bytes(4, byteorder="big") + data)

        # Start response sender before calling send (to avoid deadlock in single thread)
        import threading
        responder = threading.Thread(target=send_response)
        responder.start()

        result = decoder.send(msg)
        responder.join(timeout=2)

        assert result is not None, f"Iteration {i}: No response received"
        assert result.key == f"single{i}", f"Iteration {i}: Key mismatch"
        assert result.value == f"val{i}", f"Iteration {i}: Value mismatch"
