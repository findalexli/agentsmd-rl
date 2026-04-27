#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-ai-music-skills

# Idempotency guard
if grep -qF "| **Opus 4.5** | `claude-opus-4-5-20251101` | Music-defining output, high error " "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -38,11 +38,6 @@ This reads the state cache, finds the album, and provides a detailed status repo
 - ❌ Don't assume the path - always check state cache or read config first
 - ❌ Don't use `ls` or `find` commands
 
-**CORRECT APPROACH:**
-- ✅ Check state cache (`~/.bitwize-music/cache/state.json`) FIRST
-- ✅ Fall back to config + Glob if cache missing
-- ✅ Rebuild cache after Glob fallback
-
 ---
 
 ## Configuration
@@ -279,29 +274,13 @@ At the beginning of a fresh session:
 
 1. **Fix the immediate issue** in the current track/file
 2. **Sweep the album** for the same issue in other tracks
-3. **Draft a rule** — specific, actionable, with examples
+3. **Draft a rule** — specific, actionable, with what went wrong + before/after examples
 4. **Present to user**: "I found [issue]. Here's a rule to prevent this: [rule]. Should I add it to [location]?"
-5. **Log the lesson** — add the rule to the appropriate file (SKILL.md, CLAUDE.md, genre README, or reference doc)
-
-### What Qualifies
-
-- Pronunciation errors Suno got wrong (add to pronunciation guide)
-- Rhyme pattern violations that slipped through review
-- Formatting issues that caused generation problems
-- Assumptions that turned out wrong for a genre/style
-- Manual corrections that should be automated checks
-
-### Rule Format
+5. **Log the lesson** — add to the appropriate file (SKILL.md, CLAUDE.md, genre README, or reference doc)
 
-When proposing a rule, include:
-- **What went wrong**: The specific issue encountered
-- **Why it matters**: Impact on output quality
-- **The rule**: Clear, actionable instruction
-- **Examples**: Before/after showing the fix
+**Qualifies**: Pronunciation errors, rhyme violations, formatting issues, wrong assumptions, manual corrections that should be automated.
 
-### Key Principle
-
-**Be proactive.** When you correct something manually, ask yourself: "Should this be a rule?" If the answer is yes, propose it immediately. Don't wait to be asked.
+**Be proactive.** When you correct something manually, ask: "Should this be a rule?" If yes, propose it immediately.
 
 ---
 
@@ -463,31 +442,15 @@ Skills can update their own reference documentation when new issues are discover
 
 ### Model Strategy
 
-Skills are optimized for quality where it matters most. On the Claude Code Max subscription plan, use the best model for critical creative outputs.
-
-**Opus 4.5 (`claude-opus-4-5-20251101`)** - Music-defining output and high error cost (6 skills):
-- `/bitwize-music:lyric-writer` - Core content, storytelling, prosody
-- `/bitwize-music:suno-engineer` - Music generation prompts
-- `/bitwize-music:album-conceptualizer` - Album concept shapes everything downstream
-- `/bitwize-music:lyric-reviewer` - QC gate before generation, must catch all issues
-- `/bitwize-music:researchers-legal` - Complex legal document synthesis
-- `/bitwize-music:researchers-verifier` - High-stakes quality control
-
-**Sonnet 4.5 (`claude-sonnet-4-5-20250929`)** - Reasoning and coordination (21 skills):
-- `/bitwize-music:researcher` - Research coordination
-- `/bitwize-music:pronunciation-specialist` - Edge cases need judgment (homographs, context)
-- `/bitwize-music:explicit-checker` - Context matters for content decisions
-- All other creative and reasoning tasks
+Skills are optimized for quality where it matters most:
 
