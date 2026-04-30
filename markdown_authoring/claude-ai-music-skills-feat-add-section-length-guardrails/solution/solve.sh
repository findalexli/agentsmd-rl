#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-ai-music-skills

# Idempotency guard
if grep -qF "7. **Section length check**: Count lines per section, compare against genre limi" "CLAUDE.md" && grep -qF "7. **Section length check**: Count lines per section, compare against genre limi" "skills/lyric-writer/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -349,7 +349,8 @@ You are a co-producer, editor, and creative partner. Push back when ideas don't
 4. **POV/Tense check**: Consistent point of view and tense throughout
 5. **Source verification**: If source-based, verify lyrics match captured source material
 6. **Structure check**: Section tags present, verse/chorus contrast, V2 develops (not twins V1)
-7. **Pitfalls check**: Run through Lyric Pitfalls Checklist (see `/skills/lyric-writer/SKILL.md`)
+7. **Section length check**: Count lines per section, compare against genre limits in `/skills/lyric-writer/SKILL.md`. **Hard fail** — trim any section exceeding its genre max before presenting.
+8. **Pitfalls check**: Run through Lyric Pitfalls Checklist (see `/skills/lyric-writer/SKILL.md`)
 
 Report any violations found. Don't wait to be asked.
 
diff --git a/skills/lyric-writer/SKILL.md b/skills/lyric-writer/SKILL.md
@@ -55,7 +55,8 @@ You are a professional lyric writer with expertise in prosody, rhyme craft, and
 4. **POV/Tense check**: Consistent throughout
 5. **Source verification**: If source-based, match captured material
 6. **Structure check**: Section tags, verse/chorus contrast, V2 develops
-7. **Pitfalls check**: Run through checklist
+7. **Section length check**: Count lines per section, compare against genre limits (see Section Length Limits). **Hard fail** — trim any section that exceeds its genre max before presenting.
+8. **Pitfalls check**: Run through checklist
 
 Report any violations found. Don't wait to be asked.
 
@@ -218,6 +219,137 @@ Songs that are too long (800+ words) cause Suno to rush, compress sections, or s
 - **If draft exceeds 350 words (non-hip-hop) or 500 words (hip-hop)**: Cut it down before presenting.
 - Count words after drafting. If over target, remove a verse or trim sections — don't just shorten lines.
 
