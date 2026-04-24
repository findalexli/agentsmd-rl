# Server actions return corrupted response on dynamic SSG routes in production

## Bug Description

When running a Next.js app in **production standalone mode** with dynamic SSG routes (e.g., `[slug]`), server actions return incorrect responses. Instead of receiving just the RSC action result, the client gets the **cached fallback HTML shell** with the action result appended to it. This causes the client to fail to parse the response, breaking form submissions and `useActionState` hooks.

The issue is in the app-page request handler in `packages/next/src/build/templates/app-page.ts`.

## Steps to Reproduce

1. Create a Next.js app with `output: 'standalone'` in `next.config.ts`
2. Add a dynamic route like `app/[slug]/page.tsx` with `generateStaticParams` (making it SSG)
3. Include a server action (e.g., a form with `useActionState`)
4. Build and run in standalone mode (`next build` + `node .next/standalone/server.js`)
5. Navigate to a dynamic page (e.g., `/world`) and submit the form
6. The server action response is corrupted — the HTML shell is prepended to the action result

## Root Cause Area

The request handler computes a `staticPathKey` that determines whether a request enters the fallback rendering path. There is a condition around line 620 that decides when to set `staticPathKey` for dynamic SSG routes with fallback parameters. This condition does not account for all request types, causing certain requests to incorrectly enter the fallback rendering block instead of being handled through the normal action response path.

Server action fetch requests from the client have specific characteristics: they do NOT send the `RSC` header (`rsc: 1`) — they only send `Accept: text/x-component` and the `Next-Action` header. This means `isRSCRequest` and `isDynamicRSCRequest` are both `false` for action requests, but the `staticPathKey` condition doesn't take this into account.

## Expected Behavior

Server action requests should bypass the fallback rendering block entirely and respond with just the RSC action result payload.

## Relevant Code

- `packages/next/src/build/templates/app-page.ts` — the `handler` function, specifically the `staticPathKey` computation around lines 615-627
- Look at how `ssgCacheKey` handles this case (around line 570) for a pattern that already correctly accounts for the request type

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
- `eslint (JS/TS linter)`
