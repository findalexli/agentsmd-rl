# Bug: CPU mixed-precision WNA16 kernel fails with compressed-tensor weight format

## Summary

The CPU WNA16 mixed-precision linear kernel (`vllm/model_executor/kernels/linear/mixed_precision/cpu.py`) only works with GPTQ/marlin-style quantized weight layouts. When a model uses the **compressed-tensor (CT)** weight format — which stores weights with a different dimension ordering than marlin — the kernel crashes or produces incorrect results.

## Details

The `CPUWNA16LinearKernel` class has several issues that prevent it from working with compressed-tensor quantized models:

1. **Hardcoded weight attribute names**: The kernel directly accesses layer attributes by fixed names rather than using the generic accessor pattern provided by the parent class `MPLinearKernel`. Compressed-tensor quantization uses different attribute names for its weight parameters, so the hardcoded access fails with an `AttributeError`.

2. **No support for alternate weight layouts**: The kernel assumes a single dimension ordering for packed weights, scales, and zero points. CT format uses a different convention for which axis is the input vs output dimension. The weight processing pipeline doesn't account for this and produces garbled results.

3. **Incorrect format detection**: The method that dispatches between GPTQ and AWQ processing paths uses the wrong signal to distinguish formats. CT format can be misrouted because the current heuristic doesn't consider the actual weight layout metadata.

## Relevant files

- `vllm/model_executor/kernels/linear/mixed_precision/cpu.py` — the kernel implementation
- `vllm/model_executor/kernels/linear/mixed_precision/MPLinearKernel.py` — parent class with generic weight accessors

## Expected behavior

The CPU WNA16 kernel should handle both marlin-style (GPTQ) and compressed-tensor weight formats, using the generic weight parameter accessors from the parent class and properly handling the different dimension conventions during weight processing.
