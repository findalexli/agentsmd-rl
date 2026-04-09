# Add dump_metric to MMMU, lm-eval, and NeMo Skills eval paths

## Problem

The SGLang test infrastructure has multiple evaluation paths for benchmarking models:
- MMMU (via lmms-eval)
- lm-eval harness
- NeMo Skills (mmmu-pro)

While `run_eval.py` already has `dump_metric` calls, these three eval paths do not emit metrics. This means evaluation results are only printed to stdout and not captured in a structured format for downstream processing.

The `dump_metric` function (from `sglang.test.test_utils`) should be called after evaluation scores are computed to emit metrics in a standardized format. The function is designed to be silent on failure, so adding these calls is safe and won't break existing tests.

## Expected Behavior

After running evaluations through any of these paths, metrics should be emitted via `dump_metric` with:
- A metric name (e.g., `mmmu_score`, `{dataset}_score`, `{task}_{metric}`)
- The measured value
- Labels including model name, eval type, and API/source identifier

## Files to Look At

- `python/sglang/test/accuracy_test_runner.py` — Contains `_run_nemo_skills_eval` function that runs NeMo Skills evaluation. After parsing the accuracy score, it should call `dump_metric`.

- `python/sglang/test/kits/lm_eval_kit.py` — Contains `test_lm_eval` method that runs lm-eval harness tests. After computing each metric, it should call `dump_metric`.

- `python/sglang/test/kits/mmmu_vlm_kit.py` — Contains two MMMU test functions (`test_mmmu` and `_run_vlm_mmmu_test`) that run vision-language model evaluation. After computing mmmu_accuracy, they should call `dump_metric`.

- `python/sglang/test/test_utils.py` — Contains the `dump_metric` function that should be imported and called. Reference this for the correct function signature.
