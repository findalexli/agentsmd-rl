#!/usr/bin/env bash
set -euo pipefail

cd /workspace/agent-skills

# Idempotency guard
if grep -qF "Consider that you do not need to hardcode model names (e.g., `gemini-flash-lite-" "skills/firebase-ai-logic-basics/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/firebase-ai-logic-basics/SKILL.md b/skills/firebase-ai-logic-basics/SKILL.md
@@ -64,7 +64,7 @@ To improve the user experience by showing partial results as they arrive (like a
 
 ### Generate Images with Nano Banana
 
-- Start with Gemini for most use cases, and choose Imagen for specialized tasks where image quality and specific styles are critical. (gemini-2.5-flash-image)
+- Start with Gemini for most use cases, and choose Imagen for specialized tasks where image quality and specific styles are critical. (Example: gemini-2.5-flash-image)
 - Requires an upgraded Blaze pay-as-you-go billing plan.
 
 ### Search Grounding with the built in googleSearch tool
@@ -91,15 +91,15 @@ Recommended: The developer must enable Firebase App Check to prevent unauthorize
 
 ### Remote Config
 
-Consider that you do not need to hardcode model names (e.g., `gemini-2.5-flash-lite`). Use Firebase Remote Config to update model versions dynamically without deploying new client code.  See [Changing model names remotely](https://firebase.google.com/docs/ai-logic/change-model-name-remotely.md.txt) 
+Consider that you do not need to hardcode model names (e.g., `gemini-flash-lite-latest`). Use Firebase Remote Config to update model versions dynamically without deploying new client code.  See [Changing model names remotely](https://firebase.google.com/docs/ai-logic/change-model-name-remotely.md.txt) 
 
 ## Initialization Code References
 
 | Language, Framework, Platform | Gemini API provider | Context URL |
 | :---- | :---- | :---- |
 | Web Modular API | Gemini Developer API (Developer API) | firebase://docs/ai-logic/get-started  |
 
-**Always use gemini-2.5-flash or gemini-3-flash-preview unless another model is requested by the docs or the user. DO NOT USE gemini 1.5 flash**
+**Always use the most recent version of Gemini (gemini-flash-latest) unless another model is requested by the docs or the user. DO NOT USE gemini-1.5-flash**
 
 ## References
 
PATCH

echo "Gold patch applied."
