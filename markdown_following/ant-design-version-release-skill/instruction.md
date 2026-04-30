# Author a `version-release` skill for ant-design

The ant-design repo organizes its agent-facing playbooks under `.agents/skills/<skill-name>/SKILL.md`. Existing skills include `changelog-collect`, `commit-msg`, `create-pr`, and `issue-reply`. The maintainers want a new skill that documents the **version release** workflow — currently there is no agent-facing guidance for cutting a release of the `antd` npm package.

Your job is to author this missing skill.

## Scope

Create a new file at exactly:

```
.agents/skills/version-release/SKILL.md
```

The file must be a complete, self-contained SKILL.md that an agent could read and use to drive a real ant-design release. Match the structure used by the sibling skills under `.agents/skills/`.

## Required structure

1. **YAML frontmatter at the top of the file**, delimited by `---` lines, with at least:
   - a `name:` field (the skill identifier)
   - a `description:` field (one paragraph explaining when this skill applies, in the same style as the other skills in `.agents/skills/`)

   Inspect any existing `.agents/skills/*/SKILL.md` to see the exact frontmatter shape.

2. **Body in Markdown**, covering the topics below.

## What the skill must cover

The skill should encode ant-design's actual release procedure. Read the repo (especially `package.json` and `.github/workflows/`) to discover the real conventions before writing.

At minimum the skill must address:

- **When the skill applies.** What user requests should trigger it (preparing a release PR, bumping the version, publishing to npm, etc.). Be explicit; agents key off these phrases.
- **Branch selection.** Which base branch to use for new-feature releases vs. for bugfix/docs releases vs. for maintenance-line releases.
- **The release-PR contents.** Which files are manually updated for a release PR. Confirm these against the repo before writing.
- **The validation step before opening the PR.** Inspect `package.json` `scripts` and document the script(s) used to validate changelog content. (One of them is named `lint:changelog`. Use the literal script name as it appears in `package.json`.)
- **The canonical publish command.** Document the actual command used to publish the package to npm and explain why it is the canonical entrypoint (look at the `prepublishOnly` and `postpublish` hooks in `package.json`).
- **Anti-patterns to avoid.** The `package.json` `scripts` block contains an entry called `pub` whose body is a guard against misuse — read what it prints. Document the misuse it warns about, using the literal `npm run pub` form, and explain what the user should do instead.
- **Tagging.** Explain that release tags are pushed automatically by the `postpublish` hook; the agent must not push tags manually before publish.
- **PR title rules.** Note any constraint on PR titles for release/changelog PRs (look in `.github/workflows/` for an existing CI check that validates this).

## Style

- Match the tone and depth of the existing sibling skills (`.agents/skills/create-pr/SKILL.md`, `.agents/skills/changelog-collect/SKILL.md`, etc.). They are written in Chinese with English code identifiers preserved verbatim — follow the same convention.
- Use real script names, file paths, and workflow paths as they exist in the repo at this commit. Do not invent commands or files.
- The file should be substantive (well over 200 characters) and read as production-ready guidance, not a stub.

## Out of scope

- This skill does **not** cover collecting/writing changelog content itself — that is owned by the existing `changelog-collect` skill. Reference it where appropriate, but don't duplicate its responsibilities.
- Do not add release-automation scripts, CI workflows, or version-bump tooling. The deliverable is a single Markdown file.

## What success looks like

After your change:

1. `.agents/skills/version-release/SKILL.md` exists.
2. It has a valid YAML frontmatter block with `name:` and `description:` fields.
3. It documents the release flow using the real script names from the repo: it mentions `npm publish` (the canonical command), `npm run pub` (the misuse the repo guards against), and `lint:changelog` (the changelog validation script).
4. It is consistent in style with the other files under `.agents/skills/`.
