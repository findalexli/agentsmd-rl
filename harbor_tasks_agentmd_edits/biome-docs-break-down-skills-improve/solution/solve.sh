#!/usr/bin/env bash
set -euo pipefail
cd /workspace/biome

if grep -q 'new-changeset-empty' justfile 2>/dev/null; then
    echo "Patch already applied."; exit 0
fi

# The diff is large (new files + modifications), apply in parts for reliability.

# 1. justfile: add new-changeset-empty recipe
sed -i '/^new-changeset:$/,/^$/{
/^$/a\
# Creates a new changeset without interaction\
new-changeset-empty:\
  pnpm changeset --empty\

}' justfile

# 2. Create changeset skill
mkdir -p .claude/skills/changeset
cat > .claude/skills/changeset/SKILL.md <<'SKILLEOF'
---
name: changeset
description: Guide for creating and writing proper changesets for Biome PRs. Use when a PR introduces user-visible changes (bug fixes, new features, rule changes, formatter changes, parser changes) that need a changeset entry for the CHANGELOG. Trigger when creating changesets, writing changeset descriptions, or choosing the correct change type.
compatibility: Designed for coding agents working on the Biome codebase (github.com/biomejs/biome).
---

## Purpose

Use this skill when a PR introduces user-facing changes that require a changeset. Changesets drive CHANGELOG generation and release automation. Internal-only changes (refactors with no user-visible effect) do not need changesets.

## Create a Changeset

**Do not create changeset files manually.** Use:

```shell
just new-changeset-empty
```

The command will create an empty file `.changeset/`. Edit it directly to add detail.

> Requires `pnpm` — run `pnpm i` from repo root first.

## Choose the Correct Change Type

- `patch` — Bug fixes.
- `minor` — New features. PR must target the `next` branch.
- `major` — Breaking user API changes. PR must target the `next` branch. These are rare and strictly controlled.

