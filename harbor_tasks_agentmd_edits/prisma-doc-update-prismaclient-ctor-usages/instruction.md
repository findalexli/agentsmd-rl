# Update PrismaClient Constructor Examples to Require Adapter

## Problem

The PrismaClient instantiation examples in the repository are outdated. In Prisma 7, creating a PrismaClient requires passing a driver adapter to the constructor — you can no longer just write `new PrismaClient()` without arguments. However, several places in the codebase still show the old bare-constructor pattern as the primary usage example:

- The root `README.md` shows `const prisma = new PrismaClient()` as the main getting-started example, with adapter usage only mentioned as a secondary note below
- The JSDoc `@example` templates in both client generator packages still demonstrate the bare constructor without an adapter

## Expected Behavior

All PrismaClient instantiation examples should demonstrate the adapter-based pattern as the primary and only way to create a client. The introductory text should make clear that providing a driver adapter is required, not optional.

## Files to Look At

- `README.md` — The "Import and instantiate Prisma Client" section needs to present adapter-based instantiation as the default, not as an afterthought
- `packages/client-generator-js/src/TSClient/PrismaClient.ts` — Contains the JSDoc `@example` template for the generated PrismaClient class (traditional `prisma-client-js` generator)
- `packages/client-generator-ts/src/TSClient/PrismaClient.ts` — Contains the JSDoc `@example` template for the generated PrismaClient class (new `prisma-client` generator)

After updating the code, make sure the documentation and generated code examples are consistent with each other and with the current Prisma 7 architecture.
