# Refine AGENTS.md

Source: [JabRef/jabref#15481](https://github.com/JabRef/jabref/pull/15481)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

Claude Code gets more and more omnipresent.

It offers `CLAUDE.md` to "configure". See https://github.com/hesreallyhim/awesome-claude-code#claudemd-files- for awesome files.

Claude recommends impüroving AGENTS.m (because this is done automatically)

### Steps to test

See Claude working better - haha

### Checklist
- [x] I own the copyright of the code submitted and I license it under the [MIT license](https://github.com/JabRef/jabref/blob/main/LICENSE)
- [/] I manually tested my changes in running JabRef (always required)
- [/] I added JUnit tests for changes (if applicable)
- [/] I added screenshots in the PR description (if change is visible to the user)
- [/] I added a screenshot in the PR description showing a library with a single entry with me as author and as title the issue number
- [/] I described the change in `CHANGELOG.md` in a way that can be understood by the average user (if change is visible to the user)
- [/] I checked the [user documentation](https://docs.jabref.org/) for up to dateness and submitted a pull request to our [user documentation repository](https://github.com/JabRef/user-documentation/tree/main/en)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
