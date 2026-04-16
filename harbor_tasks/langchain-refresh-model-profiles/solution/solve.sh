#!/bin/bash
set -e

cd /workspace/langchain

# Check if already applied
if grep -q '"mistral-small-2603":' libs/partners/mistralai/langchain_mistralai/data/_profiles.py 2>/dev/null; then
    echo "Patch already applied"
    exit 0
fi

# Apply the gold patch from the actual PR diff
cat <<'PATCH' | git apply -
diff --git a/libs/partners/mistralai/langchain_mistralai/data/_profiles.py b/libs/partners/mistralai/langchain_mistralai/data/_profiles.py
--- a/libs/partners/mistralai/langchain_mistralai/data/_profiles.py
+++ b/libs/partners/mistralai/langchain_mistralai/data/_profiles.py
@@ -416,13 +416,33 @@ _PROFILES: dict[str, dict[str, Any]] = {
         "attachment": False,
         "temperature": True,
     },
+    "mistral-small-2603": {
+        "name": "Mistral Small 4",
+        "release_date": "2026-03-16",
+        "last_updated": "2026-03-16",
+        "open_weights": True,
+        "max_input_tokens": 256000,
+        "max_output_tokens": 256000,
+        "text_inputs": True,
+        "image_inputs": True,
+        "audio_inputs": False,
+        "video_inputs": False,
+        "text_outputs": True,
+        "image_outputs": False,
+        "audio_outputs": False,
+        "video_outputs": False,
+        "reasoning_output": True,
+        "tool_calling": True,
+        "attachment": True,
+        "temperature": True,
+    },
     "mistral-small-latest": {
         "name": "Mistral Small (latest)",
-        "release_date": "2024-09-01",
-        "last_updated": "2024-09-04",
+        "release_date": "2026-03-16",
+        "last_updated": "2026-03-16",
         "open_weights": True,
-        "max_input_tokens": 128000,
-        "max_output_tokens": 16384,
+        "max_input_tokens": 256000,
+        "max_output_tokens": 256000,
         "text_inputs": True,
         "image_inputs": True,
         "audio_inputs": False,
@@ -431,9 +451,9 @@ _PROFILES: dict[str, dict[str, Any]] = {
         "image_outputs": False,
         "audio_outputs": False,
         "video_outputs": False,
-        "reasoning_output": False,
+        "reasoning_output": True,
         "tool_calling": True,
-        "attachment": False,
+        "attachment": True,
         "temperature": True,
     },
     "open-mistral-7b": {
diff --git a/libs/partners/openai/langchain_openai/data/_profiles.py b/libs/partners/openai/langchain_openai/data/_profiles.py
--- a/libs/partners/openai/langchain_openai/data/_profiles.py
+++ b/libs/partners/openai/langchain_openai/data/_profiles.py
@@ -717,6 +717,32 @@ _PROFILES: dict[str, dict[str, Any]] = {
         "image_tool_message": True,
         "tool_choice": True,
     },
+    "gpt-5.3-chat-latest": {
+        "name": "GPT-5.3 Chat (latest)",
+        "release_date": "2026-03-03",
+        "last_updated": "2026-03-03",
+        "open_weights": False,
+        "max_input_tokens": 128000,
+        "max_output_tokens": 16384,
+        "text_inputs": True,
+        "image_inputs": True,
+        "audio_inputs": False,
+        "video_inputs": False,
+        "text_outputs": True,
+        "image_outputs": False,
+        "audio_outputs": False,
+        "video_outputs": False,
+        "reasoning_output": False,
+        "tool_calling": True,
+        "structured_output": True,
+        "attachment": True,
+        "temperature": True,
+        "image_url_inputs": True,
+        "pdf_inputs": True,
+        "pdf_tool_message": True,
+        "image_tool_message": True,
+        "tool_choice": True,
+    },
     "gpt-5.3-codex": {
         "name": "GPT-5.3 Codex",
         "release_date": "2026-02-05",
diff --git a/libs/partners/openrouter/langchain_openrouter/data/_profiles.py b/libs/partners/openrouter/langchain_openrouter/data/_profiles.py
--- a/libs/partners/openrouter/langchain_openrouter/data/_profiles.py
+++ b/libs/partners/openrouter/langchain_openrouter/data/_profiles.py
@@ -1750,7 +1750,7 @@ _PROFILES: dict[str, dict[str, Any]] = {
         "attachment": False,
         "temperature": True,
     },
-    "nvidia/nemotron-3-super-120b-a12b-free": {
+    "nvidia/nemotron-3-super-120b-a12b:free": {
         "name": "Nemotron 3 Super (free)",
         "release_date": "2026-03-11",
         "last_updated": "2026-03-11",
PATCH

echo "Patch applied successfully"
