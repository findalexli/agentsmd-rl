#!/usr/bin/env bash
set -euo pipefail

cd /workspace/nanoclaw

# Idempotency guard
if grep -qF "- **Replace WhatsApp** - Discord will be the only channel (sets DISCORD_ONLY=tru" ".claude/skills/add-discord/SKILL.md" && grep -qF "- **Email Address Pattern** - Emails to a specific address pattern (e.g., andy+t" ".claude/skills/add-gmail/SKILL.md" && grep -qF "AskUserQuestion: I can do deep research on [topic] using Parallel's Task API. Th" ".claude/skills/add-parallel/SKILL.md" && grep -qF "AskUserQuestion: Would you like to add Agent Swarm support? Without it, Agent Te" ".claude/skills/add-telegram/SKILL.md" && grep -qF "If yes, collect it now. If no, direct them to create one at https://platform.ope" ".claude/skills/add-voice-transcription/SKILL.md" && grep -qF "- PLATFORM=macos + APPLE_CONTAINER=installed \u2192 Use `AskUserQuestion: Docker (def" ".claude/skills/setup/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/add-discord/SKILL.md b/.claude/skills/add-discord/SKILL.md
@@ -10,11 +10,15 @@ Read `.nanoclaw/state.yaml`. If `discord` is in `applied_skills`, skip to Phase
 
 ### Ask the user
 
-1. **Mode**: Replace WhatsApp or add alongside it?
-   - Replace → will set `DISCORD_ONLY=true`
-   - Alongside → both channels active (default)
+Use `AskUserQuestion` to collect configuration:
 
-2. **Do they already have a bot token?** If yes, collect it now. If no, we'll create one in Phase 3.
+AskUserQuestion: Should Discord replace WhatsApp or run alongside it?
+- **Replace WhatsApp** - Discord will be the only channel (sets DISCORD_ONLY=true)
+- **Alongside** - Both Discord and WhatsApp channels active
+
+AskUserQuestion: Do you have a Discord bot token, or do you need to create one?
+
+If they have one, collect it now. If not, we'll create one in Phase 3.
 
 ## Phase 2: Apply Code Changes
 
diff --git a/.claude/skills/add-gmail/SKILL.md b/.claude/skills/add-gmail/SKILL.md
@@ -12,21 +12,11 @@ This skill adds Gmail capabilities to NanoClaw. It can be configured in two mode
 
 ## Initial Questions
 
-Ask the user:
+Use `AskUserQuestion` to determine the configuration:
 
-> How do you want to use Gmail with NanoClaw?
->
-> **Option 1: Tool Mode**
-> - Agent can read and send emails when you ask it to
-> - Triggered only from WhatsApp (e.g., "@Andy check my email" or "@Andy send an email to...")
-> - Simpler setup, no email polling
->
-> **Option 2: Channel Mode**
-> - Everything in Tool Mode, plus:
-> - Emails to a specific address/label trigger the agent
-> - Agent replies via email (not WhatsApp)
-> - Can schedule tasks via email
-> - Requires email polling infrastructure
+AskUserQuestion: How do you want to use Gmail with NanoClaw?
+- **Tool Mode** - Agent can read/send emails when triggered from WhatsApp (simpler setup)
+- **Channel Mode** - Emails can trigger the agent, schedule tasks, and receive email replies (requires polling)
 
 Store their choice and proceed to the appropriate section.
 
@@ -283,38 +273,17 @@ Channel Mode includes everything from Tool Mode, plus email polling and routing.
 
 ### Additional Questions for Channel Mode
 
-Ask the user:
+Use `AskUserQuestion` to configure email triggering:
 
