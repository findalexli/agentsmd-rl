# Compose Compiler Stability Inference - Cache Fix

## Problem

The Compose compiler's stability inference suffers from exponential analysis explosion when processing certain type patterns. The `StabilityInferencer` class re-analyzes the same types repeatedly during a compilation session, leading to dramatically increased compilation times.

## Files to Modify

**Primary file:**
- `plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/analysis/Stability.kt`

Look for the `StabilityInferencer` class and its `stabilityOf` methods.

## Required Changes

Add a caching mechanism to prevent redundant stability analysis:

1. **Add a cache field** to `StabilityInferencer` to store results:
   - Key: `SymbolForAnalysis`
   - Value: `Stability`

2. **Modify `stabilityOf(IrClass, ...)` method** to:
   - Check the cache at the start and return cached result if available
   - Store computed results in the cache before returning

3. **Refactor the recursive analysis** into a separate private method:
   - Extract the actual stability computation logic
   - Pass `SymbolForAnalysis` directly instead of rebuilding it
   - This enables proper cache management without recursive cache checks

## Success Criteria

Your fix should:
- Add a `cache` field of type `MutableMap<SymbolForAnalysis, Stability>`
- Check cache at entry to `stabilityOf(IrClass)` and return early if hit
- Store results in cache after computation
- Create a new private `stabilityOf` method that takes the pre-built `SymbolForAnalysis`
- Replace uses of `fullSymbol` with the direct `symbol` parameter in the recursive method
- Maintain all existing stability inference behavior (all existing checks still pass)

## Hints

- Look at how `currentlyAnalyzing` set is used to prevent infinite recursion - the cache serves a similar but distinct purpose for memoization
- The `SymbolForAnalysis` is already constructed in the entry `stabilityOf(IrClass)` method
- The key insight: separate the "cache management" (outer method) from "actual analysis" (inner method)

## Background

This fix addresses bug reports where compilation time would explode exponentially based on type complexity. By caching stability results per symbol during the analysis session, repeated analysis of the same symbol returns instantly from cache.
