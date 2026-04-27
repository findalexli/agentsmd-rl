# Add an agent prompt utility for Local Explorer

The Cloudflare workers-sdk monorepo ships a Local Explorer UI
(`packages/local-explorer-ui`). The homepage needs a "Copy prompt for agent"
feature so a developer can paste a ready-made prompt — including the
runtime-resolved Local Explorer API endpoint — into an LLM-powered coding
assistant. The wiring code already imports the helpers, but the underlying
utility module does not exist yet, so the package will not build.

## Your task

Create the file `packages/local-explorer-ui/src/utils/agent-prompt.ts`
exporting **three** functions. The file has no runtime imports — it is a
self-contained TypeScript module.

### 1. `getLocalExplorerApiEndpoint(origin, apiPath): string`

Joins the page's origin (e.g. `http://localhost:8787`) and the API path
(e.g. `/cdn-cgi/explorer/api`) into the fully-qualified API endpoint URL.
For the inputs `"http://localhost:8787"` and `"/cdn-cgi/explorer/api"` it
must return `"http://localhost:8787/cdn-cgi/explorer/api"`. The function
must work correctly for arbitrary origins and paths — do not hardcode any
specific values.

### 2. `createLocalExplorerPrompt(apiEndpoint): string`

Takes the resolved API endpoint and returns the prompt text for the agent.
The returned string MUST contain — after substituting the endpoint
parameter into the text — the following two substrings verbatim:

- `API endpoint: <ENDPOINT>.` (note the trailing period)
- `Fetch the OpenAPI schema from <ENDPOINT>`

…where `<ENDPOINT>` is the value passed to the function. The endpoint must
be substituted **everywhere** it appears (the test will exercise multiple
endpoints, so a hardcoded URL will fail). The unsubstituted placeholder
literal `{{apiEndpoint}}` must not remain in the output.

The full prompt should additionally explain (in any wording you like) that
the agent has access to local Cloudflare services (KV, R2, D1, Durable
Objects, Workflows) via the Explorer API and that the OpenAPI schema can
be fetched from the given endpoint to discover available operations.

### 3. `copyTextToClipboard(text, clipboard?): Promise<void>`

Writes `text` to a clipboard. The second parameter is an optional clipboard
implementation that supplies at least a `writeText(text: string):
Promise<void>` method (typed as `Pick<Clipboard, "writeText">`); when not
provided, it must default to `navigator.clipboard` so callers in the
browser need not pass anything. The function must `await` `writeText` and
resolve with `void`.

## Code Style Requirements

The repository's `AGENTS.md` mandates TypeScript **strict mode** for all
new code. Your file is compiled under `tsc --noEmit` with `"strict": true`
as part of the test suite, so:

- No `any` types
- No non-null assertions (`!`)
- All control flow uses curly braces
- `import type { X }` is required for type-only imports (use the
  `Clipboard` DOM type as a *type* reference, not a runtime value)
- No floating promises — `await` the clipboard call

## Where to write the file

The exact path is
`packages/local-explorer-ui/src/utils/agent-prompt.ts` inside the
workers-sdk repository at `/workspace/workers-sdk`. The directory may not
exist yet — create it.
