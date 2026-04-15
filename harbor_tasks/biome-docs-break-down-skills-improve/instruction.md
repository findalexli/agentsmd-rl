# Improve Agent Skills Organization

## Problem

The `testing-codegen` skill in `.claude/skills/testing-codegen/SKILL.md` has grown too large. It bundles multiple concerns together: snapshot testing, code generation, **and** changeset creation. The changeset creation workflow is complex enough to warrant its own dedicated skill. Additionally, agents keep opening PRs without proper structure, and there is no skill guiding them through the pull request process.

Meanwhile, the `biome-developer` skill (`.claude/skills/biome-developer/SKILL.md`) is missing guidance on how to write code comments. Agents have been observed using comments as a personal whiteboard — tying comments to specific issues or tasks instead of writing comments that help future readers understand the code.

## Expected Behavior

### 1. Extract changeset guidance into its own skill

Create a new `.claude/skills/changeset/SKILL.md` with YAML frontmatter containing the fields `name`, `description`, and `compatibility` (where `name` must be `changeset`). The body must include the following sections:

- `## Purpose` — explaining when to use this skill
- `## Changeset Format` — describing the changeset file structure
- `## Writing Guidelines` — covering how to write changeset descriptions, with guidance for the three change types: `patch`, `minor`, and `major`
- A reference to `just new-changeset-empty` as the non-interactive command for creating changesets

### 2. Create a pull-request skill

Create a new `.claude/skills/pull-request/SKILL.md` with YAML frontmatter containing the fields `name`, `description`, and `compatibility` (where `name` must be `pull-request`). The body must include the following sections:

- `## AI Assistance Disclosure` — mandatory disclosure requirements when AI is used
- `## Choose the Target Branch` — branch targeting rules (main vs next)
- `## PR Title` — formatting with conventional commits
- `## Pre-PR Checklist` — pre-submission checklist

### 3. Add Code Comments guidance to biome-developer

Add a `### Code Comments` subsection to `.claude/skills/biome-developer/SKILL.md` with:
- `**DO:**` and `**DON'T:**` labeled guidance items
- The principle that comments should help the next developer or future reader understand the code
- Code examples marked `WRONG` and `CORRECT` to illustrate the difference between task-scoped comments and reader-focused comments

### 4. Add a non-interactive changeset command

Add a `new-changeset-empty` recipe to the `justfile` that invokes `pnpm changeset --empty`.

### 5. Clean up testing-codegen skill

In `.claude/skills/testing-codegen/SKILL.md`:
- Remove the `### Create Changeset` subsection (extracted to the new skill)
- Add a reference to `changeset/SKILL.md` for changeset guidance
- Update the frontmatter `description` field so it does not mention "changeset"

### 6. Update the skills catalog

In `.claude/skills/README.md`:
- Add the `changeset` and `pull-request` skills to the skills table
- Update the testing-codegen table entry so it does not say "create changesets"
- Add `changeset/` and `pull-request/` entries to the directory tree

## Files to Look At

- `justfile` — build recipes; add the new non-interactive changeset command
- `.claude/skills/testing-codegen/SKILL.md` — extract changeset section, update references
- `.claude/skills/biome-developer/SKILL.md` — add Code Comments section
- `.claude/skills/README.md` — skills catalog; add new entries
- `.claude/skills/changeset/SKILL.md` — new file
- `.claude/skills/pull-request/SKILL.md` — new file
