# Bug: Workspace .env files can inject API credentials

## Summary

The workspace `.env` loading mechanism blocks certain dangerous environment variables
(proxy settings, state-dir overrides, `_BASE_URL` suffixes) from being loaded via a
project-local `.env` file. However, it does **not** block API credentials or gateway
authentication variables.

This means a malicious or careless workspace `.env` file can inject values for these
keys into the running process, where they would be trusted as if they came from the
user's own trusted state-dir `.env` or shell environment.

## Affected File

- `src/infra/dotenv.ts` — manages which environment variables are blocked from
  workspace .env files

## Expected Behavior

The following key categories must be **blocked** when loaded from a workspace (CWD)
`.env` file, while still being allowed from the trusted global state-dir `.env`:

### Provider API keys (exact names)
- `ANTHROPIC_API_KEY`
- `OPENAI_API_KEY`

### OAuth and secondary keys (exact names)
- `ANTHROPIC_OAUTH_TOKEN`
- `OPENAI_API_KEYS`

### Gateway authentication secrets (exact names)
- `OPENCLAW_GATEWAY_TOKEN`
- `OPENCLAW_GATEWAY_PASSWORD`
- `OPENCLAW_GATEWAY_SECRET`

### Live provider key variants (exact names)
- `OPENCLAW_LIVE_ANTHROPIC_KEY`
- `OPENCLAW_LIVE_ANTHROPIC_KEYS`
- `OPENCLAW_LIVE_OPENAI_KEY`
- `OPENCLAW_LIVE_GEMINI_KEY`

### Key families with common prefixes

Some key families follow a naming pattern with suffixes (e.g., `_SECONDARY`, `_BACKUP`,
`_V2`) that must also be blocked. For example:
- `ANTHROPIC_API_KEY_SECONDARY`
- `ANTHROPIC_API_KEY_V2`
- `OPENAI_API_KEY_BACKUP`
- `OPENAI_API_KEY_SECONDARY`

The blocking must be case-insensitive.

### Regression: existing blocking must be preserved

The following keys must **remain blocked** (do not break existing behavior):
- `ALL_PROXY`, `HTTP_PROXY`, `HTTPS_PROXY`
- `OPENCLAW_STATE_DIR`, `OPENCLAW_CONFIG_PATH`
- `_BASE_URL` suffix variants (e.g., `OPENAI_BASE_URL`, `CUSTOM_SERVICE_BASE_URL`)

### Regression: safe keys must NOT be blocked

The following unrelated keys must **NOT be blocked**:
- `MY_CUSTOM_VAR`, `DATABASE_URL`, `APP_SECRET`, `NODE_ENV`

## Reproduction

1. Create a workspace `.env` file containing `ANTHROPIC_API_KEY=sk-ant-attacker-key`
2. Run the application from that directory
3. Observe that `process.env.ANTHROPIC_API_KEY` is set to the attacker's key

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `eslint (JS/TS linter)`
