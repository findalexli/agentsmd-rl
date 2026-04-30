#!/usr/bin/env bash
set -euo pipefail

cd /workspace/phoenix

# Idempotency guard
if grep -qF "- **Custom Spans**: `setup-{lang}` \u2192 `instrumentation-manual-{lang}` \u2192 `span-{ty" "skills/phoenix-tracing/SKILL.md" && grep -qF "Track multi-turn conversations by grouping traces with session IDs. **Use `withS" "skills/phoenix-tracing/rules/sessions-typescript.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/phoenix-tracing/SKILL.md b/skills/phoenix-tracing/SKILL.md
@@ -89,53 +89,38 @@ Reference these guidelines when:
 - `attributes-graph` - Agent workflow attributes
 - `attributes-exceptions` - Error tracking
 
-## Common Attributes
-
-| Attribute                 | Purpose              | Example                |
-| ------------------------- | -------------------- | ---------------------- |
-| `openinference.span.kind` | Span type (required) | `"LLM"`, `"RETRIEVER"` |
-| `input.value`             | Operation input      | JSON or text           |
-| `output.value`            | Operation output     | JSON or text           |
-| `user.id`                 | User identifier      | `"user_123"`           |
-| `session.id`              | Conversation ID      | `"session_abc"`        |
-| `llm.model_name`          | Model identifier     | `"gpt-4"`              |
-| `llm.token_count.total`   | Token usage          | `1500`                 |
-| `tool.name`               | Tool/function name   | `"get_weather"`        |
-
 ## Common Workflows
 
-**Quick Start:**
-
-1. `setup-{lang}` → Install and configure
-2. `instrumentation-auto-{lang}` → Enable auto-instrumentation
-3. Check Phoenix for traces
-
-**Custom Spans:**
-
-1. `setup-{lang}` → Install
-2. `instrumentation-manual-{lang}` → Add decorators/wrappers
-3. `span-{type}` → Reference attributes
-
-**Production:** `production-{lang}` → Configure batching and masking
+- **Quick Start**: `setup-{lang}` → `instrumentation-auto-{lang}` → Check Phoenix
+- **Custom Spans**: `setup-{lang}` → `instrumentation-manual-{lang}` → `span-{type}`
+- **Session Tracking**: `sessions-{lang}` for conversation grouping patterns
+- **Production**: `production-{lang}` for batching, masking, and deployment
 
-## How to Use
+## How to Use This Skill
 
-Read individual rule files in `rules/` for detailed explanations and examples:
-
-```
-rules/setup-python.md
-rules/instrumentation-manual-typescript.md
-rules/span-llm.md
-```
-
-Use file prefixes to find what you need:
+**Navigation Patterns:**
 
 ```bash
-ls rules/span-*           # Span type specifications
-ls rules/*-python.md      # Python guides
-ls rules/*-typescript.md  # TypeScript guides
+# By category prefix
+rules/setup-*              # Installation and configuration
+rules/instrumentation-*    # Auto and manual tracing
+rules/span-*               # Span type specifications
+rules/sessions-*           # Session tracking
+rules/production-*         # Production deployment
+rules/fundamentals-*       # Core concepts
+rules/attributes-*         # Attribute specifications
+
+# By language
+rules/*-python.md          # Python implementations
+rules/*-typescript.md      # TypeScript implementations
 ```
 
+**Reading Order:**
+1. Start with `setup-{lang}` for your language
+2. Choose `instrumentation-auto-{lang}` OR `instrumentation-manual-{lang}`
+3. Reference `span-{type}` files as needed for specific operations
+4. See `fundamentals-*` files for attribute specifications
+
 ## References
 
 **Phoenix Documentation:**
diff --git a/skills/phoenix-tracing/rules/sessions-typescript.md b/skills/phoenix-tracing/rules/sessions-typescript.md
@@ -1,105 +1,223 @@
 # Sessions (TypeScript)
 
-Track multi-turn conversations by grouping traces with session IDs.
+Track multi-turn conversations by grouping traces with session IDs. **Use `withSpan` directly from `@arizeai/openinference-core`** - no wrappers or custom utilities needed.
 
