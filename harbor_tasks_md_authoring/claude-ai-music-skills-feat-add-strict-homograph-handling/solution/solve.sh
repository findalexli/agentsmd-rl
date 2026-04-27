#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-ai-music-skills

# Idempotency guard
if grep -qF "**Homograph handling \u2014 hard rule**: Suno CANNOT infer pronunciation from context" "CLAUDE.md" && grep -qF "Suno CANNOT infer pronunciation from context. **\"Context is clear\" is NEVER an a" "skills/lyric-writer/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -381,10 +381,6 @@ Report all issues with proposed fixes, then proceed.
 - Base guide: `/reference/suno/pronunciation-guide.md` (universal rules, common homographs, tech terms)
 - Override guide: `{overrides}/pronunciation-guide.md` (artist names, album-specific terms) - optional, merged at session start
 
-**Mandatory**: When using "live" in lyrics, ask which pronunciation (LYVE vs LIV).
-
-**Common homographs**: read, lead, wind, close, tear, bass
-
 **Always use phonetic spelling** for tricky words in the Lyrics Box:
 
 | Type | Example | Write As |
@@ -396,6 +392,13 @@ Report all issues with proposed fixes, then proceed.
 | Numbers | ninety-three, sixty-three | '93, '63 |
 | Homographs | live (verb) | lyve or liv |
 
+**Homograph handling — hard rule**: Suno CANNOT infer pronunciation from context. "Context is clear" is NEVER an acceptable resolution. When any homograph is found (live, read, lead, wound, close, bass, tear, wind, etc.):
+1. **ASK** the user which pronunciation is intended — do NOT assume or guess
+2. **Fix** with phonetic spelling in Suno lyrics only (streaming lyrics keep standard spelling)
+3. **Document** in track pronunciation table
+
+See `/skills/lyric-writer/SKILL.md` for full homograph table and process.
+
 ---
 
 ## Skills (Slash Commands)
diff --git a/skills/lyric-writer/SKILL.md b/skills/lyric-writer/SKILL.md
@@ -449,10 +449,6 @@ Before finalizing:
 
 ## Pronunciation
 
-**Mandatory**: When using "live" in lyrics, ask which pronunciation (LYVE vs LIV).
-
-**Common homographs**: read, lead, wind, close, tear, bass
-
 **Always use phonetic spelling** for tricky words:
 
 | Type | Example | Write As |
@@ -463,6 +459,36 @@ Before finalizing:
 | Numbers | ninety-three | '93 |
 | Homographs | live (verb) | lyve or liv |
 
+### Homograph Handling (Suno Pronunciation)
+
+Suno CANNOT infer pronunciation from context. **"Context is clear" is NEVER an acceptable resolution for a homograph.**
+
+**Process:**
+1. **Identify**: Flag any word with multiple pronunciations during phonetic review
+2. **ASK**: Ask the user which pronunciation is intended — do NOT assume
+3. **Fix**: Replace with phonetic spelling in Suno lyric lines only (streaming lyrics keep standard spelling)
+4. **Document**: Add to track pronunciation table with reason
+
+**Common homographs — ALWAYS ask, NEVER guess:**
+
+| Word | Pronunciation A | Phonetic | Pronunciation B | Phonetic |
+|------|----------------|----------|-----------------|----------|
+| live | real-time/broadcast | lyve | reside/exist | live |
+| read | present tense | reed | past tense | red |
+| lead | to guide | leed | metal | led |
+| wound | injury | woond | past of wind | wownd |
+| close | to shut | kloze | nearby | klohs |
+| bass | low sound | bayss | the fish | bas |
+| tear | from crying | teer | to rip | tare |
+| wind | air movement | wihnd | to turn | wynd |
+
+**Rules:**
+- NEVER mark a homograph as "context clear" in the phonetic checklist
+- ALWAYS ask the user when a homograph is encountered — do not guess
+- Only apply phonetic spelling to Suno lyrics — streaming/distributor lyrics use standard English
+- When in doubt, it's a homograph. Ask.
+- Full homograph reference: `/reference/suno/pronunciation-guide.md`
+
 ---
 
 ## Documentary Standards
PATCH

echo "Gold patch applied."