-> How should the agent be triggered from email?
->
-> **Option A: Specific Label**
-> - Create a Gmail label (e.g., "NanoClaw")
-> - Emails with this label trigger the agent
-> - You manually label emails or set up Gmail filters
->
-> **Option B: Email Address Pattern**
-> - Emails to a specific address pattern (e.g., andy+task@gmail.com)
-> - Uses Gmail's plus-addressing feature
->
-> **Option C: Subject Prefix**
-> - Emails with a subject starting with a keyword (e.g., "[Andy]")
-> - Anyone can trigger the agent by using the prefix
+AskUserQuestion: How should the agent be triggered from email?
+- **Specific Label** - Create a Gmail label (e.g., "NanoClaw"), emails with this label trigger the agent
+- **Email Address Pattern** - Emails to a specific address pattern (e.g., andy+task@gmail.com) via plus-addressing
+- **Subject Prefix** - Emails with a subject starting with a keyword (e.g., "[Andy]")
 
-Also ask:
-
-> How should email conversations be grouped?
->
-> **Option A: Per Email Thread**
-> - Each email thread gets its own conversation context
-> - Agent remembers the thread history
->
-> **Option B: Per Sender**
-> - All emails from the same sender share context
-> - Agent remembers all interactions with that person
->
-> **Option C: Single Context**
-> - All emails share the main group context
-> - Like an additional input to the main channel
+AskUserQuestion: How should email conversations be grouped?
+- **Per Email Thread** - Each email thread gets its own conversation context
+- **Per Sender** - All emails from the same sender share context
+- **Single Context** - All emails share the main group context
 
 Store their choices for implementation.
 
diff --git a/.claude/skills/add-parallel/SKILL.md b/.claude/skills/add-parallel/SKILL.md
@@ -21,11 +21,10 @@ Run all steps automatically. Only pause for user input when explicitly needed.
 
 ### 1. Get Parallel AI API Key
 
-Ask the user:
-> Do you have a Parallel AI API key, or should I help you get one?
+Use `AskUserQuestion: Do you have a Parallel AI API key, or should I help you get one?`
 
 **If they have one:**
-Ask them to provide it.
+Collect it now.
 
 **If they need one:**
 Tell them:
@@ -168,12 +167,11 @@ You have access to two Parallel AI research tools:
 
 **Speed:** Slower (1-20 minutes depending on depth)
 **Cost:** Higher (varies by processor tier)
-**Permission:** ALWAYS ask the user first before using this tool
+**Permission:** ALWAYS use `AskUserQuestion` before using this tool
 
 **How to ask permission:**
 ```
-I can do deep research on [topic] using Parallel's Task API. This will take
-2-5 minutes and provide comprehensive analysis with citations. Should I proceed?
+AskUserQuestion: I can do deep research on [topic] using Parallel's Task API. This will take 2-5 minutes and provide comprehensive analysis with citations. Should I proceed?
 ```
 
 **After permission - DO NOT BLOCK! Use scheduler instead:**
diff --git a/.claude/skills/add-telegram/SKILL.md b/.claude/skills/add-telegram/SKILL.md
@@ -15,11 +15,15 @@ Read `.nanoclaw/state.yaml`. If `telegram` is in `applied_skills`, skip to Phase
 
 ### Ask the user
 
-1. **Mode**: Replace WhatsApp or add alongside it?
-   - Replace → will set `TELEGRAM_ONLY=true`
-   - Alongside → both channels active (default)
+Use `AskUserQuestion` to collect configuration:
 
-2. **Do they already have a bot token?** If yes, collect it now. If no, we'll create one in Phase 3.
+AskUserQuestion: Should Telegram replace WhatsApp or run alongside it?
+- **Replace WhatsApp** - Telegram will be the only channel (sets TELEGRAM_ONLY=true)
+- **Alongside** - Both Telegram and WhatsApp channels active
+
+AskUserQuestion: Do you have a Telegram bot token, or do you need to create one?
+
+If they have one, collect it now. If not, we'll create one in Phase 3.
 
 ## Phase 2: Apply Code Changes
 
@@ -219,9 +223,9 @@ launchctl load ~/Library/LaunchAgents/com.nanoclaw.plist
 
 ## Agent Swarms (Teams)
 
