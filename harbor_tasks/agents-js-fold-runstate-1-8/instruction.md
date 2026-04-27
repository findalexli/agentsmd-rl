# Fold the unreleased RunState schema bump into 1.8

You are working in a clone of [`openai/openai-agents-js`](https://github.com/openai/openai-agents-js)
checked out at base commit `4e6b3fbd3355709831a1bb64472b3c947b694690` under
`/workspace/agents-js`. The repository is a pnpm-managed monorepo; the package
of interest is `@openai/agents-core` under `packages/agents-core/`.

## Background

`@openai/agents-core` serialises `RunState` to JSON for persistence/resume.
Each serialised payload carries a `$schemaVersion` string that the runtime uses
to gate compatibility logic. The set of accepted versions is enumerated by
`SUPPORTED_SCHEMA_VERSIONS`, and the version stamped on freshly serialised
payloads is the constant `CURRENT_SCHEMA_VERSION`.

The latest released version of `@openai/agents-core` at the base commit is
`v0.5.4`. Any schema versions that landed on `main` *after* `v0.5.4` are
unreleased — no shipped consumer ever saw or persisted those snapshot
formats.

On the base commit, two such unreleased versions exist:

- `1.8` — added tool search item variants to serialised run state payloads.
- `1.9` — added batched computer actions and GA computer tool aliasing.

Both `1.8` and `1.9` are post-tag, branch-local additions. Neither has a
released or otherwise supported snapshot consumer outside this branch.

## The problem

Splitting the post-tag changes across two unreleased schema steps (`1.8` and
`1.9`) creates a separate, never-shipped `1.9` step that the SDK then commits
to support forever. Per the repo's `$implementation-strategy` skill
(`.agents/skills/implementation-strategy/SKILL.md`), interface changes
introduced after the latest release tag — and not yet backing a released or
otherwise supported consumer — should be rewritten directly rather than
preserved with compatibility shims.

The two post-tag deltas should be folded into a single unreleased schema
version so that:

1. The version stamped on freshly-serialised payloads is `1.8` (not `1.9`).
2. `SUPPORTED_SCHEMA_VERSIONS` does not advertise `1.9` as a recognised
   value. Attempts to deserialise a payload stamped `$schemaVersion: '1.9'`
   must fail with the runtime's standard "Run state schema version 1.9 is
   not supported" error path (the same error path that already handles
   unknown versions like `0.1`).
3. Payloads stamped `$schemaVersion: '1.8'` continue to deserialise and must
   still recognise tool search item variants — the gating logic that
   currently treats both `1.8` and `1.9` as "supports tool_search" must be
   collapsed so that only `1.8` short-circuits the tool-search assertion.
4. The Version-history JSDoc comment that currently documents `1.8` and
   `1.9` separately should be folded into a single `1.8` entry whose
   description covers the union of changes (tool search item variants,
   batched computer actions, and GA computer tool aliasing). Do not leave a
   dangling history line for a version that no longer exists in
   `SUPPORTED_SCHEMA_VERSIONS`.

The serialisation/deserialisation logic, the tool-search assertion, and the
Version-history comment all live in `packages/agents-core/src/runState.ts`.

## Repo conventions you must follow

These are pulled from the repo's contributor guide (`AGENTS.md`) and the
`$implementation-strategy` skill, both at the repository root.

- **Add a changeset.** Any code change under `packages/` requires an entry
  under `.changeset/`. The summary line must follow Conventional Commit style
  (e.g. `fix: ...`). The change targets `@openai/agents-core` at `patch`
  level. See `AGENTS.md` (`$changeset-validation`).
- **Compatibility boundary.** Judge breaking-change risk against the latest
  release tag, not against unreleased branch churn. Unreleased post-tag
  schema versions on `main` may be rewritten directly without compatibility
  shims, because they have no released or otherwise supported snapshot
  consumer. See `.agents/skills/implementation-strategy/SKILL.md` and the
  `$implementation-strategy` section of `AGENTS.md`.
- **Comment style.** Per `AGENTS.md` "Linting & Formatting", comments end
  with a period. Keep the Version-history JSDoc consistent with that.

## Code Style Requirements

The repository's verification stack runs ESLint, Prettier, and TypeScript
type-checking. Your changes must:

- Pass `pnpm lint` (ESLint with the project's `eslint.config.mjs`).
- Pass `pnpm -F @openai/agents-core build` (TypeScript compilation).
- Match the repo's Prettier defaults — do not hand-wrap markdown prose; rely
  on Prettier formatting for line breaks. Comments must end with a period.

## Acceptance criteria

After your change:

- `CURRENT_SCHEMA_VERSION` exported from `@openai/agents-core` equals the
  string `'1.8'`.
- A freshly serialised `RunState` (e.g. `new RunState(ctx, 'x', agent, 1).toString()`)
  produces a JSON object whose `$schemaVersion` field is the string `'1.8'`.
- `RunState.fromString(agent, payload)` rejects a payload stamped
  `$schemaVersion: '1.9'`. The thrown error must be the runtime's standard
  unsupported-version error (the same one used for any other unrecognised
  version such as `'0.1'`); the error message includes both `1.9` and the
  phrase `not supported`.
- `RunState.fromString(agent, payload)` continues to accept payloads
  stamped `$schemaVersion: '1.8'`, including ones that contain tool-search
  call/output items.
- The compiled `packages/agents-core/dist/runState.js` no longer contains
  any `'1.9'` string literal.
- `pnpm exec vitest run packages/agents-core/test/runState.test.ts` passes.
- A changeset entry exists under `.changeset/` for `@openai/agents-core` at
  `patch` level using a Conventional-Commit-style summary.

You do not need to publish the package or run integration tests. The test
harness imports your source via `tsx` and invokes the repo's `build-check`
and the existing `runState.test.ts` vitest suite, so the tests reflect your
source edits without an explicit rebuild step.
