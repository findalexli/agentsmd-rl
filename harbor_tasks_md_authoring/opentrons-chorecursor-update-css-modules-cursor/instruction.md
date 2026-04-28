# chore(.cursor): update CSS Modules cursor rules

Source: [Opentrons/opentrons#19640](https://github.com/Opentrons/opentrons/pull/19640)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/css-modules.mdc`

## What to add / change

<!--
Thanks for taking the time to open a Pull Request (PR)! Please make sure you've read the "Opening Pull Requests" section of our Contributing Guide:

https://github.com/Opentrons/opentrons/blob/edge/CONTRIBUTING.md#opening-pull-requests

GitHub provides robust markdown to format your PR. Links, diagrams, pictures, and videos along with text formatting make it possible to create a rich and informative PR. For more information on GitHub markdown, see:

https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax

To ensure your code is reviewed quickly and thoroughly, please fill out the sections below to the best of your ability!
-->

# Overview
update CSS Modules cursor rules

close AUTH-2345
<!--
Describe your PR at a high level. State acceptance criteria and how this PR fits into other work. Link issues, PRs, and other relevant resources.
-->

## Test Plan and Hands on Testing

<!--
Describe your testing of the PR. Emphasize testing not reflected in the code. Attach protocols, logs, screenshots and any other assets that support your testing.
-->

## Changelog

<!--
List changes introduced by this PR considering future developers and the end user. Give careful thought and clear documentation to breaking changes.
-->

## Review requests

<!--
- What do you need from reviewers to feel confident this PR is ready to merge?
- Ask questions.
-->

## Risk

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
