# Bug: Inductor mix-order reduction assert failure on non-contiguous fused nodes

## Summary

The Inductor scheduler's mix-order reduction fusion path can trigger an assertion
error when fusing certain node combinations in `FusedMixOrderReductions`.

## Context

`FusedMixOrderReductions` (in `torch/_inductor/scheduler.py`) requires that at
least one of its two sub-nodes is contiguous (see the assertion in `__init__`).
During mix-order reduction scheduling, fusing a contiguous reduction with a
non-contiguous pointwise node can produce a fused node that violates this
contiguity requirement, causing the assertion to fire.

## How it fails

1. A contiguous reduction node (`node1`) is part of an active `FusedMixOrderReductions`.
2. A non-contiguous pointwise node (`node2`) is eligible for fusion with `node1`.
3. The fusion is approved, producing a fused node that is non-contiguous.
4. `FusedMixOrderReductions.__init__` receives both sub-nodes as non-contiguous
   → the assertion fires.

## Reproduction pattern

A model that creates:
- A contiguous reduction (e.g. `x.sum(dim=1)`)
- A pointwise op depending on both reduced and unreduced data
- A second reduction across a different dimension

With a large, asymmetric shape (e.g. `[32768, 768]`) and `split_reductions=False`,
the mix-order heuristic kicks in and triggers the assert.

## Relevant code

- `torch/_inductor/scheduler.py` — `FusedMixOrderReductions` class
  - `MixOrderReduction.is_contiguous_node` — checks whether a node is contiguous
  - `sub_node_can_fuse` — determines whether a node can be fused
  - `fuse_with` — performs the fusion
  - `__init__` — enforces the contiguity invariant via assertion

## Expected behavior

The scheduler must prevent fusions that would result in a non-contiguous
`FusedMixOrderReductions`, so that the contiguity invariant is never violated.
