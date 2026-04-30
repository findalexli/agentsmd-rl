#!/usr/bin/env bash
set -euo pipefail

cd /workspace/skills

# Idempotency guard
if grep -qF "5. **Don't batch-ask across skills.** When a request triggers both skills (\"use " "SKILL.md" && grep -qF "2. If SOUL.md or IDENTITY.md is found \u2192 extract appearance and voice traits sile" "heygen-avatar/SKILL.md" && grep -qF "**DO NOT batch-ask all of these at once.** Ask one or two items at a time. Most " "heygen-video/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/SKILL.md b/SKILL.md
@@ -98,6 +98,8 @@ Every command supports `--help`. Full reference: [../references/api-reference.md
 2. **No internal jargon.** Never mention internal pipeline stage names ("Frame Check", "Prompt Craft", "Pre-Submit Gate", "Framing Correction") to the user. These are internal pipeline stages. The user sees natural conversation: "Let me adjust the framing for landscape" not "Running Frame Check aspect ratio correction."
 3. **Polling is silent.** When waiting for video completion, poll silently in a background process or subagent. Do NOT send repeated "Checking status..." messages. Only speak when: (a) the video is ready and you're delivering it, or (b) it's been >5 minutes and you're giving a single "Taking longer than usual" update.
 4. **Deliver clean.** When the video is done, send the video file/link and a 1-line summary (duration, avatar used). Not a dump of every API field.
+5. **Don't batch-ask across skills.** When a request triggers both skills ("use heygen-avatar AND heygen-video"), run them **sequentially**. Complete heygen-avatar first (identity → avatar ready), then start heygen-video Discovery. Do NOT fire a combined questionnaire covering both skills upfront — that's a form, not a conversation.
+6. **Read workspace files before asking.** `SOUL.md`, `IDENTITY.md`, and `AVATAR-<NAME>.md` at the workspace root contain identity and existing avatar state. Check them first. Only ask the user for what's genuinely missing.
 
 ---
 
diff --git a/heygen-avatar/SKILL.md b/heygen-avatar/SKILL.md
@@ -23,6 +23,14 @@ allowed-tools: Bash, WebFetch, Read, Write, mcp__heygen__*
 
 Create and manage HeyGen avatars for anyone: the agent, the user, or named characters. Handles identity extraction, avatar generation, voice selection, and saves everything to `AVATAR-<NAME>.md` for consistent reuse.
 
+## Start Here (Critical)
+
+**Do NOT batch-ask questions.** Do not fire "give me a photo, voice preference, duration, target platform, tone, key message" all at once. Walk phases in order. Each phase asks at most one or two things at a time.
+
+**When creating for the agent itself** ("create your avatar", "bring yourself to life"), do NOT ask the user for a photo or appearance details first. Read `SOUL.md` and `IDENTITY.md` from the workspace root. The agent's identity lives there. Only ask the user for traits that are genuinely missing from those files.
+
+**Photo is a nudge, not a gate.** Prompt-based avatars work. Offer photo as an optional upgrade for face consistency across videos, not as a required input.
+
 ## Before You Start (Claude Code only)
 
 Try to read `SOUL.md` from the workspace root.
@@ -112,40 +120,50 @@ Start every invocation with:
 
 ## Workflow
 
+**DO NOT batch-ask questions upfront.** Walk phases in order. Each phase asks at most one thing at a time, and only if needed.
+
 ### Phase 0 — Who Are We Creating?
 
-Determine the target identity:
+Determine the target identity from the request. Do NOT ask the user "whose avatar?" if it's clear from phrasing:
+
+1. **Agent** — "create your avatar", "bring yourself to life", "design an avatar for you" → this is for the agent (Adam, Eve, Claude, etc.). Read `IDENTITY.md` for name.
+2. **User** — "create my avatar", "make me an avatar", "I want my face in a video" → for the user. Ask for their name if not obvious.
+3. **Named character** — "create an avatar called Cleo", "design a character named X" → use the given name.
 
-1. **Agent** — user says "create your avatar", "bring yourself to life" → read IDENTITY.md for name, then check `AVATAR-<NAME>.md`. If IDENTITY.md is not found (Claude Code environment), walk the user through designing from scratch with a few quick questions about appearance and voice.
-2. **User** — user says "create my avatar", "make me an avatar" → ask for their name, check `AVATAR-<NAME>.md`
-3. **Named character** — user says "create an avatar called Cleo" → check `AVATAR-CLEO.md`
+Then check `AVATAR-<NAME>.md` at the workspace root:
 
-If the AVATAR file exists and has a HeyGen section filled in:
-> "You already have an avatar set up. Want to add a new look, update it, or start fresh?"
+- **AVATAR file exists + HeyGen section filled in** → "You already have an avatar set up. Want to add a new look, update it, or start fresh?" Wait for answer.
+- **AVATAR file exists but HeyGen section empty** → skip to Phase 2.
+- **No AVATAR file** → proceed to Phase 1.
 
-If the AVATAR file exists but HeyGen section is empty: proceed to Reference Photo Nudge.
-If no AVATAR file exists: proceed to Phase 1.
+### Phase 1 — Identity Extraction
 
-### Reference Photo Nudge (First-Time Only)
+**Order matters. Files first, questions second.**
 
-Before generating anything, ask if they have a reference image. Photo avatars produce significantly better face consistency across videos than prompt-generated ones.
+**For the agent** (Phase 0 target = agent):
+1. Read `SOUL.md`, `IDENTITY.md`, and any existing `AVATAR-<NAME>.md` from the workspace root.
+2. If SOUL.md or IDENTITY.md is found → extract appearance and voice traits silently. Do NOT ask the user "describe your appearance" — the agent IS the subject, and its identity lives in those files. **If the files describe only personality / values with no physical description, do NOT hallucinate traits.** Ask the user conversationally for the missing appearance traits only.
+3. If neither file is found (e.g., Claude Code environment with no workspace identity) → ask the user to describe the agent's appearance and voice conversationally.
 
-Ask if they have a reference photo, explaining that a headshot or clear face photo gives much better results than text-only generation. Offer to skip for prompt-based creation. Communicate in `user_language`.
+**For users/named characters** (Phase 0 target = user or named):
+- Conversational onboarding. Ask naturally about appearance (age, hair, general vibe) and voice (calm/energetic, accent). Not as a form — one or two questions at a time. Communicate in `user_language`.
 
-This applies to ALL targets (agent, user, named character). For agents, check if a reference photo path already exists in the AVATAR file's Appearance section or in IDENTITY.md before asking.
+Write `AVATAR-<NAME>.md` with the Appearance and Voice sections filled in. Leave the HeyGen section empty until Phase 2 succeeds.
 
-- **Photo provided** → upload via `heygen asset create --file <path>` (or MCP equivalent), then use Type B (photo) creation in Phase 2
-- **Skip** → use Type A (prompt) creation in Phase 2
+Then proceed to Phase 2 via the Reference Photo Nudge.
 
-### Phase 1 — Identity Extraction
+### Reference Photo Nudge (Phase 2 entry)
 
-**For the agent:** Try to read `SOUL.md`, `IDENTITY.md`, and existing `AVATAR-<NAME>.md` from the workspace. If found, extract appearance and voice traits automatically. If not found (e.g. Claude Code environment), skip to conversational onboarding — ask the user to describe the agent's appearance and voice instead.
+Ask if they have a reference photo. A photo produces better face consistency across videos, but prompt-based avatars work well when no photo is available. **This is a nudge, not a gate — offer to skip.**
 
-**For users/named characters:** Conversational onboarding. Ask naturally about their appearance (age, hair, general vibe) and voice (calm, energetic, accent). Not as a form — be conversational. Communicate in `user_language`.
+Check first:
+- **For agents:** look at the AVATAR file's Appearance → Reference field, or IDENTITY.md for a photo path. If found, skip asking and use it.
+- **For users:** ask. Keep it one sentence: "Got a headshot? It gives better face consistency, but I can also generate from your description — just say 'skip.'"
 
-Write `AVATAR-<NAME>.md` with the Appearance and Voice sections filled in. Leave HeyGen section empty.
+Branch:
+- **Photo provided** → upload via MCP `upload_asset` or `heygen asset create --file <path>`, then Type B (photo) creation in Phase 2.
+- **Skip** → Type A (prompt) creation in Phase 2.
 
-Then proceed to the **Reference Photo Nudge** before Phase 2.
 
 ### Phase 2 — Avatar Creation
 
diff --git a/heygen-video/SKILL.md b/heygen-video/SKILL.md
@@ -82,6 +82,8 @@ Default to Full Producer. Better to ask one smart question than generate a medio
 
 Interview the user. Be conversational, skip anything already answered.
 
+**DO NOT batch-ask all of these at once.** Ask one or two items at a time. Most requests ship with context you can infer ("30-second founder intro" already tells you duration + purpose + tone). Only ask what's genuinely missing. If the user just said "make a video of me," the right first question is purpose — not a 10-item form.
+
 **Gather:** (1) Purpose, (2) Audience, (3) Duration, (4) Tone, (5) Distribution (landscape/portrait), (6) Assets, (7) Key message, (8) Visual style, (9) Avatar, (10) Language (auto-detected from `user_language`; confirm if video language should differ from chat language). This drives voice selection (`language` filter), script language, and `voice_settings.locale`.
 
 ### Assets
PATCH

echo "Gold patch applied."
