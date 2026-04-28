# Add Copilot coding agent instructions

Source: [HaxeFoundation/haxe#12611](https://github.com/HaxeFoundation/haxe/pull/12611)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

## Setup Copilot Instructions for the Haxe Repository

- [x] Research and understand Copilot instructions best practices
- [x] Create `.github/copilot-instructions.md` file with:
  - [x] Repository overview and purpose
  - [x] Build and development setup instructions
  - [x] Testing guidelines
  - [x] Code style and conventions
  - [x] Common tasks and workflows
  - [x] Important context about the Haxe compiler
- [x] Review and validate the instructions
- [x] Address code review feedback
- [x] Address PR comments from maintainer:
  - [x] Clarify std library structure with platform-independent packages and shadowing mechanism
  - [x] Expand test directory descriptions
  - [x] Clarify regression test patterns for success vs failure cases

<!-- START COPILOT ORIGINAL PROMPT -->



<details>

<summary>Original prompt</summary>

> 
> ----
> 
> *This section details on the original issue you should resolve*
> 
> <issue_title>✨ Set up Copilot instructions</issue_title>
> <issue_description>Configure instructions for this repository as documented in [Best practices for Copilot coding agent in your repository](https://gh.io/copilot-coding-agent-tips).
> 
> <Onboard this repo></issue_description>
> 
> ## Comments on the Issue (you are @copilot in this section)
> 
> <comments>
> </comments>
> 


</details>



<!-- START COPILOT CODING AGENT SUFFIX -->

- Fixes HaxeFoundation/haxe#12610

<!-- START COPILOT CODING AGENT TIPS -->
---

💬 We'd love your input! Share your thoughts on Copilot 

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
