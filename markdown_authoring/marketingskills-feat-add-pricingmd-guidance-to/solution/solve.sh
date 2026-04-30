#!/usr/bin/env bash
set -euo pipefail

cd /workspace/marketingskills

# Idempotency guard
if grep -qF "AI agents aren't just answering questions \u2014 they're becoming buyers. When an AI " "skills/ai-seo/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/ai-seo/SKILL.md b/skills/ai-seo/SKILL.md
@@ -2,7 +2,7 @@
 name: ai-seo
 description: "When the user wants to optimize content for AI search engines, get cited by LLMs, or appear in AI-generated answers. Also use when the user mentions 'AI SEO,' 'AEO,' 'GEO,' 'LLMO,' 'answer engine optimization,' 'generative engine optimization,' 'LLM optimization,' 'AI Overviews,' 'optimize for ChatGPT,' 'optimize for Perplexity,' 'AI citations,' 'AI visibility,' 'zero-click search,' 'how do I show up in AI answers,' 'LLM mentions,' or 'optimize for Claude/Gemini.' Use this whenever someone wants their content to be cited or surfaced by AI assistants and AI search engines. For traditional technical and on-page SEO audits, see seo-audit. For structured data implementation, see schema-markup."
 metadata:
-  version: 1.1.0
+  version: 1.2.0
 ---
 
 # AI SEO
@@ -226,6 +226,50 @@ AI systems don't just cite your website — they cite where you appear.
 - Create YouTube content for key how-to queries
 - Answer relevant Quora questions with depth
 
+### Machine-Readable Files for AI Agents
+
+AI agents aren't just answering questions — they're becoming buyers. When an AI agent evaluates tools on behalf of a user, it needs structured, parseable information. If your pricing is locked in a JavaScript-rendered page or a "contact sales" wall, agents will skip you and recommend competitors whose information they can actually read.
+
+Add these machine-readable files to your site root:
+
+**`/pricing.md` or `/pricing.txt`** — Structured pricing data for AI agents
+
+```markdown
+# Pricing — [Your Product Name]
+
+## Free
+- Price: $0/month
+- Limits: 100 emails/month, 1 user
+- Features: Basic templates, API access
+
+## Pro
+- Price: $29/month (billed annually) | $35/month (billed monthly)
+- Limits: 10,000 emails/month, 5 users
+- Features: Custom domains, analytics, priority support
+
+## Enterprise
+- Price: Custom — contact sales@example.com
+- Limits: Unlimited emails, unlimited users
+- Features: SSO, SLA, dedicated account manager
+```
+
+**Why this matters now:**
+- AI agents increasingly compare products programmatically before a human ever visits your site
+- Opaque pricing gets filtered out of AI-mediated buying journeys
+- A simple markdown file is trivially parseable by any LLM — no rendering, no JavaScript, no login walls
+- Same principle as `robots.txt` (for crawlers), `llms.txt` (for AI context), and `AGENTS.md` (for agent capabilities)
+
+**Best practices:**
+- Use consistent units (monthly vs. annual, per-seat vs. flat)
+- Include specific limits and thresholds, not just feature names
+- List what's included at each tier, not just what's different
+- Keep it updated — stale pricing is worse than no file
+- Link to it from your sitemap and main pricing page
+
+**`/llms.txt`** — Context file for AI systems (see [llmstxt.org](https://llmstxt.org))
+
+If you don't have one yet, add an `llms.txt` that gives AI systems a quick overview of what your product does, who it's for, and links to key pages (including your pricing).
+
 ### Schema Markup for AI
 
 Structured data helps AI systems understand your content. Key schemas:
@@ -309,7 +353,7 @@ Monthly manual check:
 - Feature comparison tables (you vs. category, not just competitors)
 - Specific metrics ("processes 10,000 transactions/sec" not "blazing fast")
 - Customer count or social proof with numbers
-- Pricing transparency (AI cites pages with visible pricing)
+- Pricing transparency (AI cites pages with visible pricing) — add a `/pricing.md` file so AI agents can parse your plans without rendering your page (see "Machine-Readable Files" above)
 - FAQ section addressing common buyer questions
 
 ### Blog Content
@@ -358,6 +402,7 @@ Monthly manual check:
 - **Ignoring third-party presence** — You may get more AI citations from a Wikipedia mention than from your own blog
 - **No structured data** — Schema markup gives AI systems structured context about your content
 - **Keyword stuffing** — Unlike traditional SEO where it's just ineffective, keyword stuffing actively reduces AI visibility by 10% (Princeton GEO study)
+- **Hiding pricing behind "contact sales" or JS-rendered pages** — AI agents evaluating your product on behalf of buyers can't parse what they can't read. Add a `/pricing.md` file
 - **Blocking AI bots** — If GPTBot, PerplexityBot, or ClaudeBot are blocked in robots.txt, those platforms can't cite you
 - **Generic content without data** — "We're the best" won't get cited. "Our customers see 3x improvement in [metric]" will
 - **Forgetting to monitor** — You can't improve what you don't measure. Check AI visibility monthly at minimum
PATCH

echo "Gold patch applied."
