# Fix Credential Leak in Callback Event Logging

## Problem

The callback processors in the app server are logging complete Event objects to production logs. These Event objects can contain sensitive information including:
- API keys (OpenAI, Anthropic, Groq, etc.)
- Bearer tokens
- Session tokens
- User messages with embedded credentials

When logged, this sensitive data appears in plaintext in production logs, creating a serious security vulnerability.

## What You Need To Do

Create a solution that redacts sensitive information before it gets logged.

### Requirements

The solution must provide a redaction utility that:

1. **Redacts secrets from text** containing API keys, URL parameters, and dict entries
2. **Redacts bare API key literals** from common providers

### API Key Patterns to Redact

The utility must detect and redact API key patterns matching these providers:
- OpenRouter: keys starting with `sk-or-v1-` followed by 20+ characters
- Generic project keys: keys starting with `sk-proj-` followed by 20+ characters
- Groq: keys starting with `gsk_` followed by 20+ characters
- HuggingFace: keys starting with `hf_` followed by 20+ characters
- GitHub Personal Access Tokens: keys starting with `ghp_` followed by 20+ characters
- Bearer tokens: `Bearer ` followed by 20+ characters

### Dict Entry Handling

The utility must redact values associated with sensitive keys such as:
- `API_KEY`, `SECRET`, `TOKEN`, `PASSWORD`, `ACCESS_TOKEN`, `AUTH`, `AUTHORIZATION`

### URL Parameter Handling

Sensitive URL query parameters that must be redacted include:
- `api_key`, `token`, `secret`, `key`, `access_token`

### Integration Requirements

The callback processors must use the redaction utility when logging Event objects. The logging should use lazy `%s` formatting (not f-strings) to avoid evaluation overhead when logging is disabled.

## Expected Behavior

After the fix:
- `api_key='sk-abc123secret'` → `api_key='<redacted>'`
- `https://example.com?token=secrettoken` → `token=<redacted>`
- `{'API_KEY': 'secret123', 'OTHER': 'visible'}` → `OTHER` remains visible, secret value becomes `<redacted>`
- `sk-or-v1-abc123def456ghi789jkl` → `<redacted>` (key not present in output)
- Non-sensitive text passes through unchanged