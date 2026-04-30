#!/usr/bin/env bash
set -euo pipefail

cd /workspace/antigravity-awesome-skills

# Idempotency guard
if grep -qF "This skill is designed to help users create high-quality, engaging, and platform" "skills/social-post-writer-seo/SKILL.md" && grep -qF "This skill is designed for Senior Content Strategists and Expert Copywriters to " "skills/wordpress-centric-high-seo-optimized-blogwriting-skill/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/social-post-writer-seo/SKILL.md b/skills/social-post-writer-seo/SKILL.md
@@ -4,19 +4,37 @@ description: "Social Media Strategist and Content Writer. Creates clear, engagin
 category: growth
 risk: safe
 source: self
+source_type: self
 date_added: "2026-04-17"
 author: WHOISABHISHEKADHIKARI
+tags: [social-media, marketing, content-writing, seo, growth]
+tools: [claude, cursor, gemini]
+version: 1.0.1
 ---
 
 # Social Media Strategist and Content Writer
 
+## Overview
+This skill is designed to help users create high-quality, engaging, and platform-optimized social media content. It focuses on clarity, readability, and platform-specific nuances for Instagram, LinkedIn, and Facebook.
+
 ## When to Use This Skill
 - Use this skill when you need a clear, engaging, and accurate social media post for Instagram, LinkedIn, or Facebook.
 - Use it to transform topics and keywords into audience-focused content with platform-native structure.
 
-Your task is to create a clear, engaging, and accurate social media post that works for a global audience on platforms like Instagram, LinkedIn, and Facebook.
+## How It Works
 
----
+### Step 1: Input Gathering
+The skill starts by collecting essential details like the topic, primary keyword, target audience, and the specific social media platform.
+
+### Step 2: Content Generation
+Based on the inputs, it follows strict writing rules to ensure simplicity, factual accuracy, and engagement. It structures the post with a hook, context, value, and a call to action.
+
+### Step 3: Platform Optimization
+The output is tailored for the selected platform, adjusting emoji density and tone (e.g., more professional for LinkedIn, more visual/casual for Instagram).
+
+## Prompt Template
+
+Your task is to create a clear, engaging, and accurate social media post that works for a global audience on platforms like Instagram, LinkedIn, and Facebook.
 
 ### INPUT:
 - **Topic**: {Insert Topic}
@@ -51,8 +69,6 @@ Create a post that is easy to understand, useful, and encourages engagement.
 4. **Call to Action**: Check the comment section or follow.
 5. **Hashtags**: 5-8 relevant tags.
 
----
-
 ## Examples
 
 ### Example: New Product Launch
@@ -64,15 +80,35 @@ Create a post that is easy to understand, useful, and encourages engagement.
 
 **Output**:
 ☕️ Your morning coffee just got a clean energy upgrade! 
-Did you know commuters throw away billions of cups annually? 
-The SolMug keeps your brew hot using only sunlight. 
-A small change for your bag, a big win for the planet. 
+Meet SolMug, a solar powered coffee mug concept for busy commutes.
+It is designed to keep your drink warm without adding another charger to your bag.
+A small change for your morning routine, with sustainability in mind.
 Check the link in bio to pre-order! 
 #ecofriendly #coffee #sustainability #tech #morningroutine
 
----
+## Best Practices
+- ✅ Always include a "Hook" in the first line to capture attention.
+- ✅ Use line breaks frequently to make the post scannable on mobile.
+- ✅ Tailor the tone: LinkedIn should be more professional, Instagram more visual/energetic.
+- ❌ Avoid using more than 10 hashtags; it can look like spam.
+- ❌ Never guess facts; if info isn't provided, stick to general industry knowledge.
 
 ## Limitations
 - This skill does not generate image or video assets.
 - It requires manual copy-pasting to the respective social media platforms.
 - It cannot schedule or post content directly to social media accounts.
