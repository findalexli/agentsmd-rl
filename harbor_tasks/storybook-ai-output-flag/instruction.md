# Add --output flag to `storybook ai prepare`

## Problem

The `storybook ai prepare` command generates a markdown prompt with project setup instructions, but it can only print the output to stdout. There is no way to write the output directly to a file, which means users have to use shell redirection (`> file.md`) and lose the informational log messages mixed into the output.

Additionally, CLI options defined on the parent `ai` command (like `--output`) are not passed through to subcommands like `prepare`, because the subcommand's action handler only receives its own options — not its parent's.

## Expected Behavior

- Running `npx storybook ai prepare -o path/to/prompt.md` should write the generated markdown to the specified file and log a confirmation message.
- Running `npx storybook ai prepare` (without `-o`) should continue printing the markdown to the console as before.
- Options defined on the `ai` parent command must be available to subcommand action handlers.

## Files to Look At

- `code/lib/cli-storybook/src/ai/types.ts` — defines the `AiPrepareOptions` interface
- `code/lib/cli-storybook/src/ai/index.ts` — implements the `aiPrepare` function that generates and outputs the markdown
- `code/lib/cli-storybook/src/bin/run.ts` — CLI command definitions using `commander`
