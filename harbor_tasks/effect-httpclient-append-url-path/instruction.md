# Fix URL Path Joining in HttpClientRequest.appendUrl

The `appendUrl` function in the platform package has a bug where it does not properly join URL paths, producing malformed URLs in certain cases.

## The Bug

When you call `appendUrl` with a path, the current implementation can produce invalid URLs:

```typescript
// Base URL without trailing slash
const request = HttpClientRequest.get("https://api.example.com/v1").pipe(
  HttpClientRequest.appendUrl("users")
)
// Current (broken) result: "https://api.example.com/v1users"
// Expected result: "https://api.example.com/v1/users"
```

## Your Task

Fix the `appendUrl` function to properly join URL paths in all cases:

| Base URL | Path | Expected Result |
|----------|------|-----------------|
| `https://api.example.com/v1` | `users` | `https://api.example.com/v1/users` |
| `https://api.example.com/v1/` | `users` | `https://api.example.com/v1/users` |
| `https://api.example.com/v1` | `/users` | `https://api.example.com/v1/users` |
| `https://api.example.com/v1/` | `/users` | `https://api.example.com/v1/users` |
| `https://api.example.com/v1` | `users/123/posts` | `https://api.example.com/v1/users/123/posts` |
| `https://api.example.com/v1` | `""` | `https://api.example.com/v1` |

## Verification

After fixing, the tests in `packages/platform/test/HttpClient.test.ts` should pass. You can run them with:

```bash
pnpm --filter @effect/platform vitest run --testNamePattern 'appendUrl'
```

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `eslint (JS/TS linter)`