+
+## Security & Safety Notes
+- This skill only generates text content and does not interact with system APIs or run shell commands.
+- Ensure any links included in the generated content are verified by the user before posting.
+
+## Common Pitfalls
+- **Problem:** Post feels too "salesy".
+  **Solution:** Focus more on the "Value/Insight" section to provide helpful info before the CTA.
+- **Problem:** Low engagement on LinkedIn.
+  **Solution:** Reduce emoji count and ensure the "Hook" addresses a professional pain point.
+
+## Related Skills
+- `@copywriting` - For longer form sales copy and landing pages.
+- `@seo-content` - For blog-style SEO content optimization.
+- `@ad-creative` - Specifically for paid social media advertisements.
diff --git a/skills/wordpress-centric-high-seo-optimized-blogwriting-skill/SKILL.md b/skills/wordpress-centric-high-seo-optimized-blogwriting-skill/SKILL.md
@@ -1,14 +1,42 @@
 ---
 name: wordpress-centric-high-seo-optimized-blogwriting-skill
-description: "Use this skill when the user asks to write a blog post, article, or SEO content. This applies a professional structure, truth boxes, click-bait-free accurate information, and outputs direct WordPress-ready content."
-version: 1.0.0
-author: Whoisabhishekadhikari
-created: 2026-04-12
+description: "Create long-form, high-quality, SEO-optimized blog posts ready for WordPress with truth boxes and FAQ schema."
 category: content
+risk: safe
+source: self
+source_type: self
+date_added: "2026-04-12"
+author: Whoisabhishekadhikari
 tags: [writing, blog, seo, content, wordpress]
+tools: [claude, cursor, gemini]
+version: 1.0.3
 ---
 
-# wordpress-centric-high-seo-optimized-blogwriting-skill
+# WordPress Centric High SEO Optimized Blog Writing Skill
+
+## Overview
+
+This skill is designed for Senior Content Strategists and Expert Copywriters to create high-quality, long-form blog posts that are ready for direct publication in WordPress. It emphasizes professional structure, factual accuracy (Truth Boxes), and comprehensive SEO optimization (Yoast elements and Schema markup).
+
+## When to Use This Skill
+
+- Use when you need to write a professional blog post or article.
+- Use when creating SEO-optimized content for a WordPress site.
+- Use when you need structured elements like Truth Boxes, Comparison Tables, and FAQ sections.
+- Use when the user requires Yoast SEO metadata and JSON-LD schema.
+
+## How It Works
+
+### Step 1: Gather Inputs
+The skill requires a Title, Primary Keyword, Intent, and Niche/Industry. It also prompts for Yoast SEO preference and image count if not provided.
+
+### Step 2: Content Generation
+The agent follows a structured prompt to generate a clickable contents section, a truth box, well-structured sections with tables, common misconceptions, and a short FAQ.
+
+### Step 3: SEO & Schema (Optional)
+If requested, the agent provides Yoast SEO metadata (Social titles, meta descriptions) and JSON-LD Schema (BlogPosting, FAQPage).
+
+## Prompt Template
 
 FINAL MASTER PROMPT (Refined & Generalized Version)
 
@@ -23,6 +51,10 @@ Primary Keyword: {Insert Primary Keyword}
 Intent: {Informational / Commercial / Transactional}
 Niche/Industry: {Insert Industry or Subject Area}
 
+USER PREFERENCES (ASK IF MISSING)
+Yoast SEO: {Are Yoast SEO elements like meta descriptions and focus keyphrases needed?}
+Image Count: {How many images should be included in the SEO plan?}
+
 Optional Context
 Brand: {Insert Brand Name}
 Target Audience: {Insert Target Audience}
@@ -52,36 +84,14 @@ Maintain clean and consistent formatting
 Make content easy to scan and copy
 
 FACT AND ACCURACY RULES
+
 Do not guess or fabricate data.
 - Requirement: Provide citation-backed estimates with a verifiable source or an explicit "no reliable estimate available" response.
 - Prohibited: Do not use vague "industry estimates suggest a range" fallbacks if no verifiable evidence was found.
 
 Avoid fake or unreliable sources
 Keep all information practical, realistic, and up-to-date
 
