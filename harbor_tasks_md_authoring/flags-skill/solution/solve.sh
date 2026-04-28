#!/usr/bin/env bash
set -euo pipefail

cd /workspace/flags

# Idempotency guard
if grep -qF "The Flags SDK (`flags` npm package) is a feature flags toolkit for Next.js and S" "skills/flags-sdk/SKILL.md" && grep -qF "Creates an App Router route handler for `/.well-known/vercel/flags`. Auto-verifi" "skills/flags-sdk/references/api.md" && grep -qF "The `hasAuthCookieFlag` checks cookie existence without authenticating. Two shel" "skills/flags-sdk/references/nextjs.md" && grep -qF "import { createSource, flagFallbacks, vercelFlagDefinitions, type Context, type " "skills/flags-sdk/references/providers.md" && grep -qF "The `x-visitorId` header ensures the visitor ID is available even on the first r" "skills/flags-sdk/references/sveltekit.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/flags-sdk/SKILL.md b/skills/flags-sdk/SKILL.md
@@ -0,0 +1,281 @@
+---
+name: flags-sdk
+description: >
+  Comprehensive guide for implementing feature flags and A/B tests using the Flags SDK (the `flags` npm package).
+  Use when: (1) Creating or declaring feature flags with `flag()`, (2) Setting up feature flag providers/adapters
+  (Vercel, Statsig, LaunchDarkly, PostHog, GrowthBook, Hypertune, Edge Config, OpenFeature, Flagsmith, Reflag,
+  Split, Optimizely, or custom adapters), (3) Implementing precompute patterns for static pages with feature flags,
+  (4) Setting up evaluation context with `identify` and `dedupe`, (5) Integrating the Flags Explorer / Vercel Toolbar,
+  (6) Working with feature flags in Next.js (App Router, Pages Router, Middleware) or SvelteKit,
+  (7) Writing custom adapters, (8) Encrypting/decrypting flag values for the toolbar,
+  (9) Any task involving the `flags`, `flags/next`, `flags/sveltekit`, `flags/react`, or `@flags-sdk/*` packages.
+  Triggers on: feature flags, A/B testing, experimentation, flags SDK, flag adapters, precompute flags,
+  Flags Explorer, feature gates, flag overrides.
+---
+
+# Flags SDK
+
+The Flags SDK (`flags` npm package) is a feature flags toolkit for Next.js and SvelteKit. It turns each feature flag into a callable function, works with any flag provider via adapters, and keeps pages static using the precompute pattern.
+
+- Docs: https://flags-sdk.dev
+- Repo: https://github.com/vercel/flags
+
+## Core Concepts
+
+### Flags as Code
+
+Each flag is declared as a function — no string keys at call sites:
+
+```ts
+import { flag } from 'flags/next';
+
+export const exampleFlag = flag({
+  key: 'example-flag',
+  decide() { return false; },
+});
+
+// Usage: just call the function
+const value = await exampleFlag();
+```
+
+### Server-Side Evaluation
+
+Evaluate flags server-side to avoid layout shift, keep pages static, and maintain confidentiality. Use routing middleware + precompute to serve static variants from CDN.
+
+### Adapter Pattern
+
+Adapters replace `decide` and `origin` on a flag declaration, enabling provider-agnostic flags:
+
+```ts
+import { flag } from 'flags/next';
+import { statsigAdapter } from '@flags-sdk/statsig';
+
+export const myGate = flag({
+  key: 'my_gate',
+  adapter: statsigAdapter.featureGate((gate) => gate.value),
+  identify,
+});
+```
+
+## Declaring Flags
+
+### Basic Flag
+
+```ts
+import { flag } from 'flags/next'; // or 'flags/sveltekit'
+
+export const showBanner = flag<boolean>({
+  key: 'show-banner',
+  description: 'Show promotional banner',
+  defaultValue: false,
+  options: [
+    { value: false, label: 'Hide' },
+    { value: true, label: 'Show' },
+  ],
+  decide() { return false; },
+});
+```
+
+### Flag with Evaluation Context
+
+Use `identify` to establish who the request is for; `decide` receives the entities:
+
+```ts
+import { dedupe, flag } from 'flags/next';
+import type { ReadonlyRequestCookies } from 'flags';
+
+interface Entities {
+  user?: { id: string };
+}
+
+const identify = dedupe(
+  ({ cookies }: { cookies: ReadonlyRequestCookies }): Entities => {
+    const userId = cookies.get('user-id')?.value;
+    return { user: userId ? { id: userId } : undefined };
+  },
+);
+
+export const dashboardFlag = flag<boolean, Entities>({
+  key: 'new-dashboard',
+  identify,
+  decide({ entities }) {
+    if (!entities?.user) return false;
+    return ['user1', 'user2'].includes(entities.user.id);
+  },
+});
+```
+
+### Flag with Adapter
+
+```ts
+import { flag } from 'flags/next';
+import { vercelAdapter } from '@flags-sdk/vercel';
+
+export const exampleFlag = flag({
+  key: 'example-flag',
+  adapter: vercelAdapter(),
+});
+```
+
+### Key Parameters
+
+| Parameter      | Type                               | Description                                          |
+| -------------- | ---------------------------------- | ---------------------------------------------------- |
+| `key`          | `string`                           | Unique flag identifier                               |
+| `decide`       | `function`                         | Resolves the flag value                              |
+| `defaultValue` | `any`                              | Fallback if `decide` returns undefined or throws     |
+| `description`  | `string`                           | Shown in Flags Explorer                              |
+| `origin`       | `string`                           | URL to manage the flag in provider dashboard         |
+| `options`      | `{ label?: string, value: any }[]` | Possible values, used for precompute + Flags Explorer|
+| `adapter`      | `Adapter`                          | Provider adapter implementing `decide` and `origin`  |
+| `identify`     | `function`                         | Returns evaluation context (entities) for `decide`   |
+
+## Dedupe
+
+Wrap shared functions (especially `identify`) in `dedupe` to run them once per request:
+
+```ts
+import { dedupe } from 'flags/next';
+
+const identify = dedupe(({ cookies }) => {
+  return { user: { id: cookies.get('uid')?.value } };
+});
+```
+
+Note: `dedupe` is not available in Pages Router.
+
+## Flags Explorer Setup
+
+### Next.js (App Router)
+
+```ts
+// app/.well-known/vercel/flags/route.ts
+import { getProviderData, createFlagsDiscoveryEndpoint } from 'flags/next';
+import * as flags from '../../../../flags';
+
+export const GET = createFlagsDiscoveryEndpoint(async () => {
+  return getProviderData(flags);
+});
+```
+
+### With External Provider Data
+
+```ts
+import { getProviderData, createFlagsDiscoveryEndpoint } from 'flags/next';
+import { getProviderData as getStatsigProviderData } from '@flags-sdk/statsig';
+import { mergeProviderData } from 'flags';
+import * as flags from '../../../../flags';
+
+export const GET = createFlagsDiscoveryEndpoint(async () => {
+  return mergeProviderData([
+    getProviderData(flags),
+    getStatsigProviderData({
+      consoleApiKey: process.env.STATSIG_CONSOLE_API_KEY,
+      projectId: process.env.STATSIG_PROJECT_ID,
+    }),
+  ]);
+});
+```
+
+### SvelteKit
+
+```ts
+// src/hooks.server.ts
+import { createHandle } from 'flags/sveltekit';
+import { FLAGS_SECRET } from '$env/static/private';
+import * as flags from '$lib/flags';
+
+export const handle = createHandle({ secret: FLAGS_SECRET, flags });
+```
+
+## FLAGS_SECRET
+
+Required for precompute and Flags Explorer. Must be 32 random bytes, base64-encoded:
+
+```sh
+node -e "console.log(crypto.randomBytes(32).toString('base64url'))"
+```
+
+Store as `FLAGS_SECRET` env var. On Vercel: `vc env add FLAGS_SECRET` then `vc env pull`.
+
+## Precompute Pattern (Overview)
+
+Use precompute to keep pages static while using feature flags. Middleware evaluates flags and encodes results into the URL via rewrite. The page reads precomputed values instead of re-evaluating.
+
+High-level flow:
+1. Declare flags and group them in an array
+2. Call `precompute(flagGroup)` in middleware, get a `code` string
+3. Rewrite request to `/${code}/original-path`
+4. Page reads flag values from `code`: `await myFlag(code, flagGroup)`
+
+For full implementation details, see framework-specific references:
+- **Next.js**: See [references/nextjs.md](references/nextjs.md) — covers proxy middleware, precompute setup, ISR, generatePermutations, multiple groups
+- **SvelteKit**: See [references/sveltekit.md](references/sveltekit.md) — covers reroute hook, middleware, precompute setup, ISR, prerendering
+
+## Custom Adapters
+
+Create an adapter factory returning an object with `origin` and `decide`:
+
+```ts
+import type { Adapter } from 'flags';
+
+export function createMyAdapter(/* options */) {
+  return function myAdapter<ValueType, EntitiesType>(): Adapter<ValueType, EntitiesType> {
+    return {
+      origin(key) {
+        return `https://my-provider.com/flags/${key}`;
+      },
+      async decide({ key }): Promise<ValueType> {
+        // evaluate against your provider
+        return false as ValueType;
+      },
+    };
+  };
+}
+```
+
+## Encryption Functions
+
+For keeping flag data confidential in the browser (used by Flags Explorer):
+
+| Function                   | Purpose                             |
+| -------------------------- | ----------------------------------- |
+| `encryptFlagValues`        | Encrypt resolved flag values        |
+| `decryptFlagValues`        | Decrypt flag values                 |
+| `encryptFlagDefinitions`   | Encrypt flag definitions/metadata   |
+| `decryptFlagDefinitions`   | Decrypt flag definitions            |
+| `encryptOverrides`         | Encrypt toolbar overrides           |
+| `decryptOverrides`         | Decrypt toolbar overrides           |
+
+All use `FLAGS_SECRET` by default. Example:
+
+```tsx
+import { encryptFlagValues } from 'flags';
+import { FlagValues } from 'flags/react';
+
+async function ConfidentialFlags({ values }) {
+  const encrypted = await encryptFlagValues(values);
+  return <FlagValues values={encrypted} />;
+}
+```
+
+## React Components
+
+```tsx
+import { FlagValues, FlagDefinitions } from 'flags/react';
+
+// Renders script tag with flag values for Flags Explorer
+<FlagValues values={{ myFlag: true }} />
+
+// Renders script tag with flag definitions for Flags Explorer
+<FlagDefinitions definitions={{ myFlag: { options: [...], description: '...' } }} />
+```
+
+## References
+
+Detailed framework and provider guides are in separate files to keep context lean:
+
+- **[references/nextjs.md](references/nextjs.md)**: Next.js quickstart, App Router, Pages Router, middleware/proxy, precompute, dedupe, dashboard pages, marketing pages, suspense fallbacks
+- **[references/sveltekit.md](references/sveltekit.md)**: SvelteKit quickstart, hooks setup, toolbar, precompute with reroute + middleware, dashboard pages, marketing pages
+- **[references/providers.md](references/providers.md)**: All provider adapters — Vercel, Edge Config, Statsig, LaunchDarkly, PostHog, GrowthBook, Hypertune, Flagsmith, Reflag, Split, Optimizely, OpenFeature, and custom adapters
+- **[references/api.md](references/api.md)**: Full API reference for `flags`, `flags/react`, `flags/next`, and `flags/sveltekit`
diff --git a/skills/flags-sdk/references/api.md b/skills/flags-sdk/references/api.md
@@ -0,0 +1,279 @@
+# API Reference
+
+## Table of Contents
+
+- [flags (core)](#flags-core)
+- [flags/react](#flagsreact)
+- [flags/next](#flagsnext)
+- [flags/sveltekit](#flagssveltekit)
+
+---
+
+## flags (core)
+
+### `verifyAccess`
+
+Verify access to the flags discovery endpoint. Returns `Promise<boolean>`.
+
+| Parameter       | Type     | Description              |
+| --------------- | -------- | ------------------------ |
+| `authorization` | `string` | Authorization token      |
+
+```ts
+import { verifyAccess } from 'flags';
+
+const access = await verifyAccess(request.headers.get('Authorization'));
+if (!access) return NextResponse.json(null, { status: 401 });
+```
+
+### `mergeProviderData`
+
+Merge provider data from multiple sources for the Flags Explorer.
+
+| Parameter | Type                                        | Description           |
+| --------- | ------------------------------------------- | --------------------- |
+| `data`    | `(ProviderData \| Promise<ProviderData>)[]` | Provider data to merge|
+
+```ts
+import { mergeProviderData } from 'flags';
+
+return mergeProviderData([
+  getProviderData(flags),
+  getStatsigProviderData({ /* ... */ }),
+]);
+```
+
+### `reportValue`
+
+Report flag value to Vercel for Runtime Logs and Web Analytics.
+
+| Parameter | Type     | Description     |
+| --------- | -------- | --------------- |
+| `key`     | `string` | Flag key        |
+| `value`   | `any`    | Resolved value  |
+
+```ts
+import { reportValue } from 'flags';
+reportValue('summer-sale', true);
+```
+
+### Encryption Functions
+
+All default to `process.env.FLAGS_SECRET`.
+
+| Function                 | Input Type           | Purpose                    |
+| ------------------------ | -------------------- | -------------------------- |
+| `encryptFlagValues`      | `FlagValuesType`     | Encrypt resolved values    |
+| `decryptFlagValues`      | `string`             | Decrypt values             |
+| `encryptFlagDefinitions` | `FlagDefinitionsType`| Encrypt definitions        |
+| `decryptFlagDefinitions` | `string`             | Decrypt definitions        |
+| `encryptOverrides`       | `FlagOverridesType`  | Encrypt toolbar overrides  |
+| `decryptOverrides`       | `string`             | Decrypt overrides          |
+
+Optional `secret` and `expirationTime` (default `'1y'`) params on encrypt functions.
+
+### `verifyAccessProof`
+
+Verify an access proof token. Returns `Promise<boolean>`.
+
+### `safeJsonStringify`
+
+XSS-safe `JSON.stringify`. Escapes `<` and other dangerous chars.
+
+```ts
+import { safeJsonStringify } from 'flags';
+safeJsonStringify({ markup: '<html></html>' });
+// '{"markup":"\\u003chtml>\\u003c/html>"}'
+```
+
+---
+
+## flags/react
+
+### `FlagValues`
+
+Renders a `<script data-flag-values>` tag for the Flags Explorer.
+
+| Prop     | Type             | Description  |
+| -------- | ---------------- | ------------ |
+| `values` | `FlagValuesType` | Flag values  |
+
+```tsx
+import { FlagValues } from 'flags/react';
+<FlagValues values={{ myFlag: true }} />
+```
+
+For confidential flags, encrypt first:
+
+```tsx
+import { encryptFlagValues } from 'flags';
+import { FlagValues } from 'flags/react';
+
+async function ConfidentialFlags({ values }) {
+  const encrypted = await encryptFlagValues(values);
+  return <FlagValues values={encrypted} />;
+}
+```
+
+### `FlagDefinitions`
+
+Renders a `<script data-flag-definitions>` tag with flag metadata.
+
+| Prop          | Type                  | Description       |
+| ------------- | --------------------- | ----------------- |
+| `definitions` | `FlagDefinitionsType` | Flag definitions  |
+
+```tsx
+import { FlagDefinitions } from 'flags/react';
+
+<FlagDefinitions definitions={{
+  myFlag: {
+    options: [{ value: false }, { value: true }],
+    origin: 'https://example.com/flag/myFlag',
+    description: 'Example flag',
+  },
+}} />
+```
+
+---
+
+## flags/next
+
+### `flag`
+
+Declare a feature flag for Next.js.
+
+| Parameter      | Type                               | Description                        |
+| -------------- | ---------------------------------- | ---------------------------------- |
+| `key`          | `string`                           | Flag identifier                    |
+| `decide`       | `function`                         | Resolves the flag value            |
+| `defaultValue` | `any`                              | Fallback value                     |
+| `description`  | `string`                           | Shown in Flags Explorer            |
+| `origin`       | `string`                           | URL to manage flag                 |
+| `options`      | `{ label?: string, value: any }[]` | Possible values                    |
+| `adapter`      | `Adapter`                          | Provider adapter                   |
+| `identify`     | `function`                         | Returns evaluation context         |
+
+### `createFlagsDiscoveryEndpoint`
+
+Creates an App Router route handler for `/.well-known/vercel/flags`. Auto-verifies access and adds version header.
+
+| Parameter        | Type       | Description                    |
+| ---------------- | ---------- | ------------------------------ |
+| `getApiData`     | `Function` | Returns flag metadata          |
+| `options.secret` | `string`   | Defaults to `FLAGS_SECRET`     |
+
+### `getProviderData`
+
+Turn `flag()` declarations into Flags Explorer-compatible definitions.
+
+| Parameter | Type                   | Description     |
+| --------- | ---------------------- | --------------- |
+| `flags`   | `Record<string, Flag>` | Your flags      |
+
+### `precompute`
+
+Evaluate multiple flags, return encoded string.
+
+| Parameter | Type         | Description |
+| --------- | ------------ | ----------- |
+| `flags`   | `function[]` | Flag group  |
+
+### `evaluate`
+
+Evaluate multiple flags, return their values as array.
+
+### `serialize`
+
+Turn evaluated flags into serialized representation.
+
+| Parameter | Type         | Description      |
+| --------- | ------------ | ---------------- |
+| `flags`   | `function[]` | Flags            |
+| `values`  | `unknown[]`  | Resolved values  |
+| `secret`  | `string`     | Signing secret   |
+
+### `getPrecomputed`
+
+Retrieve flag values from precomputation code.
+
+| Parameter         | Type                     | Description              |
+| ----------------- | ------------------------ | ------------------------ |
+| `flag`            | `function \| function[]` | Flag(s) to extract       |
+| `precomputeFlags` | `function[]`             | Group used in precompute |
+| `code`            | `string`                 | Precomputation code      |
+
+### `deserialize`
+
+Retrieve all flag values as a record from code.
+
+### `generatePermutations`
+
+Generate all possible precomputation codes for flag options.
+
+| Parameter | Type         | Description                          |
+| --------- | ------------ | ------------------------------------ |
+| `flags`   | `function[]` | Flags with options declared          |
+| `filter`  | `function`   | Optional filter for permutations     |
+| `secret`  | `string`     | Defaults to `FLAGS_SECRET`           |
+
+### `dedupe`
+
+Deduplicate function calls per request.
+
+| Parameter | Type       | Description            |
+| --------- | ---------- | ---------------------- |
+| `fn`      | `function` | Function to dedupe     |
+
+Not available in Pages Router.
+
+---
+
+## flags/sveltekit
+
+### `flag`
+
+Declare a feature flag for SvelteKit.
+
+| Parameter     | Type                               | Description                   |
+| ------------- | ---------------------------------- | ----------------------------- |
+| `key`         | `string`                           | Flag identifier               |
+| `decide`      | `function`                         | Resolves value                |
+| `description` | `string`                           | Shown in Flags Explorer       |
+| `origin`      | `string`                           | URL to manage flag            |
+| `options`     | `{ label?: string, value: any }[]` | Possible values               |
+| `identify`    | `function`                         | Returns evaluation context    |
+
+### `createHandle`
+
+Server hook that establishes context for flags and handles `/.well-known/vercel/flags`.
+
+| Parameter       | Type                                               | Description          |
+| --------------- | -------------------------------------------------- | -------------------- |
+| `options.secret`| `string`                                           | `FLAGS_SECRET`       |
+| `options.flags` | `Record<string, Flag>`                             | Your flags           |
+
+Must come first when composed with `sequence`.
+
+### `getProviderData`
+
+Turn flag declarations into Flags Explorer-compatible definitions.
+
+### `precompute`
+
+Evaluate multiple flags, return encoded string.
+
+| Parameter | Type         | Description   |
+| --------- | ------------ | ------------- |
+| `flags`   | `function[]` | Flag group    |
+| `request` | `Request`    | Current request |
+
+### `generatePermutations`
+
+Generate all precomputation codes for prerendering.
+
+| Parameter | Type         | Description                      |
+| --------- | ------------ | -------------------------------- |
+| `flags`   | `function[]` | Flags with options               |
+| `filter`  | `function`   | Optional filter                  |
+| `secret`  | `string`     | Defaults to `FLAGS_SECRET`       |
diff --git a/skills/flags-sdk/references/nextjs.md b/skills/flags-sdk/references/nextjs.md
@@ -0,0 +1,484 @@
+# Next.js Integration
+
+## Table of Contents
+
+- [Quickstart](#quickstart)
+- [App Router](#app-router)
+- [Pages Router](#pages-router)
+- [Evaluation Context](#evaluation-context)
+- [Dedupe](#dedupe)
+- [Precompute](#precompute)
+- [Dashboard Pages](#dashboard-pages)
+- [Marketing Pages](#marketing-pages)
+- [Proxy (Middleware)](#proxy-middleware)
+- [Suspense Fallbacks](#suspense-fallbacks)
+
+## Quickstart
+
+```sh
+pnpm i flags
+```
+
+Declare a flag in `flags.ts`:
+
+```ts
+import { flag } from 'flags/next';
+
+export const exampleFlag = flag({
+  key: 'example-flag',
+  decide() {
+    return Math.random() > 0.5;
+  },
+});
+```
+
+## App Router
+
+Call the flag function from any async server component or middleware:
+
+```tsx
+// app/page.tsx
+import { exampleFlag } from '../flags';
+
+export default async function Page() {
+  const example = await exampleFlag();
+  return <div>{example ? 'Flag is on' : 'Flag is off'}</div>;
+}
+```
+
+## Pages Router
+
+Pass `req` to the flag in `getServerSideProps`:
+
+```tsx
+// pages/index.tsx
+import type { InferGetServerSidePropsType, GetServerSideProps } from 'next';
+import { exampleFlag } from '../flags';
+
+export const getServerSideProps = (async ({ req }) => {
+  const example = await exampleFlag(req);
+  return { props: { example } };
+}) satisfies GetServerSideProps<{ example: boolean }>;
+
+export default function Page({
+  example,
+}: InferGetServerSidePropsType<typeof getServerSideProps>) {
+  return <div>{example ? 'Flag is on' : 'Flag is off'}</div>;
+}
+```
+
+## Evaluation Context
+
+Use `identify` to establish who the request is for. The returned entities are passed to `decide`:
+
+```ts
+import { flag, dedupe } from 'flags/next';
+import type { ReadonlyRequestCookies } from 'flags';
+
+interface Entities {
+  user?: { id: string };
+}
+
+const identify = dedupe(
+  ({ cookies }: { cookies: ReadonlyRequestCookies }): Entities => {
+    const userId = cookies.get('user-id')?.value;
+    return { user: userId ? { id: userId } : undefined };
+  },
+);
+
+export const myFlag = flag<boolean, Entities>({
+  key: 'my-flag',
+  identify,
+  decide({ entities }) {
+    return entities?.user?.id === 'user1';
+  },
+});
+```
+
+`identify` receives normalized `headers` and `cookies` that work across App Router, Pages Router, and Middleware.
+
+### Custom evaluation context
+
+Override identify at call site (use sparingly):
+
+```ts
+await exampleFlag.run({ identify: { user: { id: 'user1' } } });
+await exampleFlag.run({ identify: () => ({ user: { id: 'user1' } }) });
+```
+
+## Dedupe
+
+Wrap functions in `dedupe` to run them once per request within the same runtime:
+
+```ts
+import { dedupe } from 'flags/next';
+
+const identify = dedupe(({ cookies }) => {
+  return { user: { id: cookies.get('uid')?.value } };
+});
+```
+
+Use cases:
+- Prevent duplicate `identify` calls across multiple flags
+- Generate consistent random IDs for anonymous visitor experiments
+
+Not available in Pages Router.
+
+## Precompute
+
+Keep pages static while using feature flags. Middleware evaluates flags and encodes results into the URL.
+
+### Prerequisites
+
+Set `FLAGS_SECRET` env var (32 random bytes, base64-encoded):
+
+```sh
+node -e "console.log(crypto.randomBytes(32).toString('base64url'))"
+```
+
+### Step 1: Create flag group
+
+```ts
+// flags.ts
+import { flag } from 'flags/next';
+
+export const showSummerSale = flag({
+  key: 'summer-sale',
+  decide: () => false,
+});
+
+export const showBanner = flag({
+  key: 'banner',
+  decide: () => false,
+});
+
+export const marketingFlags = [showSummerSale, showBanner] as const;
+```
+
+### Step 2: Precompute in middleware
+
+```ts
+// proxy.ts
+import { type NextRequest, NextResponse } from 'next/server';
+import { precompute } from 'flags/next';
+import { marketingFlags } from './flags';
+
+export const config = { matcher: ['/'] };
+
+export async function proxy(request: NextRequest) {
+  const code = await precompute(marketingFlags);
+  const nextUrl = new URL(
+    `/${code}${request.nextUrl.pathname}${request.nextUrl.search}`,
+    request.url,
+  );
+  return NextResponse.rewrite(nextUrl, { request });
+}
+```
+
+### Step 3: Read precomputed values in page
+
+```tsx
+// app/[code]/page.tsx
+import { marketingFlags, showSummerSale, showBanner } from '../../flags';
+
+type Params = Promise<{ code: string }>;
+
+export default async function Page({ params }: { params: Params }) {
+  const { code } = await params;
+  const summerSale = await showSummerSale(code, marketingFlags);
+  const banner = await showBanner(code, marketingFlags);
+
+  return (
+    <div>
+      {banner && <p>welcome</p>}
+      {summerSale ? <p>summer sale live</p> : <p>summer sale soon</p>}
+    </div>
+  );
+}
+```
+
+### Enable ISR
+
+```tsx
+// app/[code]/layout.tsx
+export async function generateStaticParams() {
+  return []; // empty array enables ISR
+}
+
+export default async function Layout({ children }) {
+  return children;
+}
+```
+
+### Build-time rendering
+
+```tsx
+import { generatePermutations } from 'flags/next';
+
+export async function generateStaticParams() {
+  const codes = await generatePermutations(marketingFlags);
+  return codes.map((code) => ({ code }));
+}
+```
+
+### Declaring options
+
+Options enable efficient URL encoding and Flags Explorer display:
+
+```ts
+export const greetingFlag = flag<string>({
+  key: 'greeting',
+  options: ['Hello world', 'Hi', 'Hola'],
+  decide: () => 'Hello world',
+});
+```
+
+Or with labels:
+
+```ts
+export const greetingFlag = flag<string>({
+  key: 'greeting',
+  options: [
+    { label: 'Hello world', value: 'Hello world' },
+    { label: 'Hi', value: 'Hi' },
+  ],
+  decide: () => 'Hello world',
+});
+```
+
+### Multiple groups
+
+Avoid unnecessary permutations by creating separate flag groups per page:
+
+```ts
+export const rootFlags = [navigationFlag, bannerFlag];
+export const pricingFlags = [discountFlag];
+```
+
+File tree:
+
+```
+app/[rootCode]/
+  page.tsx
+  pricing/[pricingCode]/
+    page.tsx
+```
+
+### Pages Router precompute
+
+```tsx
+// pages/[code]/index.tsx
+import { generatePermutations } from 'flags/next';
+
+export const getStaticPaths = (async () => {
+  const codes = await generatePermutations(marketingFlags);
+  return {
+    paths: codes.map((code) => ({ params: { code } })),
+    fallback: 'blocking',
+  };
+}) satisfies GetStaticPaths;
+
+export const getStaticProps = (async (context) => {
+  if (typeof context.params?.code !== 'string') return { notFound: true };
+  const example = await exampleFlag(context.params.code, marketingFlags);
+  return { props: { example } };
+}) satisfies GetStaticProps<{ example: boolean }>;
+```
+
+## Dashboard Pages
+
+For authenticated dashboard pages, use `identify` to read user context from cookies/JWTs:
+
+```ts
+import type { ReadonlyRequestCookies } from 'flags';
+import { flag, dedupe } from 'flags/next';
+
+interface Entities {
+  user?: { id: string };
+}
+
+const identify = dedupe(
+  ({ cookies }: { cookies: ReadonlyRequestCookies }): Entities => {
+    const userId = cookies.get('dashboard-user-id')?.value;
+    return { user: userId ? { id: userId } : undefined };
+  },
+);
+
+export const dashboardFlag = flag<boolean, Entities>({
+  key: 'dashboard-flag',
+  identify,
+  decide({ entities }) {
+    if (!entities?.user) return false;
+    const allowedUsers = ['user1'];
+    return allowedUsers.includes(entities.user.id);
+  },
+});
+```
+
+Usage in a page:
+
+```tsx
+export default async function DashboardPage() {
+  const dashboard = await dashboardFlag();
+  return <div>{dashboard ? 'New Dashboard' : 'Old Dashboard'}</div>;
+}
+```
+
+## Marketing Pages
+
+For static marketing pages with A/B tests, combine precompute with visitor ID generation:
+
+### Visitor ID in middleware
+
+```ts
+// proxy.ts
+import { precompute } from 'flags/next';
+import { type NextRequest, NextResponse } from 'next/server';
+import { marketingFlags } from './flags';
+import { getOrGenerateVisitorId } from './get-or-generate-visitor-id';
+
+export async function marketingMiddleware(request: NextRequest) {
+  const visitorId = await getOrGenerateVisitorId(
+    request.cookies,
+    request.headers,
+  );
+
+  const code = await precompute(marketingFlags);
+
+  return NextResponse.rewrite(
+    new URL(`/examples/marketing-pages/${code}`, request.url),
+    {
+      headers: {
+        'Set-Cookie': `marketing-visitor-id=${visitorId}; Path=/`,
+        'x-marketing-visitor-id': visitorId,
+      },
+    },
+  );
+}
+```
+
+### Deduplicated visitor ID generation
+
+```ts
+import { nanoid } from 'nanoid';
+import { dedupe } from 'flags/next';
+import type { ReadonlyHeaders, ReadonlyRequestCookies } from 'flags';
+
+const generateId = dedupe(async () => nanoid());
+
+export const getOrGenerateVisitorId = async (
+  cookies: ReadonlyRequestCookies,
+  headers: ReadonlyHeaders,
+) => {
+  const cookieVisitorId = cookies.get('marketing-visitor-id')?.value;
+  if (cookieVisitorId) return cookieVisitorId;
+
+  const headerVisitorId = headers.get('x-marketing-visitor-id');
+  if (headerVisitorId) return headerVisitorId;
+
+  return generateId();
+};
+```
+
+### Flag using visitor ID
+
+```ts
+const identify = dedupe(
+  async ({ cookies }: { cookies: ReadonlyRequestCookies }): Promise<Entities> => {
+    const visitorId = await getOrGenerateVisitorId(cookies);
+    return { visitor: visitorId ? { id: visitorId } : undefined };
+  },
+);
+
+export const marketingAbTest = flag<boolean, Entities>({
+  key: 'marketing-ab-test-flag',
+  identify,
+  decide({ entities }) {
+    if (!entities?.visitor) return false;
+    return /^[a-n0-5]/i.test(entities.visitor.id);
+  },
+});
+```
+
+## Proxy (Middleware)
+
+Use flags in middleware to rewrite requests to static page variants:
+
+```ts
+// proxy.ts
+import { type NextRequest, NextResponse } from 'next/server';
+import { myFlag } from './flags';
+
+export const config = { matcher: ['/example'] };
+
+export async function proxy(request: NextRequest) {
+  const active = await myFlag();
+  const variant = active ? 'variant-on' : 'variant-off';
+  return NextResponse.rewrite(new URL(`/example/${variant}`, request.url));
+}
+```
+
+For multiple flags on one page, use the precompute pattern instead.
+
+## Suspense Fallbacks
+
+Combine precomputed flags with Partial Prerendering to serve matching skeletons:
+
+```tsx
+async function Example() {
+  const hasAuth = await hasAuthCookieFlag();
+
+  return (
+    <Suspense fallback={hasAuth ? <AuthedSkeleton /> : <UnauthedSkeleton />}>
+      <Dashboard />
+    </Suspense>
+  );
+}
+```
+
+The `hasAuthCookieFlag` checks cookie existence without authenticating. Two shells get prerendered — one for each auth state — served statically with no layout shift.
+
+## Flags Explorer (Next.js)
+
+### App Router
+
+```ts
+// app/.well-known/vercel/flags/route.ts
+import { getProviderData, createFlagsDiscoveryEndpoint } from 'flags/next';
+import * as flags from '../../../../flags';
+
+export const GET = createFlagsDiscoveryEndpoint(async () => {
+  return getProviderData(flags);
+});
+```
+
+### Pages Router
+
+Requires a rewrite in `next.config.js`:
+
+```js
+module.exports = {
+  async rewrites() {
+    return [
+      {
+        source: '/.well-known/vercel/flags',
+        destination: '/api/vercel/flags',
+      },
+    ];
+  },
+};
+```
+
+```ts
+// pages/api/vercel/flags.ts
+import type { NextApiRequest, NextApiResponse } from 'next';
+import { verifyAccess } from 'flags';
+
+export async function handler(req: NextApiRequest, res: NextApiResponse) {
+  const access = await verifyAccess(req.headers.authorization);
+  if (!access) return res.status(401).json(null);
+
+  const providerData = { /* ... */ };
+  return res.status(200).json(providerData);
+}
+```
diff --git a/skills/flags-sdk/references/providers.md b/skills/flags-sdk/references/providers.md
@@ -0,0 +1,594 @@
+# Provider Adapters
+
+## Table of Contents
+
+- [Vercel](#vercel)
+- [Edge Config](#edge-config)
+- [Statsig](#statsig)
+- [LaunchDarkly](#launchdarkly)
+- [PostHog](#posthog)
+- [GrowthBook](#growthbook)
+- [Hypertune](#hypertune)
+- [Flagsmith](#flagsmith)
+- [Reflag](#reflag)
+- [OpenFeature](#openfeature)
+- [Split](#split)
+- [Optimizely](#optimizely)
+- [Custom Adapters](#custom-adapters)
+
+---
+
+## Vercel
+
+Package: `@flags-sdk/vercel` (also requires `@vercel/flags-core`)
+
+```bash
+pnpm i flags @flags-sdk/vercel @vercel/flags-core
+```
+
+### Setup
+
+1. Create a flag in the Vercel dashboard
+2. Pull env vars: `vercel env pull` (sets `FLAGS` and `FLAGS_SECRET`)
+3. Declare the flag:
+
+```ts
+import { flag } from 'flags/next';
+import { vercelAdapter } from '@flags-sdk/vercel';
+
+export const exampleFlag = flag({
+  key: 'example-flag',
+  adapter: vercelAdapter(),
+});
+```
+
+### User targeting
+
+```ts
+import { dedupe, flag } from 'flags/next';
+import { vercelAdapter } from '@flags-sdk/vercel';
+
+type Entities = {
+  team?: { id: string };
+  user?: { id: string };
+};
+
+const identify = dedupe(async (): Promise<Entities> => ({
+  team: { id: 'team-123' },
+  user: { id: 'user-456' },
+}));
+
+export const exampleFlag = flag<boolean, Entities>({
+  key: 'example-flag',
+  identify,
+  adapter: vercelAdapter(),
+});
+```
+
+### Flags Explorer
+
+```ts
+import { createFlagsDiscoveryEndpoint } from 'flags/next';
+import { getProviderData } from '@flags-sdk/vercel';
+import * as flags from '../../../../flags';
+
+export const GET = createFlagsDiscoveryEndpoint(async () => {
+  return await getProviderData(flags);
+});
+```
+
+### Custom configuration
+
+```ts
+import { createVercelAdapter } from '@flags-sdk/vercel';
+
+const customAdapter = createVercelAdapter(process.env.CUSTOM_FLAGS_KEY!);
+
+export const exampleFlag = flag({
+  key: 'example-flag',
+  adapter: customAdapter(),
+});
+```
+
+---
+
+## Edge Config
+
+Package: `@flags-sdk/edge-config`
+
+```bash
+pnpm i @flags-sdk/edge-config
+```
+
+Env: `EDGE_CONFIG="edge-config-connection-string"`
+
+### Usage
+
+```ts
+import { flag } from 'flags/next';
+import { edgeConfigAdapter } from '@flags-sdk/edge-config';
+
+export const exampleFlag = flag({
+  adapter: edgeConfigAdapter(),
+  key: 'example-flag',
+});
+```
+
+Edge Config should contain:
+
+```json
+{
+  "flags": {
+    "example-flag": true,
+    "another-flag": false
+  }
+}
+```
+
+### Custom configuration
+
+```ts
+import { createEdgeConfigAdapter } from '@flags-sdk/edge-config';
+
+const myAdapter = createEdgeConfigAdapter({
+  connectionString: process.env.OTHER_EDGE_CONFIG,
+  options: {
+    edgeConfigItemKey: 'other-flags-key',
+    teamSlug: 'my-team',
+  },
+});
+```
+
+---
+
+## Statsig
+
+Package: `@flags-sdk/statsig`
+
+```bash
+pnpm i @flags-sdk/statsig
+```
+
+Env vars:
+- `STATSIG_SERVER_API_KEY` (required)
+- `STATSIG_PROJECT_ID` (optional)
+- `EXPERIMENTATION_CONFIG` (optional, Edge Config)
+- `EXPERIMENTATION_CONFIG_ITEM_KEY` (optional)
+
+### Methods
+
+```ts
+import { statsigAdapter, type StatsigUser } from '@flags-sdk/statsig';
+
+// Feature Gates
+export const myGate = flag<boolean, StatsigUser>({
+  key: 'my_feature_gate',
+  adapter: statsigAdapter.featureGate((gate) => gate.value),
+  identify,
+});
+
+// Dynamic Configs
+export const myConfig = flag<Record<string, unknown>, StatsigUser>({
+  key: 'my_dynamic_config',
+  adapter: statsigAdapter.dynamicConfig((config) => config.value),
+  identify,
+});
+
+// Experiments
+export const myExperiment = flag<Record<string, unknown>, StatsigUser>({
+  key: 'my_experiment',
+  adapter: statsigAdapter.experiment((config) => config.value),
+  identify,
+});
+
+// Autotune
+export const myAutotune = flag<Record<string, unknown>, StatsigUser>({
+  key: 'my_autotune',
+  adapter: statsigAdapter.autotune((config) => config.value),
+  identify,
+});
+
+// Layers
+export const myLayer = flag<Record<string, unknown>, StatsigUser>({
+  key: 'my_layer',
+  adapter: statsigAdapter.layer((layer) => layer.value),
+  identify,
+});
+```
+
+### Same key, different mappings
+
+Use `.` to distinguish flags from the same config:
+
+```ts
+export const text = flag<string, StatsigUser>({
+  key: 'my_config.text',
+  adapter: statsigAdapter.dynamicConfig((c) => c.value.text as string),
+  identify,
+});
+
+export const price = flag<number, StatsigUser>({
+  key: 'my_config.price',
+  adapter: statsigAdapter.dynamicConfig((c) => c.value.price as number),
+  identify,
+});
+```
+
+### Exposure logging
+
+Disabled by default (middleware prefetch would cause premature exposures). Enable explicitly:
+
+```ts
+adapter: statsigAdapter.featureGate((gate) => gate.value, {
+  exposureLogging: true,
+})
+```
+
+Log exposures from the client instead when possible.
+
+### Flags Explorer
+
+```ts
+import { getProviderData as getStatsigProviderData } from '@flags-sdk/statsig';
+import { mergeProviderData } from 'flags';
+
+export const GET = createFlagsDiscoveryEndpoint(async () => {
+  return mergeProviderData([
+    getProviderData(flags),
+    getStatsigProviderData({
+      consoleApiKey: process.env.STATSIG_CONSOLE_API_KEY,
+      projectId: process.env.STATSIG_PROJECT_ID,
+    }),
+  ]);
+});
+```
+
+---
+
+## LaunchDarkly
+
+Package: `@flags-sdk/launchdarkly`
+
+```bash
+pnpm i @flags-sdk/launchdarkly
+```
+
+Env vars:
+- `LAUNCHDARKLY_CLIENT_SIDE_ID` (required)
+- `LAUNCHDARKLY_PROJECT_SLUG` (required)
+- `EDGE_CONFIG` (required)
+
+### Usage
+
+```ts
+import { ldAdapter, type LDContext } from '@flags-sdk/launchdarkly';
+
+const identify = dedupe((async ({ headers, cookies }) => {
+  const user = await getUser(headers, cookies);
+  return { key: user.userID };
+}) satisfies Identify<LDContext>);
+
+export const exampleFlag = flag<boolean, LDContext>({
+  key: 'example-flag',
+  identify,
+  adapter: ldAdapter.variation(),
+});
+```
+
+### Flags Explorer
+
+```ts
+import { getProviderData as getLDProviderData } from '@flags-sdk/launchdarkly';
+
+return mergeProviderData([
+  getProviderData(flags),
+  getLDProviderData({
+    apiKey: process.env.LAUNCHDARKLY_API_KEY,
+    projectKey: process.env.LAUNCHDARKLY_PROJECT_KEY,
+    environment: process.env.LAUNCHDARKLY_ENVIRONMENT,
+  }),
+]);
+```
+
+---
+
+## PostHog
+
+Package: `@flags-sdk/posthog`
+
+```bash
+pnpm i @flags-sdk/posthog
+```
+
+Env vars:
+- `NEXT_PUBLIC_POSTHOG_KEY`
+- `NEXT_PUBLIC_POSTHOG_HOST` (e.g. `https://us.i.posthog.com`)
+
+### Methods
+
+```ts
+import { postHogAdapter } from '@flags-sdk/posthog';
+
+// Boolean check
+export const myFlag = flag({
+  key: 'my-flag',
+  adapter: postHogAdapter.isFeatureEnabled(),
+  identify,
+});
+
+// Multivariate value
+export const myVariant = flag({
+  key: 'my-flag',
+  adapter: postHogAdapter.featureFlagValue(),
+  identify,
+});
+
+// Payload
+export const myPayload = flag({
+  key: 'my-flag',
+  adapter: postHogAdapter.featureFlagPayload((v) => v),
+  defaultValue: {},
+  identify,
+});
+```
+
+### Flags Explorer
+
+Requires: `POSTHOG_PERSONAL_API_KEY`, `POSTHOG_PROJECT_ID`
+
+```ts
+import { getProviderData as getPostHogProviderData } from '@flags-sdk/posthog';
+
+export const GET = createFlagsDiscoveryEndpoint(() =>
+  getPostHogProviderData({
+    personalApiKey: process.env.POSTHOG_PERSONAL_API_KEY,
+    projectId: process.env.NEXT_PUBLIC_POSTHOG_PROJECT_ID,
+  }),
+);
+```
+
+---
+
+## GrowthBook
+
+Package: `@flags-sdk/growthbook`
+
+```bash
+pnpm i @flags-sdk/growthbook
+```
+
+Env: `GROWTHBOOK_CLIENT_KEY` (required)
+
+### Usage
+
+```ts
+import { growthbookAdapter, type Attributes } from '@flags-sdk/growthbook';
+
+const identify = dedupe((async ({ cookies }) => ({
+  id: cookies.get('user_id')?.value,
+})) satisfies Identify<Attributes>);
+
+export const myFlag = flag({
+  key: 'my_feature',
+  identify,
+  adapter: growthbookAdapter.feature<boolean>(),
+});
+```
+
+### Edge Config
+
+Set `GROWTHBOOK_EDGE_CONNECTION_STRING` or `EXPERIMENTATION_CONFIG` (Vercel Marketplace).
+
+### Tracking
+
+```ts
+growthbookAdapter.setTrackingCallback((experiment, result) => {
+  after(async () => {
+    console.log('Experiment', experiment.key, 'Variation', result.key);
+  });
+});
+```
+
+---
+
+## Hypertune
+
+Package: `@flags-sdk/hypertune`
+
+```bash
+pnpm i hypertune flags server-only @flags-sdk/hypertune @vercel/edge-config
+```
+
+Requires code generation: `npx hypertune`
+
+```ts
+import { createHypertuneAdapter } from '@flags-sdk/hypertune';
+import { createSource, flagFallbacks, vercelFlagDefinitions, type Context, type FlagValues } from './generated/hypertune';
+
+const hypertuneAdapter = createHypertuneAdapter<FlagValues, Context>({
+  createSource,
+  flagFallbacks,
+  flagDefinitions: vercelFlagDefinitions,
+  identify,
+});
+
+export const exampleFlag = flag(hypertuneAdapter.declarations.exampleFlag);
+```
+
+---
+
+## Flagsmith
+
+Package: `@flags-sdk/flagsmith`
+
+```bash
+pnpm i @flags-sdk/flagsmith
+```
+
+Env: `FLAGSMITH_ENVIRONMENT_ID` (required)
+
+### Usage with type coercion
+
+```ts
+import { flagsmithAdapter } from '@flags-sdk/flagsmith';
+
+export const buttonColor = flag<string>({
+  key: 'button-color',
+  defaultValue: 'blue',
+  adapter: flagsmithAdapter.getValue({ coerce: 'string' }),
+});
+
+export const showBanner = flag<boolean>({
+  key: 'show-banner',
+  defaultValue: false,
+  adapter: flagsmithAdapter.getValue({ coerce: 'boolean' }),
+});
+```
+
+Coercion options: `'string'`, `'number'`, `'boolean'`, or omit for raw value.
+
+---
+
+## Reflag
+
+Package: `@flags-sdk/reflag`
+
+```bash
+pnpm i @flags-sdk/reflag
+```
+
+Env: `REFLAG_SECRET_KEY`
+
+```ts
+import { reflagAdapter, type Context } from '@flags-sdk/reflag';
+
+const identify = dedupe((async ({ headers, cookies }) => ({
+  user: { id: 'user-id', name: 'name', email: 'email' },
+  company: { id: 'company-id' },
+})) satisfies Identify<Context>);
+
+export const myFeature = flag<boolean, Context>({
+  key: 'my_feature',
+  identify,
+  adapter: reflagAdapter.isEnabled(),
+});
+```
+
+---
+
+## OpenFeature
+
+Package: `@flags-sdk/openfeature` + `@openfeature/server-sdk`
+
+```bash
+pnpm i @flags-sdk/openfeature @openfeature/server-sdk
+```
+
+### Setup
+
+```ts
+import { createOpenFeatureAdapter } from '@flags-sdk/openfeature';
+
+// Sync provider
+OpenFeature.setProvider(new YourProvider());
+const adapter = createOpenFeatureAdapter(OpenFeature.getClient());
+
+// Async provider
+const adapter = createOpenFeatureAdapter(async () => {
+  await OpenFeature.setProviderAndWait(new YourProvider());
+  return OpenFeature.getClient();
+});
+```
+
+### Methods
+
+```ts
+adapter.booleanValue()  // boolean flags
+adapter.stringValue()   // string flags
+adapter.numberValue()   // number flags
+adapter.objectValue()   // object flags
+```
+
+All require `defaultValue` on the flag declaration.
+
+---
+
+## Split
+
+Package: `@flags-sdk/split` (Flags Explorer only, adapter coming soon)
+
+```ts
+import { getProviderData as getSplitProviderData } from '@flags-sdk/split';
+
+getSplitProviderData({
+  adminApiKey: process.env.SPLIT_ADMIN_API_KEY,
+  environmentId: process.env.SPLIT_ENVIRONMENT_ID,
+  organizationId: process.env.SPLIT_ORG_ID,
+  workspaceId: process.env.SPLIT_WORKSPACE_ID,
+});
+```
+
+---
+
+## Optimizely
+
+Package: `@flags-sdk/optimizely` (Flags Explorer only, adapter coming soon)
+
+```ts
+import { getProviderData as getOptimizelyProviderData } from '@flags-sdk/optimizely';
+
+getOptimizelyProviderData({
+  projectId: process.env.OPTIMIZELY_PROJECT_ID,
+  apiKey: process.env.OPTIMIZELY_API_KEY,
+});
+```
+
+---
+
+## Custom Adapters
+
+Create an adapter factory:
+
+```ts
+import type { Adapter } from 'flags';
+
+export function createMyAdapter(/* options */) {
+  return function myAdapter<ValueType, EntitiesType>(): Adapter<ValueType, EntitiesType> {
+    return {
+      origin(key) {
+        return `https://my-provider.com/flags/${key}`;
+      },
+      async decide({ key }): Promise<ValueType> {
+        return false as ValueType;
+      },
+    };
+  };
+}
+```
+
+### Default adapter pattern
+
+Expose a lazily-initialized default for simpler usage:
+
+```ts
+let defaultAdapter: ReturnType<typeof createMyAdapter> | undefined;
+
+export function myAdapter<V, E>(): Adapter<V, E> {
+  if (!defaultAdapter) {
+    if (!process.env.MY_API_KEY) throw new Error('Missing MY_API_KEY');
+    defaultAdapter = createMyAdapter(process.env.MY_API_KEY);
+  }
+  return defaultAdapter<V, E>();
+}
+```
+
+Usage:
+
+```ts
+import { myAdapter } from './my-adapter';
+
+export const exampleFlag = flag({
+  key: 'example',
+  adapter: myAdapter(),
+});
+```
diff --git a/skills/flags-sdk/references/sveltekit.md b/skills/flags-sdk/references/sveltekit.md
@@ -0,0 +1,408 @@
+# SvelteKit Integration
+
+## Table of Contents
+
+- [Quickstart](#quickstart)
+- [Toolbar Setup](#toolbar-setup)
+- [Flag Declaration](#flag-declaration)
+- [Evaluation Context](#evaluation-context)
+- [Precompute](#precompute)
+- [Dashboard Pages](#dashboard-pages)
+- [Marketing Pages](#marketing-pages)
+
+## Quickstart
+
+### Installation
+
+```sh
+pnpm i flags @vercel/toolbar
+```
+
+### Create a flag
+
+```ts
+// src/lib/flags.ts
+import { flag } from 'flags/sveltekit';
+
+export const showDashboard = flag<boolean>({
+  key: 'showDashboard',
+  description: 'Show the dashboard',
+  origin: 'https://example.com/#showdashboard',
+  options: [{ value: true }, { value: false }],
+  decide(_event) {
+    return false;
+  },
+});
+```
+
+### Set up the server hook
+
+One-time setup that makes the toolbar aware of your flags:
+
+```ts
+// src/hooks.server.ts
+import { createHandle } from 'flags/sveltekit';
+import { FLAGS_SECRET } from '$env/static/private';
+import * as flags from '$lib/flags';
+
+export const handle = createHandle({ secret: FLAGS_SECRET, flags });
+```
+
+When composing with other handlers via SvelteKit's `sequence`, `createHandle` must come first.
+
+### Use the flag
+
+```ts
+// src/routes/+page.server.ts
+import { showDashboard } from '$lib/flags';
+
+export const load = async () => {
+  const dashboard = await showDashboard();
+  return {
+    post: { title: dashboard ? 'New Dashboard' : 'Old Dashboard' },
+  };
+};
+```
+
+```svelte
+<!-- src/routes/+page.svelte -->
+<script lang="ts">
+  import type { PageProps } from './$types';
+  let { data }: PageProps = $props();
+</script>
+
+<h1>{data.post.title}</h1>
+```
+
+## Toolbar Setup
+
+1. Install `@vercel/toolbar`
+2. Add vite plugin:
+
+```ts
+// vite.config.ts
+import { sveltekit } from '@sveltejs/kit/vite';
+import { defineConfig } from 'vite';
+import { vercelToolbar } from '@vercel/toolbar/plugins/vite';
+
+export default defineConfig({
+  plugins: [sveltekit(), vercelToolbar()],
+});
+```
+
+3. Render toolbar in layout:
+
+```svelte
+<!-- src/routes/+layout.svelte -->
+<script lang="ts">
+  import type { LayoutProps } from './$types';
+  import { mountVercelToolbar } from '@vercel/toolbar/vite';
+  import { onMount } from 'svelte';
+
+  onMount(() => mountVercelToolbar());
+
+  let { children }: LayoutProps = $props();
+</script>
+
+<main>
+  {@render children()}
+</main>
+```
+
+## Flag Declaration
+
+```ts
+import { flag } from 'flags/sveltekit';
+
+export const showSummerSale = flag<boolean>({
+  key: 'summer-sale',
+  async decide() { return false; },
+  origin: 'https://example.com/flags/summer-sale/',
+  description: 'Show Summer Holiday Sale Banner, 20% off',
+  options: [
+    { value: false, label: 'Hide' },
+    { value: true, label: 'Show' },
+  ],
+});
+```
+
+## Evaluation Context
+
+Use `identify` to segment users. Headers and cookies are normalized:
+
+```ts
+import { flag } from 'flags/sveltekit';
+
+interface Entities {
+  user?: { id: string };
+}
+
+export const exampleFlag = flag<boolean, Entities>({
+  key: 'identify-example-flag',
+  identify({ headers, cookies }) {
+    const userId = cookies.get('user-id')?.value;
+    return { user: userId ? { id: userId } : undefined };
+  },
+  decide({ entities }) {
+    return entities?.user?.id === 'user1';
+  },
+});
+```
+
+### Deduplication
+
+Extract `identify` as a named function and reuse across flags. Calls are deduped by function identity:
+
+```ts
+import type { ReadonlyHeaders, ReadonlyRequestCookies } from 'flags';
+import { flag } from 'flags/sveltekit';
+
+interface Entities {
+  visitorId?: string;
+}
+
+function identify({
+  cookies,
+  headers,
+}: {
+  cookies: ReadonlyRequestCookies;
+  headers: ReadonlyHeaders;
+}): Entities {
+  const visitorId =
+    cookies.get('visitorId')?.value ?? headers.get('x-visitorId');
+  return { visitorId };
+}
+
+export const flag1 = flag<boolean, Entities>({
+  key: 'flag1',
+  identify,
+  decide({ entities }) { /* ... */ },
+});
+
+export const flag2 = flag<boolean, Entities>({
+  key: 'flag2',
+  identify,
+  decide({ entities }) { /* ... */ },
+});
+```
+
+## Precompute
+
+### Why both Routing Middleware and reroute
+
+- `middleware.ts` handles full page visits in production (runs before CDN)
+- `reroute` handles client-side navigations and dev-time routing
+- Middleware has access to cookies and private env vars; `reroute` runs on client and must defer to server
+
+### Step 1: Create flag group
+
+```ts
+// src/lib/flags.ts
+import { flag } from 'flags/sveltekit';
+
+export const firstPricingABTest = flag({
+  key: 'firstPricingABTest',
+  decide: () => false,
+});
+
+export const secondPricingABTest = flag({
+  key: 'secondPricingABTest',
+  decide: () => false,
+});
+```
+
+```ts
+// src/lib/precomputed-flags.ts
+import { precompute } from 'flags/sveltekit';
+import { firstPricingABTest, secondPricingABTest } from './flags';
+
+export const pricingFlags = [firstPricingABTest, secondPricingABTest];
+
+export async function computeInternalRoute(pathname: string, request: Request) {
+  if (pathname === '/pricing') {
+    return '/pricing/' + (await precompute(pricingFlags, request));
+  }
+  return pathname;
+}
+```
+
+### Step 2: Set up reroute hook
+
+```ts
+// src/hooks.ts
+export async function reroute({ url, fetch }) {
+  if (url.pathname === '/pricing') {
+    const destination = new URL('/api/reroute', url);
+    destination.searchParams.set('pathname', url.pathname);
+    return fetch(destination).then((response) => response.text());
+  }
+}
+```
+
+```ts
+// src/routes/api/reroute/+server.ts
+import { text } from '@sveltejs/kit';
+import { computeInternalRoute } from '$lib/precomputed-flags';
+
+export async function GET({ url, request }) {
+  const destination = await computeInternalRoute(
+    url.searchParams.get('pathname')!,
+    request,
+  );
+  return text(destination);
+}
+```
+
+### Step 3: Set up middleware
+
+```ts
+// middleware.ts
+import { rewrite } from '@vercel/edge';
+import { normalizeUrl } from '@sveltejs/kit';
+import { computeInternalRoute } from './src/lib/precomputed-flags';
+
+export const config = { matcher: ['/pricing'] };
+
+export default async function middleware(request: Request) {
+  const { url, denormalize } = normalizeUrl(request.url);
+  if (url.pathname === '/pricing') {
+    return rewrite(
+      denormalize(await computeInternalRoute(url.pathname, request)),
+    );
+  }
+}
+```
+
+### Step 4: Read precomputed values
+
+```ts
+// src/routes/pricing/[code]/+page.server.ts
+import type { PageServerLoad } from './$types';
+import { firstPricingABTest, secondPricingABTest } from '$lib/flags';
+import { pricingFlags } from '$lib/precomputed-flags';
+
+export const load: PageServerLoad = async ({ params }) => {
+  const flag1 = await firstPricingABTest(params.code, pricingFlags);
+  const flag2 = await secondPricingABTest(params.code, pricingFlags);
+  return {
+    first: `First: ${flag1}`,
+    second: `Second: ${flag2}`,
+  };
+};
+```
+
+```svelte
+<!-- src/routes/pricing/[code]/+page.svelte -->
+<script>
+  let { data } = $props();
+</script>
+
+<p>{data.first}</p>
+<p>{data.second}</p>
+```
+
+### Enable ISR
+
+```ts
+// src/routes/pricing/[code]/+page.server.ts
+export const config = {
+  isr: { expiration: false },
+};
+```
+
+### Enable prerendering
+
+```ts
+import { generatePermutations } from 'flags/sveltekit';
+import { pricingFlags } from '$lib/precomputed-flags';
+
+export const prerender = true;
+
+export async function entries() {
+  return (await generatePermutations(pricingFlags)).map((code) => ({ code }));
+}
+```
+
+## Dashboard Pages
+
+```ts
+// src/lib/flags.ts
+import { flag } from 'flags/sveltekit';
+
+export const showNewDashboard = flag<boolean>({
+  key: 'showNewDashboard',
+  decide({ cookies }) {
+    return cookies.get('showNewDashboard')?.value === 'true';
+  },
+});
+```
+
+```ts
+// src/routes/+page.server.ts
+import type { PageServerLoad } from './$types';
+import { showNewDashboard } from '$lib/flags';
+
+export const load: PageServerLoad = async () => {
+  const dashboard = await showNewDashboard();
+  return { title: dashboard ? 'New Dashboard' : 'Old Dashboard' };
+};
+```
+
+## Marketing Pages
+
+Combine precompute with visitor ID generation for A/B tests on static pages:
+
+### Middleware with visitor ID
+
+```ts
+// middleware.ts
+import { rewrite } from '@vercel/edge';
+import { parse } from 'cookie';
+import { normalizeUrl } from '@sveltejs/kit';
+import { computeInternalRoute, createVisitorId } from './src/lib/precomputed-flags';
+
+export const config = { matcher: ['/examples/marketing-pages'] };
+
+export default async function middleware(request: Request) {
+  const { url, denormalize } = normalizeUrl(request.url);
+
+  let visitorId = parse(request.headers.get('cookie') ?? '').visitorId || '';
+  if (!visitorId) {
+    visitorId = createVisitorId();
+    request.headers.set('x-visitorId', visitorId);
+  }
+
+  return rewrite(
+    denormalize(await computeInternalRoute(url.pathname, request)),
+  );
+}
+```
+
+### Flags with identify
+
+```ts
+// src/lib/flags.ts
+import { flag } from 'flags/sveltekit';
+
+interface Entities {
+  visitorId?: string;
+}
+
+function identify({ cookies, headers }) {
+  const visitorId =
+    cookies.get('visitorId')?.value ?? headers.get('x-visitorId');
+  if (!visitorId) throw new Error('Visitor ID not found');
+  return { visitorId };
+}
+
+export const firstMarketingABTest = flag<boolean, Entities>({
+  key: 'firstMarketingABTest',
+  identify,
+  decide({ entities }) {
+    if (!entities?.visitorId) return false;
+    return /^[a-n0-5]/i.test(entities.visitorId);
+  },
+});
+```
+
+The `x-visitorId` header ensures the visitor ID is available even on the first request before the cookie is set.
PATCH

echo "Gold patch applied."
