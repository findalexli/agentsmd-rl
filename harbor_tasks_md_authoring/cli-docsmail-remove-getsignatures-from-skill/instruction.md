# docs(mail): remove get_signatures from skill reference

Source: [larksuite/cli#545](https://github.com/larksuite/cli/pull/545)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/lark-mail/SKILL.md`

## What to add / change

## Summary

- `get_signatures` is not directly exposed as a CLI command — it's wrapped by `+signature`
- Remove the raw `get_signatures` entry from the shortcut reference list and the permissions table in `skills/lark-mail/SKILL.md`

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->

## Summary by CodeRabbit

* **Documentation**
  * Removed the `get_signatures` API method documentation from lark-cli mail.

<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
