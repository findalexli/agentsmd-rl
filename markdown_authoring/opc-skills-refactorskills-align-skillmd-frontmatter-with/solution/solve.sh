#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opc-skills

# Idempotency guard
if grep -qF "description: Create banners using AI image generation. Discuss format/style, gen" "skills/banner-creator/SKILL.md" && grep -qF "description: Search domains, compare prices, find promo codes, get purchase reco" "skills/domain-hunter/SKILL.md" && grep -qF "description: Create logos using AI image generation. Discuss style/ratio, genera" "skills/logo-creator/SKILL.md" && grep -qF "description: Generate and edit images using Google Gemini 3 Pro Image (Nano Bana" "skills/nanobanana/SKILL.md" && grep -qF "description: Search and retrieve content from Product Hunt. Get posts, topics, u" "skills/producthunt/SKILL.md" && grep -qF "description: Search and retrieve content from Reddit. Get posts, comments, subre" "skills/reddit/SKILL.md" && grep -qF "description: Generate user demand research reports from real user feedback. Scra" "skills/requesthunt/SKILL.md" && grep -qF "description: SEO & GEO (Generative Engine Optimization) for websites. Analyze ke" "skills/seo-geo/SKILL.md" && grep -qF "description: Search and retrieve content from Twitter/X. Get user info, tweets, " "skills/twitter/SKILL.md" && grep -qF "description: Clear description of what this skill does and when to use it. Inclu" "template/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/banner-creator/SKILL.md b/skills/banner-creator/SKILL.md
@@ -1,15 +1,6 @@
 ---
 name: banner-creator
-description: Create banners using AI image generation. Discuss format/style, generate variations, iterate with user feedback, crop to target ratio. Use when user wants to create a banner, header, hero image, or cover image.
-triggers:
-  - "banner"
-  - "header"
-  - "hero image"
-  - "cover image"
-  - "create banner"
-  - "github banner"
-  - "twitter header"
-  - "readme banner"
+description: Create banners using AI image generation. Discuss format/style, generate variations, iterate with user feedback, crop to target ratio. Use when user wants to create a banner, header, hero image, cover image, GitHub banner, Twitter header, or readme banner.
 ---
 
 # Banner Creator Skill
diff --git a/skills/domain-hunter/SKILL.md b/skills/domain-hunter/SKILL.md
@@ -1,14 +1,6 @@
 ---
 name: domain-hunter
-description: Search domains, compare prices, find promo codes, get purchase recommendations. Use when user wants to buy a domain, check prices, or find domain deals.
-triggers:
-  - "domain"
-  - "registrar"
-  - "buy domain"
-  - "domain price"
-  - "promo code domain"
-  - ".ai domain"
-  - ".com domain"
+description: Search domains, compare prices, find promo codes, get purchase recommendations. Use when user wants to buy a domain, check domain prices, find domain deals, compare registrars, or search for .ai/.com domains.
 ---
 
 # Domain Hunter Skill
diff --git a/skills/logo-creator/SKILL.md b/skills/logo-creator/SKILL.md
@@ -1,15 +1,6 @@
 ---
 name: logo-creator
-description: Create logos using AI image generation. Discuss style/ratio, generate variations, iterate with user feedback, crop, remove background, and export as SVG. Use when user wants to create a logo, icon, favicon, or brand mark.
-triggers:
-  - "logo"
-  - "brand"
-  - "icon"
-  - "favicon"
-  - "mascot"
-  - "emblem"
-  - "create logo"
-  - "design logo"
+description: Create logos using AI image generation. Discuss style/ratio, generate variations, iterate with user feedback, crop, remove background, and export as SVG. Use when user wants to create a logo, icon, favicon, brand mark, mascot, emblem, or design a logo.
 ---
 
 # Logo Creator Skill
diff --git a/skills/nanobanana/SKILL.md b/skills/nanobanana/SKILL.md
@@ -1,14 +1,6 @@
 ---
 name: nanobanana
-description: Generate and edit images using Google Gemini 3 Pro Image (Nano Banana Pro). Supports text-to-image, image editing, various aspect ratios, and high-resolution output (2K/4K).
-triggers:
-  - "generate image"
-  - "create image"
-  - "nano banana"
-  - "nanobanana"
-  - "gemini image"
-  - "AI image"
-  - "image generation"
+description: Generate and edit images using Google Gemini 3 Pro Image (Nano Banana Pro). Supports text-to-image, image editing, various aspect ratios, and high-resolution output (2K/4K). Use when user wants to generate images, create images, use Gemini image generation, or do AI image generation.
 ---
 
 # Nano Banana - AI Image Generation
diff --git a/skills/producthunt/SKILL.md b/skills/producthunt/SKILL.md
@@ -1,11 +1,6 @@
 ---
 name: producthunt
