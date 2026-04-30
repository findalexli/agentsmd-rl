#!/usr/bin/env bash
set -euo pipefail

cd /workspace/stagehand

# Idempotency guard
if grep -qF "This is a project that uses Stagehand V3, a browser automation framework with AI" ".cursorrules" && grep -qF "This is a project that uses Stagehand V3, a browser automation framework with AI" "claude.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursorrules b/.cursorrules
@@ -1,150 +1,263 @@
 # Stagehand Project
 
-This is a project that uses Stagehand, which amplifies Playwright with `act`, `extract`, and `observe` added to the Page class.
+This is a project that uses Stagehand V3, a browser automation framework with AI-powered `act`, `extract`, `observe`, and `agent` methods.
 
-`Stagehand` is a class that provides config, a `StagehandPage` object via `stagehand.page`, and a `StagehandContext` object via `stagehand.context`.
+The main class can be imported as `Stagehand` from `@browserbasehq/stagehand`.
 
-`Page` is a class that extends the Playwright `Page` class and adds `act`, `extract`, and `observe` methods.
-`Context` is a class that extends the Playwright `BrowserContext` class.
+**Key Classes:**
 
-Use the following rules to write code for this project.
+- `Stagehand`: Main orchestrator class providing `act`, `extract`, `observe`, and `agent` methods
+- `context`: A `V3Context` object that manages browser contexts and pages
+- `page`: Individual page objects accessed via `stagehand.context.pages()[i]` or created with `stagehand.context.newPage()`
 
-- To take an action on the page like "click the sign in button", use Stagehand `act` like this:
+## Initialize
 
 ```typescript
-await page.act("Click the sign in button");
+import { Stagehand } from "@browserbasehq/stagehand";
+
+const stagehand = new Stagehand({
+  env: "LOCAL", // or "BROWSERBASE"
+  verbose: 2, // 0, 1, or 2
+  model: "openai/gpt-4.1-mini", // or any supported model
+});
+
+await stagehand.init();
+
+// Access the browser context and pages
+const page = stagehand.context.pages()[0];
+const context = stagehand.context;
+
+// Create new pages if needed
+const page2 = await stagehand.context.newPage();
 ```
 
-- To plan an instruction before taking an action, use Stagehand `observe` to get the action to execute.
+## Act
+
+Actions are called on the `stagehand` instance (not the page). Use atomic, specific instructions:
 
 ```typescript
-const [action] = await page.observe("Click the sign in button");
+// Act on the current active page
+await stagehand.act("click the sign in button");
+
+// Act on a specific page (when you need to target a page that isn't currently active)
+await stagehand.act("click the sign in button", { page: page2 });
 ```
 
-- The result of `observe` is an array of `ObserveResult` objects that can directly be used as params for `act` like this:
+**Important:** Act instructions should be atomic and specific:
+
+- ✅ Good: "Click the sign in button" or "Type 'hello' into the search input"
+- ❌ Bad: "Order me pizza" or "Type in the search bar and hit enter" (multi-step)
 
-  ```typescript
-  const [action] = await page.observe("Click the sign in button");
-  await page.act(action);
-  ```
+### Observe + Act Pattern (Recommended)
 
-- When writing code that needs to extract data from the page, use Stagehand `extract`. Explicitly pass the following params by default:
+Cache the results of `observe` to avoid unexpected DOM changes:
 
 ```typescript
-const { someValue } = await page.extract({
-  instruction: the instruction to execute,
-  schema: z.object({
-    someValue: z.string(),
-  }), // The schema to extract
-});
+const instruction = "Click the sign in button";
+
+// Get candidate actions
+const actions = await stagehand.observe(instruction);
+
+// Execute the first action
+await stagehand.act(actions[0]);
 ```
 
