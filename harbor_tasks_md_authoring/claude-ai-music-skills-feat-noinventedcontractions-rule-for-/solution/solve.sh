#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-ai-music-skills

# Idempotency guard
if grep -qF "- No invented contractions (signal'd, TV'd \u2014 spell out instead)" "CLAUDE.md" && grep -qF "Suno only recognizes standard English contractions. Never use made-up contractio" "skills/lyric-writer/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -377,6 +377,7 @@ You are a co-producer, editor, and creative partner. Push back when ideas don't
    - Acronyms spelled out (F-B-I not FBI, G-P-S not GPS)
    - Tech terms (Lin-ucks not Linux, sequel not SQL)
    - Numbers (use '93 not ninety-three)
+   - No invented contractions (signal'd, TV'd — spell out instead)
    - Reference `/reference/suno/pronunciation-guide.md`
 4. **POV/Tense check**: Consistent point of view and tense throughout
 5. **Source verification**: If source-based, verify lyrics match captured source material
diff --git a/skills/lyric-writer/SKILL.md b/skills/lyric-writer/SKILL.md
@@ -51,7 +51,7 @@ You are a professional lyric writer with expertise in prosody, rhyme craft, and
 **After writing or revising any lyrics**, automatically run through:
 1. **Rhyme check**: Repeated end words, self-rhymes, lazy patterns
 2. **Prosody check**: Stressed syllables align with strong beats
-3. **Pronunciation check**: Proper nouns, homographs, acronyms, tech terms
+3. **Pronunciation check**: Proper nouns, homographs, acronyms, tech terms, invented contractions (no noun'd/brand'd)
 4. **POV/Tense check**: Consistent throughout
 5. **Source verification**: If source-based, match captured material
 6. **Structure check**: Section tags, verse/chorus contrast, V2 develops
@@ -549,6 +549,7 @@ Before finalizing:
 - [ ] Too many proper nouns in a single verse (max 3 introductions per verse)
 - [ ] Density mismatch (Musical Direction says "laid back" but verses are packed)
 - [ ] Chorus lead-in repeats chorus (last line before chorus duplicates hook phrase or rhyme word)
+- [ ] Invented contractions (signal'd, TV'd — Suno only handles standard pronoun/auxiliary contractions)
 
 ---
 
@@ -594,6 +595,18 @@ Suno CANNOT infer pronunciation from context. **"Context is clear" is NEVER an a
 - When in doubt, it's a homograph. Ask.
 - Full homograph reference: `/reference/suno/pronunciation-guide.md`
 
+### No Invented Contractions (Suno)
+
+Suno only recognizes standard English contractions. Never use made-up contractions by appending 'd, 'll, etc. to nouns, brand names, or non-standard words.
+
+**Standard (OK for Suno):** they'd, he'd, you'd, she'd, we'd, I'd, wouldn't, couldn't, shouldn't
+
+**Invented (will break Suno):** signal'd, TV'd, network'd, podcast'd, channel'd
+
+**Fix:** Spell it out — "signal would" not "signal'd", "TV could" not "TV'd"
+
+**Rule:** If the base word isn't a pronoun or standard auxiliary verb, don't contract it. Suno will mispronounce or skip invented contractions.
+
 ---
 
 ## Documentary Standards
PATCH

echo "Gold patch applied."
