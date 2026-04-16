# Task: Reduce CPU overhead in Pulumi Python SDK type system

## Problem

The Pulumi Python SDK incurs significant CPU overhead during serialization because several functions are called repeatedly but recompute identical results for a given class each time. This overhead compounds during bulk serialization operations.

## Goal

Identify and eliminate the repeated computation overhead in the SDK's type system by adding caching where appropriate.

## Verification Criteria

Your implementation must satisfy all of the following:

### 1. Repeated computations must be cached

The SDK must cache results of repeated computations. The cache implementation must:
- Expose a `cache_info()` method that returns a namedtuple with `hits`, `misses`, `maxsize`, and `currsize` attributes
- Expose a `cache_clear()` method to reset the cache
- Return the same object instance when called with the same arguments
- Return immutable results (sequences, not lazy iterators)

### 2. Module-level caches in the runtime type system

The module `pulumi.runtime.known_types` must store class-reference caches at module level. The cache variable names that must exist are:
- `_Asset`
- `_Archive`
- `_Resource`
- `_CustomResource`
- `_CustomTimeouts`
- `_Stack`
- `_Output`

These cache variables are used internally by type-checker functions and must be populated lazily on first use.

### 3. Existing functionality preserved

The existing SDK tests must continue to pass:
- Unit tests in `lib/test/test_types.py`, `lib/test/test_types_input_type.py`, `lib/test/test_types_output_type.py`
- Serialization tests in `lib/test/test_next_serialize.py`
- Linting with `ruff` on the modified files
- Type-checking with `mypy` on the modified files

## Files to Examine

Focus on Python SDK type system files:
- `sdk/python/lib/pulumi/_types.py`
- `sdk/python/lib/pulumi/runtime/known_types.py`

## Approach

Profile or trace the SDK during serialization to identify functions that are called repeatedly with identical arguments. Apply caching to those functions. Ensure cached results are immutable to prevent accidental mutation.

Your solution will be validated by running the test suite and checking that the caching behavior is correctly implemented.