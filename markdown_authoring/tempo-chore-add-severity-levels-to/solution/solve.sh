#!/usr/bin/env bash
set -euo pipefail

cd /workspace/tempo

# Idempotency guard
if grep -qF "The severity label on each comment signals whether it blocks merge: CRITICAL and" ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -13,6 +13,37 @@ Only flag issues that matter. Ask questions rather than making demands. Provide
 
 `</role>`
 
+## Severity levels
+`<severity-levels>`
+
+Label every comment with one of four severity levels. Put the label at the start of the comment so authors and reviewers can prioritise at a glance.
+
+**CRITICAL** — Correctness bugs, data corruption, panics, or security holes that affect production behaviour. Always block merge.
+
+Examples from this repo:
+- `randomDedicatedBlobString` returned raw `crypto/rand` bytes cast to `string`. `gogo/protobuf` rejects non-UTF-8 strings, so any code path serialising those attributes would return an error at runtime. (#6914)
+- `uint64` subtraction in `formatSpanForCard` underflows when `EndTimeUnixNano < StartTimeUnixNano`, producing a wildly incorrect duration in the output. (#6840)
+- A goroutine range-loop captured the loop variable `read` by reference; all goroutines ended up calling the same function, making a race-condition regression test completely ineffective at catching the bug it was meant to guard. (#6773)
+
+**HIGH** — Significant behavioural gaps, config knobs that silently do nothing, API contracts broken for callers, or unbounded resource usage. Resolve before merge; if intentionally deferred, the PR must say why.
+
+Examples from this repo:
+- `localCompleteBlockLifecycle` read `cfg.CompleteBlockConcurrency` into `flushConcurrency` but only ever launched one flush goroutine, so the config knob had no effect on throughput. (#6941)
+- `instance.deleteOldBlocks()` delegated eligibility to a lifecycle that kept all unflushed complete blocks indefinitely, risking unbounded disk growth during a prolonged backend outage. (#6941)
+- Moving the lag check inside `withInstance` meant the `FailOnHighLag` safeguard was silently skipped whenever no tenant instance existed yet. (#6911)
+- `w.Iterator()` and `resp.Results` were never closed inside a race-condition test, leaking file descriptors and making the test flaky once the OS limit was reached. (#6773)
+
+**MEDIUM** — Worth fixing but not blocking: deprecated settings without startup warnings, missing tests for non-trivial logic, flaky test patterns, retry loops with no bound.
+
+Examples from this repo:
+- `rf1_after` was removed but the config field was still accepted and silently ignored with no startup warning, so operators upgrading would have no signal the setting had no effect. (#6969)
+- A new multi-worker shared queue was added, but tests only covered single-worker usage; concurrent dequeue correctness (all items processed exactly once, `Stop` unblocks all waiters) was left untested. (#6936)
+- A test used a shared global Prometheus counter with a fixed label value; running in parallel, another package touching the same label set could advance the counter and cause spurious failures. (#6932)
+
+**LOW** — Naming, wording, doc-comment accuracy, and minor style issues. Do not leave comments on LOW items.
+
+`</severity-levels>`
+
 ## Repeated patterns
 `<repeated-patterns>`
 
@@ -126,7 +157,7 @@ Ask questions rather than making demands. Prefer "what do you think about X?" or
 
 Give a brief rationale with each comment so the author understands the concern, not just the fix.
 
-When leaving a substantive comment alongside an approval, make it clear you are not blocking — for example: "LGTM, one optional thought below."
+The severity label on each comment signals whether it blocks merge: CRITICAL and HIGH block; MEDIUM does not. When leaving only MEDIUM comments alongside an approval there is no need to add a separate "this doesn't block" disclaimer — the label already says that.
 
 When a PR has a small number of remaining issues after a round of feedback, acknowledge the progress: "Looking good, just a few small things."
 
PATCH

echo "Gold patch applied."
