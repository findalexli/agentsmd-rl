# Add additional `option` macro functions to Move stdlib

The `std::option` module in the Sui Framework is missing several useful macro functions that would make working with `Option` types more ergonomic. You need to implement five new macro functions.

## What you need to do

Add the following macro functions to `crates/sui-framework/packages/move-stdlib/sources/option.move`:

### 1. `map_mut`
Map an `Option<T>` to `Option<U>` by applying a function to a contained value by **mutable reference**. The original `Option<T>` should be preserved, though potentially modified.

- Signature: `public macro fun map_mut<$T, $U>($o: &mut Option<$T>, $f: |&mut $T| -> $U): Option<$U>`
- Should return `Some(f(value))` if the option is `Some`, otherwise `None`

### 2. `is_none_or`
Return `true` if the value is `None`, or if the predicate returns `true` for the contained value.

- Signature: `public macro fun is_none_or<$T>($o: &Option<$T>, $f: |&$T| -> bool): bool`
- Should return `true` for `None`, otherwise apply the predicate to the contained value

### 3. `fold`
Consume the option and return a default value if it is `None`, otherwise apply a function to the contained value.

- Signature: `public macro fun fold<$T, $R>($o: Option<$T>, $none: $R, $some: |$T| -> $R): $R`
- The `$none` value should only be evaluated if the option is `None`
- Should consume the option using `destroy_some()` and `destroy_none()`

### 4. `fold_ref`
Apply a function to the borrowed value if `Some`, otherwise return a default value. The original option is preserved.

- Signature: `public macro fun fold_ref<$T, $R>($o: &Option<$T>, $none: $R, $some: |&$T| -> $R): $R`
- The `$none` value should only be evaluated if the option is `None`

### 5. `fold_mut`
Apply a function to the mutably borrowed value if `Some`, otherwise return a default value.

- Signature: `public macro fun fold_mut<$T, $R>($o: &mut Option<$T>, $none: $R, $some: |&mut $T| -> $R): $R`
- The `$none` value should only be evaluated if the option is `None`

## Requirements

1. Add appropriate doc comments for each macro explaining the behavior
2. Follow the existing macro patterns in the file (look at `map`, `map_ref`, `is_some_and` for reference)
3. Add unit tests in `crates/sui-framework/packages/move-stdlib/tests/option_tests.move` that cover:
   - The `Some` case for each function
   - The `None` case for each function
   - Mutation side effects for `map_mut` and `fold_mut`
   - **For `map_mut` tests**: Use mutation pattern `*x = 100` to verify the mutable reference works. Example: `opt.map_mut!(|x| { *x = 100; vector[*x] })`
   - **For `is_none_or` tests**: Test both matching and non-matching predicates using `*x == 5` (matching) and `*x == 6` (non-matching)
   - **For `fold` tests**: Use `option::some(5u64).fold!` and `option::none<u64>().fold!` with a value like `0` for the `$none` parameter

## Files to modify

- `crates/sui-framework/packages/move-stdlib/sources/option.move` - Add the 5 new macro functions
- `crates/sui-framework/packages/move-stdlib/tests/option_tests.move` - Add tests for the new functions

## Implementation notes

- `fold_ref` implementation must use `o.borrow()` (not `destroy_some()`) to borrow the option value
- `fold_mut` implementation must use `o.borrow_mut()` for mutable borrow
- `map_mut` should return `Some(f(value))` if the option is `Some`, otherwise `None`

## Hints

- Look at existing macros like `map_ref` and `is_some_and` to understand the pattern
- The macro syntax uses `$` prefix for type parameters and macro-local variables
- For consuming options, use `destroy_some()` and `destroy_none()`
- For borrowing, use `borrow()` and `borrow_mut()`
- Make sure to run `cargo build -p sui-framework` to verify your changes compile

## Testing

After implementing the functions, verify they work by running:

```bash
cargo test -p sui-framework -- option
```

All option-related tests should pass.
