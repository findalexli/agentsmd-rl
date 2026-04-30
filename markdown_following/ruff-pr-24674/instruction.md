# Optimize Callable Subtype Checking with Positional Argument Fast Path

## Problem

The ty type checker's `TypeRelationChecker` performs detailed per-parameter type comparisons for every source/target callable signature pair. When checking subtype relationships for overloaded callables, overloads whose positional parameter count is incompatible with the target still go through expensive individual parameter type checks before being rejected.

For callables with many overloads at different arities, this results in substantial unnecessary work — a quick positional-argument count comparison would suffice to reject the incompatible overloads.

The `Parameters` struct (representing a function's parameter list) has helper methods for checking specific parameter-list kinds:
- `is_gradual()` — returns `true` if the parameters represent a gradual form
- `is_top()` — returns `true` if the parameters are the top type

The most common case — standard parameter lists — has no dedicated method, requiring callers to match against `ParametersKind::Standard` directly.

## What To Do

1. **Add a standard-parameter-list check to `Parameters`.** Following the pattern of existing `const fn` methods like `is_gradual()` and `is_top()`, add a method that returns `true` when the parameter list is standard (not gradual, top, `ParamSpec`, or `Concatenate`).

2. **Add a fast path in the callable subtype checker.** In the subtype comparison logic for callable signatures, insert an early check before the per-parameter comparison loop that:
   - Verifies both source and target have standard parameter lists
   - Checks if the target callable can accept positional arguments the source cannot provide (because the target has more positional parameters, or has variadic parameters, while the source does not)
   - When the target accepts extra positionals: provides appropriate error context when the source's next parameter after its last positional is keyword-only, then returns early with a "never a subtype" result

3. **Add mdtest fixtures.** In the existing `is_subtype_of.md` test fixture file, add test cases for an overloaded callable with many arity-incompatible overloads. The test should define a callable `many` with five overloads (1 through 5 positional `int` parameters) and verify:
   - `is_subtype_of(RegularCallableTypeOf[many], RegularCallableTypeOf[two_args])` — where `two_args` takes 2 positional `int` parameters
   - `is_subtype_of(RegularCallableTypeOf[many], RegularCallableTypeOf[five_args])` — where `five_args` takes 5 positional `int` parameters
   - `not is_subtype_of(RegularCallableTypeOf[many], RegularCallableTypeOf[six_args])` — where `six_args` takes 6 positional `int` parameters
   - `not is_subtype_of(RegularCallableTypeOf[many], RegularCallableTypeOf[variadic_args])` — where `variadic_args` takes `*args: int`

## Verification

The test suite verifies:
- The new `Parameters` method exists and correctly identifies standard vs. non-standard parameter lists (using `Parameters::empty()` and `Parameters::todo()` as test fixtures)
- The crate compiles without errors (`cargo check -p ty_python_semantic`)
- Existing unit tests continue to pass (`todo_types`)

## Relevant Files

- Callable signature types and subtype checking: `crates/ty_python_semantic/src/types/signatures.rs`
- Subtype test fixtures: `crates/ty_python_semantic/resources/mdtest/type_properties/is_subtype_of.md`
- Repository guidelines: see `AGENTS.md` for development conventions

## Running Tests

```sh
# Check compilation
cargo check -p ty_python_semantic

# Run a specific test
cargo test -p ty_python_semantic -- todo_types

# Run mdtest for a specific file
cargo test -p ty_python_semantic --test mdtest
```
