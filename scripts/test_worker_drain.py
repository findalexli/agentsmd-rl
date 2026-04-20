#!/usr/bin/env python3
"""
Unit test for the worker drain barrier in taskforge.e2b_worker.run_batch.

The old get_nowait() version had a bug: if a worker re-enqueued an item (on
rate-limit), nearby workers could exit on QueueEmpty BEFORE seeing the new
item, leaving it orphaned in the queue. After the fix (blocking queue.get()
+ queue.join() drain barrier + sentinel shutdown), re-enqueued items always
get picked up.

This test monkey-patches run_task to return rate_limited for the first N
attempts on each item, verifying:
  (a) all items eventually complete (no orphans),
  (b) the batch returns promptly once everything is processed,
  (c) the correct number of retries was observed.
"""

from __future__ import annotations

import asyncio
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from taskforge import e2b_worker  # noqa: E402


# ---------------------------------------------------------------------------
# Fake run_task: returns rate_limited for the first K attempts, then success
# ---------------------------------------------------------------------------

class FakeHarness:
    def __init__(self, items: list[str], fails_before_success: int = 2):
        self.items = items
        self.fails_before_success = fails_before_success
        self.attempt_count: dict[str, int] = {i: 0 for i in items}
        self.calls: list[str] = []

    async def fake_run_task(self, task_ref, task_dir, pool, sandbox_sem, **kwargs):
        # run_task("", ..., pr_ref=...) when is_new; use pr_ref if given
        ref = kwargs.get("pr_ref") or task_ref
        self.calls.append(ref)
        self.attempt_count[ref] += 1

        # Simulate some work
        await asyncio.sleep(0.01)

        # Fail with rate_limited until the threshold is reached
        if self.attempt_count[ref] <= self.fails_before_success:
            return e2b_worker.WorkerResult(
                task_ref=ref, mode="pipeline",
                error=f"rate limited: fake attempt {self.attempt_count[ref]}",
            )

        # Success
        r = e2b_worker.WorkerResult(task_ref=ref, mode="pipeline")
        r.valid = True
        r.task_name = ref.replace("/", "-").replace("#", "-")
        return r


async def _run(items: list[str], fails: int, concurrency: int, max_retries: int):
    harness = FakeHarness(items, fails_before_success=fails)

    # Monkey-patch run_task and create_worker_sandbox so we don't hit E2B
    original_run_task = e2b_worker.run_task
    e2b_worker.run_task = harness.fake_run_task
    try:
        # Wrap items as {"pr_ref": X} dicts so worker routes them to run_task(pr_ref=...)
        dict_items = [{"pr_ref": i} for i in items]

        start = time.monotonic()
        results = await e2b_worker.run_batch(
            items=dict_items,
            mode="pipeline",
            task_dir=REPO / "harbor_tasks",
            pool=None,
            concurrency=concurrency,
            max_retries=max_retries,
        )
        elapsed = time.monotonic() - start

    finally:
        e2b_worker.run_task = original_run_task

    return results, harness, elapsed


def assert_eq(actual, expected, label):
    if actual != expected:
        print(f"  ❌ {label}: got {actual!r}, expected {expected!r}")
        return False
    print(f"  ✓ {label}: {actual}")
    return True


