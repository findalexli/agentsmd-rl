#!/usr/bin/env bash
set -euo pipefail

cd /workspace/nanoclaw

# Idempotency guard
if grep -qF "description: Format messages for Slack using mrkdwn syntax. Use when responding " "container/skills/slack-formatting/SKILL.md" && grep -qF "Format messages based on the channel you're responding to. Check your group fold" "groups/global/CLAUDE.md" && grep -qF "Use Slack mrkdwn syntax. Run `/slack-formatting` for the full reference. Key rul" "groups/main/CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/container/skills/slack-formatting/SKILL.md b/container/skills/slack-formatting/SKILL.md
@@ -0,0 +1,94 @@
+---
+name: slack-formatting
+description: Format messages for Slack using mrkdwn syntax. Use when responding to Slack channels (folder starts with "slack_" or JID contains slack identifiers).
+---
+
+# Slack Message Formatting (mrkdwn)
+
+When responding to Slack channels, use Slack's mrkdwn syntax instead of standard Markdown.
+
+## How to detect Slack context
+
+Check your group folder name or workspace path:
+- Folder starts with `slack_` (e.g., `slack_engineering`, `slack_general`)
+- Or check `/workspace/group/` path for `slack_` prefix
+
+## Formatting reference
+
+### Text styles
+
+| Style | Syntax | Example |
+|-------|--------|---------|
+| Bold | `*text*` | *bold text* |
+| Italic | `_text_` | _italic text_ |
+| Strikethrough | `~text~` | ~strikethrough~ |
+| Code (inline) | `` `code` `` | `inline code` |
+| Code block | ` ```code``` ` | Multi-line code |
+
+### Links and mentions
+
+```
+<https://example.com|Link text>     # Named link
+<https://example.com>                # Auto-linked URL
+<@U1234567890>                       # Mention user by ID
+<#C1234567890>                       # Mention channel by ID
+<!here>                              # @here
+<!channel>                           # @channel
+```
+
+### Lists
+
+Slack supports simple bullet lists but NOT numbered lists:
+
+```
+• First item
+• Second item
+• Third item
+```
+
+Use `•` (bullet character) or `- ` or `* ` for bullets.
+
+### Block quotes
+
+```
+> This is a block quote
+> It can span multiple lines
+```
+
+### Emoji
+
+Use standard emoji shortcodes: `:white_check_mark:`, `:x:`, `:rocket:`, `:tada:`
+
+## What NOT to use
+
+- **NO** `##` headings (use `*Bold text*` for headers instead)
+- **NO** `**double asterisks**` for bold (use `*single asterisks*`)
+- **NO** `[text](url)` links (use `<url|text>` instead)
+- **NO** `1.` numbered lists (use bullets with numbers: `• 1. First`)
+- **NO** tables (use code blocks or plain text alignment)
+- **NO** `---` horizontal rules
+
+## Example message
+
+```
+*Daily Standup Summary*
+
+_March 21, 2026_
+
+• *Completed:* Fixed authentication bug in login flow
+• *In Progress:* Building new dashboard widgets
+• *Blocked:* Waiting on API access from DevOps
+
+> Next sync: Monday 10am
+
+:white_check_mark: All tests passing | <https://ci.example.com/builds/123|View Build>
+```
+
+## Quick rules
+
+1. Use `*bold*` not `**bold**`
+2. Use `<url|text>` not `[text](url)`
+3. Use `•` bullets, avoid numbered lists
+4. Use `:emoji:` shortcodes
+5. Quote blocks with `>`
+6. Skip headings — use bold text instead
diff --git a/groups/global/CLAUDE.md b/groups/global/CLAUDE.md
@@ -49,10 +49,28 @@ When you learn something important:
 
 ## Message Formatting
 
-NEVER use markdown. Only use WhatsApp/Telegram formatting:
-- *single asterisks* for bold (NEVER **double asterisks**)
-- _underscores_ for italic
-- • bullet points
-- ```triple backticks``` for code
+Format messages based on the channel you're responding to. Check your group folder name:
 
-No ## headings. No [links](url). No **double stars**.
+### Slack channels (folder starts with `slack_`)
+
+Use Slack mrkdwn syntax. Run `/slack-formatting` for the full reference. Key rules:
+- `*bold*` (single asterisks)
+- `_italic_` (underscores)
+- `<https://url|link text>` for links (NOT `[text](url)`)
+- `•` bullets (no numbered lists)
+- `:emoji:` shortcodes
+- `>` for block quotes
+- No `##` headings — use `*Bold text*` instead
+
+### WhatsApp/Telegram channels (folder starts with `whatsapp_` or `telegram_`)
+
+- `*bold*` (single asterisks, NEVER **double**)
+- `_italic_` (underscores)
+- `•` bullet points
+- ` ``` ` code blocks
+
+No `##` headings. No `[links](url)`. No `**double stars**`.
+
+### Discord channels (folder starts with `discord_`)
+
+Standard Markdown works: `**bold**`, `*italic*`, `[links](url)`, `# headings`.
diff --git a/groups/main/CLAUDE.md b/groups/main/CLAUDE.md
@@ -43,15 +43,33 @@ When you learn something important:
 - Split files larger than 500 lines into folders
 - Keep an index in your memory for the files you create
 
-## WhatsApp Formatting (and other messaging apps)
+## Message Formatting
 
-Do NOT use markdown headings (##) in WhatsApp messages. Only use:
-- *Bold* (single asterisks) (NEVER **double asterisks**)
-- _Italic_ (underscores)
-- • Bullets (bullet points)
-- ```Code blocks``` (triple backticks)
+Format messages based on the channel. Check the group folder name prefix:
 
-Keep messages clean and readable for WhatsApp.
+### Slack channels (folder starts with `slack_`)
+
+Use Slack mrkdwn syntax. Run `/slack-formatting` for the full reference. Key rules:
+- `*bold*` (single asterisks)
+- `_italic_` (underscores)
+- `<https://url|link text>` for links (NOT `[text](url)`)
+- `•` bullets (no numbered lists)
+- `:emoji:` shortcodes like `:white_check_mark:`, `:rocket:`
+- `>` for block quotes
+- No `##` headings — use `*Bold text*` instead
+
+### WhatsApp/Telegram (folder starts with `whatsapp_` or `telegram_`)
+
+- `*bold*` (single asterisks, NEVER **double**)
+- `_italic_` (underscores)
+- `•` bullet points
+- ` ``` ` code blocks
+
+No `##` headings. No `[links](url)`. No `**double stars**`.
+
+### Discord (folder starts with `discord_`)
+
+Standard Markdown: `**bold**`, `*italic*`, `[links](url)`, `# headings`.
 
 ---
 
PATCH

echo "Gold patch applied."
