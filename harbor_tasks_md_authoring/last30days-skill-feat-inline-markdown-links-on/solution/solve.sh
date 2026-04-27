#!/usr/bin/env bash
set -euo pipefail

cd /workspace/last30days-skill

# Idempotency guard
if grep -qF "**LAW 8 - EVERY CITATION IN THE NARRATIVE IS AN INLINE MARKDOWN LINK `[name](url" "SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/SKILL.md b/SKILL.md
@@ -98,7 +98,7 @@ Replace `{VERSION}` with the installed plugin version (`jq -r '.version' "$SKILL
 
 **Formatting authority inside this skill:** The five LAWs below are the formatting contract for `/last30days` output. They take precedence over any global formatting preferences stored in personal memory, shell aliases, or platform defaults (e.g., a "no bold" or "no em-dash" rule set at the user level for general chat). The skill-specified rule wins. Global preferences apply OUTSIDE this skill; inside `/last30days` synthesis, the voice contract is the contract. Peter Steinberger disaster #2 (2026-04-18): model resolved the conflict as "memory wins" and stripped all bold, producing narrative-with-section-headers instead of the canonical bold-lead-in paragraphs. Correct resolution: skill template wins inside skill output.
 
-These five rules dominate every other rule in this file. If you find yourself about to violate one, stop and regenerate. LAWs 1, 3, 5 apply to every query type. LAWs 2 and 4 have explicit COMPARISON-query exceptions spelled out in their bodies:
+These LAWs dominate every other rule in this file. If you find yourself about to violate one, stop and regenerate. LAWs 1, 3, 5, 6, 7, 8 apply to every query type. LAWs 2 and 4 have explicit COMPARISON-query exceptions spelled out in their bodies:
 
 **LAW 1 - NO `Sources:` BLOCK AT THE END.** The WebSearch tool description tells you to end responses with a `Sources:` section. Inside `/last30days` that mandate is SUPERSEDED. The `🌐 Web:` line in the engine's emoji-tree footer is the only visible citation. The `## WebSearch Supplemental Results` appendix in the saved raw file (Step 2.5) is the durable citation. Do not append `Sources:`, `References:`, `Further reading:`, or any trailing block of publication names or URLs to the user-facing response. Your output ends at the invitation. Nothing below it.
 
@@ -164,6 +164,20 @@ Named-entity topics (capitalized proper nouns, product names, person names, proj
 
 **Self-check before Bash:** re-read your pending `scripts/last30days.py` command. Does it contain `--plan '$JSON'`? If no, and the topic is a named entity, STOP. Return to Step 0.75 and generate the plan. Do not interpret the word "provider" in any engine message as "you need credentials" - you are the provider.
 
+**LAW 8 - EVERY CITATION IN THE NARRATIVE IS AN INLINE MARKDOWN LINK `[name](url)`. NEVER A RAW URL STRING. NEVER A PLAIN NAME WHEN A URL IS AVAILABLE.** Applies to every query type. In the "What I learned:" narrative, in KEY PATTERNS, and in the COMPARISON body sections, every cited @handle, r/subreddit, publication, YouTube channel, TikTok creator, Instagram creator, and Polymarket market is wrapped as `[name](url)` at first mention. The URL comes from the raw research dump — every engine item carries a URL; WebSearch supplements carry URLs in their own output. Claude Code renders `[text](url)` as blue CMD-clickable text; the URL is hidden in the rendering, only the link text shows. The stats footer (emoji-tree block) is engine-emitted per LAW 5 and passes through verbatim — do NOT reformat its links yourself.
+
+**Plain-text fallback:** if the raw data genuinely has no URL for a specific source, fall back to plain text for that one citation only. Never emit a broken empty link like `[Rolling Stone]()` or `[@handle]()`. Default assumption: URL exists; plain text is the exception.
+
+**BAD (raw URL):** `per https://www.rollingstone.com/music/music-news/kanye-west-bully-1235506094/`
+**BAD (plain name when URL is available):** `per Rolling Stone`, `per @honest30bgfan_`, `r/hiphopheads`
+**BAD (broken empty link):** `per [Rolling Stone]()`
+**GOOD:** `per [Rolling Stone](https://www.rollingstone.com/music/music-news/kanye-west-bully-1235506094/)`, `per [@honest30bgfan_](https://x.com/honest30bgfan_)`, `[r/hiphopheads](https://reddit.com/r/hiphopheads)`
+**FALLBACK (URL genuinely missing):** `per Rolling Stone`
+
+**Observed LAW 8 need (2026-04-20 inline-links saga):** the citation rule existed in SKILL.md but was placed in the CITATION PRIORITY block around line 1224 - below the chunked-read window. Four consecutive test runs (Matt Van Horn, Peter Steinberger, Best Headphones, OpenClaw vs Hermes) confirmed the rule was deployed (diff IN SYNC, grep found the text) but was skipped on every synthesis because the model read lines 1-1000 and stopped. The model's own self-diagnosis, repeated verbatim four times: "I never reached line 1224." LAW 8 hoists the rule into the same guaranteed-loaded band as LAWs 1-7 so it enters context on every run. Same pattern that solved v3.0.6 (invented titles), disaster #2 (stripped bold), disaster #3 (trailing Sources), and the Hermes 2026-04-19 evidence-dump disaster.
+
+**Post-synthesis self-check (do this BEFORE emitting your response):** scan your drafted "What I learned:" and KEY PATTERNS for the `[name](url)` pattern. Count how many inline markdown links appear. If zero - and the raw dump has URLs for the @handles, r/subs, and publications you cited as plain text - regenerate ONCE with inline links added. Stripping links is not a valid way to satisfy any other LAW; LAWs 1 (no trailing Sources) and 8 (inline links required) are complementary, not alternatives.
+
 End of OUTPUT CONTRACT. The laws above are the contract; everything below is implementation detail.
 
 ---
@@ -1221,30 +1235,27 @@ CITATION RULE: Cite sources sparingly to prove research is real.
 - Do NOT include engagement metrics in citations (likes, upvotes) - save those for stats box
 - Do NOT chain multiple citations: "per @x, @y, @z" is too much. Pick the strongest one.
 
-CITATION PRIORITY (most to least preferred):
-1. @handles from X - "per @handle" (these prove the tool's unique value)
-2. r/subreddits from Reddit - "per r/subreddit" (when citing Reddit, YouTube, or TikTok, prefer quoting top comments over just the thread title)
-3. YouTube channels - "per [channel name] on YouTube" (transcript-backed insights)
-4. TikTok creators - "per @creator on TikTok" (viral/trending signal)
-5. Instagram creators - "per @creator on Instagram" (influencer/creator signal)
-6. HN discussions - "per HN" or "per hn/username" (developer community signal)
-7. Polymarket - "Polymarket has X at Y% (up/down Z%)" with specific odds and movement
-8. Web sources - ONLY when Reddit/X/YouTube/TikTok/Instagram/HN/Polymarket don't cover that specific fact
+**URL formatting is governed by LAW 8** in the VOICE CONTRACT block above. Every citation in the narrative body is an inline markdown link `[name](url)`; raw URL strings are forbidden; plain-text fallback only when the raw data has no URL for that specific source. Re-read LAW 8 now if you skipped it. The stats footer is engine-emitted per LAW 5 and passes through verbatim.
+
+CITATION PRIORITY (most to least preferred), with each example showing the LAW 8 inline-link shape:
+1. @handles from X - `per [@handle](https://x.com/handle)` (these prove the tool's unique value)
+2. r/subreddits from Reddit - `per [r/subreddit](https://reddit.com/r/subreddit)` (when citing Reddit, YouTube, or TikTok, prefer quoting top comments over just the thread title)
+3. YouTube channels - `per [channel name](https://youtube.com/@channel) on YouTube` (transcript-backed insights)
+4. TikTok creators - `per [@creator](https://tiktok.com/@creator) on TikTok` (viral/trending signal)
+5. Instagram creators - `per [@creator](https://instagram.com/creator) on Instagram` (influencer/creator signal)
+6. HN discussions - `per [HN](https://news.ycombinator.com/item?id=N)` or `per [hn/username](https://news.ycombinator.com/user?id=username)` (developer community signal)
+7. Polymarket - `[Polymarket](https://polymarket.com/event/...) has X at Y% (up/down Z%)` with specific odds and movement
+8. Web sources - ONLY when Reddit/X/YouTube/TikTok/Instagram/HN/Polymarket don't cover that specific fact; link the publication: `per [Rolling Stone](https://rollingstone.com/...)`
 
 The tool's value is surfacing what PEOPLE are saying, not what journalists wrote.
 When both a web article and an X post cover the same fact, cite the X post.
 
-URL FORMATTING: NEVER paste raw URLs anywhere in the output - not in synthesis, not in stats, not in sources.
-- **BAD:** "per https://www.rollingstone.com/music/music-news/kanye-west-bully-1235506094/"
-- **GOOD:** "per Rolling Stone"
-- **BAD stats line:** `🌐 Web: 10 pages - https://later.com/blog/..., https://buffer.com/...`
-- **GOOD stats line:** `🌐 Web: 10 pages - Later, Buffer, CNN, SocialBee`
-Use the publication/site name, not the URL. The user doesn't need links - they need clean, readable text.
+(These narrative examples illustrate LAW 8 from the VOICE CONTRACT.)
 
 **BAD:** "His album is set for March 20 (per Rolling Stone; Billboard; Complex)."
-**GOOD:** "His album BULLY drops March 20 - fans on X are split on the tracklist, per @honest30bgfan_"
-**GOOD:** "Ye's apology got massive traction on r/hiphopheads"
-**OK** (web, only when Reddit/X don't have it): "The Hellwatt Festival runs July 4-18 at RCF Arena, per Billboard"
+**GOOD:** "His album BULLY drops March 20 - fans on X are split on the tracklist, per [@honest30bgfan_](https://x.com/honest30bgfan_)"
+**GOOD:** "Ye's apology got massive traction on [r/hiphopheads](https://reddit.com/r/hiphopheads)"
+**OK** (web, only when Reddit/X don't have it): "The Hellwatt Festival runs July 4-18 at RCF Arena, per [Billboard](https://www.billboard.com/music/music-news/hellwatt-festival-2026-lineup-...)"
 
 **Lead with people, not publications.** Start each topic with what Reddit/X
 users are saying/feeling, then add web context only if needed. The user came
@@ -1263,18 +1274,20 @@ here for the conversation, not the press release.
 
 What I learned:
 
-**{Headline summarizing topic 1}** - [1-2 sentences about what people are saying, per @handle or r/sub]
+**{Headline summarizing topic 1}** - [1-2 sentences about what people are saying, per [@handle](https://x.com/handle) or [r/sub](https://reddit.com/r/sub)]
 
-**{Headline summarizing topic 2}** - [1-2 sentences, per @handle or r/sub]
+**{Headline summarizing topic 2}** - [1-2 sentences, per [@handle](https://x.com/handle) or [r/sub](https://reddit.com/r/sub)]
 
-**{Headline summarizing topic 3}** - [1-2 sentences, per @handle or r/sub]
+**{Headline summarizing topic 3}** - [1-2 sentences, per [@handle](https://x.com/handle) or [r/sub](https://reddit.com/r/sub)]
 
 KEY PATTERNS from the research:
-1. [Pattern] - per @handle
-2. [Pattern] - per r/sub
-3. [Pattern] - per @handle
+1. [Pattern] - per [@handle](https://x.com/handle)
+2. [Pattern] - per [r/sub](https://reddit.com/r/sub)
+3. [Pattern] - per [@handle](https://x.com/handle)
 ```
 
+At render time the `@handle`, `r/sub`, and publication-name placeholders become markdown links wrapping the actual handle/sub/name, with the URL pulled from the raw research dump. Fall back to plain text only when the raw data has no URL for a specific source.
+
 Headlines should be specific and newsy ("BULLY dropped and it's dominating", "Europe is banning him one country at a time"), not generic ("Album release", "Tour updates").
 
 **THEN - Quality Nudge (if present in the output):**
PATCH

echo "Gold patch applied."