-- when writing a schema for `extract`, if the user is attempting to extract links or URLs, use `z.string().url()` to define the link or URL field
+To target a specific page:
 
 ```typescript
-const { someLink } = await page.extract({
-  instruction: the instruction to execute,
-  schema: z.object({
-    someLink: z.string().url(),
-  }), // The schema to extract
+const actions = await stagehand.observe("select blue as the favorite color", {
+  page: page2,
 });
+await stagehand.act(actions[0], { page: page2 });
 ```
 
-## Initialize
+## Extract
+
+Extract data from pages using natural language instructions. The `extract` method is called on the `stagehand` instance.
+
+### Basic Extraction (with schema)
 
 ```typescript
-import { Stagehand } from "@browserbasehq/stagehand";
-import StagehandConfig from "./stagehand.config";
+import { z } from "zod/v3";
+
+// Extract with explicit schema
+const data = await stagehand.extract(
+  "extract all apartment listings with prices and addresses",
+  z.object({
+    listings: z.array(
+      z.object({
+        price: z.string(),
+        address: z.string(),
+      }),
+    ),
+  }),
+);
 
-const stagehand = new Stagehand(StagehandConfig);
-await stagehand.init();
+console.log(data.listings);
+```
 
-const page = stagehand.page; // Playwright Page with act, extract, and observe methods
-const context = stagehand.context; // Playwright BrowserContext
+### Simple Extraction (without schema)
+
+```typescript
+// Extract returns a default object with 'extraction' field
+const result = await stagehand.extract("extract the sign in button text");
+
+console.log(result);
+// Output: { extraction: "Sign in" }
+
+// Or destructure directly
+const { extraction } = await stagehand.extract(
+  "extract the sign in button text",
+);
+console.log(extraction); // "Sign in"
 ```
 
-## Act
+### Targeted Extraction
 
-You can cache the results of `observe` and use them as params for `act` like this:
+Extract data from a specific element using a selector:
 
 ```typescript
-const instruction = "Click the sign in button";
-const cachedAction = await getCache(instruction);
+const reason = await stagehand.extract(
+  "extract the reason why script injection fails",
+  z.string(),
+  { selector: "/html/body/div[2]/div[3]/iframe/html/body/p[2]" },
+);
+```
+
+### URL Extraction
 
-if (cachedAction) {
-  await page.act(cachedAction);
-} else {
-  try {
-    const results = await page.observe(instruction);
-    await setCache(instruction, results);
-    await page.act(results[0]);
-  } catch (error) {
-    await page.act(instruction); // If the action is not cached, execute the instruction directly
-  }
-}
+When extracting links or URLs, use `z.string().url()`:
+
+```typescript
+const { links } = await stagehand.extract(
+  "extract all navigation links",
+  z.object({
+    links: z.array(z.string().url()),
+  }),
+);
 ```
 
-Be sure to cache the results of `observe` and use them as params for `act` to avoid unexpected DOM changes. Using `act` without caching will result in more unpredictable behavior.
+### Extracting from a Specific Page
 
-Act `action` should be as atomic and specific as possible, i.e. "Click the sign in button" or "Type 'hello' into the search input".
-AVOID actions that are more than one step, i.e. "Order me pizza" or "Type in the search bar and hit enter".
+```typescript
+// Extract from a specific page (when you need to target a page that isn't currently active)
+const data = await stagehand.extract(
+  "extract the placeholder text on the name field",
+  { page: page2 },
+);
+```
 
-## Extract
+## Observe
 
-If you are writing code that needs to extract data from the page, use Stagehand `extract`.
+Plan actions before executing them. Returns an array of candidate actions:
 
 ```typescript
-const signInButtonText = await page.extract("extract the sign in button text");
+// Get candidate actions on the current active page
+const [action] = await stagehand.observe("Click the sign in button");
+
+// Execute the action
+await stagehand.act(action);
 ```
 
