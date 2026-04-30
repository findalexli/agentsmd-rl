# Cursor rules for pixel registry definitions

Source: [duckduckgo/apple-browsers#3474](https://github.com/duckduckgo/apple-browsers/pull/3474)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/pixel-definitions.mdc`

## What to add / change

<!--
Note: This template is a reminder of our Engineering Expectations and Definition of Done. Remove sections that don't apply to your changes.

⚠️ If you're an external contributor, please file an issue before working on a PR. Discussing your changes beforehand will help ensure they align with our roadmap and that your time is well spent.
-->

Task/Issue URL: https://app.asana.com/1/137249556945/task/1213143587385064
Tech Design URL:
CC:

### Description

This PR adds a Cursor rules file for pixel registry definitions.

### Testing Steps
<!-- Assume the reviewer is unfamiliar with this part of the app -->
1. Check the included pixel and its definition to verify that it's correct - that pixel was added as a test case, after which I asked Cursor to use the new rules file to write a definition for it
2. Check that the rules are accurate and there's nothing missing

<!-- 
### Testability Challenges
If you encountered issues writing tests due to any class in the codebase, please report it in the [Testability Challenges Document](https://app.asana.com/1/137249556945/project/1204186595873227/task/1211703869786699)

1. **Check the Document:** First, check the **Testability Challenges Table** to see if the class you encountered is listed.
3. **If the Class Exists:**
   - Update the **Encounter Count** by increasing it by 1.
4. **If the Class Does Not Exist:**
   - Add a new entry
-->

### Impact and Risks
<!-- 
What's the impact on users if something 

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
