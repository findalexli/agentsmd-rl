#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-ai-music-skills

# Idempotency guard
if grep -qF "| **Opus 4.5** | `claude-opus-4-5-20251101` | Music-defining output, high error " "CLAUDE.md" && grep -qF "1. **Load override first** - Read config for overrides path, then check `{overri" "skills/lyric-writer/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -448,7 +448,7 @@ Skills are optimized for quality where it matters most:
 
 | Tier | Model | When to Use | Examples |
 |------|-------|-------------|----------|
-| **Opus 4.5** | `claude-opus-4-5-20251101` | Music-defining output, high error cost (6 skills) | lyric-writer, suno-engineer, album-conceptualizer, lyric-reviewer |
+| **Opus 4.5** | `claude-opus-4-5-20251101` | Music-defining output, high error cost (6 skills) | lyric-writer, suno-engineer, album-conceptualizer, lyric-reviewer, researchers-legal, researchers-verifier |
 | **Sonnet 4.5** | `claude-sonnet-4-5-20250929` | Reasoning and coordination (21 skills) | researcher, pronunciation-specialist, explicit-checker |
 | **Haiku 4.5** | `claude-haiku-4-5-20251001` | Rule-based operations (11 skills) | validate-album, test, imports, clipboard |
 
diff --git a/skills/lyric-writer/SKILL.md b/skills/lyric-writer/SKILL.md
@@ -187,7 +187,7 @@ These apply universally regardless of genre:
 Before finalizing any lyrics, verify:
 1. Read each rhyming pair aloud — do the end words actually rhyme (per genre expectations)?
 2. Are there any orphan lines that should rhyme with something but don't?
-3. Is syllable count roughly consistent across corresponding lines? (±2 for pop/rock/country, ±3 for hip-hop, flexible for metal/electronic)
+3. Is syllable count roughly consistent across corresponding lines? (see tolerance in Line Length table)
 4. Are there filler phrases ("spoke the words", "you know what I mean") padding lines?
 5. Do quoted/paraphrased lines come from sourced material (for documentary albums)?
 6. Does the rhyme scheme match the genre? (Don't use AABB couplets for a folk ballad, don't use ABCB for hip-hop)
@@ -232,7 +232,7 @@ Before finalizing any lyrics, verify:
 | Energy | Building | Peak |
 | Detail | Specific sensory | Abstract emotional |
 
-### No Verse-Chorus Echo (Phrase Deduplication)
+### No Verse-Chorus Echo
 
 A verse must never repeat a key phrase, image, or rhyme word that appears in the chorus it leads into. The chorus is the hook — if the verse already said it, the chorus loses its impact.
 
@@ -281,11 +281,12 @@ Good:
 ## Line Length
 
 ### General Ranges by Genre
-| Genre | Syllables/Line |
-|-------|----------------|
-| Pop/Folk/Punk | 6-8 |
-| Rock/Indie | 8-10 |
-| Hip-Hop/Rap | 10-13+ |
+| Genre | Syllables/Line | Tolerance |
+|-------|----------------|-----------|
+| Pop/Folk/Punk | 6-8 | ±2 |
+| Rock/Indie | 8-10 | ±2 |
+| Hip-Hop/Rap | 10-13+ | ±3 |
+| Metal/Electronic | Varies | Flexible |
 
 **Critical**: Verse 1 line lengths must match Verse 2 line lengths.
 
@@ -330,7 +331,7 @@ Songs that are too long (800+ words) cause Suno to rush, compress sections, or s
 | Chorus / Hook | 4–6 | Shorter hooks hit harder |
 | Bridge | 4–6 | |
 | Pre-Chorus | 2–4 | |
-| Outro | Flexible | Spoken word / ad-lib sections exempt |
+| Outro | 2–4 | Spoken word / ad-lib sections exempt from limit |
 
 #### Pop / Synth-Pop / Dance-Pop / K-Pop / Piano Pop
 
@@ -698,7 +699,7 @@ As the lyric writer, you:
 
 ## Remember
 
-1. **Load override first** - Check for `{overrides}/lyric-writing-guide.md` at invocation
+1. **Load override first** - Read config for overrides path, then check `{overrides}/lyric-writing-guide.md`
 2. **Watch your rhymes** - No self-rhymes, no lazy patterns
 3. **Prosody matters** - Stressed syllables on strong beats
 4. **Show don't tell** - Action, imagery, sensory detail
PATCH

echo "Gold patch applied."
