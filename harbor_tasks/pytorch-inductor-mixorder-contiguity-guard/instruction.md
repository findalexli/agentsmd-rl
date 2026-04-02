# Bug: Inductor mix-order reduction assert failure on non-contiguous fused nodes

## Summary

The Inductor scheduler's mix-order reduction fusion path can trigger an assertion
error when a pointwise node is fused into one side of a `FusedMixOrderReductions`
and the resulting fused node loses its contiguity property.

## Context

`FusedMixOrderReductions` (in `torch/_inductor/scheduler.py`) requires that at
least one of its two sub-nodes is contiguous (see the assertion in `__init__`).
The `sub_node_can_fuse` method currently checks whether the scheduler allows the
fusion and whether it would introduce producer/consumer cycles — but it does
**not** verify that the contiguity invariant is preserved after the fusion.

## How it fails

1. `node1` starts out contiguous (a reduction). A non-contiguous pointwise node
   arrives that is eligible for fusion with `node1`.
2. `sub_node_can_fuse` approves the fusion because it only looks at ancestry and
   score thresholds.
3. `fuse_with` calls `backend.fuse(node1, pointwise)`, producing a **non-contiguous**
   fused node.
4. `FusedMixOrderReductions.__init__` is called with **both** sub-nodes now
   non-contiguous → the assertion fires.

## Reproduction pattern

A model that creates:
- A contiguous reduction (e.g. `x.sum(dim=1)`)
- A pointwise op depending on both reduced and unreduced data
- A second reduction across a different dimension

With a large, asymmetric shape (e.g. `[32768, 768]`) and `split_reductions=False`,
the mix-order heuristic kicks in and triggers the assert.

## Relevant code

- `torch/_inductor/scheduler.py` — `FusedMixOrderReductions` class
  - `sub_node_can_fuse` (around line 2140)
  - `fuse_with` (around line 2195)
  - `MixOrderReduction.is_contiguous_node` (around line 379)

## Expected behavior

The fusion should be rejected before it reaches `FusedMixOrderReductions.__init__`,
so that the contiguity invariant is never violated.
