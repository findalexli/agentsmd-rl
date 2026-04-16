The MXFP4 quantizer in `src/transformers/quantizers/quantizer_mxfp4.py` combines `is_triton_available()` and `is_kernels_available()` into a single `kernels_available` boolean. When a dependency is missing, the error or warning message says "Triton and kernels" are required, making it impossible for the user to identify which specific dependency is missing.

For example, if only `triton` is installed but `kernels` is not, the user sees:
> "MXFP4 quantization requires Triton and kernels installed..."

This is confusing because the user cannot tell which package to install.

The `validate_environment` method needs to check `triton` and `kernels` separately and produce specific, actionable error messages for each missing dependency. This follows the established pattern already used in `quantizer_higgs.py` where each dependency is checked individually.

## Requirements

When `pre_quantized=True` and a dependency is missing:
- A warning must be logged that mentions the specific missing dependency by name (either "triton" or "kernels")
- The warning message must NOT use the combined phrase "triton and kernels"
- The `quantization_config.dequantize` attribute must be set to `True`
- The warning should include installation instructions for the specific missing package

When `pre_quantized=False` and a dependency is missing:
- A `ValueError` must be raised with a message mentioning the specific missing dependency by name (either "triton" or "kernels")
- The error message must NOT use the combined phrase "triton and kernels"
- The error should include installation instructions for the specific missing package

## Structural and Style Requirements

- The `validate_environment` method must contain at least 80 AST nodes (i.e., it must be a substantial implementation, not a minimal stub)
- The modified source file must still contain the strings `is_triton_available`, `is_kernels_available`, and `pre_quantized`
- `is_triton_available` and `is_kernels_available` must remain importable at the module level from `transformers.quantizers.quantizer_mxfp4` (i.e., they must be module-level imports, not just internal references). `Mxfp4HfQuantizer` must also remain importable from the same module.
- The top-level `transformers` package must still import correctly (e.g., `import transformers` and `from transformers import AutoModelForCausalLM` must work)
- The file must pass ruff linting with the rule set `--select=E,W,F,I --ignore=E501`
- The file must pass `ruff format --check`
- The file must have valid Python syntax

## File to Modify

- `src/transformers/quantizers/quantizer_mxfp4.py`

## Verification

After modification, the following test classes in the repository must pass:
- `tests.quantization.mxfp4.test_mxfp4.Mxfp4ConfigTest`
- `tests.quantization.mxfp4.test_mxfp4.Mxfp4QuantizerTest`
- `tests.quantization.mxfp4.test_mxfp4.Mxfp4IntegrationTest`

Additionally, the following repo-level CI checks must pass:
- `python utils/check_copies.py`
- `python utils/check_inits.py`
- `python utils/check_doc_toc.py`
