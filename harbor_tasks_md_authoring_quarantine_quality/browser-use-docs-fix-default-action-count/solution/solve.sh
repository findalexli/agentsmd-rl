#!/usr/bin/env bash
set -euo pipefail

cd /workspace/browser-use

# Idempotency guard
if grep -qF "* `max_actions_per_step` (default: `3`): Maximum actions per step, e.g. for form" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -300,7 +300,7 @@ Check out all customizable parameters <a href="https://docs.browser-use.com/cust
 ### Actions & Behavior
 
 * `initial_actions`: List of actions to run before the main task without LLM. [Example](https://github.com/browser-use/browser-use/blob/main/examples/features/initial_actions.py)
-* `max_actions_per_step` (default: `4`): Maximum actions per step, e.g. for form filling the agent can output 4 fields at once. We execute the actions until the page changes.
+* `max_actions_per_step` (default: `3`): Maximum actions per step, e.g. for form filling the agent can output 3 fields at once. We execute the actions until the page changes.
 * `max_failures` (default: `3`): Maximum retries for steps with errors
 * `final_response_after_failure` (default: `True`): If True, attempt to force one final model call with intermediate output after max\_failures is reached
 * `use_thinking` (default: `True`): Controls whether the agent uses its internal "thinking" field for explicit reasoning steps.
@@ -351,7 +351,7 @@ history = await agent.run()
 
 # Access useful information
 history.urls()                    # List of visited URLs
-history.screenshot_paths()        # List of screenshot paths  
+history.screenshot_paths()        # List of screenshot paths
 history.screenshots()             # List of screenshots as base64 strings
 history.action_names()            # Names of executed actions
 history.extracted_content()       # List of extracted content from all actions
@@ -390,7 +390,7 @@ history = await agent.run()
 
 # Access useful information
 history.urls()                    # List of visited URLs
-history.screenshot_paths()        # List of screenshot paths  
+history.screenshot_paths()        # List of screenshot paths
 history.screenshots()             # List of screenshots as base64 strings
 history.action_names()            # Names of executed actions
 history.extracted_content()       # List of extracted content from all actions
@@ -422,7 +422,7 @@ For structured output, use the `output_model_schema` parameter with a Pydantic m
 
 
 # Agent Prompting Guide
-> Tips and tricks 
+> Tips and tricks
 
 Prompting can drastically improve performance and solve existing limitations of the library.
 
@@ -967,7 +967,7 @@ os.environ["ANONYMIZED_TELEMETRY"] = "false"
 # Local Setup
 Source: (go to or request this content to learn more) https://docs.browser-use.com/development/setup/local-setup
 
-We're excited to have you join our community of contributors. 
+We're excited to have you join our community of contributors.
 ## Welcome to Browser Use Development!
 
 ```bash  theme={null}
PATCH

echo "Gold patch applied."