Refer to the [versioning page](https://biomejs.dev/internals/versioning/) when unsure.

## Changeset Format

```markdown
---
"@biomejs/biome": patch
---

Description here.
```

If you need headers inside the description, use `####` or `#####` only. Other header levels break the CHANGELOG tooling.

## Writing Guidelines

### General Rules

- Write about **user-facing changes only**. No changeset needed for pure refactoring. Describe how the change affects the user.
- Be **concise and clear** — 1 to 3 sentences. Longer entries signal to users that the change deserves attention.
- **Past tense** for what you did: "Added", "Fixed", "Changed".
- **Present tense** for Biome behavior: "Biome now supports...", "The rule now detects...".
- End every sentence with a **full stop** (`.`).

### Bug Fixes

Start with a link to the issue:

```markdown
Fixed [#4444](https://github.com/biomejs/biome/issues/4444): [`useOptionalChain`](https://biomejs.dev/linter/rules/use-optional-chain/) now detects negated logical OR chains.
```

### New Lint Rules

Show an example of an invalid case. Use inline code for simple things, a code block for complex ones:

```markdown
Added a new nursery rule [`noDuplicateSelectors`](https://biomejs.dev/linter/rules/no-duplicate-selectors/), that disallows duplicate selector lists within the same at-rule context.

For example, the following snippet triggers the rule:

` ` `css
.foo {}
.foo {}
` ` `
```

### Changes to Existing Rules

Clearly show what is now invalid that was not before (or vice versa). Show both sides if helpful:

```markdown
Fixed [#7211](https://github.com/biomejs/biome/issues/7211): [`useOptionalChain`](https://biomejs.dev/linter/rules/use-optional-chain/) now detects negated logical OR chains. The following code is now considered invalid:

` ` `js
!foo || !foo.bar
` ` `
```

### Formatter Changes

Show the formatting diff:

```markdown
Changed formatting of arrow function parameters. Example:

` ` `diff
- const fn = (  a,  b  ) => {};
+ const fn = (a, b) => {};
` ` `
```

### Parser Changes

Brief inline example of what can now be parsed:

```markdown
Added support for parsing `using` declarations in JavaScript.
```

Use a code block if multiline clarity helps.

### Linking Rules and Assists

Always link to the website, even if the page does not exist yet (it will after merge):

- Rules: `` [`useConst`](https://biomejs.dev/linter/rules/use-const/) ``
- Assists: `` [`organizeImports`](https://biomejs.dev/assist/actions/organize-imports/) ``

## Tips

- Create the changeset before opening the PR; you can edit it after.
- Look at existing files in `.changeset/` or recent `CHANGELOG.md` entries for reference.
- One changeset per PR is typical. Multiple changesets are allowed if the PR addresses multiple, distinct bugs.

## References

- Contribution guide: `CONTRIBUTING.md` section "Changelog"
- Versioning policy: https://biomejs.dev/internals/versioning/
- Changesets documentation: https://github.com/changesets/changesets
SKILLEOF

# 3. Create pull-request skill
mkdir -p .claude/skills/pull-request
cat > .claude/skills/pull-request/SKILL.md <<'SKILLEOF'
---
name: pull-request
description: Guide for creating proper pull requests for the Biome project. Use when opening a PR, writing a PR description, choosing the correct target branch, or filling out the PR template. Trigger when creating PRs, writing PR summaries, or preparing code for review.
compatibility: Designed for coding agents working on the Biome codebase (github.com/biomejs/biome).
---

## Purpose

Use this skill when creating a pull request for the Biome repository. It covers branch targeting, title formatting, the PR template, and AI disclosure requirements.

## AI Assistance Disclosure

If AI was used in any capacity to produce the PR, **you must disclose it** in the PR description. Examples:

> This PR was written primarily by Claude Code.
>
> I consulted ChatGPT to understand the codebase but the solution was fully authored manually by myself.

This is mandatory. It helps reviewers apply appropriate scrutiny.

## Choose the Target Branch

| Change type | Target branch |
| --- | --- |
| Bug fix (code or docs) | `main` |
| New **nursery** rule | `main` |
| Rule promotion from nursery | `next` |
| New feature (user-facing) | `next` |
| New feature (internal only) | `main` |

## PR Title

Use **conventional commit format**. The title becomes the squash-merge commit message.

```
<type>(<scope>): <short description>
```

Supported prefixes:

- `feat:` — new feature
- `fix:` — bugfix
- `docs:` — documentation update
- `refactor:` — code refactor (no behavior change)
- `test:` — test update
- `chore:` — housekeeping
- `perf:` — performance improvement
- `ci:` — CI change
- `build:` — build system or dependency change
- `revert:` — revert a previous change

Examples:

```
feat(css): add noDuplicateSelectors rule
fix(linter): handle edge case in useOptionalChain
docs: update contributing guide
refactor(parser): simplify HTML attribute parsing
```

The CI runs [action-semantic-pull-request](https://github.com/amannn/action-semantic-pull-request) to validate the title. Fix it if the workflow fails.

## PR Template

The repository has a PR template at `.github/PULL_REQUEST_TEMPLATE.md`. Every PR description must follow this structure:

```markdown
## Summary

<!-- Explain the motivation for this change. What problem does it solve? -->
<!-- Link relevant issues or Discord discussions. -->
<!-- If user-facing, mention the changeset. -->

## Test Plan

<!-- What demonstrates correctness? Mention tests added/updated. -->

## Docs

<!-- For new rules/actions/options: docs are inline in the code (rustdoc). -->
<!-- For other features: link a docs PR to the `next` branch of biomejs/website. -->
```

### Writing a Good Summary

- **Bug fixes**: Explain the fix concisely. If the fix introduces exceptions or unusual code paths, call those out so reviewers know what to watch for.
- **New concepts**: If the PR adds new abstractions, types, or patterns to the codebase, explain the technical design so reviewers can evaluate it.
- **General rule**: Provide enough context for reviewers to understand how to review the PR. The summary serves the reviewer.
- Link related issues: `Fixes #1234` or `Related to #5678`.
- A changeset description is a good starting point, but the summary should add context the changelog alone would not convey (design decisions, trade-offs, scope limitations).

### Test Plan

Keep it brief. Examples:

- "Added new tests from the bug report."
- "Extended existing snapshot tests to cover the new edge case."

Do not list individual test files — the diff speaks for itself. If automated tests were not possible, state that manual testing is required.

### Docs

- New features require documentation. This section is for linking the PR against the `next` branch of [biomejs/website](https://github.com/biomejs/website/).
- Lint rules and helps to carry their own docs as rustdoc in the source code — no separate website PR needed.
- If the PR doesn't need for documentation changes, add `N/A` under the section.

## Pre-PR Checklist

Before opening, ensure:

1. Code compiles: `cargo check`
2. Tests pass: `cargo test` (or `just test-crate <crate>` for scoped runs)
3. Code is formatted: `just f`
4. Lints pass: `just l`
5. Code generation is up to date (CI autofix handles this, but check if unsure):
   - Lint rules: `just gen-rules && just gen-configuration`
   - Grammar: `just gen-grammar <lang>`
   - Bindings: `just gen-bindings`
6. Changeset created (if user-facing change): `just new-changeset-empty`
7. Snapshot tests reviewed: `cargo insta review`

## References

- Contribution guide: `CONTRIBUTING.md` sections "Commit messages" and "Creating pull requests"
- PR template: `.github/PULL_REQUEST_TEMPLATE.md`
- Conventional commits: https://www.conventionalcommits.org/en/v1.0.0-beta.2/
- Versioning policy: https://biomejs.dev/internals/versioning/
SKILLEOF

# 4. Update biome-developer SKILL.md — add Code Comments section after the Clippy section
# Insert after the closing ``` of the let chains example block, before "### Cargo Dependencies"
sed -i '/^### Cargo Dependencies: `workspace = true` vs `path = "\.\.\."`$/i\
### Code Comments\
\
Comments exist for the next developer who reads this code, not for the developer currently writing it.\
\
**DO:**\
- Explain code that is hard to read, or document exceptions and edge cases\
- Provide context when names alone are not descriptive enough\
- Describe the business logic a function implements\
- Clarify contextual words like "normalize" — e.g., "normalize a file path" and "normalize a URL" mean different things; spell out what normalization means here\
\
**DON'\''T:**\
- Do NOT embed the context of the current work into comments. A comment like `// As per issue #1234, we skip this case` ties the code to a transient artifact. Instead, explain *why* the case is skipped in terms any future reader would understand.\
- Do NOT scope comments to the specific trigger that prompted the change. For example, if a bug was reported for Astro but the fix applies broadly, do NOT write `// Fix for Astro embedding`. Write a comment that describes the general condition being handled.\
\
**Think big picture, not current task.** Before writing a comment, ask: "If someone reads this a year from now with no knowledge of the issue or PR, does this comment give them the context they need?"\
\
**Example:**\
```rust\
// WRONG: Carries issue/task context\
// Fix for #5678: Astro files need special handling here\
if is_embedded_script(node) {\
    return normalize_offset(node);\
}\
\
// WRONG: Describes what the code does (the code already says that)\
// Check if the node is an embedded script and normalize the offset\
if is_embedded_script(node) {\
    return normalize_offset(node);\
}\
\
// CORRECT: Explains why and clarifies "normalize"\
// Embedded script blocks (e.g. <script> inside .vue/.svelte/.astro files)\
// report offsets relative to the embedding document, not the script itself.\
// Normalize here means: subtract the script block'\''s start position so the\
// offset is relative to the script content.\
if is_embedded_script(node) {\
    return normalize_offset(node);\
}\
```\
' .claude/skills/biome-developer/SKILL.md

# 5. Update skills README.md — add new skills to table and directory tree
# Update the skills table: replace the testing-codegen line and add changeset + pull-request
sed -i 's/| \*\*\[testing-codegen\](\.\/testing-codegen\/SKILL\.md)\*\* | Run tests, manage snapshots, create changesets, generate code | Any agent |/| **[testing-codegen](\.\/testing-codegen\/SKILL.md)** | Run tests, manage snapshots, generate code | Any agent |\n| **[changeset](\.\/changeset\/SKILL.md)** | Create and write proper changesets for the CHANGELOG | Any agent |\n| **[pull-request](\.\/pull-request\/SKILL.md)** | Create PRs with proper titles, descriptions, and branch targeting | Any agent |/' .claude/skills/README.md

# Add changeset/ to directory tree (after biome-developer/)
sed -i '/├── biome-developer\//a\
│   └── SKILL.md\
├── changeset\/\
│   └── SKILL.md' .claude/skills/README.md 2>/dev/null || true

# Add pull-request/ to directory tree (after parser-development/)
sed -i '/├── parser-development\//a\
│   └── SKILL.md\
├── pull-request\/' .claude/skills/README.md 2>/dev/null || true

# 6. Update testing-codegen SKILL.md — remove changeset section and update references
# Update description
sed -i 's/creating changesets for PRs, managing/managing/' .claude/skills/testing-codegen/SKILL.md
# Update purpose
sed -i 's/Use this skill for testing, code generation, and preparing contributions\. Covers snapshot testing with/Use this skill for testing and code generation. Covers snapshot testing with/' .claude/skills/testing-codegen/SKILL.md
sed -i 's/`insta`, code generation commands, and changeset creation\./`insta` and code generation commands./' .claude/skills/testing-codegen/SKILL.md

# Remove the "Create Changeset" subsection (from "### Create Changeset" to before "### Run Doctests")
sed -i '/^### Create Changeset$/,/^### Run Doctests$/{/^### Run Doctests$/!d}' .claude/skills/testing-codegen/SKILL.md

# Remove changeset timing tip
sed -i '/^- \*\*Changeset timing\*\*: Create before opening PR, can edit after$/d' .claude/skills/testing-codegen/SKILL.md

# Update changeset reference
sed -i "s|- Changeset guide: \`CONTRIBUTING.md\` § Changelog|- Changeset guide: \`../changeset/SKILL.md\`|" .claude/skills/testing-codegen/SKILL.md

echo "Patch applied successfully."
