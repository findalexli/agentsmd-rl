# Migrate from Prettier to oxfmt

## Problem

The Mantine monorepo currently uses `prettier` (with `@ianvs/prettier-plugin-sort-imports`) for code formatting. The project wants to switch to `oxfmt`, a faster Rust-based formatter that handles import sorting natively.

The migration involves:
1. Replacing the prettier dependency with oxfmt in `package.json`
2. Creating an oxfmt config file (`.oxfmtrc.json`) that preserves the same formatting rules — print width, quote style, trailing commas, and import sort order
3. Renaming the npm scripts from `prettier:*` to `format:*` (and updating all internal references like `test:all`)
4. Removing the old prettier config files (`.prettierrc.mjs`, `.prettierignore`)
5. Updating the VS Code settings and `scripts/utils/chmod.sh` to reference the new tool

After making the code and configuration changes, update the project's agent instruction files to reflect the new formatter. The `CLAUDE.md`, skill files under `.claude/skills/`, and `llms/testing.md` all reference prettier commands that agents use — these must be updated so that agents run the correct formatting commands going forward.

## Files to Look At

- `package.json` — npm scripts and dependencies
- `.prettierrc.mjs` — current prettier config (formatting rules to preserve)
- `.prettierignore` — ignore patterns to carry over
- `CLAUDE.md` — agent instructions referencing prettier commands
- `.claude/skills/update-dependencies/SKILL.md` — skill referencing prettier
- `llms/testing.md` — testing guide mentioning prettier
- `scripts/utils/chmod.sh` — makes formatter binary executable
