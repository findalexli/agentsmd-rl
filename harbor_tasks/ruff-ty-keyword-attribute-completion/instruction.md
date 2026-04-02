# ty: Attribute completion missing for keyword-prefixed names

## Bug Description

When using ty's autocompletion for attribute access on objects, completions fail to appear when the partially-typed attribute name happens to match a Python keyword.

For example, given a set literal `{1}`, typing `{1}.is` and triggering completion should suggest attributes like `isdisjoint`, `issubset`, etc. However, no completions are returned.

The root cause is in `crates/ty_ide/src/completion.rs`. The Python lexer tokenizes partially-typed attribute names as keyword tokens when they happen to match a keyword. For example, `is` gets lexed as `TokenKind::Is` rather than `TokenKind::Name`. The completion logic currently only recognizes `TokenKind::Name` tokens after a dot, so it silently drops these cases.

This affects any attribute prefix that matches a Python keyword — `is`, `in`, `for`, `not`, `and`, `or`, `as`, `if`, `import`, etc.

## Relevant Code

- `crates/ty_ide/src/completion.rs` — The `ContextCursor` methods and `CompletionTargetTokens::find` function
- Look at how tokens after the dot are matched in `CompletionTargetTokens::find` and how the cursor determines valid completion positions

## Expected Behavior

Typing `{1}.is` should produce completions like `isdisjoint`, `issubset`, `issuperset`, etc.

## Actual Behavior

No completions are returned when the partially-typed attribute name happens to be a Python keyword token.
