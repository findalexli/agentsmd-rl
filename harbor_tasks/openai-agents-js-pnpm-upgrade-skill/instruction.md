# Add a `pnpm-upgrade` skill and a daily upgrade workflow

The `openai/openai-agents-js` monorepo manages its toolchain with **pnpm** and pins `pnpm/action-setup` in every CI workflow. Today there is no documented procedure for refreshing those pins, and the existing workflows reference `pnpm/action-setup@v4` (a floating major-version tag rather than a SemVer pin). Both are gaps the maintainers want closed.

You are working from the repo root (`/workspace/openai-agents-js`). Add a Codex skill that documents the upgrade procedure, an automation prompt, a scheduled GitHub Actions workflow that runs the skill, and pin the existing workflows to specific `pnpm/action-setup` tags.

## What to deliver

### 1. New skill: `.codex/skills/pnpm-upgrade/SKILL.md`

A Markdown file with **YAML frontmatter** (terminated by `---`) at the top declaring at least:

- `name: pnpm-upgrade`
- `description:` — a multi-sentence description that mentions, in plain prose: running `pnpm self-update` (or the corepack fallback), aligning `packageManager` in `package.json`, and bumping `pnpm/action-setup` in `.github/workflows`.

The body must lay out the upgrade steps. It must explicitly cover:

- **Update pnpm locally.** Try `pnpm self-update`; if that fails or pnpm is missing, fall back to `corepack prepare pnpm@latest --activate`. Capture the resulting version.
- **Align `package.json`.** Set the `packageManager` field to `pnpm@<captured-version>`, preserving formatting.
- **Discover the latest `pnpm/action-setup` tag.** The skill must instruct querying the GitHub Releases API at `https://api.github.com/repos/pnpm/action-setup/releases/latest` (and may suggest using `GITHUB_TOKEN`/`GH_TOKEN` for higher rate limits). Hard-coded tags are not acceptable.
- **Update each workflow under `.github/workflows/` that uses `pnpm/action-setup`** by hand — set the `uses:` tag to the discovered version and, where a `with: version:` field exists, set it to the captured pnpm version. The skill must explicitly **warn against blanket regex / multiline sed-style replacements** across files. Acceptable phrasings include "no broad regex", "no blanket regex", "blunt search/replace", or "avoid multiline sed".

### 2. New prompt: `.github/codex/prompts/pnpm-upgrade.md`

A short Markdown prompt for the scheduled CI run that points the Codex agent at the `pnpm-upgrade` skill. It must reference the skill by name and reference the `PNPM_VERSION` capture step (the prompt is what the workflow feeds to Codex via `prompt-file:`).

### 3. New workflow: `.github/workflows/pnpm-upgrade.yml`

A GitHub Actions workflow that:

- Triggers on a `schedule:` (a daily `cron:` entry) **and** on `workflow_dispatch:` for manual runs.
- Sets up Node.js, enables Corepack, installs `jq`.
- Calls `openai/codex-action` with `prompt-file: .github/codex/prompts/pnpm-upgrade.md` and `codex-args: --skill pnpm-upgrade --full-auto --max-steps 200` (or compatible — the `--skill pnpm-upgrade` token must appear).
- After the Codex step succeeds, opens a pull request via `peter-evans/create-pull-request`. The commit message and PR title must be the literal string `chore: upgrade pnpm toolchain` (Conventional Commits — see `AGENTS.md`).

### 4. Pin existing workflows

Every workflow under `.github/workflows/` that currently references `pnpm/action-setup@v4` must be updated to pin a specific SemVer tag of the form `vX.Y.Z` (or a 40-character commit SHA). Bare `@v4` / `@v3` is not acceptable. The five workflows that need pinning are:

- `.github/workflows/changeset.yml`
- `.github/workflows/docs.yml`
- `.github/workflows/release.yml`
- `.github/workflows/test.yml`
- `.github/workflows/update-docs.yml`

Where a workflow does not yet declare `with: version:` for `pnpm/action-setup` but the upgrade procedure expects it, add the field with the current pinned pnpm version that the rest of the repo uses (look at peer workflows for the value to use).

## Constraints

- Keep workflow edits minimal — touch only the `pnpm/action-setup` block (and its `with:` keys), never adjacent steps.
- All YAML must continue to parse (no unbalanced quoting, no broken indentation).
- Follow the repository's existing `.codex/skills/*/SKILL.md` style. Look at the other skills (e.g. `.codex/skills/changeset-validation/SKILL.md`, `.codex/skills/code-change-verification/SKILL.md`) for the frontmatter shape and tone.
- Do not modify unrelated files.

## Code Style Requirements

This task is documentation and YAML only — no JavaScript/TypeScript build or lint is invoked by the verifier. The `AGENTS.md` Conventional-Commits rule still applies to any commit messages written into the workflow (`chore: upgrade pnpm toolchain`).
