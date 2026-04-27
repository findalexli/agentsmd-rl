# Fix `HrefError` types and messages for nameless wildcards and missing params

The `@remix-run/route-pattern` package generates URLs from route patterns via
`pattern.href(params)`. Today it raises `HrefError` instances whose `details`
discriminator and stringified message do not match the package's documented
intent. This task is to fix the discriminator and tighten the error messages.

The package source lives under `packages/route-pattern/`. All work for this
task happens inside that package; the rest of the monorepo can be ignored.

## Bugs to fix

### 1. Top-level nameless wildcard reports the wrong error type

A *nameless wildcard* is a `*` token in a pattern with no name — e.g. the
hostname `://*.example.com/path` or the pathname `/files/*`. Such a wildcard
captures nothing and is not a parameter the caller can supply a value for.

Currently, calling `.href()` on a pattern that contains a top-level (non-optional)
nameless wildcard throws `HrefError` with `details.type === 'missing-params'`.
That is misleading: there is no missing param — the pattern itself is
unusable for href generation in this position.

It must instead throw `HrefError` with `details.type === 'nameless-wildcard'`.
The `'nameless-wildcard'` discriminator already exists in the
`HrefErrorDetails` union; what is missing is that any code path actually
constructs and throws it.

Both of these patterns must surface the new discriminator:

```ts
new RoutePattern('://*.example.com/path').href() // throw nameless-wildcard
new RoutePattern('/files/*').href()              // throw nameless-wildcard
```

A nameless wildcard *inside* an optional, e.g. `'/api(/v:version)/*'`, is not
in scope here — those are still simply skipped when the optional is dropped.
This bug only fires when the bare `*` sits at the top level of a part pattern.

### 2. `missing-params` does not report which params are missing

When required params are absent, the `HrefError` raised with
`type: 'missing-params'` does not tell callers (or the error formatter) which
specific names were missing. The details object must gain a new field:

```ts
{
  type: 'missing-params'
  pattern: RoutePattern
  partPattern: PartPattern
  missingParams: Array<string>   // <-- new
  params: Record<string, string | number>
}
```

`missingParams` must be an array of the required param names that the caller
did not supply, in the order they appear in the pattern. The first such name
must be present. Examples:

| Pattern                                  | `.href(args)`         | `missingParams[0]` |
| ---------------------------------------- | --------------------- | ------------------ |
| `https://example.com/:id`                | `()`                  | `'id'`             |
| `https://example.com/:collection/:id`    | `()`                  | `'collection'`     |
| `https://example.com/:a/:b/:c`           | `({ a: 'x' })`        | `'b'`              |

Optional segments containing missing names must still be skipped (they do not
contribute to `missingParams`); only required params that the caller failed
to supply count. Names that *were* provided must not appear in
`missingParams`.

### 3. New stringified error messages

The `HrefError.message` formatter must produce the following exact strings.

**`missing-params`** — drop the per-variant breakdown. The new message is:

```
HrefError: missing param(s): 'collection', 'id'

Pattern: https://example.com/:collection/:id
Params: {}
```

Format: `missing param(s): ` followed by each name from `missingParams`
wrapped in single quotes and joined by `, `, then a blank line, then
`Pattern: <pattern.toString()>`, then `Params: <JSON.stringify(details.params)>`.
The previous "Pathname variants:" / "Hostname variants:" block is removed.

**`missing-search-params`** — change the separator to a colon and quote each
name individually:

```
HrefError: missing required search param(s): 'q', 'sort'

Pattern: https://example.com/search?q=&sort=
Search params: {"page":1}
```

For a single missing name:

```
HrefError: missing required search param(s): 'q'

Pattern: https://example.com/search?q=
Search params: {}
```

Old format: `missing required search param(s) 'q, sort'` (no colon after
`(s)`, names concatenated with commas inside one pair of quotes). New format
inserts `: ` after `(s)` and quotes each name independently.

The other discriminators (`missing-hostname`, `nameless-wildcard`) keep their
existing messages.

## Tests

Update the existing tests so that they exercise the corrected discriminators
and message formats. In particular, the cases in
`packages/route-pattern/src/lib/route-pattern.test.ts` that currently assert
`hrefError('missing-params')` for top-level bare wildcards must assert
`hrefError('nameless-wildcard')` instead, and the `missing-params` /
`missing-search-params` snapshot tests in
`packages/route-pattern/src/lib/route-pattern/href.test.ts` must match the new
message strings shown above.

## Constraints

- Keep the `Href.part` function's responsibility focused: a function that
  generates an href for a single part pattern can either return the rendered
  string or throw `HrefError`; it should not need a separate caller-side
  helper to translate a `null` return into a thrown error.
- Do not regress any other test in the package. `pnpm --filter
  @remix-run/route-pattern run test` and `pnpm --filter
  @remix-run/route-pattern run typecheck` must both pass.
- Add a change file at
  `packages/route-pattern/.changes/patch.<short-slug>.md` summarising the
  user-visible change, following the conventions in `CONTRIBUTING.md` and the
  shape of the other files under `packages/route-pattern/.changes/`.

## Code Style Requirements

The repository runs Prettier and ESLint in CI. Code you write must conform to
the project conventions documented in `AGENTS.md`:

- Prettier: `printWidth: 100`, no semicolons, single quotes, spaces (not tabs).
- `import type { X }` for type-only imports; relative imports include the
  `.ts` extension; `verbatimModuleSyntax` is on.
- Prefer `let` for locals, `const` only at module scope; never `var`.
- Regular function declarations by default; arrow functions only as callbacks.
- Generic type parameters use descriptive lowercase names (e.g. `source`).
- No `for` loops or conditionals inside `describe()` blocks in test files.
- Comments only when the code is doing something non-obvious.
