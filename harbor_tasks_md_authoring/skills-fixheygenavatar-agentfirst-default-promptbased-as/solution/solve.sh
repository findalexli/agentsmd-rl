#!/usr/bin/env bash
set -euo pipefail

cd /workspace/skills

# Idempotency guard
if grep -qF "2. If SOUL.md or IDENTITY.md is found \u2192 extract appearance and voice traits sile" "heygen-avatar/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/heygen-avatar/SKILL.md b/heygen-avatar/SKILL.md
@@ -1,21 +1,24 @@
 ---
 name: heygen-avatar
 description: |
-  Create a persistent HeyGen avatar that looks and sounds like a specific person — the user,
-  the agent, or any named character — powered by HeyGen Avatar V technology.
-  Upload a photo → HeyGen builds a digital twin → reuse across unlimited videos.
-  Use when: (1) someone wants to appear in a video as themselves ("I want my face in a video",
-  "create my HeyGen avatar", "build a digital twin of me"), (2) setting up a HeyGen identity
-  before making videos or sending video messages — the correct FIRST step for new users,
-  (3) "create my avatar", "design an avatar", "give me a consistent look across my videos",
-  "bring yourself to life", "set up my identity on HeyGen", "set up my HeyGen identity",
-  "get started with HeyGen", "help me get started with AI video".
+  Create a persistent HeyGen avatar — a reusable face + voice identity for the agent,
+  the user, or any named character — powered by HeyGen Avatar V technology.
+  Prompt-based creation by default (description → HeyGen builds it); photo upload is
+  optional for real-person digital twins.
+  Use when: (1) giving the agent a face + voice so it can present videos
+  ("bring yourself to life", "create your avatar", "give yourself an avatar",
+  "design a presenter", "set up an avatar", "let's make an avatar"),
+  (2) the user wants to appear in videos as themselves ("create my avatar",
+  "I want my face in a video", "digital twin of me", "build me an avatar"),
+  (3) building a named character presenter ("create an avatar called Cleo",
+  "design a character named X"), (4) establishing HeyGen identity before making videos —
+  the correct FIRST step when no avatar exists yet.
   Chain signal: when the user says both an identity/avatar action AND a video action in the same
