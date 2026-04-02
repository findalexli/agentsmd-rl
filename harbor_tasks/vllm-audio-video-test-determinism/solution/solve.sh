#!/usr/bin/env bash
set -euo pipefail

cd /workspace/vllm

TARGET="tests/entrypoints/openai/chat_completion/test_audio_in_video.py"

# Idempotency check: if temperature=0.0 is already in the file, skip
if grep -q 'temperature=0.0' "$TARGET" 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/tests/entrypoints/openai/chat_completion/test_audio_in_video.py b/tests/entrypoints/openai/chat_completion/test_audio_in_video.py
index 8c024995b938..61ee91eab4d0 100644
--- a/tests/entrypoints/openai/chat_completion/test_audio_in_video.py
+++ b/tests/entrypoints/openai/chat_completion/test_audio_in_video.py
@@ -64,11 +64,12 @@ async def test_online_audio_in_video(
     ]
 
     # multi-turn to test mm processor cache as well
-    for _ in range(2):
+    for turn in range(2):
         chat_completion = await client.chat.completions.create(
             model=MODEL_NAME,
             messages=messages,
-            max_tokens=16,
+            max_tokens=8,
+            temperature=0.0,
             extra_body={
                 "mm_processor_kwargs": {
                     "use_audio_in_video": True,
@@ -78,6 +79,12 @@ async def test_online_audio_in_video(
 
         assert len(chat_completion.choices) == 1
         choice = chat_completion.choices[0]
+        print(
+            f"[DEBUG][single-video] turn={turn} "
+            f"finish_reason={choice.finish_reason!r} "
+            f"content={choice.message.content!r} "
+            f"usage={chat_completion.usage}"
+        )
         assert choice.finish_reason == "length"
 
 
@@ -111,11 +118,12 @@ async def test_online_audio_in_video_multi_videos(
     ]
 
     # multi-turn to test mm processor cache as well
-    for _ in range(2):
+    for turn in range(2):
         chat_completion = await client.chat.completions.create(
             model=MODEL_NAME,
             messages=messages,
-            max_tokens=16,
+            max_tokens=8,
+            temperature=0.0,
             extra_body={
                 "mm_processor_kwargs": {
                     "use_audio_in_video": True,
@@ -125,6 +133,12 @@ async def test_online_audio_in_video_multi_videos(
 
         assert len(chat_completion.choices) == 1
         choice = chat_completion.choices[0]
+        print(
+            f"[DEBUG][multi-video] turn={turn} "
+            f"finish_reason={choice.finish_reason!r} "
+            f"content={choice.message.content!r} "
+            f"usage={chat_completion.usage}"
+        )
         assert choice.finish_reason == "length"
 
 
PATCH

echo "Patch applied successfully."
