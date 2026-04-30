# Clarify cargo test command examples in CLAUDE.md

The repository's top-level `CLAUDE.md` documents how to run tests in the inner-loop development workflow. The current examples in the **Inner loop** code block show two `cargo insta test` invocations whose comments are vague and whose syntax is misleading enough to teach the wrong filter pattern.

## What needs to change

Edit the `Inner loop` example block in `CLAUDE.md` so that:

1. The block contains **two** filtered-test examples in addition to the existing `task prqlc:test` line: one for unit tests and one for integration tests.
2. The unit-test example is shown **before** the integration-test example (the faster inner loop runs first).
3. Each example uses the **`--` test-filter separator** form. A bare positional argument after `--lib` (e.g. `--lib some_module::path`) is the wrong syntax for filtering by test name and must not appear; the correct form puts the filter token after a `--` separator.
4. Each example has a comment line directly above it that **specifies what the example demonstrates by filter behavior**, rather than by vague phrasing like "Or run specific tests you're working on" or "Run unit tests for a specific module".
5. The unit-test example must invoke the unit (library) tests of the `prqlc` package and filter to a test name `resolver`.
6. The integration-test example must invoke the integration test binary `integration` of the `prqlc` package and filter to a test name `date`.

The exact comment lines that must label the two examples are:

- `# Unit tests filtered by test name`
- `# Integration tests filtered by test name`

## What must stay unchanged

- The `# Run fast tests on core packages (from project root)` comment and its `task prqlc:test` line at the top of the inner-loop block.
- The **Outer loop** section, including the `task test-all` command.
- All other sections of `CLAUDE.md` (Tests, Running the CLI, Linting, Documentation).
- The fenced code-block structure (no extra or unclosed ``` fences).

## Scope

- Modify `CLAUDE.md` only. No other files in the repository should be touched.
- Do not add new sections, headings, or extra examples beyond the two filtered-test examples requested.
- Keep the existing tone (terse, command-oriented) and Markdown style of the surrounding document.
