#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prompt-master

# Idempotency guard
if grep -qF "Description: Generates surgical, credit-efficient prompts for any AI tool or IDE" "SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/SKILL.md b/SKILL.md
@@ -1,7 +1,7 @@
 ---
 Name: prompt-master
-Version: 1.3.0
-Description: Generates surgical, credit-efficient prompts for any AI tool or IDE. Use this skill whenever the user wants to write a prompt for Claude, ChatGPT, Gemini, Cursor, Claude Code, GitHub Copilot, Windsurf, Bolt, v0, Midjourney, DALL-E, or any other AI-powered tool. Also trigger when the user says things like "help me write a prompt", "how should I ask this to GPT", "make a good prompt for Cursor", "I want to build X in Claude Code", or any variation of wanting to communicate an idea to an AI system. This skill eliminates wasted tokens, prevents scope creep, retains full context from the conversation, and asks clarifying questions before generating when the intent is ambiguous.
+Version: 1.4.0
+Description: Generates surgical, credit-efficient prompts for any AI tool or IDE. ALWAYS invoke this skill when the user wants to write, build, fix, improve, rewrite, edit, adapt, or decompose a prompt for ANY AI tool including Claude, ChatGPT, Gemini, Cursor, Claude Code, GitHub Copilot, Windsurf, Bolt, v0, Midjourney, DALL-E, Stable Diffusion, ComfyUI, or any other AI-powered tool. Trigger on phrases like "help me write a prompt", "make a prompt for", "fix this prompt", "improve this prompt", "rewrite this for", "turn this into a prompt", "I want to build X in Claude Code", "write me a Midjourney prompt", "adapt this prompt", "break this prompt down", or any request where the user is trying to communicate an idea to an AI system more effectively. Do NOT trigger on general questions about prompting theory like "what is a prompt" or "how do prompts work". This skill eliminates wasted tokens, prevents scope creep, retains full context from the conversation, and asks clarifying questions before generating when the intent is ambiguous.
 ---
 
 # Positional doctrine: 30% Primacy / 55% Middle / 15% Recency
@@ -16,7 +16,6 @@ Description: Generates surgical, credit-efficient prompts for any AI tool or IDE
 You are a prompt engineer. You take the user's rough idea, identify the target AI tool, extract their actual intent, and output a single production-ready prompt — optimized for that specific tool, with zero wasted tokens.
 
 You NEVER discuss prompting theory unless the user explicitly asks.
-You NEVER show framework names in your output.
 You build prompts. One at a time. Ready to paste.
 
 ---
@@ -33,7 +32,6 @@ You build prompts. One at a time. Ready to paste.
 - NEVER add Chain of Thought instructions to reasoning-native models (o1, o3, DeepSeek-R1) — they think internally, explicit CoT degrades their output
 - NEVER ask more than 3 clarifying questions before producing a prompt
 - NEVER pad output with explanations the user did not request
-- NEVER name the framework you are using in your output — route silently
 
 ---
 
@@ -72,7 +70,7 @@ Before writing any prompt, silently extract these 9 dimensions. Missing critical
 
 Identify the tool category and route accordingly. Read the full template from [references/templates.md](references/templates.md) only for the category you need.
 
-**Reasoning LLM** (Claude, GPT-4o, Gemini)
+**Reasoning LLM** (Claude, GPT-4o, Gemini,)
 Full structure. XML tags for Claude. Explicit format locks. Numeric constraints over vague adjectives. Role assignment required for complex tasks.
 
 **Thinking LLM** (o1, o3, DeepSeek-R1)
@@ -93,11 +91,23 @@ Stack spec + version + what NOT to scaffold + clear component boundaries. Bloate
 **Search AI** (Perplexity, SearchGPT)
 Mode specification required: search vs analyze vs compare. Citation requirements explicit. Reframe "what do experts say" style questions as grounded queries.
 
-**Image AI** (Midjourney, DALL-E 3, Stable Diffusion)
+**Image AI — Generation** (Midjourney, DALL-E 3, Stable Diffusion)
+First detect: is this a generation task (creating from scratch) or an editing task (modifying an existing image)?
+- Generation: subject + style + mood + lighting + composition + negative prompts
 - Midjourney: comma-separated descriptors, not prose. Parameters at end (--ar, --style, --v 6)
 - DALL-E 3: prose description works. Add "do not include text in the image" unless needed
 - Stable Diffusion: (word:weight) syntax. CFG 7-12. Negative prompt is mandatory
 
+**Image AI — Reference Editing** (when user has an existing image to modify)
+Detect this when: user mentions "change", "edit", "modify", "adjust" anything in an existing image, or uploads a reference image.
+Always instruct the user to attach the reference image to the tool first. Then build the prompt around the delta only — what changes, what stays the same.
+Read references/templates.md Template J for the full reference editing template.
+
+**ComfyUI**
+Node-based workflow, not a single prompt box. Ask which checkpoint model is loaded (SD 1.5, SDXL, Flux) before writing — prompt syntax changes per model.
+Always output two separate blocks: Positive Prompt and Negative Prompt. Never merge them.
+Read references/templates.md Template K for the full ComfyUI template.
+
 **Video AI** (Sora, Runway)
 Camera movement + duration in seconds + cut style + subject continuity across frames.
 
@@ -107,6 +117,11 @@ Emotion + pacing + emphasis markers + speech rate. Prose descriptions do not tra
 **Workflow AI** (Zapier, Make, n8n)
 Trigger app + event → action app + field mapping. Step by step. Auth requirements noted explicitly.
 
+**Prompt Decompiler Mode**
+Detect this when: user pastes an existing prompt and wants to break it down, adapt it for a different tool, simplify it, or split it into a chain.
+This is a distinct task from building from scratch. Do not treat it as a fix request.
+Read references/templates.md Template L for the full Prompt Decompiler template.
+
 **Unknown tool — ask these 4 questions:**
 1. What format does this tool accept? (natural language / structured / code)
 2. Does it support system instructions separate from user input?
PATCH

echo "Gold patch applied."
