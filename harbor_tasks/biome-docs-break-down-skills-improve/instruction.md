# Improve Agent Skills Organization

## Problem

The `testing-codegen` skill in `.claude/skills/testing-codegen/SKILL.md` has grown too large. It bundles multiple concerns together: snapshot testing, code generation, **and** changeset creation. The changeset creation workflow is complex enough to warrant its own dedicated skill. Additionally, agents keep opening PRs without proper structure, and there is no skill guiding them through the pull request process.

Meanwhile, the `biome-developer` skill (`.claude/skills/biome-developer/SKILL.md`) is missing guidance on how to write code comments. Agents have been observed using comments as a personal whiteboard — tying comments to specific issues or tasks instead of writing comments that help future readers understand the code.

## Expected Behavior

1. **Extract changeset guidance into its own skill.** Create a new `.claude/skills/changeset/SKILL.md` that covers how to create changesets (using a non-interactive command), choose the correct change type (patch/minor/major), write proper changeset descriptions, and follow Biome's formatting conventions. The `testing-codegen` skill should no longer contain changeset instructions — it should reference the new skill instead.

2. **Create a pull-request skill.** Create a new `.claude/skills/pull-request/SKILL.md` that covers branch targeting (main vs next), PR title formatting with conventional commits, the PR template structure, writing good summaries, AI disclosure requirements, and a pre-PR checklist.

3. **Add Code Comments guidance to biome-developer.** Add a section to `.claude/skills/biome-developer/SKILL.md` explaining how to write good code comments — focused on helping future readers, not on documenting the current task or issue being worked on.

4. **Add a non-interactive changeset command.** The existing `just new-changeset` command is interactive and doesn't work with agents. Add a `just new-changeset-empty` recipe to the `justfile` that creates an empty changeset without interaction.

5. **Update the skills catalog.** The `.claude/skills/README.md` should list the new skills in the skills table and directory tree.

## Files to Look At

- `justfile` — build recipes; add the new non-interactive changeset command
- `.claude/skills/testing-codegen/SKILL.md` — extract changeset section, update references
- `.claude/skills/biome-developer/SKILL.md` — add Code Comments section
- `.claude/skills/README.md` — skills catalog; add new entries
- `.claude/skills/changeset/SKILL.md` — new file
- `.claude/skills/pull-request/SKILL.md` — new file
