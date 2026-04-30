#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ai-setup

# Idempotency guard
if grep -qF "- **Interface contract**: Provider MUST implement `LLMProvider` from `src/llm/ty" ".agents/skills/llm-provider/SKILL.md" && grep -qF "- **Streaming via callbacks**: `stream()` invokes `callbacks.onText(text)` for e" ".cursor/skills/llm-provider/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/llm-provider/SKILL.md b/.agents/skills/llm-provider/SKILL.md
@@ -6,7 +6,7 @@ description: Adds a new LLM provider implementing LLMProvider interface from src
 
 ## Critical
 
-- **Interface contract**: Provider MUST implement `LLMProvider` from `src/llm/types.ts` — both `call()` (non-streaming) and `stream()` methods are required
+- **Interface contract**: Provider MUST implement `LLMProvider` from `src/llm/types.ts` — both `call(options: LLMCallOptions): Promise<string>` and `stream(options: LLMStreamOptions, callbacks: LLMStreamCallbacks): Promise<void>` are required
 - **No authentication in code**: API keys/tokens come from env vars only (e.g., `process.env.PROVIDER_API_KEY`). Never hardcode secrets
 - **Validation before integration**: Provider must pass a unit test in `src/llm/__tests__/` before wiring into config/factory
 - **Error handling**: All errors must extend or match the patterns in `src/llm/types.ts` (e.g., `LLMError` or provider-specific exceptions)
