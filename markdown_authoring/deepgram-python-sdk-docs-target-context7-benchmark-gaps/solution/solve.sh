#!/usr/bin/env bash
set -euo pipefail

cd /workspace/deepgram-python-sdk

# Idempotency guard
if grep -qF "For a higher-level breakdown, set `utterances=True` to get pre-grouped speaker t" ".agents/skills/deepgram-python-audio-intelligence/SKILL.md" && grep -qF "Pass `callback=\"https://your.app/webhook\"` and the request **returns immediately" ".agents/skills/deepgram-python-speech-to-text/SKILL.md" && grep -qF "**Reconnect after disconnect (preserve conversation context):** `Settings` canno" ".agents/skills/deepgram-python-voice-agent/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/deepgram-python-audio-intelligence/SKILL.md b/.agents/skills/deepgram-python-audio-intelligence/SKILL.md
@@ -96,6 +96,47 @@ response = client.listen.v1.media.transcribe_file(
 )
 ```
 
+## Quick start — diarization with word-level timings
+
+Enable speaker separation and word-level timestamps in a single request, then iterate the per-word objects to build a speaker-labelled transcript with timing.
+
+```python
+response = client.listen.v1.media.transcribe_url(
+    url="https://dpgr.am/spacewalk.wav",
+    model="nova-3",
+    diarize=True,        # tag each word with a speaker id
+    smart_format=True,   # punctuated_word for cleaner output
+    punctuate=True,
+)
+
+words = response.results.channels[0].alternatives[0].words or []
+
+# Per-word: speaker, timestamps, confidence
+for w in words:
+    speaker = getattr(w, "speaker", None)
+    text = w.punctuated_word or w.word
+    print(f"[speaker {speaker}] {text}  ({w.start:.2f}s–{w.end:.2f}s, conf={w.confidence:.2f})")
+
+# Group consecutive words by speaker into utterances
+from itertools import groupby
+for speaker, group in groupby(words, key=lambda w: getattr(w, "speaker", None)):
+    text = " ".join((w.punctuated_word or w.word) for w in group)
+    print(f"Speaker {speaker}: {text}")
+```
+
+Per-word fields available on each entry:
+
+| Field | Type | Description |
+|---|---|---|
+| `word` | `str` | Lowercase token |
+| `punctuated_word` | `str \| None` | Token with smart-formatted casing/punctuation (when `smart_format=True`) |
+| `start`, `end` | `float` | Audio timestamps in seconds |
+| `confidence` | `float` | 0.0–1.0 confidence |
+| `speaker` | `int \| None` | Speaker id (when `diarize=True`); `None` if diarization disabled |
+| `speaker_confidence` | `float \| None` | Speaker-id confidence |
+
+For a higher-level breakdown, set `utterances=True` to get pre-grouped speaker turns at `response.results.utterances`. Set `paragraphs=True` for a `paragraphs` view organised by speaker turn boundaries.
+
 ## Quick start — WSS subset (diarize / redact / entities only)
 
 ```python
