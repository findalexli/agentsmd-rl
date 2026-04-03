# Add MiniMax LLM Provider Support

## Problem

EdgeQuake currently supports OpenAI, Anthropic, Gemini, xAI, OpenRouter, Ollama, LM Studio, and Mock as LLM providers, but does not support MiniMax. Users who want to use MiniMax's models (particularly the MiniMax-M2.7 flagship model with 204K context window) cannot configure the system to use them.

## Expected Behavior

MiniMax should be available as a fully integrated LLM provider:

1. **Backend**: The `models.toml` configuration should include a MiniMax provider entry (using `openaicompatible` type since MiniMax exposes an OpenAI-compatible API at `https://api.minimax.io/v1`) with model definitions for M2.7, M2.7-highspeed, M2.5, and M2.5-highspeed.

2. **API layer**: The provider registration in `edgequake-api` should list MiniMax alongside other providers, checking `MINIMAX_API_KEY` for availability, and the safety limits should include a default model fallback for MiniMax.

3. **Frontend**: The web UI should recognize `minimax` as a provider — display name mapping, icon configuration, and provider status card setup instructions.

4. **Documentation**: After adding the code changes, update the relevant documentation to reflect the new provider. The project README's architecture diagram, the operations configuration docs, and the `.env.example` should all be updated so users and contributors know MiniMax is available and how to configure it.

## Files to Look At

- `edgequake/models.toml` — provider and model definitions (TOML configuration)
- `edgequake/crates/edgequake-api/src/provider_types.rs` — provider registration with env var checks
- `edgequake/crates/edgequake-api/src/safety_limits.rs` — default model fallback mapping
- `edgequake_webui/src/hooks/use-providers.ts` — provider display names and styling
- `edgequake_webui/src/components/models/model-card.tsx` — provider icon mapping
- `edgequake_webui/src/components/models/model-selector.tsx` — provider icon in selector
- `edgequake_webui/src/components/settings/provider-status-card.tsx` — provider display name and config snippet
- `README.md` — architecture diagram listing LLM providers
- `docs/operations/configuration.md` — environment variable reference tables
- `.env.example` — configuration documentation for users
