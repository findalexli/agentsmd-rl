# Task: Add an `antd-commit-msg` Claude skill to the ant-design repo

You are working in the [ant-design/ant-design](https://github.com/ant-design/ant-design) repository, checked out at `/workspace/ant-design`. The maintainers want to add a new Claude Code [skill](https://docs.claude.com/en/docs/claude-code/skills) that auto-generates a one-line git commit message based on the current staged changes and the repository's existing commit style.

The skill must live alongside the existing `.claude/skills/issue-reply/` skill and follow the same authoring conventions used by that file.

## What you must produce

Create exactly two new markdown files at these paths, relative to the repo root:

1. `.claude/skills/commit-msg/SKILL.md` — the skill definition
2. `.claude/skills/commit-msg/references/format-and-examples.md` — reference companion document

Do **not** modify any other file in the repository.

## Required contents of `SKILL.md`

`SKILL.md` is a YAML-frontmatter + Markdown document. The frontmatter (delimited by `---` lines at the very top of the file) must include:

- `name: antd-commit-msg`
- `description:` — a single-string description that explains the skill's purpose **and** lists the trigger phrases the user might use. The description must explicitly mention all three of these triggers: the literal token `msg`, the phrase `commit msg`, and the Chinese phrase `写提交信息`. It must be substantial (at least ~60 characters) so Claude's auto-trigger heuristics can pick it up.

The body of `SKILL.md` (after the frontmatter) must, at minimum:

- Tell the agent to inspect git state by running these four commands (these exact strings must appear in the document so the agent can copy them):
  - `git status --short`
  - `git diff --cached --stat`
  - `git diff --cached`
  - `git log --oneline -10`
- State that the final reply must be a **single line** (一行) commit message — no explanations, no bullet points, no surrounding quotes or backticks — unless the user explicitly asks for reasoning.
- State that the subject line should aim to stay within **72 characters**.
- Enumerate the eight commit `type` values used in the antd repo: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `ci`, `site`.
- Link to the companion reference file via the relative path `references/format-and-examples.md` somewhere near the end of the document.

## Required contents of `references/format-and-examples.md`

This file is plain Markdown (no frontmatter). It must:

- List the same eight `type` values (`feat`, `fix`, `docs`, `refactor`, `chore`, `site`, ...).
- Show at least one concrete commit-message example in the **`type(scope): subject`** form (e.g. `fix(Table): correct pagination when data is empty`) wrapped in inline-code backticks.
- Show at least one concrete commit-message example in the **`scope: subject`** form (e.g. `site: add one-click copy theme code button`) wrapped in inline-code backticks.

## How to model the new skill

The repo already has one Claude skill at `.claude/skills/issue-reply/SKILL.md`. Read it first — your new SKILL.md should follow the same overall shape (YAML frontmatter, then Chinese-language section headers describing the goal, core principles, trigger scenarios, basic rules, execution steps, and prohibitions). Match the tone and structure of that file.

The skill is intended for ant-design maintainers and contributors, so:

- Use Chinese for the body prose (matching the existing `issue-reply` skill style).
- Show the `git ...` commands in fenced bash blocks.
- Reference real antd commit conventions (e.g. that the repo uses both `type(scope): subject` and `scope: subject` forms, and that `site:` is commonly used as a top-level prefix for documentation-site changes).

## Behaviour the skill must encode

When invoked, the skill should make the agent:

1. Read **only the staged changes** by default (`git diff --cached`), not the full working tree.
2. Look at recent commits (`git log --oneline -10`) to mirror the repo's existing style.
3. Refuse to fabricate a message if the staging area is empty.
4. Output exactly one line — no analysis, no markdown, no surrounding punctuation.

## Out of scope

- No changes to source code, build config, tests, or other docs.
- No additional skill files beyond the two listed above.
- No modifications to `AGENTS.md`, `.github/copilot-instructions.md`, or the existing `issue-reply` skill.