-  request ("design an avatar AND make a video", "set up my identity THEN create a video",
+  request ("create an avatar AND make a video", "set up identity THEN create a video",
   "design a presenter AND immediately record"), run heygen-avatar first, then heygen-video.
   Returns avatar_id + voice_id — pass directly to heygen-video to create HeyGen videos.
   NOT for: generating videos (use heygen-video), translating videos, or TTS-only tasks.
-argument-hint: "[photo_url_or_description]"
+argument-hint: "[name_or_description]"
 allowed-tools: Bash, WebFetch, Read, Write, mcp__heygen__*
 ---
 
@@ -25,11 +28,13 @@ Create and manage HeyGen avatars for anyone: the agent, the user, or named chara
 
 ## Start Here (Critical)
 
-**Do NOT batch-ask questions.** Do not fire "give me a photo, voice preference, duration, target platform, tone, key message" all at once. Walk phases in order. Each phase asks at most one or two things at a time.
+**Default target = the agent.** The primary use of this skill is giving the agent a face + voice so it can present videos. Route to "user" only on explicit "my avatar" / "me" / "my photo" language. When in doubt, make the agent's avatar.
 
-**When creating for the agent itself** ("create your avatar", "bring yourself to life"), do NOT ask the user for a photo or appearance details first. Read `SOUL.md` and `IDENTITY.md` from the workspace root. The agent's identity lives there. Only ask the user for traits that are genuinely missing from those files.
+**Do NOT batch-ask questions.** No "give me a photo, voice preference, duration, target platform, tone, key message" all at once. Walk phases in order. Each phase asks at most one or two things at a time.
 
-**Photo is a nudge, not a gate.** Prompt-based avatars work. Offer photo as an optional upgrade for face consistency across videos, not as a required input.
+**For agent avatars: read SOUL.md and IDENTITY.md first, then go straight to prompt-based creation.** Do NOT ask the user for a photo or appearance details first. The agent's identity lives in those workspace files. Only ask the user for traits that are genuinely missing.
+
+**Prompt-based is the default creation path.** Photo is opt-in, only relevant when the user explicitly wants a real-person digital twin of themselves. Agents and named characters almost always use prompt-based creation.
 
 ## Before You Start (Claude Code only)
 
@@ -128,11 +133,15 @@ Start every invocation with:
 
 ### Phase 0 — Who Are We Creating?
 
-Determine the target identity from the request. Do NOT ask the user "whose avatar?" if it's clear from phrasing:
+See the Start Here block above for the default-to-agent rule. Only route to "user" or "named character" when the phrasing is unambiguous.
+
+Routing signals (in priority order):
+
+1. **User** (explicit only) — "create **my** avatar", "make **me** an avatar", "I want my face in a video", "a digital twin of **me**", "based on **my** photo". Requires a possessive pronoun referring to the user OR explicit mention of their photo. Ask for their name if not obvious.
+2. **Named character** (explicit only) — "create an avatar called Cleo", "design a character named X", "build a presenter named Y" → use the given name.
+3. **Agent** (default) — everything else: "create your avatar", "bring yourself to life", "set up an avatar", "let's make an avatar", "create an avatar", "design a presenter", "I want you to appear in videos", or any ambiguous phrasing. Read `IDENTITY.md` for name.
 
-1. **Agent** — "create your avatar", "bring yourself to life", "design an avatar for you" → this is for the agent (Adam, Eve, Claude, etc.). Read `IDENTITY.md` for name.
-2. **User** — "create my avatar", "make me an avatar", "I want my face in a video" → for the user. Ask for their name if not obvious.
-3. **Named character** — "create an avatar called Cleo", "design a character named X" → use the given name.
+**When unsure, default to agent.** Do NOT ask the user for their name, appearance, or voice on an ambiguous request — that's the wrong first move. If after reading IDENTITY.md + SOUL.md the intent still feels ambiguous, ask one short clarifying question to disambiguate (phrase it naturally — something like "quick check: this avatar is for you, or for me?").
 
 Then check `AVATAR-<NAME>.md` at the workspace root:
 
@@ -142,32 +151,34 @@ Then check `AVATAR-<NAME>.md` at the workspace root:
 
 ### Phase 1 — Identity Extraction
 
-**Order matters. Files first, questions second.**
+**Order matters. Files first, questions second. Prompt-based creation is the default path — photo is an opt-in upgrade.**
 
 **For the agent** (Phase 0 target = agent):
 1. Read `SOUL.md`, `IDENTITY.md`, and any existing `AVATAR-<NAME>.md` from the workspace root.
-2. If SOUL.md or IDENTITY.md is found → extract appearance and voice traits silently. Do NOT ask the user "describe your appearance" — the agent IS the subject, and its identity lives in those files. **If the files describe only personality / values with no physical description, do NOT hallucinate traits.** Ask the user conversationally for the missing appearance traits only.
+2. If SOUL.md or IDENTITY.md is found → extract appearance and voice traits silently. Do NOT ask the user "describe your appearance" — the agent IS the subject, and its identity lives in those files. **If the files describe only personality / values with no physical description, do NOT hallucinate traits.** Ask the user conversationally for the missing appearance traits only (one or two at a time).
 3. If neither file is found (e.g., Claude Code environment with no workspace identity) → ask the user to describe the agent's appearance and voice conversationally.
+4. Proceed directly to **Type A (prompt) creation** in Phase 2 by default. Do NOT ask for a photo unless the user volunteers one or explicitly asks for photo realism — agents almost always use prompt-based creation.
 
 **For users/named characters** (Phase 0 target = user or named):
-- Conversational onboarding. Ask naturally about appearance (age, hair, general vibe) and voice (calm/energetic, accent). Not as a form — one or two questions at a time. Communicate in `user_language`.
+- Conversational onboarding. Ask naturally about appearance and voice — one or two questions at a time, not a form. Communicate in `user_language`.
+- **User path only:** after the onboarding Q&A, run the Reference Photo Nudge below.
+- **Named character path:** skip the nudge, go straight to Type A (prompt) creation.
 
 Write `AVATAR-<NAME>.md` with the Appearance and Voice sections filled in. Leave the HeyGen section empty until Phase 2 succeeds.
 
-Then proceed to Phase 2 via the Reference Photo Nudge.
+### Reference Photo Nudge (user path only)
 
-### Reference Photo Nudge (Phase 2 entry)
+Only run this step when Phase 0 target = **user** (real-person digital twin) OR when the user explicitly asks for photo realism.
 
-Ask if they have a reference photo. A photo produces better face consistency across videos, but prompt-based avatars work well when no photo is available. **This is a nudge, not a gate — offer to skip.**
-
-Check first:
-- **For agents:** look at the AVATAR file's Appearance → Reference field, or IDENTITY.md for a photo path. If found, skip asking and use it.
-- **For users:** ask. Keep it one sentence: "Got a headshot? It gives better face consistency, but I can also generate from your description — just say 'skip.'"
+- Check AVATAR file's Appearance → Reference field first. If a photo is already on file, skip asking and use it.
+- Otherwise, ask one sentence: *"Got a headshot? It gives better face consistency for videos of you. I can also generate from your description — just say 'skip.'"*
 
 Branch:
 - **Photo provided** → upload via MCP `upload_asset` or `heygen asset create --file <path>`, then Type B (photo) creation in Phase 2.
 - **Skip** → Type A (prompt) creation in Phase 2.
 
+For agents and named characters, skip this entire step — go straight to Type A (prompt) creation.
+
 
 ### Phase 2 — Avatar Creation
 
PATCH

echo "Gold patch applied."