-After completing the Telegram setup, ask the user:
+After completing the Telegram setup, use `AskUserQuestion`:
 
-> Would you like to add Agent Swarm support? Without it, Agent Teams still work — they just operate behind the scenes. With Swarm support, each subagent appears as a different bot in the Telegram group so you can see who's saying what and have interactive team sessions.
+AskUserQuestion: Would you like to add Agent Swarm support? Without it, Agent Teams still work — they just operate behind the scenes. With Swarm support, each subagent appears as a different bot in the Telegram group so you can see who's saying what and have interactive team sessions.
 
 If they say yes, invoke the `/add-telegram-swarm` skill.
 
diff --git a/.claude/skills/add-voice-transcription/SKILL.md b/.claude/skills/add-voice-transcription/SKILL.md
@@ -15,7 +15,11 @@ Read `.nanoclaw/state.yaml`. If `voice-transcription` is in `applied_skills`, sk
 
 ### Ask the user
 
-1. **Do they have an OpenAI API key?** If yes, collect it now. If no, they'll need to create one at https://platform.openai.com/api-keys.
+Use `AskUserQuestion` to collect information:
+
+AskUserQuestion: Do you have an OpenAI API key for Whisper transcription?
+
+If yes, collect it now. If no, direct them to create one at https://platform.openai.com/api-keys.
 
 ## Phase 2: Apply Code Changes
 
diff --git a/.claude/skills/setup/SKILL.md b/.claude/skills/setup/SKILL.md
@@ -15,7 +15,7 @@ Run setup steps automatically. Only pause when user action is required (WhatsApp
 
 Run `bash setup.sh` and parse the status block.
 
-- If NODE_OK=false → Node.js is missing or too old. Ask the user if they'd like you to install it:
+- If NODE_OK=false → Node.js is missing or too old. Use `AskUserQuestion: Would you like me to install Node.js 22?` If confirmed:
   - macOS: `brew install node@22` (if brew available) or install nvm then `nvm install 22`
   - Linux: `curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash - && sudo apt-get install -y nodejs`, or nvm
   - After installing Node, re-run `bash setup.sh`
@@ -38,14 +38,14 @@ Run `npx tsx setup/index.ts --step environment` and parse the status block.
 Check the preflight results for `APPLE_CONTAINER` and `DOCKER`, and the PLATFORM from step 1.
 
 - PLATFORM=linux → Docker (only option)
-- PLATFORM=macos + APPLE_CONTAINER=installed → Ask user: Docker (default, cross-platform) or Apple Container (native macOS)? If Apple Container, run `/convert-to-apple-container` now, then skip to 3c.
+- PLATFORM=macos + APPLE_CONTAINER=installed → Use `AskUserQuestion: Docker (default, cross-platform) or Apple Container (native macOS)?` If Apple Container, run `/convert-to-apple-container` now, then skip to 3c.
 - PLATFORM=macos + APPLE_CONTAINER=not_found → Docker (default)
 
 ### 3a-docker. Install Docker
 
 - DOCKER=running → continue to 3b
 - DOCKER=installed_not_running → start Docker: `open -a Docker` (macOS) or `sudo systemctl start docker` (Linux). Wait 15s, re-check with `docker info`.
-- DOCKER=not_found → **ask the user for confirmation before installing.** Tell them Docker is required for running agents and ask if they'd like you to install it. If confirmed:
+- DOCKER=not_found → Use `AskUserQuestion: Docker is required for running agents. Would you like me to install it?` If confirmed:
   - macOS: install via `brew install --cask docker`, then `open -a Docker` and wait for it to start. If brew not available, direct to Docker Desktop download at https://docker.com/products/docker-desktop
   - Linux: install with `curl -fsSL https://get.docker.com | sh && sudo usermod -aG docker $USER`. Note: user may need to log out/in for group membership.
 
PATCH

echo "Gold patch applied."
