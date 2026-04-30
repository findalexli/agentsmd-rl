# Task: Improve CI Workflow Reliability and Add pnpm-upgrade Skill

## Problem

The CI workflows use `pnpm/action-setup` to install the pnpm package manager, but two reliability issues exist:

1. **Floating action versions**: Workflow files reference `pnpm/action-setup` with a floating major-only version tag (`@v4`). Since `@v4` always resolves to the latest v4.x release, CI builds can silently pick up breaking changes from new action releases.

2. **Missing pnpm version pins**: Not every workflow step that invokes `pnpm/action-setup` explicitly declares which pnpm version to install via a `version:` key inside its `with:` block. Without it, the pnpm version installed is whatever that action release defaults to, which creates drift across workflows.

3. **Inconsistent step naming**: The `docs.yml` workflow has its pnpm setup step labeled differently from the same step in the other workflow files. The current label describes what happens after pnpm is installed, not the pnpm installation itself. Match the naming convention established by the other workflow files that use `pnpm/action-setup`.

Additionally, the repository has no documented procedure for upgrading the pnpm toolchain. Other Codex skills in this repo follow a pattern of living under `.codex/skills/<skill-name>/SKILL.md` with YAML frontmatter containing at minimum `name` and `description` fields.

## Requirements

### Workflow hardening

Open every YAML file under `.github/workflows/` that references `pnpm/action-setup`. For each one:

- Replace the floating major-only action tag with a pinned tag that includes both major and minor version components (e.g., `@vX.Y` rather than `@vX`). Do not leave any `pnpm/action-setup` usage at a bare major version.
- Add a `version:` field under `with:` that specifies the exact pnpm version number, if one is not already present. All workflow files that use this action must declare the pnpm version explicitly in their `with:` block.
- Correct the step name in `docs.yml` so it describes pnpm installation rather than dependency installation. Use the naming convention visible in the other workflow files.

### Create the pnpm-upgrade skill

Create a new skill file at `.codex/skills/pnpm-upgrade/SKILL.md`. Base it on the conventions of the other skill files in `.codex/skills/`. The skill should document a repeatable procedure for upgrading the pnpm toolchain. It must cover:

- Updating pnpm itself (using `pnpm self-update`, falling back to `corepack prepare pnpm@latest --activate`)
- Aligning the `packageManager` field in the root `package.json` to the new version
- Querying the GitHub Releases API for the latest `pnpm/action-setup` tag
- Editing workflow files by hand (not with broad regex replacements) to update action tags and pnpm version pins
- Verification steps that confirm the upgrade worked
- A follow-up step specifying the conventional commit message to use and that a PR should be opened

Consult `AGENTS.md` at the repository root for repository conventions on commit message format, code style, and workflow-editing guidelines.

Create the corresponding Codex prompt file at `.github/codex/prompts/pnpm-upgrade.md` that an automated CI job would use to invoke the skill in unattended mode. It should summarize the key steps and instruct the agent not to commit or push changes.
