"""
Task: gradio-sync-generator-cancel-valueerror
Repo: gradio-app/gradio @ a09c0e891709e007e4f265fc48f466175f5a2a22
PR:   13134

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import asyncio
import sys
import time
import threading

sys.path.insert(0, "/workspace/gradio")

REPO = "/workspace/gradio"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class FakeIterator:
    """Iterator whose close() fails N times with ValueError before succeeding."""

    def __init__(self, fail_count=0):
        self.close_call_count = 0
        self._fail_count = fail_count
        self._closed = False

    def close(self):
        self.close_call_count += 1
        if self.close_call_count <= self._fail_count:
            raise ValueError("generator already executing")
        self._closed = True

    def __next__(self):
        raise StopIteration

    def __iter__(self):
        return self


class RacingIterator:
    """Iterator that is 'executing' for a set duration, simulating a real race."""

    def __init__(self, fail_for_ms=50):
        self._closed = False
        self._lock = threading.Lock()
        self.fail_until = time.monotonic() + (fail_for_ms / 1000)

    def close(self):
        with self._lock:
            if time.monotonic() < self.fail_until:
                raise ValueError("generator already executing")
            self._closed = True

    def __next__(self):
        return "item"

    def __iter__(self):
        return self


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """gradio/utils.py must parse without syntax errors."""
    import py_compile
    py_compile.compile(f"{REPO}/gradio/utils.py", doraise=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_aclose_retries_on_already_executing():
    """aclose() retries when close() raises ValueError('generator already executing')."""
    from gradio.utils import SyncToAsyncIterator

    fake = FakeIterator(fail_count=2)
    iterator = SyncToAsyncIterator(fake, limiter=None)

    asyncio.run(iterator.aclose(retry_interval=0.01, timeout=5.0))

    assert fake._closed, "iterator was not closed"
    assert fake.close_call_count == 3, (
        f"expected 3 close() calls (2 failures + 1 success), got {fake.close_call_count}"
    )


# [pr_diff] fail_to_pass
def test_aclose_retries_higher_fail_count():
    """aclose() retries correctly with more failures (fail_count=5)."""
    from gradio.utils import SyncToAsyncIterator

    fake = FakeIterator(fail_count=5)
    iterator = SyncToAsyncIterator(fake, limiter=None)

    asyncio.run(iterator.aclose(retry_interval=0.01, timeout=5.0))

    assert fake._closed, "iterator was not closed"
    assert fake.close_call_count == 6, (
        f"expected 6 close() calls (5 failures + 1 success), got {fake.close_call_count}"
    )


# [pr_diff] fail_to_pass
def test_aclose_timeout_raises():
    """aclose() raises ValueError after timeout is exceeded."""
    from gradio.utils import SyncToAsyncIterator
    import pytest

    fake = FakeIterator(fail_count=999)
    iterator = SyncToAsyncIterator(fake, limiter=None)

    with pytest.raises(ValueError, match="already executing"):
        asyncio.run(iterator.aclose(timeout=0.1, retry_interval=0.02))


# [pr_diff] fail_to_pass
def test_aclose_race_condition():
    """aclose() handles time-based race where close() fails temporarily."""
    from gradio.utils import SyncToAsyncIterator

    racing = RacingIterator(fail_for_ms=60)
    iterator = SyncToAsyncIterator(racing, limiter=None)

    asyncio.run(iterator.aclose(timeout=2.0, retry_interval=0.01))

    assert racing._closed, "iterator was not closed after race resolved"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_aclose_propagates_non_matching_valueerror():
    """aclose() does not retry on ValueError without 'already executing'."""
    from gradio.utils import SyncToAsyncIterator
    import pytest

    class BadIterator:
        def close(self):
            raise ValueError("some other error")

    iterator = SyncToAsyncIterator(BadIterator(), limiter=None)
    with pytest.raises(ValueError, match="some other error"):
        asyncio.run(iterator.aclose())


# [pr_diff] pass_to_pass
def test_safe_aclose_works_with_async_generator():
    """safe_aclose_iterator() works with native async generators."""
    from gradio.utils import safe_aclose_iterator

    async def gen():
        yield 1
        yield 2

    async def run():
        ag = gen()
        await safe_aclose_iterator(ag)
        # After aclose, async generator should be exhausted
        try:
            await ag.__anext__()
            return False  # should not reach here
        except StopAsyncIteration:
            return True

    assert asyncio.run(run()), "async generator was not closed"


# [static] fail_to_pass
def test_not_stub():
    """aclose() method has real logic — not just pass or self.iterator.close()."""
    from gradio.utils import SyncToAsyncIterator

    # Verify the method has retry behavior by checking that a single-failure
    # iterator is handled without raising (a stub would just call close() once)
    fake = FakeIterator(fail_count=1)
    iterator = SyncToAsyncIterator(fake, limiter=None)

    try:
        asyncio.run(iterator.aclose())
    except ValueError:
        raise AssertionError(
            "aclose() raised ValueError on first failure — likely a stub "
            "that just calls self.iterator.close() without retry"
        )

    assert fake._closed, "iterator was not closed"
