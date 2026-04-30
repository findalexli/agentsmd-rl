# Add per-signal safety filtering to the buffer workflow

## Problem

The signal processing pipeline currently only checks for prompt injection and manipulation at the **report level** — after signals have already been grouped, summarized, and passed through expensive LLM operations. Evals show a significant leak rate for malicious signals (prompt injection, data exfiltration attempts, social engineering) that make it through to the grouping stage unchecked.

The existing `safety_judge_activity` (in `safety_judge.py`) only runs during the summary workflow on fully-formed reports. There is no per-signal filtering before signals enter the buffer and get flushed to S3.

## Expected Behavior

1. **New safety filter**: Create a per-signal safety classifier that runs in the buffer workflow *before* signals are flushed to S3. It should classify each raw signal against a threat taxonomy (instruction injection, hidden instructions, encoded payloads, security-weakening requests, data exfiltration, social engineering, code injection via patches). Signals classified as unsafe should be dropped from the batch. If the entire batch is unsafe, skip the flush and grouping steps.

2. **Rename existing safety judge**: The existing `safety_judge.py` should be renamed to `report_safety_judge.py` to clearly distinguish it as the report-level (second layer) safety check. All references to the old name — function names, constants, imports in `__init__.py`, `summary.py`, the eval, and the module integrity test — must be updated.

3. **New error type**: Add an `EmptyLLMResponseError` exception to `llm.py` (replacing the generic `ValueError` in `_extract_text_content`). The safety filter should handle this error by treating the signal as unsafe (with threat type `provider_safety_filter`).

4. **Eval integration**: Add the safety filter step to the e2e grouping eval pipeline so it runs before matching. Capture a `signal-safety-filter` eval metric for each signal processed.

## Files to Look At

- `products/signals/backend/temporal/buffer.py` — buffer workflow, where safety filtering should be added before S3 flush
- `products/signals/backend/temporal/safety_judge.py` — existing report-level safety judge to rename
- `products/signals/backend/temporal/llm.py` — LLM helper utilities
- `products/signals/backend/temporal/__init__.py` — activity registration
- `products/signals/backend/temporal/summary.py` — summary workflow (imports safety judge)
- `products/signals/eval/eval_grouping_e2e.py` — e2e eval pipeline
- `products/signals/eval/data_spec.py` — eval data spec (content property)
- `posthog/temporal/tests/ai/test_module_integrity.py` — activity registry test

After making the code changes, update the relevant architecture documentation (`products/signals/ARCHITECTURE.md`) to describe the new safety filter module, its place in the pipeline, and how it relates to the existing report-level safety judge. Also update `products/signals/eval/AGENTS.md` with HogQL query templates for analyzing eval results including the new safety filter metrics.
