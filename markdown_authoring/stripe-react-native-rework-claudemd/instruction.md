# Rework CLAUDE.md

Source: [stripe/stripe-react-native#2402](https://github.com/stripe/stripe-react-native/pull/2402)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/add-native-feature/SKILL.md`
- `CLAUDE.md`

## What to add / change

## Summary
Trimmed CLAUDE.md from ~610 lines to ~27 lines based on the [best practices guide](https://code.claude.com/docs/en/best-practices):

  - **Removed** architecture overview, directory descriptions, and duplicated dev commands (already in CONTRIBUTING.md).

  > Exclude "Anything Claude can figure out by reading code" and "File-by-file descriptions of the codebase"

  - **Moved** ~460-line native feature tutorial to `.claude/skills/add-native-feature/SKILL.md`. A separate PR can verify tutorial quality and decide if it should also be human-facing docs.

  > "For domain knowledge or workflows that are only relevant sometimes, use skills instead. Claude loads them on demand without bloating every conversation."

  - **Kept** only what Claude gets wrong without being told: `GH_HOST` env quirk (verified real), old-arch patch gotcha, test commands not covered by pre-commit hooks.


## Testing
<!-- Did you test your changes? Ideally you should check both of the following boxes. -->
- [x] I tested this manually
- [ ] I added automated tests
<!-- Ignored Tests: Did you newly ignore a test in this PR?  If so, please open an R4 incident so that the test can be re-enabled as soon as possible-->

## Documentation

Select one: 
- [ ] I have added relevant documentation for my changes.
- [x] This PR does not result in any developer-facing changes.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
