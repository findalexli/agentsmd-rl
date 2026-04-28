# Update CLAUDE.md

Source: [xmtp/libxmtp#2827](https://github.com/xmtp/libxmtp/pull/2827)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

<!-- Macroscope's pull request summary starts here -->
<!-- Macroscope will only edit the content between these invisible markers, and the markers themselves will not be visible in the GitHub rendered markdown. -->
<!-- If you delete either of the start / end markers from your PR's description, Macroscope will post its summary as a comment. -->
### Update CLAUDE.md to add testing guidance and code change requirements for Rust and bindings_node
Add spacing adjustments in Testing Tips, add a bullet to use the `tester!` macro for wallet-reliant tests, introduce Code Change Requirements to run `./dev/lint` for Rust and `yarn` plus `yarn format:check` for `bindings_node`, and note to add new test coverage when appropriate in [CLAUDE.md](https://github.com/xmtp/libxmtp/pull/2827/files#diff-6ebdb617a8104a7756d0cf36578ab01103dc9f07e4dc6feb751296b9c402faf7).

#### 📍Where to Start
Start with the new Code Change Requirements and Testing Tips updates in [CLAUDE.md](https://github.com/xmtp/libxmtp/pull/2827/files#diff-6ebdb617a8104a7756d0cf36578ab01103dc9f07e4dc6feb751296b9c402faf7).

----
<!-- Macroscope's review summary starts here -->

<a href="https://app.macroscope.com">Macroscope</a> summarized a7eea7c.
<!-- Macroscope's review summary ends here -->

<!-- macroscope-ui-refresh -->
<!-- Macroscope's pull request summary ends here -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