-description: Search and retrieve content from Product Hunt. Get posts, topics, users, and collections via the GraphQL API.
-triggers:
-  - "producthunt"
-  - "product hunt"
-  - "PH"
-  - "launch"
+description: Search and retrieve content from Product Hunt. Get posts, topics, users, and collections via the GraphQL API. Use when user mentions Product Hunt, PH, or product launches.
 ---
 
 # ProductHunt Skill
diff --git a/skills/reddit/SKILL.md b/skills/reddit/SKILL.md
@@ -1,10 +1,6 @@
 ---
 name: reddit
-description: Search and retrieve content from Reddit. Get posts, comments, subreddit info, and user profiles via the public JSON API.
-triggers:
-  - "reddit"
-  - "subreddit"
-  - "r/"
+description: Search and retrieve content from Reddit. Get posts, comments, subreddit info, and user profiles via the public JSON API. Use when user mentions Reddit, a subreddit, or r/ links.
 ---
 
 # Reddit Skill
diff --git a/skills/requesthunt/SKILL.md b/skills/requesthunt/SKILL.md
@@ -1,14 +1,6 @@
 ---
 name: requesthunt
-description: Generate user demand research reports from real user feedback. Scrape and analyze feature requests, complaints, and questions from Reddit, X, and GitHub.
-triggers:
-  - "requesthunt"
-  - "request hunt"
-  - "feature request"
-  - "user demand"
-  - "demand research"
-  - "用户需求"
-  - "需求调研"
+description: Generate user demand research reports from real user feedback. Scrape and analyze feature requests, complaints, and questions from Reddit, X, and GitHub. Use when user wants to do demand research, find feature requests, analyze user demand, or run RequestHunt queries.
 ---
 
 # RequestHunt Skill
diff --git a/skills/seo-geo/SKILL.md b/skills/seo-geo/SKILL.md
@@ -1,24 +1,6 @@
 ---
 name: seo-geo
-description: |
-  SEO & GEO (Generative Engine Optimization) for websites.
-  Analyze keywords, generate schema markup, optimize for AI search engines
-  (ChatGPT, Perplexity, Gemini, Copilot, Claude) and traditional search (Google, Bing).
-  Use when user wants to improve search visibility.
-triggers:
-  - "SEO"
-  - "GEO"
-  - "search optimization"
-  - "schema markup"
-  - "JSON-LD"
-  - "meta tags"
-  - "keyword research"
-  - "search ranking"
-  - "AI visibility"
-  - "ChatGPT ranking"
-  - "Perplexity"
-  - "Google AI Overview"
-  - "indexing"
+description: SEO & GEO (Generative Engine Optimization) for websites. Analyze keywords, generate schema markup, optimize for AI search engines (ChatGPT, Perplexity, Gemini, Copilot, Claude) and traditional search (Google, Bing). Use when user wants to improve search visibility, search optimization, search ranking, AI visibility, ChatGPT ranking, Google AI Overview, indexing, JSON-LD, meta tags, or keyword research.
 ---
 
 # SEO/GEO Optimization Skill
diff --git a/skills/twitter/SKILL.md b/skills/twitter/SKILL.md
@@ -1,10 +1,6 @@
 ---
 name: twitter
-description: Search and retrieve content from Twitter/X. Get user info, tweets, replies, followers, communities, spaces, and trends via twitterapi.io.
-triggers:
-  - "twitter"
-  - "X"
-  - "tweet"
+description: Search and retrieve content from Twitter/X. Get user info, tweets, replies, followers, communities, spaces, and trends via twitterapi.io. Use when user mentions Twitter, X, or tweets.
 ---
 
 # Twitter/X Skill
diff --git a/template/SKILL.md b/template/SKILL.md
@@ -1,13 +1,6 @@
 ---
 name: skill-name
-description: Clear description of what this skill does and when to use it
-triggers:
-  - trigger1
-  - trigger2
-  - another-trigger
-dependencies:
-  dependency-skill: ">=1.0.0"
-  another-skill: ">=2.0.0"
+description: Clear description of what this skill does and when to use it. Include trigger keywords and contexts inline, e.g. "Use when user wants to X, Y, or Z."
 ---
 
 # Skill Name
@@ -123,17 +116,7 @@ The YAML frontmatter at the top of this file is required:
 | Field | Type | Required | Description |
 |-------|------|----------|-------------|
 | `name` | string | ✓ | Unique identifier (kebab-case) |
-| `description` | string | ✓ | What the skill does and when to use it |
-| `triggers` | array | ✓ | Keywords that activate this skill |
-| `dependencies` | object | | Dependent skills (format: `skill-name: ">=X.Y.Z"`) |
-
-### Dependency Format
-
-Use semantic versioning format:
-- `"^1.0.0"` - Compatible with 1.x versions
-- `">=1.0.0"` - Version 1.0.0 or higher
-- `"1.0.0"` - Exact version only
-- `">=1.0.0,<2.0.0"` - Range of versions
+| `description` | string | ✓ | What the skill does and when to use it. Include trigger keywords and "Use when..." contexts inline. |
 
 ## Creating Your Skill
 
PATCH

echo "Gold patch applied."
