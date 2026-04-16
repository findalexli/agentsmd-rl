# Fix Moonshot Provider for Kimi Model Reasoning Support

## Problem

When using Kimi models (kimi-k2.5, kimi-k1.5, etc.) through the Moonshot provider with thinking/reasoning enabled, the API returns a 400 error with a message about reasoning_content missing from the assistant tool call message.

The Moonshot provider is located at `core/llm/llms/Moonshot.ts`. The Kimi API has different requirements than the standard Moonshot API for reasoning-enabled models.

## Requirements

1. The Moonshot class must properly initialize the OpenAI base class by calling its constructor with options
2. The solution must enable reasoning content support for models whose names begin with "kimi" (case-sensitive prefix)
3. Models whose names do not start with "kimi" must not have reasoning content support unconditionally enabled
4. TypeScript compilation must pass without errors: `cd core && npx tsc --noEmit`
5. The Moonshot module must import the OpenAI class from the local OpenAI.js module

## Technical Background

The Moonshot provider extends the OpenAI class. The OpenAI base class provides a configurable flag for reasoning content field support. When this flag is not properly set for certain model families, the API call fails with a 400 error.

## Verification

Your solution must:
- Allow Kimi family models (kimi-k2.5, kimi-k1.5, etc.) to use reasoning content with the Moonshot API
- Continue working correctly with moonshot-v1-* models without reasoning content requirements
- Pass all linting and type checking in the core module