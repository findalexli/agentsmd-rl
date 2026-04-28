# Add verify-changes Codex Skill

The `AGENTS.md` file in the OpenAI Agents JS monorepo documents a mandatory
verification sequence that contributors must run after any code change:
`pnpm i`, `pnpm build`, `pnpm -r build-check`, `pnpm lint`, `pnpm test`.
This sequence is listed in multiple places as inline bash blocks, making it
easy to skip steps or run them out of order.

The repo needs a reusable `verify-changes` **Codex skill** that encapsulates
the full verification stack so contributors (human and agent) invoke a single
command instead of manually piecing together commands from multiple sections
of `AGENTS.md`.

## Requirements

### 1. Codex skill directory and SKILL.md

Codex skills live at `.codex/skills/<skill-name>/SKILL.md` — see
https://developers.openai.com/codex/skills for the specification and
frontmatter format (name, description, content sections).

Create the skill at `.codex/skills/verify-changes/SKILL.md` with
frontmatter that includes `name: verify-changes`. The SKILL.md must:

- Documents the verification purpose: ensure work is complete only after
  install, build, type-check, lint, and tests pass.
- Includes a **Quick start** section telling users where to keep the skill
  and how to invoke the bundled scripts on macOS/Linux, Windows, and what to
  do on failure.
- Includes a **Manual workflow** section documenting the commands in their
  required order from the repository root. The sequence is:
  `pnpm i` → `pnpm build` → `pnpm -r build-check` → `pnpm lint` → `pnpm test`.
  Emphasize not skipping steps and re-running the full stack after fixes.
- Includes a **Resources** section referencing the helper scripts.

### 2. Helper scripts

Create two scripts alongside the skill that automate the verification
sequence with fail-fast semantics (stop on first error):

- `.codex/skills/verify-changes/scripts/run.sh` — bash script for macOS/Linux.
  Must `cd` to the repository root (resolve via `git rev-parse --show-toplevel`
  with a relative-path fallback), then run the five pnpm commands in order
  with an echo before each step. Print a success banner after all commands
  pass. Must have the executable permission bit.

- `.codex/skills/verify-changes/scripts/run.ps1` — PowerShell script for
  Windows. Same verification sequence, using `Set-StrictMode -Version Latest`
  and `$ErrorActionPreference = "Stop"`. Resolve repo root via git or path
  traversal. Define a helper function to run each pnpm step and exit on
  failure. Print a success banner after all commands pass.

### 3. Update AGENTS.md

The root-level `AGENTS.md` is the contributor guide for this repository. It
currently contains inline bash blocks with the verification commands in two
places: the "Mandatory Local Run Order" section and step 4 of the
"Development Workflow." It also lacks a top-level instruction that agent
contributors must use the verification skill.

Update `AGENTS.md` to:

- Insert a new `## Mandatory Skill Usage` heading as the first section
  after the Table of Contents, followed by text instructing contributors
  (and agents) to always invoke the `$verify-changes` skill after any code
  change before considering work complete. Rerun the full stack after
  fixing failures. Reference the skill with the `$verify-changes` syntax.

- Update the Table of Contents to include the new section (renumbering
  subsequent entries).

- In the "Mandatory Local Run Order" subsection, replace the inline bash
  block with text saying to run the full verification stack locally via the
  `$verify-changes` skill; do not skip any step or change the order.

- In the "Development Workflow" section, replace step 4's inline bash block
  with: "Run all checks using the `$verify-changes` skill to execute the full
  verification stack in order before considering the work complete."

- In the "Testing & Automated Checks" intro paragraph, add a sentence after
  "Before submitting changes, ensure all checks pass..." stating that after
  any code modification, the contributor must invoke the `$verify-changes`
  skill and rerun the full stack after fixes.

- In the "ExecPlans" paragraph, add a sentence about calling out potential
  backward compatibility or public API risks in plans.

- In the docs bullet under "Repo Structure & Important Files", append a note
  that translated docs under `docs/src/content/docs/ja`,
  `docs/src/content/docs/ko`, and `docs/src/content/docs/zh` are generated
  via `pnpm docs:translate` and must not be edited manually.

Read the current `AGENTS.md` to understand the full content and structure
before editing. Preserve all existing sections and formatting that do not
conflict with the changes above.

## References

- Codex skills specification: https://developers.openai.com/codex/skills
- Current repo files: `AGENTS.md`, `package.json` (for available pnpm scripts)
