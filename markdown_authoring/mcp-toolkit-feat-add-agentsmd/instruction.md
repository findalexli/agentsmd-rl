# feat: add `AGENTS.md`

Source: [nuxt-modules/mcp-toolkit#44](https://github.com/nuxt-modules/mcp-toolkit/pull/44)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

<!---
☝️ PR title should follow conventional commits (https://conventionalcommits.org)
Here are the available types and scopes:


### Types
- breaking (fix or feature that would cause existing functionality to change) 💥
- feat (a non-breaking change that adds functionality) ✨
- fix (a non-breaking change that fixes an issue) 🐞
- build (changes that affect the build system or external dependencies) 🏗
- ci (changes to our CI configuration files and scripts) 🚀
- docs (updates to the documentation or readme) 📖
- enhancement (improving an existing functionality) 🌈
- chore (updates to the build process or auxiliary tools and libraries) 📦
- perf (a code change that improves performance) ⚡️
- style (changes that do not affect the meaning of the code) 💅
- test (adding or updating tests) 🧪
- refactor (a code change that neither fixes a bug nor adds a feature) 🛠
- revert (reverts a previous commit) 🔄

### Scopes
- docs (the documentation)
- playground (the playground)
- module (the module)
-->

### 🔗 Linked issue

<!-- If it resolves an open issue, please link the issue here. For example "Resolves #123" -->

### 📚 Description

<!-- Describe your changes in detail -->
<!-- Why is this change required? What problem does it solve? -->

### 📝 Checklist

<!-- Put an `x` in all the boxes that apply. -->
<!-- If your change requires a documentation PR, please link it appropriately -->
<!-- If you're unsure about any of these, don't hesitate to ask. We're 

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
