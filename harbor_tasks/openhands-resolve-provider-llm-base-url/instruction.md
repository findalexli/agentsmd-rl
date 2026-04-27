# Apply deployment LLM proxy URL override consistently

You are working in the OpenHands repository at `/workspace/openhands`.

## Background

OpenHands is deployed in multiple environments (production, staging, ad-hoc
feature deployments). Each deployment uses its own LLM proxy URL. The
production proxy is hard-coded into the SDK as the default:

```
https://llm-proxy.app.all-hands.dev/
```

Non-production deployments configure their own proxy URL via the environment
variable `OPENHANDS_PROVIDER_BASE_URL` (with `LLM_BASE_URL` accepted as a
backward-compatible fallback).

When a user record stores the SDK default proxy URL but the request is being
served by a non-production deployment, the deployment must substitute its own
provider URL before handing the LLM config back to the caller. Otherwise the
caller authenticates against the wrong proxy and sees:

```
litellm.AuthenticationError: Authentication Error, Invalid proxy server token passed.
```

This URL-substitution rule was already implemented inline inside
`openhands.app_server.app_conversation.live_status_app_conversation_service._configure_llm`.
However, other callers that read the user's stored LLM config did **not**
apply the override, so they sent traffic to the wrong proxy.

## Task

Centralise the URL-substitution logic into a single, reusable helper, and
have the existing inline call site use it.

### 1. Add the helper to `openhands/app_server/config.py`

Add a public, module-level function with this exact signature:

```python
def resolve_provider_llm_base_url(
    model: str | None,
    base_url: str | None,
    provider_base_url: str | None = None,
) -> str | None:
    ...
```

Add a module-level constant named `_SDK_DEFAULT_PROXY` (string) holding the
SDK default proxy URL given above. The constant must be importable as
`from openhands.app_server.config import _SDK_DEFAULT_PROXY`.

The helper must implement these rules. Priority order:
**user-explicit URL > deployment provider URL > SDK default.**

1. **Non-matching model.** If `model` is falsy (None or empty string) OR does
   not start with `openhands/` and does not start with `litellm_proxy/`,
   return `base_url` unchanged. (Plain models like `gpt-4` or
   `anthropic/claude-3-opus` are out of scope for the override.)

2. **User-set custom URL.** If `base_url` is truthy and, after stripping
   trailing `/`, differs from `_SDK_DEFAULT_PROXY` (also stripped of trailing
   `/`), the user has configured a custom URL — return `base_url` unchanged.
   Trailing-slash differences must NOT count as a custom URL: both
   `https://llm-proxy.app.all-hands.dev/` and
   `https://llm-proxy.app.all-hands.dev` must be recognised as the SDK
   default.

3. **Deployment override.** Otherwise the stored URL is the SDK default (or
   missing). Determine the deployment provider URL:
   * If the caller passed a non-`None` `provider_base_url`, use that value
     (an empty string explicitly means "no override configured" and must
     not be substituted).
   * If the caller passed `provider_base_url=None`, fall back to the
     existing helper `get_openhands_provider_base_url()`, which reads
     `OPENHANDS_PROVIDER_BASE_URL` and then `LLM_BASE_URL` from the
     environment.
   If a non-empty provider URL is found, return it. Otherwise return
   `base_url` (which preserves a `None` input or the SDK default).

### 2. Use the helper inside `_configure_llm`

In
`openhands/app_server/app_conversation/live_status_app_conversation_service.py`,
the method `_configure_llm` currently has an inline block that performs the
same URL substitution it always did. Replace that inline block with a call to
`resolve_provider_llm_base_url(...)` so there is only one source of truth.
Pass `self.openhands_provider_base_url` through as `provider_base_url`. The
externally-observable behaviour of `_configure_llm` must not change.

The helper must be imported into that module from
`openhands.app_server.config`.

### 3. Apply the same helper in `enterprise/server/routes/users_v1.py`

The function `_inject_sdk_compat_fields` populates the flat compatibility
fields (`llm_model`, `llm_base_url`) on the response of
`GET /api/v1/users/me`. The current implementation copies the user's stored
`base_url` verbatim. Update it so that `content['llm_base_url']` is set to
`resolve_provider_llm_base_url(model, llm.get('base_url'))` (positional args;
the env-var fallback inside the helper supplies the deployment URL). The
helper must be imported from `openhands.app_server.config`.

## Behavioural contract (summary)

| `model`                 | `base_url`                                | `provider_base_url`           | Result                        |
|-------------------------|-------------------------------------------|-------------------------------|-------------------------------|
| `'openhands/gpt-4'`     | `'https://llm-proxy.app.all-hands.dev/'`  | `'https://staging.example/'`  | `'https://staging.example/'`  |
| `'openhands/gpt-4'`     | `'https://my-proxy.example/v1'`           | `'https://staging.example/'`  | `'https://my-proxy.example/v1'` |
| `'openhands/gpt-4'`     | `'https://llm-proxy.app.all-hands.dev/'`  | `''`                          | `'https://llm-proxy.app.all-hands.dev/'` |
| `'openhands/gpt-4'`     | `'https://llm-proxy.app.all-hands.dev'` (no slash) | `'https://staging.example/'` | `'https://staging.example/'`  |
| `'litellm_proxy/x'`     | `'https://llm-proxy.app.all-hands.dev/'`  | `'https://staging.example/'`  | `'https://staging.example/'`  |
| `'gpt-4'`               | `'https://api.openai.com/v1'`             | `'https://staging.example/'`  | `'https://api.openai.com/v1'` |
| `None` or `''`          | anything                                  | anything                      | (returns `base_url`)          |
| `'openhands/gpt-4'`     | `None`                                    | `'https://staging.example/'`  | `'https://staging.example/'`  |
| `'openhands/gpt-4'`     | `None`                                    | (none, no env)                | `None`                        |
| `'openhands/gpt-4'`     | SDK default                               | `None`, env `OPENHANDS_PROVIDER_BASE_URL=URL` | `URL`            |
| `'openhands/gpt-4'`     | SDK default                               | `None`, env `LLM_BASE_URL=URL` (no `OPENHANDS_PROVIDER_BASE_URL`) | `URL` |

## Code Style Requirements

The repository runs the following checks via pre-commit. Your changes must
respect them:

- **ruff** — formatting and linting (single quotes, trailing whitespace,
  newline at end of file).
- **mypy** — keep the type hints accurate. The helper's signature is exactly
  `(model: str | None, base_url: str | None, provider_base_url: str | None = None) -> str | None`.

## Out of scope

- Changing how `OPENHANDS_PROVIDER_BASE_URL` / `LLM_BASE_URL` are read; reuse
  the existing `get_openhands_provider_base_url()` helper.
- Touching any callers other than the three named above.
- Modifying the SDK default URL value.
