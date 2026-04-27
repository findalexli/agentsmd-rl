#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-ai-music-skills

# Idempotency guard
if grep -qF "1. **Load configuration** - Read `~/.bitwize-music/config.yaml` and resolve all " "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -208,16 +208,7 @@ grep -r "<!-- SERVICE:" templates/
 
 At the beginning of a fresh session:
 
-1. **Load configuration** - Read `~/.bitwize-music/config.yaml` and resolve paths:
-   - Set `{content_root}` (where artists/albums live)
-   - Set `{audio_root}` (where mastered audio goes)
-   - Set `{documents_root}` (where PDFs/primary sources go)
-   - If config missing, tell user:
-     ```
-     Config not found. To set up:
-       Option 1: Run /bitwize-music:configure (interactive)
-       Option 2: mkdir -p ~/.bitwize-music && cp config/config.example.yaml ~/.bitwize-music/config.yaml
-     ```
+1. **Load configuration** - Read `~/.bitwize-music/config.yaml` and resolve all path variables (see Path Resolution above). If config missing, tell user to run `/bitwize-music:configure` or copy `config/config.example.yaml`.
 
 1b. **Load overrides (if present)** - Check for user's override files:
    - Read `paths.overrides` from config (default: `{content_root}/overrides`)
@@ -274,40 +265,6 @@ At the beginning of a fresh session:
 
 **Finally, ask:** "What would you like to work on?"
 
-## Resuming Work on an Album
-
-**Trigger**: User says "let's work on [album]" or "continue with [album]" or mentions an album name
-
-**RECOMMENDED: Use `/bitwize-music:resume` skill**
-
-Invoke the resume skill with the album name:
-```
-/bitwize-music:resume my-album
-```
-
-The skill automatically:
-- Reads state cache (`~/.bitwize-music/cache/state.json`) for fast lookup
-- Finds the album by matching `state.albums` keys
-- Checks album and track statuses
-- Determines current workflow phase
-- Updates session context via `indexer.py session`
-- Reports detailed status and next steps
-
-See `/skills/resume/SKILL.md` for full documentation.
-
-**If skill not available - Manual steps:**
-
-1. Read state cache: `~/.bitwize-music/cache/state.json`
-2. Search `state.albums` keys for album name (case-insensitive)
-3. If cache missing: read config, Glob for album, then rebuild cache
-4. Report status and next actions
-
-**Common mistakes to avoid:**
-- ❌ Don't skip the state cache - it's faster than Glob
-- ❌ Don't assume paths - check state cache or read config first
-- ❌ Don't search from current directory - use config paths
-- ✅ Use `/bitwize-music:resume` skill whenever possible
-
 ## Mid-Session Workflow Updates
 
 **When CLAUDE.md or templates are modified during a session**, immediately incorporate those changes into your workflow. Don't wait for a new session.
@@ -358,27 +315,12 @@ You are a co-producer, editor, and creative partner. Push back when ideas don't
 
 **Preserve exact casing and spelling.** If the user says their artist is "bitwize", write "bitwize" - never auto-capitalize to "Bitwize". Same for album names, track titles, and any user-provided text. Their stylistic choices are intentional.
 
-### Watch Your Rhymes
-
-- Don't rhyme the same word twice in consecutive lines
-- Don't rhyme a word with itself
-- Avoid near-repeats (mind/mind, time/time)
-- Check end words before presenting lyrics - fix lazy patterns proactively
-
 ### Automatic Lyrics Review
 
 **After writing or revising any lyrics**, automatically run through:
 1. **Rhyme check**: Repeated end words, self-rhymes, lazy/predictable patterns
 2. **Prosody check**: Stressed syllables align with strong beats (see `/skills/lyric-writer/SKILL.md`)
-3. **Pronunciation check**:
-   - Scan every proper noun (names, places, brands)
-   - Check homographs (live, lead, read, wind, tear, bass, close)
-   - Foreign language names need phonetic spelling (Loh-ray-nah, Gah-yo)
-   - Acronyms spelled out (F-B-I not FBI, G-P-S not GPS)
-   - Tech terms (Lin-ucks not Linux, sequel not SQL)
-   - Numbers (use '93 not ninety-three)
-   - No invented contractions (signal'd, TV'd — spell out instead)
-   - Reference `/reference/suno/pronunciation-guide.md`
+3. **Pronunciation check**: Apply all rules from the Pronunciation section below (proper nouns, homographs, phonetic spelling, acronyms, tech terms, numbers, no invented contractions)
 4. **POV/Tense check**: Consistent point of view and tense throughout
 5. **Source verification**: If source-based, verify lyrics match captured source material
 6. **Structure check**: Section tags present, verse/chorus contrast, V2 develops (not twins V1)
@@ -547,21 +489,6 @@ Skills are optimized for quality where it matters most. On the Claude Code Max s
 
 **Full documentation**: See `/reference/model-strategy.md` for complete rationale for all 38 skills.
 
----
-
-## Quick Reference: Lyric Writing
-
-Use `/bitwize-music:lyric-writer` for full guidance. See `/skills/lyric-writer/SKILL.md` for documentation.
-
-### Key Principles
-
-- **Watch Your Rhymes** - No self-rhymes, no lazy patterns
-- **Automatic Review** - Check rhyme, prosody, POV, tense, pronunciation after every draft
-- **Prosody Matters** - Stressed syllables on strong beats
-- **Show Don't Tell** - Action, imagery, sensory detail
-- **V2 ≠ V1** - Second verse must develop, not twin the first
-
-
 ---
 
 ## Directory Structure
@@ -1000,18 +927,3 @@ Use explicit flag when lyrics contain: fuck, shit, bitch, cunt, cock, dick, puss
 
 **Full guidelines**: See `/reference/distribution.md` for complete formatting rules and explicit word lists.
 
----
-
-## Using Skills for Research
-
-For true-story albums, invoke specialized researcher skills:
-
-| Task | Skill |
-|------|-------|
-| DOJ press releases | `/bitwize-music:researchers-gov` |
-| Court documents | `/bitwize-music:researchers-legal` |
-| Investigative journalism | `/bitwize-music:researchers-journalism` |
-| SEC filings | `/bitwize-music:researchers-financial` |
-| Lyric verification | `/bitwize-music:researchers-verifier` |
-
-Each researcher returns: Source URL, key facts, relevant quotes with citations, discrepancies found.
PATCH

echo "Gold patch applied."
