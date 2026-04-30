# Fix Docusaurus SSG crash on API documentation pages

You are working in a sparse checkout of the [Apache Superset](https://github.com/apache/superset) repository at `/workspace/superset`. The relevant subtree for this task is `docs/`, the Docusaurus documentation site.

## The bug

All 242 generated API documentation pages (`/user-docs/api/...`) fail to build during static site generation. The Netlify (and any equivalent Docusaurus SSG) build aborts with:

```
TypeError: Cannot destructure property 'store' of 'i' as it is null.
    at MethodEndpoint
```

### Root cause

`docs/package.json` resolves `docusaurus-theme-openapi-docs` to **v4.7.1** (from the `^4.6.0` range). Starting in that release, the theme's `MethodEndpoint` component (used on every API endpoint page) calls a `react-redux` hook (`useTypedSelector` / `useSelector`) at the **top level of the component body**. During Docusaurus static site generation, no Redux `Provider` is mounted, so the store is `null` and the hook throws when destructuring it. Every API page using this component fails to render at build time.

We cannot fix this upstream package on our deploy schedule. The standard Docusaurus remedy is to **swizzle** the theme component — provide a local override at the matching path under `docs/src/theme/` that Docusaurus prefers over the package's version.

## What to do

Create a swizzled replacement of `MethodEndpoint` in this repository at the exact swizzle path Docusaurus expects:

```
docs/src/theme/ApiExplorer/MethodEndpoint/index.tsx
```

The replacement must reproduce the visible DOM output of the upstream component (so the rendered API pages look unchanged to readers) **while never invoking the Redux hook during static site generation**. Defer any Redux-derived rendering to the browser-only render path so SSG can complete without a store.

You can read the upstream source for reference at:
<https://github.com/PaloAltoNetworks/docusaurus-openapi-docs/blob/v4.7.1/packages/docusaurus-theme-openapi-docs/src/theme/ApiExplorer/MethodEndpoint/index.tsx>

## Required behavior

The component must `export default` a React functional component that accepts these props:

```ts
{ method: string; path: string; context?: "endpoint" | "callback" }
```

### Render output

- The whole output is wrapped in a `<pre>` element with the CSS class `openapi__method-endpoint`.
- Inside the `<pre>`, render a method badge: a `<span>` with class `"badge badge--<color>"` where `<color>` is determined from the `method` prop (case-insensitive):

  | `method` (lowercased) | badge color class suffix |
  |---|---|
  | `get`    | `primary`   |
  | `post`   | `success`   |
  | `delete` | `danger`    |
  | `put`    | `info`      |
  | `patch`  | `warning`   |
  | `head`   | `secondary` |
  | `event`  | `secondary` |

  So a `GET` request renders `<span class="badge badge--primary">…</span>`.

- The badge **text** is the method in upper case (`GET`, `POST`, …) — **except** when `method === "event"`, in which case the badge text is the literal string `Webhook`.

- For every method **except** `"event"`, render an `<h2>` with class `openapi__method-endpoint-path` after the badge, containing:

  1. The resolved server URL prefix (see below).
  2. The path string with each `{name}` placeholder converted to `:name`. The substitution applies to identifiers consisting of letters, digits, hyphens, or underscores. Example: `"/users/{user_id}/posts/{post_id}"` becomes `"/users/:user_id/posts/:post_id"`.

  When `method === "event"`, the `<h2>` heading must **not** be rendered.

- After the `<pre>`, render a sibling `<div>` with class `openapi__divider`.

### Server URL — the SSG-safe part

The server URL prefix comes from a Redux store slice (`state.server.value`) that is only populated at runtime in the browser. The original component reads it via a top-level Redux hook, which is the source of the SSG crash.

Your replacement must:

- **Never** call any react-redux hook from inside `MethodEndpoint`'s own function body — i.e., not at the top level. Calling Redux hooks during SSG (no Provider) throws.
- Defer all Redux access to a render path that only executes in the browser. Docusaurus provides `@docusaurus/BrowserOnly` for exactly this purpose: its `children` callback only runs on the client, never during SSG.
- When `context === "callback"`, do **not** render the server URL at all (callback endpoints are documented as paths only). The `<h2>` heading and the substituted path must still render for callbacks.
- When the Redux store is present (browser path) and `state.server.value` is set, render the configured `url`, with any `{variable}` tokens substituted from `state.server.value.variables[variable].default`. Strip any trailing slash from the base URL before appending the path.

## Constraints

This file is new code in the Apache Superset repository. The repository's contributor guidelines (`CLAUDE.md`, `AGENTS.md`, `.cursor/rules/dev-standard.mdc`) require:

- **Apache License header**: every new code file must begin with the standard ASF license header (`Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements…` through `… limitations under the License.`).
- **TypeScript only — no `any` types**: the file must be `.tsx` and must not use `any` as a type annotation, cast (`as any`), generic argument (`<any>`), or array element (`any[]`). Define proper types for the Redux store slice.
- **Functional components with hooks** — no class components.
- **Avoid time-specific language** in comments (no "now", "currently", "today" — comments should remain accurate over time).
- **No custom CSS** — preserve the upstream CSS class names exactly so the site's existing stylesheet styles the badge and heading without changes.

## Code Style Requirements

The file is checked at lint/typecheck time as part of `yarn typecheck` / `yarn build` (the docs CI pipeline). It must be syntactically valid TypeScript JSX that the project's bundler (esbuild) can compile.
