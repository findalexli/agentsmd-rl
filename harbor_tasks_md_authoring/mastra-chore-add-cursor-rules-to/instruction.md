# chore: add cursor rules to frontend

Source: [mastra-ai/mastra#9875](https://github.com/mastra-ai/mastra/pull/9875)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `packages/playground-ui/.cursor/rules/frontend.mdc`
- `packages/playground-ui/CLAUDE.md`
- `packages/playground/.cursor/rules/frontend.mdc`
- `packages/playground/CLAUDE.md`

## What to add / change

## Description

Add cursor rules helper for playground and playground-ui packages

## Related Issue(s)

<!-- Link to the issue(s) this PR addresses, using hashtag notation: #123 -->

## Type of Change

- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to change)
- [ ] Documentation update
- [ ] Code refactoring
- [ ] Performance improvement
- [ ] Test update

## Checklist

- [ ] I have made corresponding changes to the documentation (if applicable)
- [ ] I have added tests that prove my fix is effective or that my feature works


<!-- This is an auto-generated comment: release notes by coderabbit.ai -->
## Summary by CodeRabbit

* **Documentation**
  * Added frontend component standards for the UI library and playground: styling rules and token-driven design, Tailwind guidance, component naming and export conventions, React/data-fetching patterns and where fetching belongs, explicit prop typing guidance, state and derived-value best practices, composition-only architecture for the playground, and cross-environment compatibility principles.
<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
