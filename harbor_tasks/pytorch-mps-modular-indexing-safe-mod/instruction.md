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

## Expected Behavior

The codegen should detect the problematic pattern and emit code that prevents
the Metal compiler from applying its buggy optimization on the fused
division-modulo expression. The `c10/metal/utils.h` header should provide
the necessary primitive.
