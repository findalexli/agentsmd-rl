# Bug: Workspace .env files can inject API credentials

## Summary

The workspace `.env` loading mechanism in `src/infra/dotenv.ts` blocks certain dangerous
environment variables (proxy settings, state-dir overrides, `_BASE_URL` suffixes) from
being loaded via a project-local `.env` file. However, it does **not** block API
credentials or gateway authentication variables.

This means a malicious or careless workspace `.env` file can inject values for keys like
provider API keys, OAuth tokens, and gateway auth secrets into the running process.
These would then be trusted as if they came from the user's own trusted state-dir `.env`
or shell environment.

## Affected File

- `src/infra/dotenv.ts` — specifically the `BLOCKED_WORKSPACE_DOTENV_KEYS` set and the
  `shouldBlockWorkspaceDotEnvKey` function.

## Expected Behavior

Credential and gateway authentication environment variables should be **blocked** when
loaded from a workspace (CWD) `.env` file, while still being allowed from the trusted
global state-dir `.env` (loaded via `loadRuntimeDotEnvFile`).

The variables that need to be blocked from workspace `.env` include:
- Provider API keys (for Anthropic, OpenAI, and similar)
- OAuth tokens
- Gateway authentication secrets (tokens, passwords, secrets)
- Live/test provider key variants

Additionally, some key families follow a naming pattern with suffixes (e.g.,
`_SECONDARY`) that should also be blocked — consider whether a prefix-based approach
covers these variants rather than enumerating every possible suffix.

## Reproduction

1. Create a workspace `.env` file containing `ANTHROPIC_API_KEY=sk-ant-attacker-key`
2. Run the application from that directory
3. Observe that `process.env.ANTHROPIC_API_KEY` is set to the attacker's key

## Hints

- Look at how `BLOCKED_WORKSPACE_DOTENV_SUFFIXES` works for `_BASE_URL` — a similar
  pattern could handle key families with common prefixes.
- The trusted state-dir `.env` uses `loadRuntimeDotEnvFile` which has its own
  (narrower) blocking — credential keys should remain allowed there.
- Existing tests in `src/infra/dotenv.test.ts` show the pattern for testing blocked keys.
