#!/usr/bin/env bash
set -euo pipefail

cd /workspace/nanoclaw

# Idempotency guard
if grep -qF "**UX Note:** When asking the user questions, prefer using the `AskUserQuestion` " ".claude/skills/setup/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/setup/SKILL.md b/.claude/skills/setup/SKILL.md
@@ -7,6 +7,8 @@ description: Run initial NanoClaw setup. Use when user wants to install dependen
 
 Run all commands automatically. Only pause when user action is required (scanning QR codes).
 
+**UX Note:** When asking the user questions, prefer using the `AskUserQuestion` tool instead of just outputting text. This integrates with Claude's built-in question/answer system for a better experience.
+
 ## 1. Install Dependencies
 
 ```bash
@@ -171,7 +173,43 @@ If they choose something other than `Andy`, update it in these places:
 
 Store their choice - you'll use it when creating the registered_groups.json and when telling them how to test.
 
-## 7. Register Main Channel
+## 7. Understand the Security Model
+
+Before registering your main channel, you need to understand an important security concept.
+
+**Use the AskUserQuestion tool** to present this:
+
+> **Important: Your "main" channel is your admin control portal.**
+>
+> The main channel has elevated privileges:
+> - Can see messages from ALL other registered groups
+> - Can manage and delete tasks across all groups
+> - Can write to global memory that all groups can read
+> - Has read-write access to the entire NanoClaw project
+>
+> **Recommendation:** Use your personal "Message Yourself" chat or a solo WhatsApp group as your main channel. This ensures only you have admin control.
+>
+> **Question:** Which setup will you use for your main channel?
+>
+> Options:
+> 1. Personal chat (Message Yourself) - Recommended
+> 2. Solo WhatsApp group (just me)
+> 3. Group with other people (I understand the security implications)
+
+If they choose option 3, ask a follow-up:
+
+> You've chosen a group with other people. This means everyone in that group will have admin privileges over NanoClaw.
+>
+> Are you sure you want to proceed? The other members will be able to:
+> - Read messages from your other registered chats
+> - Schedule and manage tasks
+> - Access any directories you've mounted
+>
+> Options:
+> 1. Yes, I understand and want to proceed
+> 2. No, let me use a personal chat or solo group instead
+
+## 8. Register Main Channel
 
 Ask the user:
 > Do you want to use your **personal chat** (message yourself) or a **WhatsApp group** as your main control channel?
@@ -215,7 +253,7 @@ Ensure the groups folder exists:
 mkdir -p groups/main/logs
 ```
 
-## 8. Configure External Directory Access (Mount Allowlist)
+## 9. Configure External Directory Access (Mount Allowlist)
 
 Ask the user:
 > Do you want the agent to be able to access any directories **outside** the NanoClaw project?
@@ -242,7 +280,7 @@ Skip to the next step.
 
 If **yes**, ask follow-up questions:
 
-### 8a. Collect Directory Paths
+### 9a. Collect Directory Paths
 
 Ask the user:
 > Which directories do you want to allow access to?
@@ -259,14 +297,14 @@ For each directory they provide, ask:
 > Read-write is needed for: code changes, creating files, git commits
 > Read-only is safer for: reference docs, config examples, templates
 
-### 8b. Configure Non-Main Group Access
+### 9b. Configure Non-Main Group Access
 
 Ask the user:
 > Should **non-main groups** (other WhatsApp chats you add later) be restricted to **read-only** access even if read-write is allowed for the directory?
 >
 > Recommended: **Yes** - this prevents other groups from modifying files even if you grant them access to a directory.
 
-### 8c. Create the Allowlist
+### 9c. Create the Allowlist
 
 Create the allowlist file based on their answers:
 
@@ -322,7 +360,7 @@ Tell the user:
 > }
 > ```
 
-## 9. Configure launchd Service
+## 10. Configure launchd Service
 
 Generate the plist file with correct paths automatically:
 
PATCH

echo "Gold patch applied."
