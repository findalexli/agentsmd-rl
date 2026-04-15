# MPS Codegen: Fused integer division-modulo produces wrong results

## Bug Description

The Metal (MPS) inductor codegen emits expressions like `(x / A) % B` for
`ModularIndexing` nodes. On Apple's Metal compiler, when `A` is a power of two
(e.g., 65536) and `B` is **not** a power of two, the compiler's optimizer fuses
the division and modulo and produces incorrect results. This manifests as
corrupted tensor reads from non-contiguous memory layouts — for example,
scaled dot-product attention (SDPA) returns NaN when the number of heads is
not a power of two (e.g., 6).

The root cause is a Metal compiler optimization bug: the fused
`(uint / power_of_2) % non_power_of_2` pattern silently computes wrong
values for integral types.

## Affected Files

- `torch/_inductor/codegen/mps.py` — `MetalExprPrinter._print_ModularIndexing`
  currently emits a bare `(x) % (mod)` expression for all cases.
- `c10/metal/utils.h` — the Metal utility header has helper functions like
  `floor_divide` and `fmod`, but lacks a workaround for this compiler bug.

## Reproduction

Any inductor-compiled MPS kernel that uses `ModularIndexing` with
`div = 65536` and a non-power-of-two `mod` will produce incorrect results.
A concrete example: run SDPA with `n_head = 6` and `n_embd = 384` through
`torch.compile` on MPS — the output will contain NaN values.

## Required Solution Components

The fix has two parts:

### 1. Codegen change (`torch/_inductor/codegen/mps.py`)

The `_print_ModularIndexing` method must detect when the fused
division-modulo pattern is problematic (div is a power of two such as 65536
AND mod is not a power of two) and emit a function call instead of bare `%`
to prevent the Metal compiler from applying its buggy optimization.

For all other cases (e.g., div is 1, or mod is a power of two, or div is not
a power of two), the existing behavior should be preserved.

### 2. Utility header change (`c10/metal/utils.h`)

A new safe-modulo function must be added to the `c10::metal` namespace. This
function must:

- Perform the modulo/remainder operation correctly on integral types
- Use an optimization barrier (e.g., `volatile`, `optnone`,
  `__attribute__((noinline))`, inline `asm`, or similar) to prevent the Metal
  compiler from fusing the division and modulo operations
- Be usable from MPS device code

The function name is flexible (examples: `safe_mod`, `mod_safe`, `safe_modulo`,
`safe_remainder`), but it must appear in `c10/metal/utils.h` and contain an
optimization barrier near its definition.
