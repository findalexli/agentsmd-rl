# Metal shader codegen emits bare float literals for half-precision types

## Bug Description

The MPS (Metal Performance Shaders) backend in `torch._inductor` compiles Python operations into Metal shaders. Metal Shading Language is strict about implicit type conversions — in particular, it **rejects implicit float-to-bfloat and float-to-half conversions**.

The codegen in `torch/_inductor/codegen/mps.py` has methods in the `MetalOverrides` class that emit bare float literals (e.g., `0.0`) into the generated shader source without casting them to the target variable's type. This causes Metal shader compilation failures when the target dtype is `bfloat16` or `float16`.

## Affected Methods

Two methods in the `MetalOverrides` class are affected:

1. **`masked()`** — When generating the if/else construct, the assignment of both the scoped body result and the else-branch fallback value are written as bare values without any type cast to match the declared variable type.

2. **`where()`** — The ternary expression's false-branch value is passed through `value_to_metal()` but never cast to match the type of the true-branch operand.

## Reproduction

Compiling a simple operation that uses `masked` or `where` on half-precision tensors will trigger Metal shader compilation errors. For example, a reduction (which internally uses `masked`) or an explicit `torch.where()` on bfloat16/float16 MPS tensors will fail.

## Files to Examine

- `torch/_inductor/codegen/mps.py` — The `MetalOverrides` class, specifically the `masked()` and `where()` static methods.

Note how other methods in the same file (e.g., `maximum()`, `minimum()`) handle type casting for their operands — the `masked()` and `where()` methods should follow a similar approach to ensure Metal shader compilation succeeds for all float types.
