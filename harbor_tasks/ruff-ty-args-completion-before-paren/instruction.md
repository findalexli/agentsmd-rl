# ty: Panic in argument completion when cursor is before opening parenthesis

## Bug Description

When using ty's autocomplete feature, placing the cursor between a subscript expression and its call parentheses causes a debug assertion panic. For example, with `list[int]<CURSOR>()`, requesting completions triggers a panic in a debug build.

The problem is in `crates/ty_ide/src/completion.rs`, in the `add_argument_completions` function. This function walks the ancestor nodes of the cursor's covering node looking for `ExprCall` nodes. When it finds one, it checks whether the cursor is inside the call's arguments using a range containment check. However, when the cursor is positioned *before* the opening parenthesis (not inside the arguments at all), this range check can produce incorrect results — the cursor's covering node ancestry doesn't pass through the `Arguments` node, yet the code still tries to check argument range containment against the cursor position.

## Relevant Code

- `crates/ty_ide/src/completion.rs` — the `add_argument_completions` function (around line 1394)
- Look at how `ExprCall` is matched during ancestor walking and how the cursor's position relative to the arguments is determined

## Expected Behavior

Requesting completions at `list[int]<CURSOR>()` should not panic. It should gracefully determine that the cursor is not inside the call arguments and skip argument completions.

## Actual Behavior

A debug assertion panic occurs when the range containment check encounters a cursor position that is outside the arguments node.
