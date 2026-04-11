# Add a verify-changes skill and update AGENTS.md

## Problem

The OpenAI Agents JS monorepo requires contributors to manually run a sequence of pnpm commands (`pnpm i`, `pnpm build`, `pnpm -r build-check`, `pnpm lint`, `pnpm test`) in the correct order before submitting changes. This is error-prone — contributors sometimes skip steps, run them out of order, or forget to re-run after fixing issues. The inline bash snippets in `AGENTS.md` are scattered across multiple sections and easy to miss.

## What needs to happen

1. Create a new **Codex skill** under `.codex/skills/verify-changes/` that automates the full verification sequence. The skill needs:
   - A `SKILL.md` with proper frontmatter (`name`, `description`) and documentation
   - A `scripts/run.sh` (bash) that runs all five pnpm commands in order with fail-fast semantics
   - A `scripts/run.ps1` (PowerShell) equivalent for Windows users

2. Update `AGENTS.md` to reference this new skill:
   - Add a section near the top making it mandatory for contributors to use this skill after code changes
   - Replace the scattered inline `pnpm lint && pnpm build && ...` bash snippets with references to the skill
   - Update the Table of Contents to reflect the new section
   - Add guidance about calling out backward compatibility or public API risks in ExecPlans
   - Note that translated docs under `docs/src/content/docs/{ja,ko,zh}` are generated and should not be edited manually

## Files to Look At

- `AGENTS.md` — the contributor guide that needs updating
- `.codex/skills/` — where the new skill should live (this directory may not exist yet)
