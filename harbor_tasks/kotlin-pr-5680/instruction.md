# Fix Exponential Explosion in Compose Compiler Stability Inference

The Compose compiler's stability inference has a performance bug that causes exponential explosion in the amount of analyzed types during compilation. When analyzing complex type hierarchies, the same types are analyzed repeatedly without caching, leading to severe compilation slowdowns.

## Task

Identify and fix the performance issue in the stability inference logic within the `StabilityInferencer` class. The fix should prevent redundant analysis of the same types.

## Requirements

The corrected implementation must include:

1. A cache field named `cache` with type `MutableMap<SymbolForAnalysis, Stability>`, initialized as `mutableMapOf()`

2. Cache lookup logic that checks `if (fullSymbol in cache) return cache[fullSymbol]!!` before performing analysis

3. Cache storage logic that stores results with `cache[fullSymbol] = result` after computing them

4. A private `stabilityOf` method with parameters `(declaration: IrClass, symbol: SymbolForAnalysis, substitutions: Map<IrTypeParameterSymbol, IrTypeArgument>, currentlyAnalyzing: Set<SymbolForAnalysis>)` returning `Stability`

5. Cycle detection using `currentlyAnalyzing.contains(symbol)` and recursive tracking using `currentlyAnalyzing + symbol` within the private method

6. Execution order: check cache → compute result if not cached → store result → return
