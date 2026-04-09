# Fix Move Compiler Panic on Temporary Variable Borrow Edge Overflow

## Problem

The Move compiler crashes with a panic (Internal Compiler Error - ICE) when compiling specific code patterns involving:
1. Multiple conditional borrows (10+ branches)
2. Temporary variables created from boolean operations
3. The borrow checker hitting an edge case in its overflow handling

The panic message is:
```
ICE invalid use of tmp local <N> with borrows [...]
```

## Files to Modify

The fix should be in:
- `external-crates/move/crates/move-compiler/src/cfgir/borrows/state.rs`

## Expected Behavior

Instead of panicking, the compiler should:
1. Produce proper error messages like "Invalid assignment of temporary variable" and "Invalid move of temporary variable"
2. Handle temporary variables gracefully without crashing
3. Continue processing to report other borrow checking errors

## Test Case

You can reproduce the issue with this Move code pattern:

```move
module 0x42::m;

public fun f(test: bool): &u64 {
    let (a, b, c, d, e, f, g, h, i, j, k) = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);
    let mut x = &a;
    if (test) x = &b;
    if (test) x = &c;
    if (test) x = &d;
    if (test) x = &e;
    if (test) x = &f;
    if (test) x = &g;
    if (test) x = &h;
    if (test) x = &i;
    if (test) x = &j;
    if (test) x = &k;
    test && test;  // This creates a temporary that triggers the bug
    x
}
```

## Hints

1. Look at the `BorrowState` implementation in `state.rs`
2. Search for `DisplayVar::Tmp` handling - there are multiple places where this pattern is matched
3. The fix involves handling temporary variables properly instead of panicking
4. You'll need to add a guard check for `DisplayVar::Orig(_)` variant in at least one location
5. Some existing `panic!` calls should be replaced with `unreachable!()` or proper error formatting

## Verification

After the fix:
- The compiler should not panic on the test case above
- The compiler should produce meaningful error messages
- Existing borrow checker tests should still pass
- The move-compiler crate should build successfully
