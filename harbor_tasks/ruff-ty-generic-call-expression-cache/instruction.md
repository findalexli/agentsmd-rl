# Excessive runtime for nested generic calls in ty type inference

## Bug Description

The `ty` type checker exhibits exponential runtime blowup when inferring types for deeply nested generic function calls. For example, type-checking a simple chain of nested `OrderedDict` constructor calls takes an unreasonable amount of time:

```python
from collections import OrderedDict

OrderedDict(OrderedDict(OrderedDict(OrderedDict(OrderedDict(OrderedDict(("one", 1)))))))
```

Even modest nesting depths (5-6 levels) cause inference to take 10+ seconds, making `ty` impractical for real-world code that uses nested generic calls.

## Root Cause Area

The issue is in `crates/ty_python_semantic/src/types/infer/builder.rs`, specifically in the generic call inference logic. When `ty` encounters a generic call, it performs speculative inference for each parameter type. For nested generic calls, inner expressions are repeatedly re-inferred with the same type context across different speculative attempts, leading to exponential work.

The method `infer_expression_with_tcx` is called many times with identical `(expression, type_context)` pairs during multi-inference, but results are never cached between speculative inference attempts.

## Expected Behavior

Nested generic calls should type-check in reasonable time, scaling roughly linearly with nesting depth rather than exponentially.

## Relevant Files

- `crates/ty_python_semantic/src/types/infer/builder.rs` — the `TypeInferenceBuilder` struct and its `infer_expression_with_tcx` / generic call inference methods
