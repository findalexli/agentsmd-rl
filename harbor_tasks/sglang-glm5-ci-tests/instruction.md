# Add CI Tests for GLM-5 Model

## Problem

The SGLang CI test suite needs to include the new GLM-5 model (zai-org/GLM-5-FP8) for comprehensive model coverage. The current test files only cover DeepSeek-V3.2 models and need to be expanded to include GLM-5 test configurations.

The existing test files have overly specific names (test_deepseek_v32_*.py) that don't reflect their broader purpose of testing DSA (DeepSeek-AI) models. These files should be renamed to test_dsa_models_*.py to accommodate multiple model families.

Additionally, the MTP (Multi-Token Prediction) speculative decoding tests need to:
1. Use the SGLANG_ENABLE_SPEC_V2 feature flag during server launch
2. Have corrected test class names (TestDeepseekV32DPMTPV2 → TestDeepseekV32TPMTP)
3. Update memory fraction settings for GLM-5 tests

## Expected Behavior

After the changes:

1. `test/registered/8-gpu-models/test_deepseek_v32_basic.py` is renamed to `test_dsa_models_basic.py`
2. `test/registered/8-gpu-models/test_deepseek_v32_mtp.py` is renamed to `test_dsa_models_mtp.py`
3. Both files define `GLM5_MODEL_PATH = "zai-org/GLM-5-FP8"` constant
4. New test classes are added:
   - `TestGLM5DP` and `TestGLM5TP` in the basic test file
   - `TestGLM5DPMTP` and `TestGLM5TPMTP` in the MTP test file
5. `register_cuda_ci` est_time is updated from 360 to 720 in the basic test
6. MTP tests wrap server launch with `envs.SGLANG_ENABLE_SPEC_V2.override(True)`
7. Test class `TestDeepseekV32DPMTPV2` is renamed to `TestDeepseekV32TPMTP`
8. GLM5 MTP tests use `mem-frac 0.8` instead of 0.7

## Files to Look At

- `test/registered/8-gpu-models/test_deepseek_v32_basic.py` — needs renaming and GLM-5 test additions
- `test/registered/8-gpu-models/test_deepseek_v32_mtp.py` — needs renaming, env var wrapping, and GLM-5 tests

## Notes

- These are GPU-specific integration tests that require 8x H200 GPUs to actually execute
- The tests launch real model servers and run accuracy/speed benchmarks
- Focus on the structural changes (file names, class names, constants, env vars)
- Do not attempt to run the actual tests (they need GPUs and model weights)
