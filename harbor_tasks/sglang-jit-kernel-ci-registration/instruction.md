# Missing CI Registration for JIT Kernel Test and Benchmark Files

## Problem

SGLang's CI runner (`test/run_suite.py`) discovers test and benchmark files by
statically parsing each Python file's AST, looking for top-level
`register_cuda_ci(...)` calls from `sglang.test.ci.ci_register`. Files that
lack these registration calls are invisible to the CI collector — they never
run in CI even though they exist in the repo.

Four JIT kernel files are currently missing their CI registration entries:

- `python/sglang/jit_kernel/benchmark/bench_cast.py` — benchmark for the
  FP8 downcast kernel, should be collected by the kernel benchmark suite
- `python/sglang/jit_kernel/benchmark/bench_fused_qknorm_rope.py` — benchmark
  for the fused QK-norm + RoPE kernel, same suite
- `python/sglang/jit_kernel/tests/test_cast.py` — correctness tests for the
  FP8 downcast kernel, should be collected by the kernel unit test suite (and
  optionally the nightly kernel suite)
- `python/sglang/jit_kernel/tests/test_fused_qknorm_rope.py` — correctness
  tests for the fused QK-norm + RoPE kernel, same suites

Because these files have no `register_cuda_ci()` calls, `run_suite.py`'s
`collect_tests()` raises a `ValueError` ("No CI registry found") when it
encounters them, or they are silently skipped depending on the sanity-check
flag.

## Expected Behavior

Each file should have the appropriate `register_cuda_ci()` calls at module
level so that `run_suite.py` can collect and dispatch them to the correct CI
suites.

## Relevant Files

- `python/sglang/test/ci/ci_register.py` — the registration API
- `test/run_suite.py` — the suite runner that discovers files via AST parsing
- `.claude/skills/write-sglang-test/SKILL.md` — documents registration patterns
- `.claude/skills/add-jit-kernel/SKILL.md` — documents JIT kernel test/benchmark conventions

## Hints

- Look at other registered files in `python/sglang/jit_kernel/tests/` and
  `python/sglang/jit_kernel/benchmark/` for the expected pattern.
- Benchmark files register for `stage-b-kernel-benchmark-1-gpu-large`.
- Test files register for `stage-b-kernel-unit-1-gpu-large` (per-commit) and
  optionally `nightly-kernel-1-gpu` (nightly with `nightly=True`).
- The `est_time` parameter should reflect realistic estimated runtime in seconds.
