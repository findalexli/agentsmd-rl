# 🤖 update agents.md

Source: [SSWConsulting/SSW.CleanArchitecture#601](https://github.com/SSWConsulting/SSW.CleanArchitecture/pull/601)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

﻿> 1. What triggered this change? (PBI link, Email Subject, conversation + reason, etc)

Conversation with @danielmackay and @GordonBeeming 

> 2. What was changed?

Updated the title of the file + removed "copilot instructions" 

<!-- E.g. I worked with @gordonbeeming and @sethdailyssw -->

<!-- 
Check out the relevant rules
- https://www.ssw.com.au/rules/rules-to-better-pull-requests
- https://www.ssw.com.au/rules/write-a-good-pull-request
- https://www.ssw.com.au/rules/over-the-shoulder-prs 
- https://www.ssw.com.au/rules/do-you-use-co-creation-patterns
-->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
