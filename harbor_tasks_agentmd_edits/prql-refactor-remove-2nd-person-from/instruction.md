# Remove 2nd person pronouns from error messages

## Problem

Several error and hint messages in the PRQL compiler use 2nd person pronouns ("you", "your") which can sound accusatory or overly informal. For example:

- `"you can only use column names with self-equality operator"` in the semantic AST expansion
- `"are you missing \`from\` statement?"` and `"did you forget to specify the column name?"` in the lowering pass
- `"Have you forgotten an argument ..."` in the type resolver

These should be reworded to avoid addressing the user directly, using softer modal verbs like "might" for hints and direct imperative statements for hard constraints.

## Expected Behavior

All compiler error and hint messages should avoid 2nd person pronouns. Hints should use a friendlier tone with modal verbs (e.g., "X might be missing?"), while hard constraint errors should use imperative form (e.g., "X requires Y").

Any inline test snapshots that contain these messages must also be updated to match.

## Documentation

After updating the error messages, the project's `CLAUDE.md` should be updated to document these error message style guidelines so that future contributors follow the same conventions.

## Files to Look At

- `prqlc/prqlc/src/semantic/ast_expand.rs` — error messages for self-equality operator
- `prqlc/prqlc/src/semantic/lowering.rs` — hint messages for missing `from` and column names
- `prqlc/prqlc/src/semantic/resolver/types.rs` — hint message for missing arguments
- `prqlc/prqlc/tests/integration/bad_error_messages.rs` — snapshot tests for error output
- `prqlc/prqlc/tests/integration/sql.rs` — snapshot test for table reference errors
- `CLAUDE.md` — project conventions and guidelines