diff --git a/.agents/skills/deepgram-python-speech-to-text/SKILL.md b/.agents/skills/deepgram-python-speech-to-text/SKILL.md
@@ -58,7 +58,9 @@ response = client.listen.v1.media.transcribe_file(
 
 `request=` accepts raw `bytes` or an iterator of `bytes` (stream large files chunk-by-chunk). Do NOT pass a file handle.
 
-## Quick start — WebSocket (live streaming)
+## Quick start — WebSocket (live streaming with interim results)
+
+Live transcription emits **interim** (partial) and **final** results. Pass `interim_results=True` and switch on `is_final` to display partial text in real time, then overwrite it with the final transcript when the speaker pauses.
 
 ```python
 import threading
@@ -68,15 +70,40 @@ from deepgram.listen.v1.types import (
     ListenV1SpeechStarted, ListenV1UtteranceEnd,
 )
 
-with client.listen.v1.connect(model="nova-3") as conn:
+with client.listen.v1.connect(
+    model="nova-3",
+    interim_results=True,    # ← emit partial results while user is still speaking
+    utterance_end_ms=1000,   # silence (ms) before server emits UtteranceEnd
+    vad_events=True,         # SpeechStarted events
+    smart_format=True,
+) as conn:
+    # Mutable container so the on_message closure can update state without `global`
+    state = {"last_interim_len": 0}
+
     def on_message(m):
         if isinstance(m, ListenV1Results) and m.channel and m.channel.alternatives:
-            print(m.channel.alternatives[0].transcript)
-
-    conn.on(EventType.OPEN,    lambda _: print("open"))
+            transcript = m.channel.alternatives[0].transcript
+            if not transcript:
+                return
+            if m.is_final:
+                # Final segment: overwrite the running interim line, newline if utterance ended
+                pad = " " * max(0, state["last_interim_len"] - len(transcript))
+                end = "\n" if m.speech_final else ""
+                print(f"\r{transcript}{pad}", end=end, flush=True)
+                state["last_interim_len"] = 0
+            else:
+                # Interim: keep overwriting the same console line as the user speaks
+                print(f"\r{transcript}", end="", flush=True)
+                state["last_interim_len"] = len(transcript)
+        elif isinstance(m, ListenV1UtteranceEnd):
+            print()  # newline; UtteranceEnd fires after final results when audio goes silent
+        elif isinstance(m, ListenV1SpeechStarted):
+            pass  # optional: reset UI when a new utterance begins
+
+    conn.on(EventType.OPEN,    lambda _: print("connected"))
     conn.on(EventType.MESSAGE, on_message)
-    conn.on(EventType.CLOSE,   lambda _: print("close"))
-    conn.on(EventType.ERROR,   lambda e: print(f"err: {e}"))
+    conn.on(EventType.CLOSE,   lambda _: print("\nclosed"))
+    conn.on(EventType.ERROR,   lambda e: print(f"\nerr: {e}"))
 
     # Start receive loop in background so we can send concurrently
     threading.Thread(target=conn.start_listening, daemon=True).start()
@@ -87,6 +114,15 @@ with client.listen.v1.connect(model="nova-3") as conn:
     conn.send_finalize()               # flush final partial before closing
 ```
 
+### Interim vs. final flag semantics
+
+- **`is_final = False`** — interim hypothesis. Will be revised. Display in a non-committal style (lighter colour, italic) and overwrite when the next message arrives.
+- **`is_final = True`, `speech_final = False`** — confirmed segment, but the speaker is still talking. Append to the transcript; another final will follow.
+- **`is_final = True`, `speech_final = True`** — confirmed segment AND the utterance ended (silence detected). Commit the line and start a new one.
+- **`from_finalize = True`** — this final was triggered by your explicit `send_finalize()` call (vs natural endpointing). Useful to distinguish "I asked for a flush" from "the speaker paused".
+
+Send `send_finalize()` to force the server to emit final results immediately (e.g. user clicks "stop"). Send `send_close_stream()` after `send_finalize` to terminate cleanly.
+
 WSS message types live under `deepgram.listen.v1.types`.
 
 ## Async equivalents
@@ -102,6 +138,59 @@ async with client.listen.v1.connect(model="nova-3") as conn:
     await conn.start_listening()
 ```
 
+## Async / deferred result patterns
+
+There are **two distinct** notions of "async" — don't confuse them.
+
+### 1. Python `async/await` (sync-style, immediate result)
+
+`AsyncDeepgramClient` returns `Awaitable[<full response>]`. The result is delivered when you `await`, not later. Use this when integrating with FastAPI, aiohttp, or any asyncio app.
+
+```python
+import asyncio
+from deepgram import AsyncDeepgramClient
+
+client = AsyncDeepgramClient()
+
+async def transcribe(url: str) -> str:
+    response = await client.listen.v1.media.transcribe_url(
+        url=url,
+        model="nova-3",
+        smart_format=True,
+    )
+    # `response` is the FULL transcription — no polling, no callback, just await.
+    return response.results.channels[0].alternatives[0].transcript
+
+text = asyncio.run(transcribe("https://dpgr.am/spacewalk.wav"))
+```
+
+### 2. Deferred via callback URL (webhook, results posted later)
+
+Pass `callback="https://your.app/webhook"` and the request **returns immediately** with a `request_id`. Deepgram processes the audio in the background and POSTs the final result to your webhook URL. There is **no polling endpoint** — your server must be reachable to receive the result.
+
+```python
+response = client.listen.v1.media.transcribe_url(
+    url="https://dpgr.am/spacewalk.wav",
+    callback="https://your.app/deepgram-webhook",
+    callback_method="POST",         # or "PUT"
+    model="nova-3",
+    smart_format=True,
+)
+print(f"Accepted; tracking id: {response.request_id}")
+# response is a "listen accepted" — NOT the transcript. Wait for your webhook.
+```
+
+The webhook receives the same JSON body you would have received from a synchronous `transcribe_url` call. Use this for very long files or when you don't want the request hanging open.
+
+| Pattern | Returns | When to use |
+|---|---|---|
+| `client.listen.v1.media.transcribe_url(...)` | full transcription synchronously | files up to ~10 min; HTTP timeout-bound |
+| `await AsyncDeepgramClient().listen.v1.media.transcribe_url(...)` | full transcription, non-blocking | inside asyncio apps |
+| `transcribe_url(..., callback="https://...")` | `{request_id}` immediately, transcription POSTs to webhook later | very long files; no long-lived HTTP connection |
+| `client.listen.v1.connect(...)` (WebSocket) | streaming events as audio is sent | live audio (mic, telephony) |
+
+See `examples/12-transcription-prerecorded-callback.py` for a working callback example.
+
 ## Key parameters
 
 `model`, `language`, `encoding`, `sample_rate`, `channels`, `multichannel`, `punctuate`, `smart_format`, `diarize`, `endpointing`, `interim_results`, `utterance_end_ms`, `vad_events`, `keywords`, `search`, `redact`, `numerals`, `paragraphs`, `utterances`.
diff --git a/.agents/skills/deepgram-python-voice-agent/SKILL.md b/.agents/skills/deepgram-python-voice-agent/SKILL.md
@@ -124,6 +124,145 @@ with client.agent.v1.connect() as agent:
 
 You can persist the **`agent` block** of a Settings message server-side and reuse it by `agent_id`. `client.voice_agent.configurations.create` stores a JSON string representing the `agent` object only (listen / think / speak providers + prompt) — NOT the full `AgentV1Settings` payload. Do not send top-level Settings fields like `audio` to that API; those still go in the live Settings message at connect time. The returned `agent_id` replaces the inline `agent` object in future Settings messages. Managed via `client.voice_agent.configurations.*` — see `deepgram-python-management-api`.
 
+## Dynamic mid-session adjustment
+
+You can change agent behavior **without disconnecting** by sending control messages on the live socket. Each method is available on the agent connection object (`agent` in the quick-start) for both sync and async clients.
+
+```python
+from deepgram.agent.v1.types import (
+    AgentV1UpdatePrompt,
+    AgentV1UpdateSpeak,
+    AgentV1UpdateSpeakSpeak,        # type alias accepting SpeakSettingsV1 or list
+    AgentV1UpdateThink,
+    AgentV1UpdateThinkThink,        # type alias accepting ThinkSettingsV1 or list
+    AgentV1InjectAgentMessage,
+    AgentV1InjectUserMessage,
+    AgentV1KeepAlive,
+)
+from deepgram.types.speak_settings_v1 import SpeakSettingsV1
+from deepgram.types.speak_settings_v1provider import SpeakSettingsV1Provider_Deepgram
+from deepgram.types.think_settings_v1 import ThinkSettingsV1
+from deepgram.types.think_settings_v1provider import ThinkSettingsV1Provider_OpenAi
+
+# 1. Swap the LLM system prompt mid-conversation (e.g. escalate to a different persona)
+agent.send_update_prompt(
+    AgentV1UpdatePrompt(prompt="You are now in expert escalation mode. Be precise and concise.")
+)
+# Server replies with a `PromptUpdated` event when the new prompt is in effect.
+
+# 2. Swap the TTS voice without reconnecting (e.g. switch language or persona)
+agent.send_update_speak(
+    AgentV1UpdateSpeak(
+        speak=SpeakSettingsV1(
+            provider=SpeakSettingsV1Provider_Deepgram(
+                type="deepgram", model="aura-2-luna-en",
+            ),
+        ),
+    )
+)
+# Server replies with a `SpeakUpdated` event.
+
+# 3. Swap the LLM provider/model (e.g. cheaper model for follow-ups)
+agent.send_update_think(
+    AgentV1UpdateThink(
+        think=ThinkSettingsV1(
+            provider=ThinkSettingsV1Provider_OpenAi(
+                type="open_ai", model="gpt-4o-mini", temperature=0.3,
+            ),
+            prompt="You are a helpful assistant. Keep replies brief.",
+        ),
+    )
+)
+# Server replies with a `ThinkUpdated` event.
+
+# 4. Force the agent to say something specific (without waiting for user audio)
+agent.send_inject_agent_message(
+    AgentV1InjectAgentMessage(message="Quick reminder: your call is being recorded.")
+)
+# Useful for proactive prompts, status updates, or scripted segues.
+
+# 5. Inject a user message (e.g. text input from a chat sidebar alongside voice)
+agent.send_inject_user_message(
+    AgentV1InjectUserMessage(content="Schedule a follow-up for next Tuesday at 2pm.")
+)
+# Server may reply with `InjectionRefused` if the agent is mid-utterance — retry after `AgentAudioDone`.
+
+# 6. Idle-period keep-alive (no payload required; the SDK fills in the type literal)
+agent.send_keep_alive(AgentV1KeepAlive())
+# Or simply: agent.send_keep_alive()  — the message arg is optional.
+```
+
+Async client equivalents are identical but `await`-prefixed:
+
+```python
+await agent.send_update_prompt(AgentV1UpdatePrompt(prompt="..."))
+await agent.send_inject_agent_message(AgentV1InjectAgentMessage(message="..."))
+```
+
+## Stream lifecycle & recovery
+
+Continuous voice agents need explicit handling for idle periods, stream pauses, and reconnects.
+
+**Pause / idle (no audio for several seconds):** stop calling `send_media`, but emit a `KeepAlive` every ~5 seconds. Without it, the server closes the socket at ~10 seconds of idle.
+
+```python
+import threading, time
+
+stop = threading.Event()
+
+def keepalive_loop():
+    while not stop.is_set():
+        if stop.wait(5):
+            return
+        try:
+            agent.send_keep_alive()
+        except Exception:
+            return  # socket closed; outer loop will reconnect
+
+threading.Thread(target=keepalive_loop, daemon=True).start()
+```
+
+**Resume after pause:** just call `send_media` again. No control message is required — the agent picks up VAD on the next chunk.
+
+**Reconnect after disconnect (preserve conversation context):** `Settings` cannot be re-sent on the same closed socket; open a new connection and resend the same `Settings`. To carry conversation history forward, include it in the new `Settings.agent.context.messages` so the LLM resumes with prior turns:
+
+```python
+from deepgram.agent.v1.types import (
+    AgentV1SettingsAgentContext,
+    AgentV1SettingsAgentContextMessagesItem,
+    AgentV1SettingsAgentContextMessagesItemContent,
+    AgentV1SettingsAgentContextMessagesItemContentRole,
+)
+
+# Build the new Settings with the captured prior turns
+context = AgentV1SettingsAgentContext(
+    messages=[
+        AgentV1SettingsAgentContextMessagesItem(
+            content=AgentV1SettingsAgentContextMessagesItemContent(
+                role=AgentV1SettingsAgentContextMessagesItemContentRole.USER,
+                content="Hi, I'd like to schedule a meeting.",
+            ),
+        ),
+        AgentV1SettingsAgentContextMessagesItem(
+            content=AgentV1SettingsAgentContextMessagesItemContent(
+                role=AgentV1SettingsAgentContextMessagesItemContentRole.ASSISTANT,
+                content="Sure — what day works best?",
+            ),
+        ),
+    ],
+)
+new_settings = settings.model_copy(update={"agent": settings.agent.model_copy(update={"context": context})})
+
+# Open a fresh connection and replay
+with client.agent.v1.connect() as agent2:
+    agent2.send_settings(new_settings)
+    # ... same handlers + audio loop as before
+```
+
+The server emits a `History` message on connect when the SDK has captured prior turns; in Python you receive this as an `AgentV1History` object (wire `type` literal: `"History"`). Persist these turns in your application so a reconnect can rebuild `context.messages`.
+
+**Detect disconnects:** the `EventType.CLOSE` handler fires before the `with` block exits. Catch it and trigger your reconnect logic from there. Check `EventType.ERROR` payloads for cause (network drop vs server-initiated close vs warning).
+
 ## API reference (layered)
 
 1. **In-repo reference**: `reference.md` — "Agent V1 Connect", "Voice Agent Configurations".
PATCH

echo "Gold patch applied."
