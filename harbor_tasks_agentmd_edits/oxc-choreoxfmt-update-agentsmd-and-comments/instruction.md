# chore(oxfmt): Update AGENTS.md with Prettier comparison guide

## Task

Update the `apps/oxfmt/AGENTS.md` file to add documentation explaining how to compare oxfmt's formatting output with Prettier.

## What to Add

After the "To manually verify the CLI behavior after building:" section and before the "## Test Organization" section, add a new section titled:

```
## Comparing with Prettier
```

This section should document how users can compare oxfmt's output with Prettier's output using a shared config file. Include:

1. Explanation that a shared config file is needed because oxfmt and Prettier have different default printWidth values
2. Example config file content (JSON format with printWidth: 80)
3. The two commands to run for comparison:
   - oxfmt command using stdin with `--config` and `--stdin-filepath` flags
   - Prettier command using `--config` flag

## Files to Edit

- `apps/oxfmt/AGENTS.md` — Add the new "Comparing with Prettier" section with proper markdown formatting and code examples

## Notes

- The section should use proper markdown formatting with code blocks
- The commands should be practical and copy-paste ready for developers
- This documentation helps contributors verify that oxfmt's output matches or is comparable to Prettier
