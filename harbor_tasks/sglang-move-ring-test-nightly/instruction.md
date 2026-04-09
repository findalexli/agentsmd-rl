# Move Ring-2.5-1T test to nightly suite

## Problem

The `test_ring_2_5_1t.py` test is currently registered in the `stage-c-test-8-gpu-h200` CI suite. This test requires 8 H200 GPUs and takes significant time to run (est_time=1000 seconds). Given its resource requirements and runtime, it should be moved to the nightly test suite instead of running on every PR.

The test also needs additional timeout configuration to handle the long-running nature of testing a ~1T parameter MoE model (Ring-2.5-1T with TP=8).

## Expected Behavior

The test should be registered in the `nightly-8-gpu-common` suite with the `nightly=True` flag, indicating it's part of the nightly CI pipeline rather than per-PR CI.

Additionally, the test configuration should include:
- `est_time` increased from 1000 to 1800 seconds
- A `--soft-watchdog-timeout 1800` argument added to the base_args list

## Files to Look At

- `test/registered/8-gpu-models/test_ring_2_5_1t.py` — Contains the test class and `register_cuda_ci()` call that controls CI registration

## References

The `register_cuda_ci()` function is a marker parsed via AST by the CI system. See `python/sglang/test/ci/ci_register.py` for the registration format.
