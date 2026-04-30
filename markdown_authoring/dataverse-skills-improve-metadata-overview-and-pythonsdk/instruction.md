# Improve metadata, overview and python-sdk skills based on support agent scenario evaluation

Source: [microsoft/Dataverse-skills#7](https://github.com/microsoft/Dataverse-skills/pull/7)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/plugins/dataverse/skills/metadata/SKILL.md`
- `.github/plugins/dataverse/skills/overview/SKILL.md`
- `.github/plugins/dataverse/skills/python-sdk/SKILL.md`
- `.github/plugins/dataverse/skills/solution/SKILL.md`

## What to add / change

Improves four Dataverse skills based on findings from running the            support agent end-to-end scenario and scoring against the [plugin test       rubric](../dataverse-plugin-test-rubric.md). The changes address the      
   top-scoring gaps: missing environment confirmation, no pull-to-repo
   enforcement, undocumented error codes, and metadata propagation
   pitfalls.

   ### metadata/SKILL.md
   - Add environment confirmation reminder (references overview skill to     
   avoid duplication)
   - Add `FormatName` reference for `StringAttributeMetadata` — documents    
   that `Email` is **not** a valid value
   - Add "Report Logical Names" guidance — after creating columns, surface   
    logical names to the user
   - Add common Web API error codes table (`0x80040216`, `0x80048d19`,       
   `0x80040237`, `0x8004431a`, `0x80060891`)
   - Add metadata propagation delays section with mitigation guidance        
   (wait times, retry patterns)
   - Add mandatory "Session Closing: Pull to Repo" section with solution     
   component verification

   ### overview/SKILL.md
   - Strengthen Multi-Environment Rule to MANDATORY with explicit 3-step     
   confirmation flow
   - Add "Before Any Metadata Change: Confirm Solution" section
   (solution-first workflow)
   - Mark pull-to-repo as MANDATORY

   ### python-sdk/SKILL.md
   - Add `@odata.bind` lookup binding notes (propagation delays, integer     
   values for choices, error recovery)



## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
