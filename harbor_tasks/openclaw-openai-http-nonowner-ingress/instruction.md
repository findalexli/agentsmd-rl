# Bug: OpenAI-compatible HTTP chat completions endpoint grants owner-level tool access

## Summary

The OpenAI-compatible HTTP chat completions endpoint at `POST /v1/chat/completions` in `src/gateway/openai-http.ts` dispatches agent runs with owner-level privileges. This means external HTTP API callers can invoke owner-only tools that should be restricted to the device owner.

## Reproduction

When a request comes in through the `/v1/chat/completions` endpoint, the `buildAgentCommandInput` function constructs the agent command input. The context flag that controls tool-access scope is incorrectly set, treating all HTTP callers as owners.

This is a security concern: the OpenAI-compatible HTTP ingress is an external-facing API surface, and callers through this path should be treated as non-owner external input. Owner-only tools (e.g., file system access, configuration changes) should not be available to these callers.

## Expected behavior

The `/v1/chat/completions` endpoint should dispatch agent runs with non-owner context, so that owner-only tools are excluded from the agent's tool set when handling requests from this external HTTP API surface.

## Relevant files

- `src/gateway/openai-http.ts` — the `buildAgentCommandInput` function
- `src/gateway/openai-http.test.ts` — existing e2e test suite for the endpoint
