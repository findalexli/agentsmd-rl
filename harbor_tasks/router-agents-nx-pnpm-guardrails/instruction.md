# Task: Tighten `AGENTS.md` Nx execution guidance for sandboxed agents

The repository at `/workspace/router` is a checkout of [TanStack/router](https://github.com/TanStack/router) — a pnpm + Nx monorepo. The repo's top-level `AGENTS.md` is the contract that AI coding agents (including this benchmark's agents) read before doing work in this repo.

The current `AGENTS.md` has two problems we need you to fix:

## Problem 1 — `npx nx` / `npx vitest` is not the recommended invocation

Throughout `AGENTS.md`, package-manager and test-runner commands are documented as `npx nx ...` and `npx vitest ...`. In a pnpm workspace this is wrong:

- `pnpm nx ...` is the canonical form and resolves through pnpm's workspace.
- Calling `npx vitest run ...` directly bypasses Nx, which means the test target's task dependencies (notably the `build` it depends on) are *not* re-run, so an agent can run a "passing" test against stale build output.

You must rewrite the affected lines so that:

- Every `npx nx ...` invocation is replaced by the equivalent `pnpm nx ...` invocation. Specifically: `npx nx show projects` → `pnpm nx show projects`; `npx nx run ...` → `pnpm nx run ...`; `npx nx run-many ...` → `pnpm nx run-many ...`; `npx nx affected ...` → `pnpm nx affected ...`.
- The "Granular Vitest testing within packages" subsection is replaced by an equivalent "**Granular unit testing through Nx (recommended):**" subsection in which every command is `pnpm nx run @tanstack/react-router:test:unit -- ...`. Filter arguments (specific test files, `-t "..."`, `--exclude="..."`, `list`) are passed *after* the `--` separator. Drop the explicit `cd packages/react-router` step — Nx resolves the project. Drop the standalone "Through nx" line; the whole subsection is now through nx.
- In the "Efficient targeted testing workflow" numbered list and the "Pro tips" / "Example workflow" lines, every `npx vitest run tests/...` invocation becomes `pnpm nx run @tanstack/react-router:test:unit -- tests/...`. The "Combine nx package targeting with vitest file targeting" tip becomes a single tip about keeping all test filtering arguments behind `pnpm nx run ... -- ...`.
- Update the "Testing strategy" line to describe the levels in nx-arg terms (Package level → File-level args via nx → Test-level args (`-t`) via nx → Pattern-level args (`--exclude`) via nx).

After your edits, the file must contain **no** occurrences of `npx nx show projects`, `npx nx run`, `npx nx affected`, or `npx vitest run`.

## Problem 2 — `AGENTS.md` lacks sandbox-aware execution guardrails

`AGENTS.md` has no guidance for an agent running in a constrained sandbox where the Nx daemon may misbehave or hang. Add a new bullet at the bottom of the **Dev environment tips** list — immediately after the existing "Testing strategy" bullet — that introduces and lists these guardrails. The bullet's heading must be exactly:

```
- **Agent execution guardrails (important):**
```

Under that heading, add six sub-bullets (in this order) covering these rules. The wording must match these exact strings where called out:

1. Always prefer `pnpm nx ...` over `npx nx ...`.
2. Prefer Nx targets over direct test runners so task dependencies (including required builds) remain in the graph.
3. In sandbox, run Nx with `CI=1 NX_DAEMON=false pnpm nx run <project>:<target> --outputStyle=stream --skipRemoteCache` (this exact command literal must appear in the document).
4. `Run only one Nx command at a time.` (this exact sentence must appear).
5. If an Nx command shows no output for ~20 seconds, stop, run `pnpm nx reset` once, and retry once. (Both `pnpm nx reset` and the phrase `20 seconds` must appear.)
6. `Do not loop retries indefinitely.` (this exact sentence must appear) — if it still hangs or sandbox blocks graph/daemon behavior, request escalation immediately.

The new bullets belong inside the existing "Dev environment tips" section (under `## Dev environment tips`) and must be the last item in that section, directly before the `## Testing instructions` heading.

## Constraints

- Edit **only** `AGENTS.md` at the repository root. No other files.
- Preserve the rest of the document (project overview, setup commands, code style, PR instructions, package structure, etc.) — do not delete or reorder unrelated sections.
- Keep the file as valid markdown: bullet lists stay bullet lists, the `# AGENTS.md` top-level heading stays, the `## Dev environment tips` and `## Testing instructions` section headings stay.
- The file must remain non-empty and substantive (at least several hundred characters of guidance).