-You can also pass in params like an output schema in Zod, and a flag to use text extraction:
+Observing on a specific page:
 
 ```typescript
-const data = await page.extract({
-  instruction: "extract the sign in button text",
-  schema: z.object({
-    text: z.string(),
-  }),
+// Target a specific page (when you need to target a page that isn't currently active)
+const actions = await stagehand.observe("find the next page button", {
+  page: page2,
 });
+await stagehand.act(actions[0], { page: page2 });
 ```
 
-`schema` is a Zod schema that describes the data you want to extract. To extract an array, make sure to pass in a single object that contains the array, as follows:
+## Agent
+
+Use the `agent` method to autonomously execute complex, multi-step tasks.
+
+### Basic Agent Usage
 
 ```typescript
-const data = await page.extract({
-  instruction: "extract the text inside all buttons",
-  schema: z.object({
-    text: z.array(z.string()),
-  }),
+const page = stagehand.context.pages()[0];
+await page.goto("https://www.google.com");
+
+const agent = stagehand.agent({
+  model: "google/gemini-2.0-flash",
+  executionModel: "google/gemini-2.0-flash",
+});
+
+const result = await agent.execute({
+  instruction: "Search for the stock price of NVDA",
+  maxSteps: 20,
 });
+
+console.log(result.message);
 ```
 
-## Agent
+### Computer Use Agent (CUA)
 
-Use the `agent` method to automonously execute larger tasks like "Get the stock price of NVDA"
+For more advanced scenarios using computer-use models:
 
 ```typescript
-// Navigate to a website
-await stagehand.page.goto("https://www.google.com");
+const agent = stagehand.agent({
+  cua: true, // Enable Computer Use Agent mode
+  model: "anthropic/claude-sonnet-4-20250514",
+  // or "google/gemini-2.5-computer-use-preview-10-2025"
+  systemPrompt: `You are a helpful assistant that can use a web browser.
+    Do not ask follow up questions, the user will trust your judgement.`,
+});
+
+await agent.execute({
+  instruction: "Apply for a library card at the San Francisco Public Library",
+  maxSteps: 30,
+});
+```
 
+### Agent with Custom Model Configuration
+
+```typescript
 const agent = stagehand.agent({
-  // You can use either OpenAI or Anthropic
-  provider: "openai",
-  // The model to use (claude-3-7-sonnet-20250219 or claude-3-5-sonnet-20240620 for Anthropic)
-  model: "computer-use-preview",
-
-  // Customize the system prompt
-  instructions: `You are a helpful assistant that can use a web browser.
-	Do not ask follow up questions, the user will trust your judgement.`,
-
-  // Customize the API key
-  options: {
-    apiKey: process.env.OPENAI_API_KEY,
+  model: {
+    modelName: "google/gemini-2.5-computer-use-preview-10-2025",
+    apiKey: process.env.GEMINI_API_KEY,
   },
+  systemPrompt: `You are a helpful assistant.`,
 });
+```
 