-## Setup
+## Core Concept
+
+**Session Pattern:**
+1. Generate a unique `session.id` once at application startup
+2. Export SESSION_ID, import `withSpan` where needed
+3. Use `withSpan` to create a parent CHAIN span with `session.id` for each interaction
+4. All child spans (LLM, TOOL, AGENT, etc.) automatically group under the parent
+5. Query traces by `session.id` in Phoenix to see all interactions
+
+## Implementation (Best Practice)
+
+### 1. Setup (instrumentation.ts)
 
 ```typescript
-import { context } from "@opentelemetry/api";
-import { setSession } from "@arizeai/openinference-core";
+import { register } from "@arizeai/phoenix-otel";
+import { randomUUID } from "node:crypto";
+
+// Initialize Phoenix
+register({
+  projectName: "your-app",
+  url: process.env.PHOENIX_COLLECTOR_ENDPOINT || "http://localhost:6006",
+  apiKey: process.env.PHOENIX_API_KEY,
+  batch: true,
+});
+
+// Generate and export session ID
+export const SESSION_ID = randomUUID();
+```
 
-await context.with(
-  setSession(context.active(), { sessionId: "user_123_conv_456" }),
+### 2. Usage (app code)
+
+```typescript
+import { withSpan } from "@arizeai/openinference-core";
+import { SESSION_ID } from "./instrumentation";
+
+// Use withSpan directly - no wrapper needed
+const handleInteraction = withSpan(
   async () => {
-    const response = await llm.invoke(prompt);
+    const result = await agent.generate({ prompt: userInput });
+    return result;
+  },
+  {
+    name: "cli.interaction",
+    kind: "CHAIN",
+    attributes: { "session.id": SESSION_ID },
   }
 );
-```
 
-## Best Practices
+// Call it
+const result = await handleInteraction();
+```
 
-**Bad: Only parent span gets session ID**
+### With Input Parameters
 
 ```typescript
-const span = trace.getActiveSpan();
-span?.setAttribute(SemanticConventions.SESSION_ID, sessionId);
-const response = await client.chat.completions.create(...);
+const processQuery = withSpan(
+  async (query: string) => {
+    return await agent.generate({ prompt: query });
+  },
+  {
+    name: "process.query",
+    kind: "CHAIN",
+    attributes: { "session.id": SESSION_ID },
+  }
+);
+
+await processQuery("What is 2+2?");
 ```
 
-**Good: All child spans inherit session ID**
+## Key Points
 
-```typescript
-await context.with(
-  setSession(context.active(), { sessionId }),
-  async () => {
-    const response = await client.chat.completions.create(...);
-    const result = await myCustomFunction();
+### Session ID Scope
+- **CLI/Desktop Apps**: Generate once at process startup
+- **Web Servers**: Generate per-user session (e.g., on login, store in session storage)
+- **Stateless APIs**: Accept session.id as a parameter from client
+
+### Span Hierarchy
+```
+cli.interaction (CHAIN) ← session.id here
+├── ai.generateText (AGENT)
+│   ├── ai.generateText.doGenerate (LLM)
+│   └── ai.toolCall (TOOL)
+└── ai.generateText.doGenerate (LLM)
+```
+
+The `session.id` is only set on the **root span**. Child spans are automatically grouped by the trace hierarchy.
+
+### Querying Sessions
+
+```bash
+# Get all traces for a session
+npx @arizeai/phoenix-cli traces \
+  --endpoint http://localhost:6006 \
+  --project your-app \
+  --format raw \
+  --no-progress | \
+  jq '.[] | select(.spans[0].attributes["session.id"] == "YOUR-SESSION-ID")'
+```
+
+## Dependencies
+
+```json
+{
+  "dependencies": {
+    "@arizeai/openinference-core": "^2.0.5",
+    "@arizeai/phoenix-otel": "^0.4.1"
   }
-);
+}
 ```
 
-**Why:** `setSession()` propagates session ID to all nested spans automatically.
+**Note:** `@opentelemetry/api` is NOT needed - it's only for manual span management.
+
+## Why This Pattern?
+
+1. **Simple**: Just export SESSION_ID, use withSpan directly - no wrappers
+2. **Built-in**: `withSpan` from `@arizeai/openinference-core` handles everything
+3. **Type-safe**: Preserves function signatures and type information
+4. **Automatic lifecycle**: Handles span creation, error tracking, and cleanup
+5. **Framework-agnostic**: Works with any LLM framework (AI SDK, LangChain, etc.)
+6. **No extra deps**: Don't need `@opentelemetry/api` or custom utilities
 
-## Session ID Patterns
+## Advanced: Custom Input/Output Processing
 
 ```typescript
-import { randomUUID } from "crypto";
+const processWithLogging = withSpan(
+  async (query: string) => {
+    const result = await llm.generate(query);
+    return result;
+  },
+  {
+    name: "query.process",
+    kind: "CHAIN",
+    attributes: { "session.id": SESSION_ID },
+    processInput: (query) => ({
+      "input.value": query,
+      "input.length": query.length,
+    }),
+    processOutput: (result) => ({
+      "output.value": result.text,
+      "output.tokens": result.usage?.totalTokens,
+    }),
+  }
+);
+```
 
-const sessionId = randomUUID();
-const sessionId = `user_${userId}_conv_${conversationId}`;
-const sessionId = `debug_${timestamp}`;
+## Adding More Attributes
+
+```typescript
+import { withSpan } from "@arizeai/openinference-core";
+import { SESSION_ID } from "./instrumentation";
+
+const handleWithContext = withSpan(
+  async (userInput: string) => {
+    return await agent.generate({ prompt: userInput });
+  },
+  {
+    name: "cli.interaction",
+    kind: "CHAIN",
+    attributes: {
+      "session.id": SESSION_ID,
+      "user.id": userId,              // Track user
+      "metadata.environment": "prod",  // Custom metadata
+    },
+  }
+);
 ```
 
-Good: `randomUUID()`, `"user_123_conv_456"`
-Bad: `"session_1"`, `"test"`, empty string
+## Anti-Pattern: Don't Create Wrappers
 
-## Multi-Turn Chatbot Example
+❌ **Don't do this:**
+```typescript
+// Unnecessary wrapper
+export function withSessionTracking(fn) {
+  return withSpan(fn, { attributes: { "session.id": SESSION_ID } });
+}
+```
 
+✅ **Do this instead:**
 ```typescript
-import { randomUUID } from "crypto";
-import { context } from "@opentelemetry/api";
-import { setSession } from "@arizeai/openinference-core";
+// Use withSpan directly
+import { withSpan } from "@arizeai/openinference-core";
+import { SESSION_ID } from "./instrumentation";
 
-const sessionId = randomUUID();
-const messages: any[] = [];
-
-async function sendMessage(userInput: string): Promise<string> {
-  messages.push({ role: "user", content: userInput });
-
-  return context.with(
-    setSession(context.active(), { sessionId }),
-    async () => {
-      const response = await client.chat.completions.create({
-        model: "gpt-4",
-        messages
-      });
-      const content = response.choices[0].message.content!;
-      messages.push({ role: "assistant", content });
-      return content;
-    }
-  );
-}
+const handler = withSpan(fn, {
+  attributes: { "session.id": SESSION_ID }
+});
 ```
 
-## Additional Attributes
+## Alternative: Context API Pattern
+
+For web servers or complex async flows where you need to propagate session IDs through middleware, you can use the Context API:
 
 ```typescript
-import { trace } from "@opentelemetry/api";
+import { context } from "@opentelemetry/api";
+import { setSession } from "@arizeai/openinference-core";
 
 await context.with(
-  setSession(context.active(), { sessionId }),
+  setSession(context.active(), { sessionId: "user_123_conv_456" }),
   async () => {
-    const span = trace.getActiveSpan();
-    span?.setAttributes({
-      "user.id": "user_123",
-      "metadata.tier": "premium"
-    });
     const response = await llm.invoke(prompt);
   }
 );
 ```
 
-## See Also
+**Use Context API when:**
+- Building web servers with middleware chains
+- Session ID needs to flow through many async boundaries
+- You don't control the call stack (e.g., framework-provided handlers)
+
+**Use withSpan when:**
+- Building CLI apps or scripts
+- You control the function call points
+- Simpler, more explicit code is preferred
+
+## Related
 
-- **Python sessions:** `sessions-python.md`
-- **Session docs:** https://docs.arize.com/phoenix/tracing/sessions
+- `fundamentals-universal-attributes.md` - Other universal attributes (user.id, metadata)
+- `span-chain.md` - CHAIN span specification
+- `sessions-python.md` - Python session tracking patterns
PATCH

echo "Gold patch applied."