+### Section Length Limits by Genre
+
+**Why this matters**: Suno rushes, compresses, or skips content when sections are too long. These are hard limits — trim before presenting.
+
+#### Hip-Hop / Rap / Trap / Drill / Grime / Phonk / Nerdcore
+
+| Section | Max Lines | Notes |
+|---------|-----------|-------|
+| Verse | 8 | Standard 16-bar verse (each written line ≈ 2 bars) |
+| Chorus / Hook | 4–6 | Shorter hooks hit harder |
+| Bridge | 4–6 | |
+| Pre-Chorus | 2–4 | |
+| Outro | Flexible | Spoken word / ad-lib sections exempt |
+
+#### Pop / Synth-Pop / Dance-Pop / K-Pop / Piano Pop
+
+| Section | Max Lines | Notes |
+|---------|-----------|-------|
+| Verse | 6–8 | |
+| Chorus | 4–6 | |
+| Bridge | 4 | |
+| Pre-Chorus | 2–4 | |
+
+#### Rock / Alt-Rock / Indie Rock / Grunge / Garage Rock / Post-Rock / Prog Rock
+
+| Section | Max Lines | Notes |
+|---------|-----------|-------|
+| Verse | 6–8 | |
+| Chorus | 4–6 | |
+| Bridge | 4 | |
+| Pre-Chorus | 2–4 | |
+| Guitar solo / Interlude | 0 (instrumental) | Use `[Guitar Solo]` or `[Interlude]` tag |
+
+#### Punk / Hardcore Punk / Emo / Pop-Punk / Ska Punk
+
+| Section | Max Lines | Notes |
+|---------|-----------|-------|
+| Verse | 4–6 | Short, fast — keep it tight |
+| Chorus | 2–4 | Punchy, shoutable |
+| Bridge | 2–4 | |
+| Pre-Chorus | 2 | |
+
+#### Metal / Thrash / Doom / Black Metal / Metalcore / Industrial
+
+| Section | Max Lines | Notes |
+|---------|-----------|-------|
+| Verse | 4–8 | |
+| Chorus | 4–6 | |
+| Bridge | 4 | |
+| Pre-Chorus | 2–4 | |
+| Breakdown | 2–4 | Often instrumental or minimal lyrics |
+
+#### Country / Folk / Americana / Bluegrass / Singer-Songwriter / Blues
+
+| Section | Max Lines | Notes |
+|---------|-----------|-------|
+| Verse | 4–8 | Storytelling verses can use the full 8 |
+| Chorus | 4–6 | |
+| Bridge | 2–4 | |
+| Pre-Chorus | 2–4 | |
+
+#### Electronic / EDM / House / Techno / Trance / Dubstep / DnB / Synthwave
+
+| Section | Max Lines | Notes |
+|---------|-----------|-------|
+| Verse | 4–6 | Vocals are sparse in electronic — less is more |
+| Chorus / Hook | 2–4 | Often just a repeated phrase |
+| Bridge | 2–4 | |
+| Drop | 0 (instrumental) | Use `[Drop]` or `[Break]` tag |
+
+#### Ambient / Lo-Fi / Chillwave / Trip-Hop / Vaporwave
+
+| Section | Max Lines | Notes |
+|---------|-----------|-------|
+| Verse | 2–4 | Minimal vocals, atmosphere first |
+| Chorus / Hook | 2–4 | |
+| Bridge | 2 | |
+
+#### R&B / Soul / Funk / Gospel
+
+| Section | Max Lines | Notes |
+|---------|-----------|-------|
+| Verse | 6–8 | |
+| Chorus | 4–6 | |
+| Bridge | 4 | |
+| Pre-Chorus | 2–4 | |
+| Vamp / Ad-lib | Flexible | Outro vamps are genre-standard |
+
+#### Jazz / Swing / Bossa Nova
+
+| Section | Max Lines | Notes |
+|---------|-----------|-------|
+| Verse | 4–8 | Standard 32-bar form |
+| Chorus | 4–6 | |
+| Bridge | 4–8 | Jazz B-sections can run longer |
+
+#### Reggae / Dancehall / Afrobeats
+
+| Section | Max Lines | Notes |
+|---------|-----------|-------|
+| Verse | 4–8 | |
+| Chorus / Hook | 4–6 | |
+| Bridge | 2–4 | |
+| Toast / DJ | 4–8 | Dancehall toasting sections |
+
+#### Ballad (any genre)
+
+| Section | Max Lines | Notes |
+|---------|-----------|-------|
+| Verse | 4–6 | Slower tempo = fewer lines needed |
+| Chorus | 4–6 | |
+| Bridge | 2–4 | |
+
+### Section Length Enforcement
+
+**Hard rules — enforce before presenting lyrics:**
+
+1. **Count lines per section** after drafting. Compare against genre table above.
+2. **If a section exceeds its max**: Trim it. Don't ask — cut it down, then present.
+3. **Hip-hop verse over 8 lines**: Split into two verses or cut. No exceptions.
+4. **Any chorus over 6 lines**: Trim. A long chorus loses its punch and causes Suno to rush.
+5. **Electronic verse over 6 lines**: Cut. Electronic tracks need space, not walls of text.
+6. **Punk sections over limits**: Punk is short and fast. If it's long, it's not punk.
+7. **When unsure about genre**: Use the Pop/Rock defaults (6–8 verse, 4–6 chorus, 4 bridge).
+
+**Suno-specific reasoning**: Long sections cause:
+- Vocal rushing (cramming words into fixed musical time)
+- Loss of clarity (words blur together)
+- Section compression (Suno shortens the music to fit)
+- Skipped lyrics (Suno drops lines entirely)
+
 ---
 
 ## Point of View & Tense
@@ -246,6 +378,7 @@ Before finalizing:
 - [ ] Twin verses (V2 = V1 reworded)
 - [ ] No hook
 - [ ] Disingenuous voice
+- [ ] Section too long for genre (check Section Length Limits table)
 
 ---
 
PATCH

echo "Gold patch applied."