-// Execute the agent
-await agent.execute(
-  "Apply for a library card at the San Francisco Public Library"
-);
+### Agent with Integrations (MCP/External Tools)
+
+```typescript
+const agent = stagehand.agent({
+  integrations: [`https://mcp.exa.ai/mcp?exaApiKey=${process.env.EXA_API_KEY}`],
+  systemPrompt: `You have access to the Exa search tool.`,
+});
+```
+
+## Advanced Features
+
+### DeepLocator (XPath Targeting)
+
+Target specific elements across shadow DOM and iframes:
+
+```typescript
+await page
+  .deepLocator("/html/body/div[2]/div[3]/iframe/html/body/p")
+  .highlight({
+    durationMs: 5000,
+    contentColor: { r: 255, g: 0, b: 0 },
+  });
+```
+
+### Multi-Page Workflows
+
+```typescript
+const page1 = stagehand.context.pages()[0];
+await page1.goto("https://example.com");
+
+const page2 = await stagehand.context.newPage();
+await page2.goto("https://example2.com");
+
+// Act/extract/observe operate on the current active page by default
+// Pass { page } option to target a specific page
+await stagehand.act("click button", { page: page1 });
+await stagehand.extract("get title", { page: page2 });
 ```
diff --git a/claude.md b/claude.md
@@ -1,150 +1,263 @@
 # Stagehand Project
 
-This is a project that uses Stagehand, which amplifies Playwright with `act`, `extract`, and `observe` added to the Page class.
+This is a project that uses Stagehand V3, a browser automation framework with AI-powered `act`, `extract`, `observe`, and `agent` methods.
 
-`Stagehand` is a class that provides config, a `StagehandPage` object via `stagehand.page`, and a `StagehandContext` object via `stagehand.context`.
+The main class can be imported as `Stagehand` from `@browserbasehq/stagehand`.
 
-`Page` is a class that extends the Playwright `Page` class and adds `act`, `extract`, and `observe` methods.
-`Context` is a class that extends the Playwright `BrowserContext` class.
+**Key Classes:**
 
-Use the following rules to write code for this project.
+- `Stagehand`: Main orchestrator class providing `act`, `extract`, `observe`, and `agent` methods
+- `context`: A `V3Context` object that manages browser contexts and pages
+- `page`: Individual page objects accessed via `stagehand.context.pages()[i]` or created with `stagehand.context.newPage()`
 
-- To take an action on the page like "click the sign in button", use Stagehand `act` like this:
+## Initialize
 
 ```typescript
-await page.act("Click the sign in button");
+import { Stagehand } from "@browserbasehq/stagehand";
+
+const stagehand = new Stagehand({
+  env: "LOCAL", // or "BROWSERBASE"
+  verbose: 2, // 0, 1, or 2
+  model: "openai/gpt-4.1-mini", // or any supported model
+});
+
+await stagehand.init();
+
+// Access the browser context and pages
+const page = stagehand.context.pages()[0];
+const context = stagehand.context;
+
+// Create new pages if needed
+const page2 = await stagehand.context.newPage();
 ```
 
-- To plan an instruction before taking an action, use Stagehand `observe` to get the action to execute.
+## Act
+
+Actions are called on the `stagehand` instance (not the page). Use atomic, specific instructions:
 
 ```typescript
-const [action] = await page.observe("Click the sign in button");
+// Act on the current active page
+await stagehand.act("click the sign in button");
+
+// Act on a specific page (when you need to target a page that isn't currently active)
+await stagehand.act("click the sign in button", { page: page2 });
 ```
 
-- The result of `observe` is an array of `ObserveResult` objects that can directly be used as params for `act` like this:
+**Important:** Act instructions should be atomic and specific:
+
+- ✅ Good: "Click the sign in button" or "Type 'hello' into the search input"
+- ❌ Bad: "Order me pizza" or "Type in the search bar and hit enter" (multi-step)
 
-  ```typescript
-  const [action] = await page.observe("Click the sign in button");
-  await page.act(action);
-  ```
+### Observe + Act Pattern (Recommended)
 
-- When writing code that needs to extract data from the page, use Stagehand `extract`. Explicitly pass the following params by default:
+Cache the results of `observe` to avoid unexpected DOM changes:
 
 ```typescript
-const { someValue } = await page.extract({
-  instruction: the instruction to execute,
-  schema: z.object({
-    someValue: z.string(),
-  }), // The schema to extract
-});
+const instruction = "Click the sign in button";
+
+// Get candidate actions
+const actions = await stagehand.observe(instruction);
+
+// Execute the first action
+await stagehand.act(actions[0]);
 ```
 
-- when writing a schema for `extract`, if the user is attempting to extract links or URLs, use `z.string().url()` to define the link or URL field
+To target a specific page:
 
 ```typescript
