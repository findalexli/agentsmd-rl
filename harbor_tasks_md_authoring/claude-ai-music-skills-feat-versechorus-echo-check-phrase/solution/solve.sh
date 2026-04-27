#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-ai-music-skills

# Idempotency guard
if grep -qF "11. **Verse-chorus echo check**: Compare last 2 lines of every verse against fir" "CLAUDE.md" && grep -qF "11. **Verse-chorus echo check**: Compare last 2 lines of every verse against fir" "skills/lyric-writer/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -386,7 +386,7 @@ You are a co-producer, editor, and creative partner. Push back when ideas don't
 8. **Rhyme scheme check**: Verify rhyme scheme matches the genre (see `/skills/lyric-writer/SKILL.md` Default Rhyme Schemes by Genre). No orphan lines, no random scheme switches mid-verse.
 9. **Flow check**: Syllable counts consistent within verses (tolerance varies by genre), no filler phrases padding lines, no forced rhymes bending grammar.
 10. **Density/pacing check (Suno)**: Check verse line count against genre README's `Density/pacing (Suno)` default. Flag any verse exceeding the genre's max lines/verse. Cross-reference BPM/mood from Musical Direction. **Hard fail** — trim or split any verse over the limit before presenting.
-11. **Chorus lead-in check**: Compare the last line before each chorus against the chorus opening. Flag if they share key phrases, rhyme words, or restate the hook. The chorus is the payoff — the lead-in should set it up, not pre-deliver it.
+11. **Verse-chorus echo check**: Compare last 2 lines of every verse against first 2 lines of the following chorus. Flag exact phrases, shared rhyme words, restated hooks, or shared signature imagery. Check ALL verse-to-chorus and bridge-to-chorus transitions. The chorus is the payoff — the verse should set it up, not pre-deliver it.
 12. **Pitfalls check**: Run through Lyric Pitfalls Checklist (see `/skills/lyric-writer/SKILL.md`)
 
 Report any violations found. Don't wait to be asked.
diff --git a/skills/lyric-writer/SKILL.md b/skills/lyric-writer/SKILL.md
@@ -59,7 +59,7 @@ You are a professional lyric writer with expertise in prosody, rhyme craft, and
 8. **Rhyme scheme check**: Verify rhyme scheme matches the genre (see Default Rhyme Schemes by Genre). No orphan lines, no random scheme switches mid-verse. Read each rhyming pair aloud.
 9. **Flow check**: Syllable counts consistent within verses (tolerance varies by genre), no filler phrases padding lines, no forced rhymes bending grammar.
 10. **Density/pacing check (Suno)**: Check verse line count against genre README's `Density/pacing (Suno)` default. Flag any verse exceeding the genre's max. Cross-reference BPM/mood from Musical Direction. **Hard fail** — trim or split any verse over the limit.
-11. **Chorus lead-in check**: Compare the last line before each chorus against the chorus opening. Flag if they share key phrases, rhyme words, or restate the hook.
+11. **Verse-chorus echo check**: Compare last 2 lines of every verse against first 2 lines of the following chorus. Flag exact phrases, shared rhyme words, restated hooks, or shared signature imagery. Check ALL verse-to-chorus and bridge-to-chorus transitions.
 12. **Pitfalls check**: Run through checklist
 
 Report any violations found. Don't wait to be asked.
@@ -232,21 +232,31 @@ Before finalizing any lyrics, verify:
 | Energy | Building | Peak |
 | Detail | Specific sensory | Abstract emotional |
 
-### Chorus Lead-In Rule
+### No Verse-Chorus Echo (Phrase Deduplication)
 
-The line immediately before a chorus must NOT repeat key phrases from the chorus itself. The chorus is the payoff — if the preceding line already said it, the chorus lands flat.
+A verse must never repeat a key phrase, image, or rhyme word that appears in the chorus it leads into. The chorus is the hook — if the verse already said it, the chorus loses its impact.
 
-**What to check:**
-- Compare the last line of each verse/section that precedes a chorus
-- Look for repeated words, phrases, or rhyme endings that duplicate the chorus opening
-- This applies to ALL instances — first chorus, second chorus, final chorus
+**What to check** — before finalizing any track, compare:
+1. The last 2 lines of every verse/section that precedes a chorus
+2. The first 2 lines of the chorus
+
+Flag any of these overlaps:
+- **Exact phrase**: Same words appear in both (e.g., "digital heart" / "digital heart")
+- **Same rhyme word**: Verse ends on "start," chorus opens on "start"
+- **Restated hook**: Verse paraphrases the chorus hook in different words
+- **Shared imagery**: Verse uses the chorus's signature image (e.g., both say "warehouse")
 
 **Red flags:**
-- Last line of verse ends with the same phrase the chorus opens with
-- Last line of verse uses the same rhyme word as the chorus first line
-- Last line restates the chorus hook in slightly different words
+- Last line of verse contains ANY phrase from the chorus first line
+- A signature chorus word (the hook word) appears anywhere in the preceding verse
+- The verse "gives away" the chorus before it hits
+
+**Fix:**
+1. Rewrite the verse line to use DIFFERENT imagery that SETS UP the chorus
+2. The verse should create tension or expectation — the chorus resolves it
+3. Complementary, not redundant: verse says "spark," chorus says "start"
 
-**Fix:** Rewrite the lead-in to SET UP the chorus without SAYING it. Use complementary imagery — the verse closes one thought, the chorus opens the next. The lead-in should make you WANT the chorus, not pre-deliver it.
+**Scope:** This applies to EVERY verse-to-chorus transition in the track, not just the first one. Check all of them. Also check bridge-to-chorus transitions.
 
 **Example:**
 
@@ -548,7 +558,7 @@ Before finalizing:
 - [ ] 8-line verse at BPM under 100 (too dense for Suno — split or trim)
 - [ ] Too many proper nouns in a single verse (max 3 introductions per verse)
 - [ ] Density mismatch (Musical Direction says "laid back" but verses are packed)
-- [ ] Chorus lead-in repeats chorus (last line before chorus duplicates hook phrase or rhyme word)
+- [ ] Verse-chorus echo (verse repeats chorus phrase, rhyme word, hook, or signature imagery)
 - [ ] Invented contractions (signal'd, TV'd — Suno only handles standard pronoun/auxiliary contractions)
 
 ---
PATCH

echo "Gold patch applied."
