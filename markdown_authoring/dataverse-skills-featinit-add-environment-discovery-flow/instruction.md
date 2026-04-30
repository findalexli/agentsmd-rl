# feat(init): add Environment Discovery flow for smarter env selection/creation

Source: [microsoft/Dataverse-skills#10](https://github.com/microsoft/Dataverse-skills/pull/10)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/plugins/dataverse/skills/init/SKILL.md`

## What to add / change

## Problem

The init skill asks 'What is your Dataverse environment URL?' and blocks until the user answers. This creates a poor UX when:

1. The user doesn't know the URL but has PAC CLI authenticated (the agent should just check)
2. The user wants to **create a new environment** (the skill has zero guidance for this)
3. The user wants to **pick from existing environments** (no listing flow exists)

In practice this caused **4+ unnecessary back-and-forth exchanges** before the agent finally ran `pac auth list` and discovered the environments.

## Solution

Added an **Environment Discovery** section to `init/SKILL.md` that both Scenarios A and B reference:

- Proactively checks `pac auth list` + `pac env list` before asking questions
- Presents 3 choices: use active environment, pick from list, or create new
- Handles `pac admin create` for new environments (with name/type/region)
- Connects and confirms before proceeding

Also optimizes tenant ID discovery by parsing `pac org who` output (which already contains the tenant ID) instead of making a separate HTTP request.

## Changes

- `.github/plugins/dataverse/skills/init/SKILL.md` (+112/-47)
  - New **Environment Discovery** section before both scenarios
  - Scenario A step 6: references discovery flow instead of blind asking
  - Scenario B step 2: discovery-first flow replaces 'ask URL and block'
  - Scenario B step 6: simplified to verification only
  - Fixed stale MCP step references in header
  - Added trigger phrases: '

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