-const { someLink } = await page.extract({
-  instruction: the instruction to execute,
-  schema: z.object({
-    someLink: z.string().url(),
-  }), // The schema to extract
+const actions = await stagehand.observe("select blue as the favorite color", {
+  page: page2,
 });
+await stagehand.act(actions[0], { page: page2 });
 ```
 
-## Initialize
+## Extract
+
+Extract data from pages using natural language instructions. The `extract` method is called on the `stagehand` instance.
+
+### Basic Extraction (with schema)
 
 ```typescript
-import { Stagehand } from "@browserbasehq/stagehand";
-import StagehandConfig from "./stagehand.config";
+import { z } from "zod/v3";
+
+// Extract with explicit schema
+const data = await stagehand.extract(
+  "extract all apartment listings with prices and addresses",
+  z.object({
+    listings: z.array(
+      z.object({
+        price: z.string(),
+        address: z.string(),
+      }),
+    ),
+  }),
+);
 
-const stagehand = new Stagehand(StagehandConfig);
-await stagehand.init();
+console.log(data.listings);
+```
 
-const page = stagehand.page; // Playwright Page with act, extract, and observe methods
-const context = stagehand.context; // Playwright BrowserContext
+### Simple Extraction (without schema)
+
+```typescript
+// Extract returns a default object with 'extraction' field
+const result = await stagehand.extract("extract the sign in button text");
+
+console.log(result);
+// Output: { extraction: "Sign in" }
+
+// Or destructure directly
+const { extraction } = await stagehand.extract(
+  "extract the sign in button text",
+);
+console.log(extraction); // "Sign in"
 ```
 
-## Act
+### Targeted Extraction
 
-You can cache the results of `observe` and use them as params for `act` like this:
+Extract data from a specific element using a selector:
 
 ```typescript
-const instruction = "Click the sign in button";
-const cachedAction = await getCache(instruction);
+const reason = await stagehand.extract(
+  "extract the reason why script injection fails",
+  z.string(),
+  { selector: "/html/body/div[2]/div[3]/iframe/html/body/p[2]" },
+);
+```
+
+### URL Extraction
 
-if (cachedAction) {
-  await page.act(cachedAction);
-} else {
-  try {
-    const results = await page.observe(instruction);
-    await setCache(instruction, results);
-    await page.act(results[0]);
-  } catch (error) {
-    await page.act(instruction); // If the action is not cached, execute the instruction directly
-  }
-}
+When extracting links or URLs, use `z.string().url()`:
+
+```typescript
+const { links } = await stagehand.extract(
+  "extract all navigation links",
+  z.object({
+    links: z.array(z.string().url()),
+  }),
+);
 ```
 
-Be sure to cache the results of `observe` and use them as params for `act` to avoid unexpected DOM changes. Using `act` without caching will result in more unpredictable behavior.
+### Extracting from a Specific Page
 
-Act `action` should be as atomic and specific as possible, i.e. "Click the sign in button" or "Type 'hello' into the search input".
-AVOID actions that are more than one step, i.e. "Order me pizza" or "Type in the search bar and hit enter".
+```typescript
+// Extract from a specific page (when you need to target a page that isn't currently active)
+const data = await stagehand.extract(
+  "extract the placeholder text on the name field",
+  { page: page2 },
+);
+```
 
-## Extract
+## Observe
 
-If you are writing code that needs to extract data from the page, use Stagehand `extract`.
+Plan actions before executing them. Returns an array of candidate actions:
 
 ```typescript
-const signInButtonText = await page.extract("extract the sign in button text");
+// Get candidate actions on the current active page
+const [action] = await stagehand.observe("Click the sign in button");
+
+// Execute the action
+await stagehand.act(action);
 ```
 
-You can also pass in params like an output schema in Zod, and a flag to use text extraction:
+Observing on a specific page:
 
 ```typescript
-const data = await page.extract({
-  instruction: "extract the sign in button text",
-  schema: z.object({
-    text: z.string(),
-  }),
+// Target a specific page (when you need to target a page that isn't currently active)
+const actions = await stagehand.observe("find the next page button", {
+  page: page2,
 });
+await stagehand.act(actions[0], { page: page2 });
 ```
 
-`schema` is a Zod schema that describes the data you want to extract. To extract an array, make sure to pass in a single object that contains the array, as follows:
+## Agent
+
+Use the `agent` method to autonomously execute complex, multi-step tasks.
+
+### Basic Agent Usage
 
 ```typescript
-const data = await page.extract({
-  instruction: "extract the text inside all buttons",
-  schema: z.object({
-    text: z.array(z.string()),
-  }),
+const page = stagehand.context.pages()[0];
+await page.goto("https://www.google.com");
+
+const agent = stagehand.agent({
+  model: "google/gemini-2.0-flash",
+  executionModel: "google/gemini-2.0-flash",
+});
+
+const result = await agent.execute({
+  instruction: "Search for the stock price of NVDA",
+  maxSteps: 20,
 });
+
+console.log(result.message);
 ```
 
-## Agent
+### Computer Use Agent (CUA)
 
-Use the `agent` method to automonously execute larger tasks like "Get the stock price of NVDA"
+For more advanced scenarios using computer-use models:
 
 ```typescript
-// Navigate to a website
-await stagehand.page.goto("https://www.google.com");
+const agent = stagehand.agent({
+  cua: true, // Enable Computer Use Agent mode
+  model: "anthropic/claude-sonnet-4-20250514",
+  // or "google/gemini-2.5-computer-use-preview-10-2025"
+  systemPrompt: `You are a helpful assistant that can use a web browser.
+    Do not ask follow up questions, the user will trust your judgement.`,
+});
+
+await agent.execute({
+  instruction: "Apply for a library card at the San Francisco Public Library",
+  maxSteps: 30,
+});
+```
 
+### Agent with Custom Model Configuration
+
+```typescript
 const agent = stagehand.agent({
-  // You can use either OpenAI or Anthropic
-  provider: "openai",
-  // The model to use (claude-3-7-sonnet-20250219 or claude-3-5-sonnet-20240620 for Anthropic)
-  model: "computer-use-preview",
-
-  // Customize the system prompt
-  instructions: `You are a helpful assistant that can use a web browser.
-	Do not ask follow up questions, the user will trust your judgement.`,
-
-  // Customize the API key
-  options: {
-    apiKey: process.env.OPENAI_API_KEY,
+  model: {
+    modelName: "google/gemini-2.5-computer-use-preview-10-2025",
+    apiKey: process.env.GEMINI_API_KEY,
   },
+  systemPrompt: `You are a helpful assistant.`,
 });
+```
 
-// Execute the agent
-await agent.execute(
-  "Apply for a library card at the San Francisco Public Library",
-);
+### Agent with Integrations (MCP/External Tools)
+
+```typescript
+const agent = stagehand.agent({
+  integrations: [`https://mcp.exa.ai/mcp?exaApiKey=${process.env.EXA_API_KEY}`],
+  systemPrompt: `You have access to the Exa search tool.`,
+});
+```
+
+## Advanced Features
+
+### DeepLocator (XPath Targeting)
+
+Target specific elements across shadow DOM and iframes:
+
+```typescript
+await page
+  .deepLocator("/html/body/div[2]/div[3]/iframe/html/body/p")
+  .highlight({
+    durationMs: 5000,
+    contentColor: { r: 255, g: 0, b: 0 },
+  });
+```
+
+### Multi-Page Workflows
+
+```typescript
+const page1 = stagehand.context.pages()[0];
+await page1.goto("https://example.com");
+
+const page2 = await stagehand.context.newPage();
+await page2.goto("https://example2.com");
+
+// Act/extract/observe operate on the current active page by default
+// Pass { page } option to target a specific page
+await stagehand.act("click button", { page: page1 });
+await stagehand.extract("get title", { page: page2 });
 ```
PATCH

echo "Gold patch applied."
