# Add SFT/GRPO Integration Test for Megatron Train Engine

## Problem

The SFT and GRPO integration tests in `areal/tests/sft/` and `areal/tests/grpo/` currently only support the FSDP backend. The tests reference a single `config.yaml` and `ref_losses.json`, meaning there is no test coverage for the Megatron train engine. Megatron-specific regressions can go undetected.

## Expected Behavior

Both `test_sft` and `test_grpo` must run against both `fsdp` and `megatron` backends. This requires:

1. **Parametrization**: Each test function must be parametrized with `@pytest.mark.parametrize` to accept a `backend` parameter accepting values `"fsdp"` and `"megatron"`.

2. **Backend-specific config files**: Each test must load its config via a path constructed from the `backend` parameter (e.g., `config_{backend}.yaml`). This means there must be a `config_fsdp.yaml` (the renamed original) and a `config_megatron.yaml` for each of SFT and GRPO.

3. **GRPO megatron config** (`areal/tests/grpo/config_megatron.yaml`):
   - Must contain `allocation_mode:` with value containing `megatron`
   - Must have `experiment_name: tests-grpo`
   - Must be valid YAML

4. **SFT megatron config** (`areal/tests/sft/config_megatron.yaml`):
   - Must contain `allocation_mode:` with value containing `megatron`
   - Must have `experiment_name: tests-sft`
   - Must be valid YAML

5. **SFT reference losses for megatron** (`areal/tests/sft/ref_losses_megatron.json`):
   - Must be a JSON array of exactly **16 float values**
   - Each value must be strictly between `0.0` and `10.0`

6. **File renaming**: The existing FSDP-only files (`config.yaml`, `ref_losses.json`) must be renamed to include a `_fsdp` suffix so the parametrized config loading can distinguish them from the new megatron files.

7. **No hardcoded config paths**: The test functions must not contain any literal `"config.yaml"` string as an active (non-comment, non-fixture) config path argument to `load_expr_config`.

## Files to Look At

- `areal/tests/grpo/test_grpo.py` — GRPO integration test
- `areal/tests/grpo/config.yaml` — Current FSDP-only GRPO config
- `areal/tests/sft/test_sft.py` — SFT integration test
- `areal/tests/sft/config.yaml` — Current FSDP-only SFT config
- `areal/tests/sft/ref_losses.json` — Current FSDP-only reference losses
- `docs/cli_reference.md` — CLI reference docs (formatting update from pre-commit)

## Verification

After applying the fix, running `pytest` on the test suite should run both fsdp and megatron variants for each integration test.