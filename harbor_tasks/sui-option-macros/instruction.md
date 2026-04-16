Add 5 missing macro functions to the Move standard library's `option` module.

The std::option module at `crates/sui-framework/packages/move-stdlib/sources/option.move` is missing several useful utility macros that would make working with Option types more ergonomic in Move.

**What you need to implement:**

1. **`map_mut`** - Transform the contained value via mutable reference
   - Takes `&mut Option<T>` and a function `|&mut T| -> U`
   - Returns `Option<U>`
   - The original Option is preserved (though the value inside may be modified)

2. **`is_none_or`** - Check if None or satisfies predicate
   - Takes `&Option<T>` and a function `|&T| -> bool`
   - Returns `true` if the option is None, OR if the predicate returns true for the contained value

3. **`fold`** - Consume the option and provide default
   - Takes `Option<T>`, a default value of type `$R`, and a function `|T| -> R`
   - Returns the default if None, otherwise applies the function to the contained value
   - Note: the default should only be evaluated if the option is None

4. **`fold_ref`** - Borrow version of fold
   - Takes `&Option<T>`, a default value of type `$R`, and a function `|&T| -> R`
   - Original option is preserved
   - Default only evaluated if option is None

5. **`fold_mut`** - Mutable borrow version of fold
   - Takes `&mut Option<T>`, a default value of type `$R`, and a function `|&mut T| -> R`
   - Default only evaluated if option is None

**Where to add the code:**
Look at the existing macro functions in `crates/sui-framework/packages/move-stdlib/sources/option.move`. The new functions should be added near similar existing macros:
- `map_mut` should go near `map` and `map_ref`
- `is_none_or` should go near `is_some_and`
- `fold`, `fold_ref`, and `fold_mut` should be grouped together (placement is flexible)

**Pattern to follow:**
Study the existing macro definitions like `map_ref` and `is_some_and` to understand:
- How to declare type parameters (`$T`, `$U`, `$R`)
- How to capture parameters with `$o` syntax
- How to use the macro body pattern with `let o = $o;`

**Testing:**
After implementing, verify the code compiles:
```bash
cd crates/sui-framework/packages/move-stdlib
sui move build
```

You do NOT need to add test functions - just implement the macros themselves.
