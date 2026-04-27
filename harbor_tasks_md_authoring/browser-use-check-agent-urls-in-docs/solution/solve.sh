#!/usr/bin/env bash
set -euo pipefail

cd /workspace/browser-use

# Idempotency guard
if grep -qF "* `tools`: Registry of <a href=\"https://docs.browser-use.com/customize/tools/ava" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -3,7 +3,7 @@
 Browser-Use is an AI agent that autonomously interacts with the web. It takes a user-defined task, navigates web pages using Chromium via CDP, processes HTML, and repeatedly queries a language model to decide the next action—until the task is completed.
 
 # Development Rules
-- Always use [`uv`](mdc:https:/github.com/astral-sh/uv) instead of `pip`
+- Always use [`uv`](https://github.com/astral-sh/uv) instead of `pip`
 ```bash
 uv venv --python 3.11
 source .venv/bin/activate
@@ -170,7 +170,7 @@ See [Supported Models](https://docs.browser-use.com/supported-models#supported-m
   ```
 </CodeGroup>
 
-<Note> Custom browsers can be configured in one line. Check out <a href="customize/browser/basics">browsers</a> for more. </Note>
+<Note> Custom browsers can be configured in one line. Check out <a href="https://docs.browser-use.com/customize/browser/basics">browsers</a> for more. </Note>
 
 ## 4. Going to Production
 
@@ -191,7 +191,7 @@ async def production_task(browser: Browser):
 asyncio.run(production_task())
 ```
 
-See [Going to Production](/production) for how to sync your cookies to the cloud.
+See [Going to Production](https://docs.browser-use.com/production) for how to sync your cookies to the cloud.
 
 
 # Going to Production
@@ -256,7 +256,7 @@ Your cloud browser is already logged in!
 
 ***
 
-For more sandbox parameters and events, see [Sandbox Quickstart](/customize/sandbox/quickstart).
+For more sandbox parameters and events, see [Sandbox Quickstart](https://docs.browser-use.com/customize/sandbox/quickstart).
 
 # Agent Basics
 ```python  theme={null}
@@ -272,13 +272,13 @@ async def main():
 ```
 
 * `task`: The task you want to automate.
-* `llm`: Your favorite LLM. See <a href="/customize/supported-models">Supported Models</a>.
+* `llm`: Your favorite LLM. See <a href="https://docs.browser-use.com/customize/agent/supported-models">Supported Models</a>.
 
 The agent is executed using the async `run()` method:
 
 * `max_steps` (default: `100`): Maximum number of steps an agent can take.
 
-Check out all customizable parameters <a href="/customize/agent/all-parameters"> here</a>.
+Check out all customizable parameters <a href="https://docs.browser-use.com/customize/agent/all-parameters"> here</a>.
 
 # Agent All Parameters
 > Complete reference for all agent configuration options
@@ -287,7 +287,7 @@ Check out all customizable parameters <a href="/customize/agent/all-parameters">
 
 ### Core Settings
 
-* `tools`: Registry of <a href="../tools/available">tools</a> the agent can call. <a href="../tools/basics">Example</a>
+* `tools`: Registry of <a href="https://docs.browser-use.com/customize/tools/available">tools</a> the agent can call. <a href="https://docs.browser-use.com/customize/tools/basics">Example</a>
 * `browser`: Browser object where you can specify the browser settings.
 * `output_model_schema`: Pydantic model class for structured output validation. [Example](https://github.com/browser-use/browser-use/blob/main/examples/features/custom_output.py)
 
@@ -460,7 +460,7 @@ task = """
 """
 ```
 
-See [Available Tools](/customize/tools/available) for the complete list of actions.
+See [Available Tools](https://docs.browser-use.com/customize/tools/available) for the complete list of actions.
 
 ### 3. Handle interaction problems via keyboard navigation
 
@@ -538,7 +538,7 @@ async def main():
 > Complete reference for all browser configuration options
 
 <Note>
-  The `Browser` instance also provides all [Actor](/customize/actor/all-parameters) methods for direct browser control (page management, element interactions, etc.).
+  The `Browser` instance also provides all [Actor](https://docs.browser-use.com/customize/actor/all-parameters) methods for direct browser control (page management, element interactions, etc.).
 </Note>
 
 ## Core Settings
@@ -793,7 +793,7 @@ agent = Agent(
 ```
 
 <Note>
-  Use `browser` parameter in tools for deterministic [Actor](/customize/actor/basics) actions.
+  Use `browser` parameter in tools for deterministic [Actor](https://docs.browser-use.com/customize/actor/basics) actions.
 </Note>
 
 
PATCH

echo "Gold patch applied."
