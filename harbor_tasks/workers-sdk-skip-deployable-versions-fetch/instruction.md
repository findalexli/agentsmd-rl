# Wrangler `versions deploy` — skip the deployable-versions fetch when not needed

You are working in the `cloudflare/workers-sdk` monorepo at
`/workspace/workers-sdk`. The relevant package is `wrangler`
(`packages/wrangler/`).

## Symptom

When a user runs `wrangler versions deploy <id1> <id2> ... --yes` (i.e.
non-interactively, with all version IDs explicitly provided), the command is
unnecessarily slow because Wrangler always fetches the **full list of
deployable versions** for the Worker — even though that list is only used to
populate an interactive selection prompt that is never shown when `--yes`
suppresses it.

The fetch in question hits `GET /accounts/:accountId/workers/scripts/:name/versions?deployable=true`,
which can be slow on Workers that have a large deployable-versions catalog.

## Expected behavior

Inside `promptVersionsToDeploy` (the function that powers the interactive
selection step of `wrangler versions deploy`), the deployable-versions fetch
must be **conditional**:

- **Skip** the deployable-versions list fetch when **both** of the following
  hold: the user passed `--yes` (so the interactive selector won't run)
  **and** at least one version ID was explicitly supplied on the command
  line. In that case, only the specific versions the user named need to be
  fetched (one `GET /versions/:id` per ID via the existing `fetchVersions`
  call).
- **Otherwise** fetch the deployable-versions list as before so the
  interactive selector can render the choices.

Additionally, the spinner that wraps this work should announce
**`Fetching versions`** (instead of the previous `Fetching deployable
versions`) — the new message reflects that the deployable-versions list is
no longer always fetched.

The set of HTTP calls Wrangler makes must change accordingly:

| Invocation | Old behavior | New behavior |
|---|---|---|
| `wrangler versions deploy <id> --yes` | `GET …/versions?deployable=true` + `GET …/versions/<id>` | only `GET …/versions/<id>` |
| `wrangler versions deploy` (interactive) | `GET …/versions?deployable=true` + `GET …/versions/<id>` for the selected default | unchanged |
| `wrangler versions deploy --yes` (no IDs) | `GET …/versions?deployable=true` + `GET …/versions/<id>` for the latest | unchanged (no IDs were supplied) |

## Tests

The repo's existing vitest suite for `wrangler versions deploy`
(`packages/wrangler/src/__tests__/versions/versions.deploy.test.ts`)
already exercises this surface area; the inline-snapshot expectations and
MSW handler set will be updated to reflect the new behavior. Your fix must
make the (updated) suite green. In particular, two snapshots in the
"max versions restrictions" describe block exercise the
`--yes` + multiple-version-IDs path explicitly — these can only succeed
once the deployable-versions fetch is conditional.

You can run the suite with:

```
cd /workspace/workers-sdk/packages/wrangler
node_modules/.bin/vitest run src/__tests__/versions/versions.deploy.test.ts
```

## Repository conventions

Read `/workspace/workers-sdk/AGENTS.md` (root) and
`/workspace/workers-sdk/packages/wrangler/AGENTS.md` before editing.
Highlights that bear on this task:

- Use **pnpm**, never npm or yarn.
- TypeScript with strict mode; do **not** use `any` or non-null assertions
  (`!`); always brace control flow; prefix unused vars with `_`; use
  `node:` for Node.js builtins.
- No `console.*` in wrangler — use the `logger` singleton.
- No floating promises; await or explicitly `void` them.
- **Every change to a published package requires a changeset.** Add a new
  file under `.changeset/` with frontmatter `"wrangler": patch`. Read
  `.changeset/README.md` for format. Do not use h1/h2/h3 headers in the
  changeset body.

## Code Style Requirements

The repo's `tsc` typecheck (`pnpm --filter wrangler check:type`) must pass.
Format with the repo's formatter; the project enforces tabs, double quotes,
semicolons, and trailing commas (es5).
