#!/usr/bin/env bash
set -euo pipefail

cd /workspace/marketingskills

# Idempotency guard
if grep -qF "Turn one piece of content into many. The best social content isn't created from " "skills/social-content/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/social-content/SKILL.md b/skills/social-content/SKILL.md
@@ -2,7 +2,7 @@
 name: social-content
 description: "When the user wants help creating, scheduling, or optimizing social media content for LinkedIn, Twitter/X, Instagram, TikTok, Facebook, or other platforms. Also use when the user mentions 'LinkedIn post,' 'Twitter thread,' 'social media,' 'content calendar,' 'social scheduling,' 'engagement,' 'viral content,' 'what should I post,' 'repurpose this content,' 'tweet ideas,' 'LinkedIn carousel,' 'social media strategy,' or 'grow my following.' Use this for any social media content creation, repurposing, or scheduling task. For broader content strategy, see content-strategy."
 metadata:
-  version: 1.1.0
+  version: 1.2.0
 ---
 
 # Social Content
@@ -107,7 +107,7 @@ The first line determines whether anyone reads the rest.
 
 ## Content Repurposing System
 
-Turn one piece of content into many:
+Turn one piece of content into many. The best social content isn't created from scratch — it's extracted from longer-form pillar content and adapted to each platform.
 
 ### Blog Post → Social Content
 
@@ -119,13 +119,61 @@ Turn one piece of content into many:
 | Instagram | Carousel with visuals |
 | Instagram | Reel summarizing the post |
 
+### Podcast / Video → Social Content
+
+Extract "content atoms" — self-contained moments from any long-form content that work on their own:
+
+| Atom Type | What to Look For | Best Platform |
+|-----------|-----------------|---------------|
+| Quotable moment | A bold claim, hot take, or memorable line (15-60 sec) | Twitter/X, LinkedIn, TikTok |
+| Story arc | A complete mini-story with setup, conflict, resolution (60-90 sec) | Instagram Reels, TikTok, YouTube Shorts |
+| Tactical tip | A specific how-to or framework explained clearly (30-60 sec) | LinkedIn, YouTube Shorts |
+| Controversial take | A contrarian opinion that sparks debate | Twitter/X, LinkedIn |
+| Data/stat callout | A surprising number or research finding | LinkedIn carousel, Twitter/X |
+| Behind-the-scenes | Authentic, unpolished moments | Instagram Stories, TikTok |
+
+**Podcast repurposing workflow:**
+1. **Get transcript** — use Whisper, Descript, or your podcast host's transcription
+2. **Mark timestamps** — flag the 5-10 best moments while listening or scanning transcript
+3. **Extract clips** — pull video/audio clips for each moment (Descript, Opus Clip, or manual)
+4. **Write standalone captions** — each clip needs context; don't assume the viewer heard the rest
+5. **Add subtitles** — most social video is watched without sound
+6. **Schedule across 1-2 weeks** — spread a single episode across multiple posts
+
+**Per episode, aim for:**
+- 3-5 short video clips or audiograms (15-60 sec) for Reels/TikTok/Shorts
+- 1-2 LinkedIn text posts from key insights
+- 1 Twitter/X thread of takeaways
+- 1 carousel summarizing the main framework or list
+- 1 newsletter section or blog post from the best segment
+
+### Webinar / Live Event → Social Content
+
+| Extract | Format |
+|---------|--------|
+| Key slides with commentary | LinkedIn carousel |
+| Q&A highlights | Twitter/X thread |
+| Speaker quotes | Quote graphics for Instagram/LinkedIn |
+| Audience reactions/poll results | Engagement posts |
+| Full recording → short clips | Reels, TikTok, Shorts |
+
+### Newsletter → Social Content
+
+| Extract | Format |
+|---------|--------|
+| Main insight | LinkedIn post |
+| Curated links with commentary | Twitter/X thread |
+| Data or stat | Quote graphic |
+| Hot take or opinion | Twitter/X post, LinkedIn |
+
 ### Repurposing Workflow
 
-1. **Create pillar content** (blog, video, podcast)
-2. **Extract key insights** (3-5 per piece)
-3. **Adapt to each platform** (format and tone)
-4. **Schedule across the week** (spread distribution)
-5. **Update and reshare** (evergreen content can repeat)
+1. **Create pillar content** (blog, video, podcast, webinar, newsletter)
+2. **Extract content atoms** (5-10 per piece — quotes, stories, tips, data)
+3. **Adapt to each platform** (format, length, and tone)
+4. **Write standalone captions** (each post must work without context)
+5. **Schedule across the week** (spread distribution, don't dump all at once)
+6. **Update and reshare** (evergreen content can repeat every 3-6 months)
 
 ---
 
PATCH

echo "Gold patch applied."
