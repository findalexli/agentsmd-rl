# Add a `verify-changes` agent skill for the OpenAI Agents JS monorepo

The repository (`openai/openai-agents-js`) follows a strict pre-PR verification stack
that contributors must run before marking work complete. Today that stack is
described in `AGENTS.md` as a single chained `pnpm` invocation, which is easy to
skip or run out of order. We want a first-class, fail-fast agent skill that
encapsulates the full sequence and is referenced from `AGENTS.md` so that any
agent collaborating on this repo runs it automatically.

Your job is to add the new skill files and to update `AGENTS.md` so that it
delegates to the skill rather than spelling out the chained command in three
places.

## What to add

### 1. The skill itself

Create a new agent skill rooted at `.codex/skills/verify-changes/`. Codex-style
skills auto-load when they live under `.codex/skills/<skill-name>/`, so the
exact path matters.

The skill bundle must contain:

- **`.codex/skills/verify-changes/SKILL.md`** — the skill definition.
  Use a YAML frontmatter block at the top of the file with two fields:
    - `name: verify-changes` (required — this is the slug agents address the
      skill by).
    - `description:` — a one-line summary of what the skill does. The
      description should make clear that the skill runs the mandatory
      verification steps for code changes in this monorepo.

  The body of `SKILL.md` should explain when to use the skill (whenever
  wrapping up a task, before opening a PR, or when asked to confirm work is
  ready), how to invoke it on macOS/Linux and on Windows, and a manual
  fallback workflow. Anywhere the body lists the verification commands, it
  must reference each step in the stack: `pnpm i`, `pnpm build`,
  `pnpm -r build-check`, `pnpm lint`, and `pnpm test`.

- **`.codex/skills/verify-changes/scripts/run.sh`** — a Bash entry point that
  executes the verification sequence with **fail-fast semantics** (i.e. uses
  `set -e` or stricter; any failed command must abort the rest of the run).
  The script must `cd` to the repository root and invoke, in order: `pnpm i`,
  `pnpm build`, `pnpm -r build-check`, `pnpm lint`, `pnpm test`. Make the
  script executable.

- **`.codex/skills/verify-changes/scripts/run.ps1`** — a PowerShell wrapper
  that runs the same sequence with the same fail-fast semantics, for Windows
  contributors.

### 2. `AGENTS.md` updates

Edit `AGENTS.md` at the repository root so that:

- A new top-level section titled exactly `## Mandatory Skill Usage` is added
  near the top of the file (and registered in the Table of Contents). Its
  body must instruct contributors and agents to load and use the
  `$verify-changes` skill immediately after any code change and before
  considering work complete.

- The existing `### Mandatory Local Run Order` subsection no longer contains
  the raw `pnpm lint && pnpm build && pnpm -r build-check && pnpm test`
  fenced code block. Replace it with prose that delegates to the
  `$verify-changes` skill and forbids skipping or reordering steps.

- The "Development Workflow" step that currently shows the chained `pnpm`
  command should likewise be rewritten to point at the `$verify-changes`
  skill.

- Anywhere else in `AGENTS.md` that describes the post-change verification
  step, reference the skill via the `$verify-changes` syntax (this is the
  conventional way Codex skills are invoked in prose).

## Constraints and conventions

- Do **not** modify behaviour of any other file. This change is purely
  additive (new skill bundle) plus a localised rewrite of the relevant
  sections of `AGENTS.md`.
- Match the project's existing markdown style in `AGENTS.md`: lower-cased
  ATX-style headings under the top-level `# Contributor Guide`, ordered list
  for the Table of Contents, fenced code blocks for shell commands.
- Keep the verification command sequence in the documented order: install,
  build, build-check (per-package), lint, test. Do not omit any step.
- Comments in `AGENTS.md` already follow the rule "Comments must end with a
  period" — keep that style.

## How to know you're done

After your changes, the repository at `/workspace/openai-agents-js` should:

1. Contain a new `.codex/skills/verify-changes/` directory with `SKILL.md`,
   `scripts/run.sh`, and `scripts/run.ps1`.
2. Have an `AGENTS.md` that references `$verify-changes` from the new
   `## Mandatory Skill Usage` section, the testing/automated-checks intro,
   the `### Mandatory Local Run Order` subsection, and the development
   workflow step.
3. Still build cleanly conceptually — you are not running `pnpm` here, but
   the `AGENTS.md` table of contents must still match the section order.
