# Task: Fix Stability Inference Performance in Compose Compiler

## Problem Description

The Compose compiler's `StabilityInferencer` class can experience exponential explosion in the amount of analyzed types during compilation. This leads to unnecessarily long compilation times, especially for code with complex generic type hierarchies.

The root cause is that stability inference results are not cached during a compilation session, causing the same types to be re-analyzed multiple times.

## What You Need to Do

The `StabilityInferencer` class needs to cache stability inference results during a compilation session to avoid re-analyzing the same types multiple times.

Key requirements:

1. **Cache field**: The solution must include a cache field declared exactly as:
   ```kotlin
   private val cache = mutableMapOf<SymbolForAnalysis, Stability>()
   ```

2. **Cache lookup**: Before computing stability, check if the result is already cached using `fullSymbol` as the key. If `fullSymbol in cache`, return `cache[fullSymbol]!!`

3. **Cache storage**: After computing stability for `fullSymbol`, store the result with `cache[fullSymbol] = result`

4. **Refactored method signature**: The stability inference logic should be refactored so that the public entry point checks the cache, then delegates to a new private method with this exact signature:
   ```kotlin
   private fun stabilityOf(
       declaration: IrClass,
       symbol: SymbolForAnalysis,
       substitutions: Map<IrTypeParameterSymbol, IrTypeArgument>,
       currentlyAnalyzing: Set<SymbolForAnalysis>
   ): Stability
   ```

5. **Circular dependency detection**: In the new private method, the check for circular dependencies must use the `symbol` parameter (not `fullSymbol`) when calling `currentlyAnalyzing.contains(symbol)`. The `analyzing` set should be built as `currentlyAnalyzing + symbol`.

## Hints

- The issue is in the Compose compiler's analysis module
- Look for the `StabilityInferencer` class and how it currently handles recursive type analysis
- The `SymbolForAnalysis` class is used as a key to identify types being analyzed
- The "currently analyzing" set is used to detect circular type dependencies (which would be unstable)
- You'll need to understand how the stability inference currently works before adding caching

## Expected Outcome

After your changes, the `StabilityInferencer` should:
- Have a cache field mapping `SymbolForAnalysis` to `Stability` results
- Check the cache before doing expensive stability analysis
- Store computed results in the cache
- Still correctly detect circular dependencies (which indicate unstable types)
- Pass all existing Compose compiler tests

## Agent Guidelines

- Follow Kotlin coding conventions
- Ensure binary compatibility (prefer private/internal changes)
- The Compose compiler is part of the larger Kotlin compiler infrastructure
- Be careful with recursive type analysis - the circular dependency detection must still work correctly
