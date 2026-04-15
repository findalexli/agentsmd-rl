# Add SFT/GRPO Integration Test for Megatron Train Engine

## Problem

The SFT and GRPO integration tests in `areal/tests/sft/` and `areal/tests/grpo/` currently only support the FSDP backend. The tests reference a single `config.yaml` and `ref_losses.json`, meaning there is no test coverage for the Megatron train engine. Megatron-specific regressions can go undetected.

## Expected Behavior

Both `test_sft` and `test_grpo` must exercise both `fsdp` and `megatron` backends. This requires:

1. **Backend-aware test functions**: Each test function must be able to run with different backend configurations. The test functions must not hardcode a single backend.

2. **Backend-specific config files**: Each test must load its config via a path that varies based on the backend. For example, a pattern like `config_{backend}.yaml` allows distinguishing between `fsdp` and `megatron` variants.

3. **GRPO megatron config** (`areal/tests/grpo/config_megatron.yaml`):
   - Must contain `allocation_mode:` with a value that includes the string `megatron`
   - Must have `experiment_name: tests-grpo`
   - Must be valid YAML

4. **SFT megatron config** (`areal/tests/sft/config_megatron.yaml`):
   - Must contain `allocation_mode:` with a value that includes the string `megatron`
   - Must have `experiment_name: tests-sft`
   - Must be valid YAML

5. **SFT reference losses for megatron** (`areal/tests/sft/ref_losses_megatron.json`):
   - Must be a JSON array of exactly **16 float values**
   - Each value must be strictly greater than `0.0` and strictly less than `10.0`

6. **File renaming**: The existing FSDP-only config files (`config.yaml`) and reference loss files (`ref_losses.json`) should be renamed to include a `_fsdp` suffix to distinguish them from megatron-specific variants.

7. **No hardcoded config paths**: The test functions must not pass a literal `"config.yaml"` string as the config path argument to `load_expr_config`.

## Files to Look At

- `areal/tests/grpo/test_grpo.py` — GRPO integration test
- `areal/tests/grpo/config.yaml` — Current FSDP-only GRPO config
- `areal/tests/sft/test_sft.py` — SFT integration test
- `areal/tests/sft/config.yaml` — Current FSDP-only SFT config
- `areal/tests/sft/ref_losses.json` — Current FSDP-only reference losses
- `docs/cli_reference.md` — CLI reference docs (formatting update from pre-commit)

## Verification

After applying the fix, running `pytest` on the test suite should run both fsdp and megatron variants for each integration test.