# Add SFT/GRPO Integration Test for Megatron Train Engine

## Problem

The SFT and GRPO integration tests in `areal/tests/sft/` and `areal/tests/grpo/` currently only support the FSDP backend. The tests reference a single `config.yaml` and `ref_losses.json`, meaning there is no test coverage for the Megatron train engine. Megatron-specific regressions can go undetected.

## Expected Behavior

Both `test_sft` and `test_grpo` should be parametrized to run against both "fsdp" and "megatron" backends. Each backend should have its own configuration file (`config_fsdp.yaml`, `config_megatron.yaml`) and, for SFT, its own reference loss data (`ref_losses_fsdp.json`, `ref_losses_megatron.json`). The existing single `config.yaml` and `ref_losses.json` files should be renamed to include the `_fsdp` suffix.

## Files to Look At

- `areal/tests/grpo/test_grpo.py` — GRPO integration test (needs parametrization)
- `areal/tests/grpo/config.yaml` — Current FSDP-only GRPO config (rename to `config_fsdp.yaml`)
- `areal/tests/sft/test_sft.py` — SFT integration test (needs parametrization)
- `areal/tests/sft/config.yaml` — Current FSDP-only SFT config (rename to `config_fsdp.yaml`)
- `areal/tests/sft/ref_losses.json` — Current FSDP-only reference losses (rename to `ref_losses_fsdp.json`)
- `docs/cli_reference.md` — CLI reference docs (formatting update from pre-commit)