-**Haiku 4.5 (`claude-haiku-4-5-20251001`)** - Rule-based operations (11 skills):
-- `/bitwize-music:validate-album` - Structure validation
-- `/bitwize-music:test` - Runs predefined checks
-- `/bitwize-music:skill-model-updater` - Pattern matching and replacement
-- Import skills, clipboard, help, about, new-album
+| Tier | Model | When to Use | Examples |
+|------|-------|-------------|----------|
+| **Opus 4.5** | `claude-opus-4-5-20251101` | Music-defining output, high error cost (6 skills) | lyric-writer, suno-engineer, album-conceptualizer, lyric-reviewer |
+| **Sonnet 4.5** | `claude-sonnet-4-5-20250929` | Reasoning and coordination (21 skills) | researcher, pronunciation-specialist, explicit-checker |
+| **Haiku 4.5** | `claude-haiku-4-5-20251001` | Rule-based operations (11 skills) | validate-album, test, imports, clipboard |
 
-**The rule**: Opus for output that defines the music or has high error cost. Sonnet for tasks needing judgment. Haiku for mechanical operations.
-
-**Full documentation**: See `/reference/model-strategy.md` for complete rationale for all 38 skills.
+**Full skill-to-model mapping**: See `/reference/model-strategy.md`
 
 ---
 
@@ -675,18 +638,16 @@ Example: `/bitwize-music:new-album my-album rock`
 
 ---
 
-## Ready to Generate Checkpoint
-
-**Trigger**: When all track lyrics are written for an album
+## Workflow Checkpoints
 
-**Actions:**
-1. Review all track statuses
-2. Verify all tracks have: complete lyrics, phonetic review complete, Suno boxes filled, sources verified (if applicable)
-3. Run explicit content check: `/bitwize-music:explicit-checker [album-path]`
-4. Run phonetic check on all tracks
-5. Present summary to user
+All checkpoint message templates: See `/reference/workflows/checkpoint-scripts.md`
 
-**Message template**: See `/reference/workflows/checkpoint-scripts.md`
+| Checkpoint | Trigger | Key Actions |
+|------------|---------|-------------|
+| **Ready to Generate** | All track lyrics written | Review statuses, verify Suno boxes filled, run `/bitwize-music:explicit-checker`, phonetic check |
+| **Generation Complete** | All tracks have Suno Links | Verify all `Generated`, Suno Links present, Generation Log has keepers (✓) |
+| **Ready to Master** | User says "album approved" | Update statuses to `Final`, album to `Complete`, verify WAV files downloaded |
+| **Ready to Release** | Mastering + album art done | Review Album Completion Checklist, verify all items checked |
 
 ---
 
@@ -696,40 +657,10 @@ Example: `/bitwize-music:new-album my-album rock`
 
 **Stop when**: Correct vocals, good pronunciation, proper structure, acceptable quality. Don't chase perfection.
 
-**Approach**: Sequential (recommended) or batch, user's choice.
-
 **Reference**: `/bitwize-music:suno-engineer` or `/reference/suno/v5-best-practices.md`
 
 ---
 
-## Album Generation Complete Checkpoint
-
-**Trigger**: When all tracks marked `Generated` with Suno Links
-
-**Actions:**
-1. Verify all tracks have Status: `Generated`
-2. Verify all Suno Links present and working
-3. Check Generation Log - all tracks have keeper marked with ✓
-4. Present track status summary
-
-**Message template**: See `/reference/workflows/checkpoint-scripts.md`
-
----
-
-## Ready to Master Checkpoint
-
-**Trigger**: User says "album approved" after QA review
-
-**Actions:**
-1. Update all track statuses from `Generated` to `Final`
-2. Update album status to `Complete`
-3. Verify user has WAV files downloaded from Suno
-4. Guide to mastering workflow
-
-**Message template**: See `/reference/workflows/checkpoint-scripts.md`
-
----
-
 ## Status Tracking
 
 ### Track Statuses
@@ -796,19 +727,6 @@ When you find a keeper: Set Status to `Generated`, add Suno Link.
 
 ---
 
-## Ready to Release Checkpoint
-
-**Trigger**: After mastering complete and album art generated
-
-**Actions:**
-1. Review Album Completion Checklist
-2. Verify all items checked
-3. Present final status with checklist summary
-
-**Message template**: See `/reference/workflows/checkpoint-scripts.md`
-
----
-
 ## Releasing an Album
 
 **Steps**: Verify Album Completion Checklist → Update album README (`release_date` and `Status: Released`) → Upload to platforms → Add URLs to README
PATCH

echo "Gold patch applied."
