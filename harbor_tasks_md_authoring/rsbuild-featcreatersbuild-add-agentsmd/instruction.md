# feat(create-rsbuild): add AGENTS.md

Source: [web-infra-dev/rsbuild#6440](https://github.com/web-infra-dev/rsbuild/pull/6440)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `packages/create-rsbuild/template-common/AGENTS.md`

## What to add / change

## Summary

Add an `AGENTS.md` file to projects created by `create-rsbuild` to assist coding agents. The current content is fairly basic and will be iterated on based on future feedback.

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
