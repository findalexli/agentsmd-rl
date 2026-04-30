# chore: Add AGENTS.md

Source: [conda/rattler#2067](https://github.com/conda/rattler/pull/2067)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/CLAUDE.md`
- `AGENTS.md`

## What to add / change

### Description

<!--- Please include a summary of the change and which issue is fixed. --->
<!--- Please also include relevant motivation and context. -->

<!--- Add visual representation of the effect of the change when possible, e.g. before and after screenshots, code snippets, etc. --->

As discussed on discord.

### How Has This Been Tested?

<!-- Please describe the tests that you ran to verify your changes. Provide instructions so we can reproduce while reviewing your changes. -->

### AI Disclosure
<!--- Remove this section if your PR does not contain AI-generated content. --->
- [x] This PR contains AI-generated content.
  - [x] I have tested any AI-generated content in my PR.
  - [x] I take responsibility for any AI-generated content in my PR.
<!--- If you used AI to generate code, please specify the tool used and the prompt below. --->
Tools: Claude

### Checklist:
<!--- Remove the non relevant items. --->
- [x] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] I have added sufficient tests to cover my changes.

<!-- Just as a reminder, everyone in all conda org spaces (including PRs)
     must follow the Conda Org Code of Conduct (link below).

     Finally, once again, thanks for your time and effort. If you have any
     feedback in regards to your experience contributing here, please
     let us

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
