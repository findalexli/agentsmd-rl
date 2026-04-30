# docs: setup the AGENTS.md file

Source: [web-infra-dev/rsbuild#6054](https://github.com/web-infra-dev/rsbuild/pull/6054)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`
- `AGENTS.md`

## What to add / change

## Summary

- Setup the AGENTS.md file for coding agents.
- Refine instructions in `.github/copilot-instructions.md`

## Related Links

- https://agents.md/

## Checklist

<!--- Check and mark with an "x" -->

- [ ] Tests updated (or not required).
- [ ] Documentation updated (or not required).

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