async def main():
    all_ok = True

    # ------------------------------------------------------------------
    # TEST 1: 5 items, each needs 2 retries → 3 attempts each → success
    # ------------------------------------------------------------------
    print("\n=== TEST 1: 5 items × 3 attempts (2 retries before success) ===")
    items = [f"owner/repo#{100 + i}" for i in range(5)]
    results, harness, elapsed = await _run(items, fails=2, concurrency=3, max_retries=5)

    all_ok &= assert_eq(len(results), 5, "all 5 items produced results")
    all_ok &= assert_eq(
        sum(1 for r in results if r.valid), 5,
        "all 5 eventually succeeded")
    all_ok &= assert_eq(len(harness.calls), 5 * 3, "total attempts = 15 (5 × 3)")
    all_ok &= assert_eq(
        sorted({r.task_ref for r in results}),
        sorted(items),
        "every input item has exactly one final result")
    print(f"  runtime: {elapsed:.2f}s")

    # ------------------------------------------------------------------
    # TEST 2: 20 items at concurrency 4, each needs 1 retry → stress
    # ------------------------------------------------------------------
    print("\n=== TEST 2: 20 items × 2 attempts (1 retry), concurrency 4 ===")
    items = [f"org/pkg#{200 + i}" for i in range(20)]
    results, harness, elapsed = await _run(items, fails=1, concurrency=4, max_retries=3)

    all_ok &= assert_eq(len(results), 20, "all 20 items produced results")
    all_ok &= assert_eq(
        sum(1 for r in results if r.valid), 20,
        "all 20 succeeded")
    all_ok &= assert_eq(len(harness.calls), 20 * 2, "total attempts = 40")
    print(f"  runtime: {elapsed:.2f}s")

    # ------------------------------------------------------------------
    # TEST 3: max_retries exhausted — item fails more times than allowed
    # ------------------------------------------------------------------
    print("\n=== TEST 3: max_retries exhausted (should fail, not orphan) ===")
    items = [f"stuck/rate-limit#{300 + i}" for i in range(3)]
    results, harness, elapsed = await _run(items, fails=10, concurrency=2, max_retries=2)

    all_ok &= assert_eq(len(results), 3, "all 3 items produced FAIL results (no orphans)")
    all_ok &= assert_eq(
        sum(1 for r in results if r.valid), 0,
        "all 3 exhausted retries (none valid)")
    # Attempts = original + max_retries = 1 + 2 = 3 per item, × 3 items = 9
    all_ok &= assert_eq(len(harness.calls), 9, "9 total attempts (1+2 per item × 3)")
    print(f"  runtime: {elapsed:.2f}s")

    # ------------------------------------------------------------------
    # TEST 4: no failures — every item succeeds on first try
    # ------------------------------------------------------------------
    print("\n=== TEST 4: no retries needed (happy path) ===")
    items = [f"happy/path#{400 + i}" for i in range(10)]
    results, harness, elapsed = await _run(items, fails=0, concurrency=5, max_retries=3)

    all_ok &= assert_eq(len(results), 10, "10 results")
    all_ok &= assert_eq(len(harness.calls), 10, "exactly 10 attempts")
    print(f"  runtime: {elapsed:.2f}s")

    # ------------------------------------------------------------------
    # TEST 5: failed_tasks.jsonl is written correctly
    # ------------------------------------------------------------------
    print("\n=== TEST 5: failed_tasks.jsonl persistence ===")
    import tempfile, json as jsonlib
    failed_path = Path(tempfile.mkstemp(suffix=".jsonl")[1])
    try:
        items = [f"fail/resume#{500 + i}" for i in range(4)]
        harness = FakeHarness(items, fails_before_success=10)  # always fails

        original_run_task = e2b_worker.run_task
        e2b_worker.run_task = harness.fake_run_task
        try:
            dict_items = [{"pr_ref": i} for i in items]
            results = await e2b_worker.run_batch(
                items=dict_items, mode="pipeline",
                task_dir=REPO / "harbor_tasks",
                pool=None, concurrency=2, max_retries=1,
                failed_log_path=failed_path,
            )
        finally:
            e2b_worker.run_task = original_run_task

        all_ok &= assert_eq(len(results), 4, "4 terminal results")
        all_ok &= assert_eq(
            sum(1 for r in results if r.valid), 0,
            "zero valid (all exhausted retries)")

        entries = [jsonlib.loads(l) for l in failed_path.read_text().strip().splitlines()]
        all_ok &= assert_eq(len(entries), 4, "4 entries in failed_tasks.jsonl")
        all_ok &= assert_eq(
            sorted(e["pr_ref"] for e in entries),
            sorted(items),
            "every input PR has a failure entry")
        all_ok &= assert_eq(
            entries[0]["failure_type"], "rate_limit_exhausted",
            "failure_type classified correctly")
        all_ok &= assert_eq(
            all("last_error" in e for e in entries), True,
            "all entries have last_error field")
    finally:
        failed_path.unlink(missing_ok=True)

    # ------------------------------------------------------------------
    # TEST 6: SHUTDOWN sentinel doesn't collide with real items
    # ------------------------------------------------------------------
    print("\n=== TEST 6: SHUTDOWN sentinel (object identity, not equality) ===")
    # Even if a "real" item happens to have the string value that looks
    # sentinel-like, the `is _SHUTDOWN` check prevents collision.
    weird_items = ["__shutdown__", "_SHUTDOWN", "(object())"]
    results, harness, elapsed = await _run(weird_items, fails=0, concurrency=2, max_retries=2)
    all_ok &= assert_eq(len(results), 3, "all 3 weirdly-named items processed (no sentinel collision)")

    # ------------------------------------------------------------------
    # TEST 7: simplified retry (no inner retry) — outer queue handles all
    #
    # Verify: when run_task returns "rate limited" (Claude Code's 10 internal
    # retries exhausted), the outer queue re-enqueues, and a healthier later
    # attempt eventually succeeds. Models real Fire Pass dip-and-recover.
    # ------------------------------------------------------------------
    print("\n=== TEST 7: simplified retry — outer queue handles 429 ===")

    class TwoStageHarness:
        """First N attempts return rate_limited; subsequent return success."""
        def __init__(self, items, fail_rounds=1):
            self.items = items
            self.fail_rounds = fail_rounds
            self.calls = []

        async def run(self, task_ref, task_dir, pool, sandbox_sem, **kwargs):
            ref = kwargs.get("pr_ref") or task_ref
            self.calls.append(ref)
            await asyncio.sleep(0.005)
            # Each item: first `fail_rounds` calls return rate_limited; later succeed
            attempts_so_far = sum(1 for c in self.calls if c == ref)
            if attempts_so_far <= self.fail_rounds:
                return e2b_worker.WorkerResult(
                    task_ref=ref, mode="pipeline",
                    error="rate limited: Fire Pass cooldown")
            r = e2b_worker.WorkerResult(task_ref=ref, mode="pipeline")
            r.valid = True
            r.task_name = ref.replace("/", "-").replace("#", "-")
            return r

    items = [f"recovery/case#{600 + i}" for i in range(8)]
    harness = TwoStageHarness(items, fail_rounds=2)
    original = e2b_worker.run_task
    e2b_worker.run_task = harness.run
    try:
        dict_items = [{"pr_ref": i} for i in items]
        results = await e2b_worker.run_batch(
            items=dict_items, mode="pipeline",
            task_dir=REPO / "harbor_tasks",
            pool=None, concurrency=4, max_retries=3,  # ≥ fail_rounds
        )
    finally:
        e2b_worker.run_task = original

    all_ok &= assert_eq(len(results), 8, "8 results returned")
    all_ok &= assert_eq(
        sum(1 for r in results if r.valid), 8,
        "all 8 eventually succeeded after 2 fail rounds")
    # Each item: 2 fails + 1 success = 3 calls × 8 items = 24
    all_ok &= assert_eq(len(harness.calls), 24, "24 total attempts (3 per item)")

    # ------------------------------------------------------------------
    # TEST 8: cross-process claim lock — two pipelines can't pick the same PR
    # ------------------------------------------------------------------
    print("\n=== TEST 8: claim lock prevents double-pick ===")
    import tempfile
    claim_dir = Path(tempfile.mkdtemp(prefix="claim_test_"))
    try:
        # First worker claims the PR
        path1, acquired1 = e2b_worker._claim_pr(claim_dir, "owner/repo#700")
        all_ok &= assert_eq(acquired1, True, "first worker acquires claim")
        all_ok &= assert_eq(path1.exists(), True, "claim file exists on disk")

        # Second worker tries the same PR — should be denied
        path2, acquired2 = e2b_worker._claim_pr(claim_dir, "owner/repo#700")
        all_ok &= assert_eq(acquired2, False, "second worker denied (file exists)")
        all_ok &= assert_eq(path1, path2, "same claim path returned")

        # Different PR can be claimed independently
        path3, acquired3 = e2b_worker._claim_pr(claim_dir, "owner/repo#701")
        all_ok &= assert_eq(acquired3, True, "different PR claim succeeds")

        # Claim file content has PID + timestamp
        content = path1.read_text()
        all_ok &= assert_eq(
            "pid=" in content and "pr_ref=owner/repo#700" in content, True,
            "claim file records PID + pr_ref")
    finally:
        import shutil
        shutil.rmtree(claim_dir, ignore_errors=True)

    print("\n" + "=" * 60)
    if all_ok:
        print("✅ ALL TESTS PASSED — drain, failure-log, sentinel, retry, claim-lock all green.")
    else:
        print("❌ SOME TESTS FAILED")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