@@ -27,14 +27,14 @@ Implement:
 export class MyProvider implements LLMProvider<MyConfig> {
   constructor(config: MyConfig) { this.config = config; }
   
-  async call(request: LLMRequest): Promise<string> {
+  async call(options: LLMCallOptions): Promise<string> {
     // Non-streaming call
     // Return full text response
   }
-  
-  async *stream(request: LLMRequest): AsyncGenerator<string> {
-    // Streaming call — yield text chunks
-    // Handle protocol-specific events (if any)
+
+  async stream(options: LLMStreamOptions, callbacks: LLMStreamCallbacks): Promise<void> {
+    // Streaming call — invoke callbacks.onText() for each chunk
+    // Call callbacks.onEnd() when complete, callbacks.onError() on error
   }
 }
 ```
@@ -126,7 +126,7 @@ If provider requires user setup (interactive prompts), add to `src/commands/inte
 
 **"MyProvider does not implement LLMProvider"**
 - Ensure both `call()` and `stream()` methods exist and match signature in `src/llm/types.ts`
-- `call()` returns `Promise<string>`, `stream()` returns `AsyncGenerator<string>`
+- `call(options: LLMCallOptions)` returns `Promise<string>`; `stream(options: LLMStreamOptions, callbacks: LLMStreamCallbacks)` returns `Promise<void>`
 - Run `npx tsc --noEmit` for full type errors
 
 **"Provider not found in factory"**
@@ -138,7 +138,7 @@ If provider requires user setup (interactive prompts), add to `src/commands/inte
 - User must set env var or pass in config
 - Check `.env` file or shell: `echo $PROVIDER_API_KEY`
 
-**"Stream yields nothing / incomplete chunks"**
-- Verify `stream()` parses protocol correctly (event vs. line delimiters)
-- Test against mock: `npm run test -- src/llm/__tests__/my-provider.test.ts`
-- Compare event structure to `anthropic.ts` (SSE) or `openai-compat.ts` (JSON Lines)
\ No newline at end of file
+**"Stream callbacks never fire; onEnd not called"**
+- Verify `stream()` calls `callbacks.onText()` for each chunk and `callbacks.onEnd()` when done
+- Ensure the async iterator is fully consumed before `callbacks.onEnd()` is called
+- Compare streaming pattern to `anthropic.ts` as reference
\ No newline at end of file
diff --git a/.cursor/skills/llm-provider/SKILL.md b/.cursor/skills/llm-provider/SKILL.md
@@ -6,46 +6,46 @@ description: Adds a new LLM provider implementing LLMProvider interface from src
 
 ## Critical
 
-- **All providers must implement `LLMProvider` interface** from `src/llm/types.ts`: `call(messages, params)` and `stream(messages, params)` returning `AsyncIterable<StreamChunk>`
+- **All providers must implement `LLMProvider` interface** from `src/llm/types.ts`: `call(options: LLMCallOptions): Promise<string>` and `stream(options: LLMStreamOptions, callbacks: LLMStreamCallbacks): Promise<void>`
 - **No partial implementations**: Both `call()` and `stream()` must work. Streaming is not optional.
-- **StreamChunk format**: `{ type: 'text' | 'error' | 'usage'; value: string; usage?: { input: number; output: number } }`
-- **Error handling**: Catch provider-specific errors, map to `ChatError` from `src/llm/types.ts` with `code` (e.g., `'auth'`, `'rate_limit'`, `'network'`) and `message`
-- **Model validation**: Call `validateModel(modelId)` in config before accepting the model. Refer to `src/llm/config.ts` for pattern.
+- **Streaming via callbacks**: `stream()` invokes `callbacks.onText(text)` for each chunk, `callbacks.onEnd(meta?)` when complete, and `callbacks.onError(error)` on failure — it does NOT return an async generator or iterable.
+- **Error handling**: Catch all errors and either call `callbacks.onError()` (in `stream()`) or throw (in `call()`). Preserve error messages unchanged.
+- **Model validation**: Respect `options.model || this.defaultModel` pattern — never hardcode model names.
 
 ## Instructions
 
 1. **Define provider file** at `src/llm/{provider-name}.ts`
-   - Import `{ LLMProvider, ChatMessage, ChatParams, StreamChunk, ChatError }` from `src/llm/types.ts`
+   - Import `{ LLMProvider, LLMCallOptions, LLMStreamOptions, LLMStreamCallbacks, LLMConfig }` from `src/llm/types.ts`
    - Export class `{ProviderName}Provider implements LLMProvider`
-   - Constructor takes `{ apiKey?: string; model: string; baseUrl?: string }` matching config structure
-   - Store config in instance: `this.apiKey = apiKey || process.env.{PROVIDER_API_KEY}`
-   - Verify API key exists on first call, throw `ChatError` with `code: 'auth'` if missing
+   - Constructor takes `config: LLMConfig`; store `this.defaultModel = config.model`
+   - Initialize SDK client from `config.apiKey` in constructor — never lazy-initialize on first call
+   - Verify API key exists in constructor, throw `new Error('API key required')` if missing
 
 2. **Implement `call()` method**
-   - Signature: `async call(messages: ChatMessage[], params: ChatParams): Promise<string>`
-   - Make HTTP request to provider API with messages and params (temperature, max_tokens, etc.)
+   - Signature: `async call(options: LLMCallOptions): Promise<string>`
+   - Make HTTP request to provider API using `options.system`, `options.prompt`, `options.model || this.defaultModel`, `options.maxTokens`
    - Extract text from response, return as single string
-   - On error (network, auth, rate limit), throw `ChatError` with appropriate `code` and `message`
+   - On error, throw with error message unchanged (retry logic in `src/llm/index.ts` handles transient errors)
    - Verify this works before proceeding
 
 3. **Implement `stream()` method**
-   - Signature: `async *stream(messages: ChatMessage[], params: ChatParams): AsyncIterable<StreamChunk>`
-   - Use provider's streaming endpoint (e.g., SSE, WebSocket, chunked response)
-   - Yield `{ type: 'text', value: '<chunk>' }` for each text delta
-   - Yield `{ type: 'usage', value: '', usage: { input, output } }` at end if available
-   - On error, yield `{ type: 'error', value: '<error message>' }` and return
-   - Test streaming with `for await (const chunk of stream(...)) { console.log(chunk) }`
+   - Signature: `async stream(options: LLMStreamOptions, callbacks: LLMStreamCallbacks): Promise<void>`
+   - Use provider's streaming endpoint; iterate chunks
+   - For each text chunk: call `callbacks.onText(chunkText)`
+   - After iteration completes: call `callbacks.onEnd({ stopReason, usage })` (usage is optional)
+   - On error: call `callbacks.onError(error instanceof Error ? error : new Error(String(error)))`
+   - Test by verifying `callbacks.onEnd` is called and `callbacks.onText` fires for each chunk
 
 4. **Add config in `src/llm/config.ts`**
-   - Import `{ProviderName}Provider` in `getProvider(config, model)` function
-   - Add condition: `if (config.provider === '{provider-slug}') return new {ProviderName}Provider({ apiKey: config.apiKey, model, baseUrl: config.baseUrl })`
-   - Add case in `validateModel()`: check against provider's official model list or hardcode supported models
-   - Export provider slug in `SUPPORTED_PROVIDERS` array if it exists
-   - Verify config function accepts and routes your provider
+   - Add provider to `ProviderType` union in `src/llm/types.ts`
+   - Add `LLMConfig` fields if needed (beyond `apiKey`, `model`, `baseUrl`)
+   - In `resolveFromEnv()`: add env var detection block before `return null`
+   - In `readConfigFile()` validation: add your provider slug to the includes list
+   - Verify: `npx tsc --noEmit` shows no ProviderType errors
 
 5. **Register in factory at `src/llm/index.ts`**
-   - Import provider in `getProvider()` function
-   - Add to the conditional chain matching provider name from config
+   - Import provider class at top of file
+   - Add `case 'your-provider': return new YourProviderProvider(config);` in `createProvider()` switch
    - Run `npm run build && npm run test` to verify factory picks up provider
 
 6. **Add tests in `src/llm/__tests__/{provider-name}.test.ts`**
@@ -72,10 +72,9 @@ description: Adds a new LLM provider implementing LLMProvider interface from src
 
 ## Common Issues
 
-- **"Provider not recognized" in factory**: Verify provider slug matches exactly in `getProvider()` condition AND in config file. Check spelling and case sensitivity.
-- **"TypeError: stream is not async iterable"**: Ensure `stream()` is a generator function (uses `async *` and `yield`). Test with `for await` loop before deploying.
-- **"API key is undefined"**: Verify environment variable name in provider constructor matches what user sets. Log `apiKey` value in error message: `throw new ChatError('auth', 'API key missing: check {ENV_VAR_NAME}')`
-- **"Stream stops early or yields garbage"**: Check provider's response format (JSON lines, SSE, etc.). Log raw response chunk: `console.error('Raw chunk:', chunk)` to debug parsing.
-- **"Model validation fails but model is valid"**: Ensure `validateModel()` in config covers all supported models for this provider. If list is dynamic, call provider's models endpoint and cache.
-- **Type errors on ChatError**: Verify import is `from 'src/llm/types.js'` (with `.js` extension for ESM).
-- **Tests fail with "fetch is not defined"**: Add `import { fetch } from 'node-fetch'` or mock globally in `src/test/setup.ts`.
\ No newline at end of file
+- **"Unknown provider: your-provider"**: Verify `ProviderType` union updated AND `createProvider()` switch case added in `src/llm/index.ts`. Both must be updated together.
+- **"Stream callbacks never fire; onEnd not called"**: `stream()` must be `async` (not a generator). Ensure `callbacks.onEnd()` is called after the loop completes, not inside it.
+- **"API key required"**: Verify env var name in `resolveFromEnv()` matches the variable the user sets. Test: `YOUR_API_KEY=test npm run test -- src/llm/__tests__/index.test.ts`.
+- **"Stream stops early"**: Check provider's response format (JSON lines, SSE, etc.). Log raw chunks: `console.error('Raw chunk:', chunk)` to debug parsing.
+- **Type errors on LLMStreamCallbacks**: Verify import is `from './types.js'` (with `.js` extension for ESM).
+- **Tests fail with "fetch is not defined"**: Add global fetch mock or use `node-fetch` in `src/test/setup.ts`.
\ No newline at end of file
PATCH

echo "Gold patch applied."