-SEO SECTION (PLACE AT THE TOP)
-
-Provide the following:
-
-Focus Keyphrase
-SEO Title
-Slug
-Meta Description
-Social Title
-Social Description
-
-Include this exact line:
-Data accurate as of [Current Month & Year] based on market research
-
-SCHEMA MARKUP
-
-Add clean JSON-LD for:
-
-BlogPosting
-FAQPage
-
-Use placeholder URLs if needed
-
 CONTENTS SECTION
 
 Create a clickable contents section with:
@@ -104,9 +114,10 @@ MAIN BLOG STRUCTURE
 
 Main Title
 
+Introduction
+
 Truth Box
 
-Introduction
 
 [Core Topic Section 1]
 
@@ -159,7 +170,7 @@ Keep answers short and clear
 
 IMAGE SEO SECTION
 
-Include 3 to 5 images
+Include {User Requested Count} images
 
 For each image, provide:
 
@@ -184,15 +195,80 @@ Ensure clean and consistent structure
 
 OUTPUT REQUIREMENT
 
-The final output must be:
+The final output must be generated in this order:
+1. The full blog post (from Main Title to Conclusion)
+2. SEO Section (if requested)
+3. Schema Markup (if requested)
+
+The content must be:
 
 Clean and well-structured
 SEO optimized
 Human-sounding
 Professional quality
 Ready to copy and paste into WordPress
 
+SEO SECTION (YOAST)
+*Only provide this section if the user requested Yoast SEO elements.*
+
+Provide the following:
+
+Focus Keyphrase
+SEO Title
+Slug
+Meta Description
+Social Title
+Social Description
+
+If the user provided or approved reliable market sources, include this line with the actual month and year:
+Data accurate as of [Month Year] based on cited market research.
+
+If no reliable market sources were provided or reviewed, omit the line instead of implying research was performed.
+
+SCHEMA MARKUP
+*Only provide this section if the user requested Yoast/SEO schema.*
+
+Add clean JSON-LD for:
+
+BlogPosting
+FAQPage
+
+Use placeholder URLs if needed
+
+## Examples
+
+### Example 1: Informational Blog Post
+**User:** Write a blog post about "Sustainable Gardening for Beginners".
+**Agent:** (Generates Title, Truth Box, clickable contents, well-structured sections with tables, Misconceptions, and FAQ.)
+
+## Best Practices
+
+- ✅ Use short, punchy sentences.
+- ✅ Ensure tables are clean and use `|` markdown syntax.
+- ✅ Maintain the Truth Box at the very beginning of the post for high engagement.
+- ❌ Avoid using numbered headings; stick to standard markdown `#`, `##`, `###`.
+- ❌ Do not use hyphen bullets in the contents section.
+
 ## Limitations
+
+- This skill does not replace environment-specific validation, testing, or expert review.
+- Stop and ask for clarification if required inputs, permissions, or safety boundaries are missing.
 - Use this skill only when the task clearly matches the scope described above.
-- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
-- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.
+
+## Security & Safety Notes
+
+- This skill focuses on content generation and does not involve shell commands or direct system mutation.
+- Ensure any generated JSON-LD is properly escaped if used in a programmatic context.
+
+## Common Pitfalls
+
+- **Problem:** Missing Primary Keyword in Alt Text.
+  **Solution:** Ensure the `IMAGE SEO SECTION` explicitly includes the primary keyword in at least one Alt Text field.
+- **Problem:** AI-sounding or repetitive tone.
+  **Solution:** Use the "Human-sounding" requirement in the `WRITING RULES` to re-check the draft.
+
+## Related Skills
+
+- `@seo-plan` - Use for high-level SEO strategy before writing.
+- `@seo-content` - For broader SEO content optimization across different platforms.
+- `@copywriting` - General professional writing and marketing copy.
PATCH

echo "Gold patch applied."
