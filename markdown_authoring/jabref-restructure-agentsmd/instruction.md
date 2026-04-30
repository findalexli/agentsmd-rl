# Restructure AGENTS.md

Source: [JabRef/jabref#14635](https://github.com/JabRef/jabref/pull/14635)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

Follow-up https://github.com/JabRef/jabref/pull/14316

### Steps to test

Use Claude and JabRef code base

### Mandatory checks

<!--
Go through the checklist below. It is mandatory, even for a draft pull request.

Keep ALL the items. Replace the dots inside [.] and mark them as follows: 
[x] done 
[ ] TODO (yet to be done)
[/] not applicable
-->

- [x] I own the copyright of the code submitted and I license it under the [MIT license](https://github.com/JabRef/jabref/blob/main/LICENSE)
- [/] I manually tested my changes in running JabRef (always required)
- [/] I added JUnit tests for changes (if applicable)
- [/] I added screenshots in the PR description (if change is visible to the user)
- [/] I described the change in `CHANGELOG.md` in a way that is understandable for the average user (if change is visible to the user)
- [/] I checked the [user documentation](https://docs.jabref.org/): Is the information available and up to date? If not, I created an issue at <https://github.com/JabRef/user-documentation/issues> or, even better, I submitted a pull request updating file(s) in <https://github.com/JabRef/user-documentation/tree/main/en>.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
