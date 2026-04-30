# chore: add security guardrails to make-repo-contribution skill

Source: [github/awesome-copilot#746](https://github.com/github/awesome-copilot/pull/746)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/make-repo-contribution/SKILL.md`

## What to add / change

## Tighten security guardrails for make-repo-contribution skill

This PR hardens the `make-repo-contribution` skill against indirect prompt injection — where malicious instructions embedded in a repository's contribution docs (CONTRIBUTING.md, issue templates, PR templates) could be treated as trusted guidance by the agent.

### Changes

**Added `allowed-tools` to frontmatter**
Restricts the skill to `Read`, `Edit`, and scoped Bash commands (`git`, `gh issue`, `gh pr`). This is experimental per the [Agent Skills spec](https://agentskills.io/specification), but declares intent and will take effect as implementations mature.

**Added a security boundaries section**
Placed early in the skill context to establish hard rules: no running commands from repo docs, no accessing files outside the working tree, no network requests, no leaking secrets. Templates are treated as formatting structure, not executable instructions.

**Scoped "follow the guidance" language**
The original skill had broad directives like "ALWAYS defer to the guidance provided in the repository" and "follow whatever guidance is provided." These are now scoped to contribution workflow topics only (branch naming, commit formats, templates, review processes). Instructions outside that scope are flagged to the user.

**Deferred build/test execution to the user**
Rather than running `npm test`, `cargo build`, etc. directly — which would require allowing arbitrary command execution — the skill now identifies prerequisi

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
