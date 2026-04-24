# MPS Codegen: Fused integer division-modulo produces wrong results on Metal

## Bug Description

The Metal (MPS) inductor codegen in PyTorch emits expressions like `(x / A) % B`
for `ModularIndexing` nodes. On Apple's Metal compiler, when `A` is a power of two
(e.g., 65536) and `B` is **not** a power of two, the compiler's optimizer fuses
the division and modulo and produces incorrect results. This manifests as
corrupted tensor reads from non-contiguous memory layouts — for example,
scaled dot-product attention (SDPA) returns NaN when the number of heads is
not a power of two (e.g., 6).

The root cause is a Metal compiler optimization bug: the fused
`(uint / power_of_2) % non_power_of_2` pattern silently computes wrong
values for integral types.

## Repository

PyTorch repository at commit `483b55d84c74b92b3c2c67be4b9b7c7359ec2bbc`.

The MPS codegen is in `torch/_inductor/codegen/mps.py`. The Metal utility
header is `c10/metal/utils.h`.

## Observed Symptom

When `_print_ModularIndexing` in the `MetalExprPrinter` class produces the
fused division-modulo pattern for certain parameter combinations, the Metal
compiler applies a buggy optimization, producing incorrect results at runtime.

Cases where `div=1`, or where both `div` and `mod` are powers of two (e.g.,
`div=256, mod=16` or `div=65536, mod=8`), are unaffected and produce correct
results.

## Acceptance Criteria

### 1. Buggy-pattern workaround

For `_print_ModularIndexing` cases where the divisor is a power of two and
the modulo is not a power of two, the generated code must not trigger the
Metal compiler bug.

Specifically, for cases like `div=65536, mod=6` (or similar combinations
where the divisor is a power of two and the modulo is not):

- The output must not be a bare fused expression that triggers the Metal
  compiler bug.
- The output must include a function call (an identifier followed by
  parenthesized arguments) rather than relying solely on the `%` operator
  in the problematic pattern.
- The output must still reference both the base variable and the mod value.

### 2. Non-buggy patterns preserved

The following cases must continue to produce valid output (containing the mod
value in the output, and containing the division when `div > 1`):

- `div=1, mod=8`
- `div=65536, mod=8` (power-of-two mod — unaffected by the bug)
- `div=256, mod=16`
- `div=1, mod=32`

The `_print_FloorDiv` method must also continue working correctly (e.g.,
producing output containing `floor` for `FloorDiv(100, 4)`).

### 3. Metal utility header must provide workaround mechanism

`c10/metal/utils.h` must contain a function that prevents the Metal
compiler from applying the buggy fusion. This function must:

- Perform a modulo or remainder operation (its definition must use `%`
  or `remainder`).
- Include an optimization barrier mechanism near its definition to
  prevent the Metal compiler from fusing the operations.

### 4. Existing code integrity

- `floor_divide` and `fmod` functions must remain in `c10/metal/utils.h`.
- `c10/metal/utils.h` must remain a valid C++ header with a header guard
  (`#pragma once` or `#ifndef`/`#define`) and namespace declarations for
  `c10` and `metal`.
- `torch/_inductor/codegen/mps.py` must remain syntactically valid Python
  with its existing import statements intact.
- The `MetalExprPrinter` class must retain its existing methods:
  `_print_ModularIndexing`, `_print_FloorDiv`, `_print_Min`, `_print_Max`.
- `_print_ModularIndexing` must accept `self` and `expr` parameters and
  unpack `expr.args` as `x, div, mod`.
- `_print_FloorDiv` must accept `self` and `expr` parameters.
- `mps.py` must be at least 100 lines; `utils.h` must be at least 50 lines
  (no gutting the files).