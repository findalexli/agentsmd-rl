# OpenRouter API Request Identification Headers

## Problem

OpenRouter's API documentation recommends that applications send identification headers with all requests. These headers allow OpenRouter to:

1. Attribute API usage in their dashboard
2. Display the application in their App Showcase

Currently, the `OpenRouterApi` class in the `openai-adapters` package does not send any identification headers with its requests. This means:

- OpenRouter cannot attribute requests to the Continue application
- Continue does not appear in OpenRouter's App Showcase

## Required Behavior

All HTTP requests made through `OpenRouterApi` must include the following headers:

| Header | Value |
|--------|-------|
| `HTTP-Referer` | `https://www.continue.dev/` |
| `X-Title` | `Continue` |

## Constraint

User-provided headers via `requestOptions.headers` must take precedence over the default identification headers. This allows users to override the defaults if needed (e.g., for their own branding).

## Implementation Notes

- The `OpenRouterApi` class extends `OpenAIApi`
- Configuration is passed via `OpenRouterConfig` which extends `OpenAIConfig`
- The `OpenAIConfig` type includes a `requestOptions.headers` field for custom HTTP headers
- The fix should inject the default headers without removing any user-provided headers

## Verification

After implementing the fix:
1. Creating an `OpenRouterApi` instance should automatically include the identification headers
2. User-provided headers should override the defaults while preserving non-overridden default headers
3. The `OpenAIApi` base class should not be affected (its requests should not include the OpenRouter-specific headers)
