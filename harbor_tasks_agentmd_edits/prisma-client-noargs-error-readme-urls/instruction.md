# PrismaClient constructor silently fails when called without arguments

## Problem

When a `PrismaClient` subclass calls `super()` without passing any options (or when `new PrismaClient()` is called without an argument object), the constructor silently crashes with a confusing runtime error deep inside the client internals. There is no helpful error message telling the developer what they did wrong.

The underlying issue is in `packages/client/src/runtime/getPrismaClient.ts` — the constructor's `optionsArg` parameter is used without first checking whether it was provided. The old code only conditionally runs validation when `optionsArg` is truthy, but never tells the user *why* things fail when it's `undefined`.

Additionally, several documentation links in the project's root `README.md` point to outdated Prisma documentation URLs that use the old `/docs/concepts/components/` path structure, which no longer resolves correctly. There is also an outdated note about driver adapters being optional that should reflect the Prisma 7 requirement.

## Expected Behavior

1. When `PrismaClient` is constructed without arguments, the constructor should throw a clear `PrismaClientInitializationError` explaining that a valid options object is required, with example code showing the correct usage pattern.

2. After the guard, any unnecessary optional chaining on `optionsArg` should be cleaned up since it's now guaranteed to be non-null.

3. The project's `README.md` should be updated: fix all broken documentation URLs to use the current docs path structure, and update the driver adapter note to reflect Prisma 7 requirements.

## Files to Look At

- `packages/client/src/runtime/getPrismaClient.ts` — the PrismaClient constructor logic
- `README.md` — root project documentation with outdated links and notes
