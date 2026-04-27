#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cog-second-brain

# Idempotency guard
if grep -qF "Lightweight URL/tool triage that sits between \"ignore\" and `/url-dump`. Evaluate" ".claude/skills/scout/SKILL.md" && grep -qF "**Purpose:** Lightweight triage that sits between \"ignore\" and `/url-dump`. Chec" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/scout/SKILL.md b/.claude/skills/scout/SKILL.md
@@ -0,0 +1,201 @@
+---
+name: scout
+description: Evaluate URLs and tools — check vault coverage, assess relevance, recommend save or skip
+roles: [all]
+integrations: [web-fetch, web-search]
+---
+
+# COG Scout Skill
+
+## Purpose
+Lightweight URL/tool triage that sits between "ignore" and `/url-dump`. Evaluates whether a URL or tool is worth saving or skipping — checking existing vault coverage, assessing relevance to the user's profile and interests, and recommending a clear next action.
+
+## When to Invoke
+- User wants to evaluate a URL or tool before committing to a full save
+- User says "scout this", "evaluate this", "should I save this?", "is this relevant?"
+- User shares one or more URLs and wants a quick relevance assessment
+- User mentions a tool/service name and wants to know if it's worth investigating
+
+## Agent Mode Awareness
+
+**Check `agent_mode` in `00-inbox/MY-PROFILE.md` frontmatter:**
+- If `agent_mode: team` — delegate vault scanning and web fetching to parallel sub-agents (one for vault search, one for content fetch/analysis). Combine results for recommendation.
+- If `agent_mode: solo` (default) — handle all scanning and analysis directly in the conversation. No delegation.
+
+## Pre-Flight Check
+
+**Before executing, check for user profile:**
+
+1. Look for `00-inbox/MY-PROFILE.md` and `00-inbox/MY-INTERESTS.md` in the vault
+2. If NOT found:
+   ```
+   Welcome to COG! Scout works best with a profile for relevance matching.
+
+   Would you like to run /onboarding first, or should I evaluate with general criteria?
+   ```
+3. If found:
+   - Read `MY-PROFILE.md` for active projects and role
+   - Read `MY-INTERESTS.md` for topic areas
+   - Read `00-inbox/MY-INTEGRATIONS.md` for active integrations (check if `web-fetch` and `web-search` are available)
+
+## Boundary with `/url-dump`
+
+**Scout evaluates** ("should I save this?"). **URL-dump saves** ("save this now").
+
+- Scout checks existing coverage, assesses relevance, and recommends an action
+- If the recommendation is **Save**, scout hands off to `/url-dump` with pre-filled category
+- Users who already know they want to save should use `/url-dump` directly
+
+## Process Flow
+
+### 1. Accept Input
+
+Accept one or more of:
+- **URL(s):** Direct links to evaluate
+- **Tool/service name(s):** Will search for the tool first
+- **Mixed:** Combination of URLs and names
+
+**Prompt (if no input provided):**
+```
+What URL(s) or tool(s) would you like me to evaluate?
+(You can paste URLs, tool names, or a mix)
+```
+
+**Batch mode:** Multiple URLs/names in one invocation are processed together with a summary table at the end.
+
+### 2. Vault Coverage Check
+
+For each URL or tool name, search the **entire vault** for existing coverage.
+
+**Search strategy:**
+- Extract domain from URL (e.g., `github.com/owner/repo` → search for repo name)
+- Search for tool/service name across the whole vault (grep for domain, repo name, tool name)
+- Match against URL strings in frontmatter (`url:` fields) and inline links
+
+**If found:**
+```
+🔍 Existing coverage found for [name]:
+- [file path] — saved [date], category: [category]
+- [file path] — mentioned in [context]
+
+Want me to check if an update is needed, or skip this one?
+```
+
+### 3. Content Fetch & Analysis
+
+**If URL provided and web-fetch is active:**
+- Fetch the URL content using WebFetch
+- Extract: title, description, content type, author, date
+
+**If tool name provided (no URL):**
+- Use WebSearch to find the tool's primary page
+- Fetch and analyze the top result
+
+**Content type detection:**
+- **Tool/Service:** Software, SaaS, API, library, framework
+- **Article/Blog:** Long-form content, tutorial, opinion piece
+- **Repository:** GitHub/GitLab repo (extract stars, last commit, language)
+- **Research:** Paper, study, academic content
+- **News:** Industry news, announcement
+- **Reference:** Documentation, spec, standard
+
+### 4. Relevance Assessment
+
+Score relevance against user context:
+
+**Profile Match (from MY-PROFILE.md):**
+- Does it relate to an active project? Which one?
+- Does it align with the user's role?
+- Does it fit the user's tech stack?
+
+**Interest Match (from MY-INTERESTS.md):**
+- Does it match any declared interest topics?
+- How directly relevant is it?
+
+**Quality Signals:**
+- For repos: stars, recent activity, maintainer health
+- For tools: pricing model, maturity, adoption
+- For articles: author credibility, publication quality, recency
+- For all: uniqueness vs. what's already in the vault
+
+### 5. Recommendation
+
+Based on analysis, recommend one of two actions:
+
+#### **Save** — Worth adding to the knowledge base
+```
+✅ SAVE — [Title/Name]
+Category: [suggested category for url-dump]
+Relevance: [High/Medium] — [why it matters]
+Projects: [affected project(s) if any]
+
+Shall I hand off to /url-dump to save it?
+```
+
+#### **Skip** — Not relevant or not worth the time
+```
+⏭️ SKIP — [Title/Name]
+Reason: [clear explanation — wrong stack, low quality, already covered, irrelevant to interests]
+```
+
+### 6. Batch Summary (for multiple items)
+
+When processing multiple URLs/tools, end with a summary table:
+
+```markdown
+## Scout Summary
+
+| # | Item | Verdict | Reason |
+|---|------|---------|--------|
+| 1 | [Name 1] | ✅ Save | [brief reason] |
+| 2 | [Name 2] | ⏭️ Skip | [brief reason] |
+
+**Actions:**
+- [X] items ready to save via /url-dump
+```
+
+### 7. Execute Follow-up Actions
+
+Based on user confirmation:
+- **Save items:** Hand off to `/url-dump` with pre-filled category suggestion
+- **Skip items:** No action needed
+
+## Fallback Behavior
+
+| Scenario | Behavior |
+|----------|----------|
+| web-fetch unavailable | Evaluate based on URL structure, domain reputation, and vault search only. Note that content wasn't fetched. |
+| web-search unavailable | For tool-name inputs (no URL), ask the user for a direct URL instead. For URL inputs, proceed normally — web-search is not needed. |
+| No user profile | Evaluate with general quality/relevance criteria, skip personalized relevance scoring |
+| URL is paywalled | Note limitation, evaluate based on available preview and metadata |
+| Tool not found via search | Ask user for more context or a direct URL |
+
+## Uncertainty Handling
+
+- **High confidence:** Clear relevance match or clear irrelevance — give direct recommendation
+- **Medium confidence:** Partial match — present pros/cons, let user decide
+- **Low confidence:** Can't determine relevance — explain what's unclear, ask user for context
+
+## Integration with Other Skills
+
+### Downstream
+- **Save** → hands off to `/url-dump` with pre-filled category
+
+### Upstream
+- `/daily-brief` may surface new tools/services → user can run `/scout` to evaluate
+- `/auto-research` may discover tools during research → scout can triage them
+
+## Success Metrics
+- Quick triage (< 1 minute for single URL in solo mode)
+- Clear, actionable recommendations
+- Accurate vault coverage detection (no duplicate saves)
+- Relevance scoring matches user expectations
+- Smooth handoff to `/url-dump` when saving
+
+## Philosophy
+
+Scout embodies COG's "evaluate before you accumulate" principle:
+- Not everything deserves a bookmark — be selective
+- Existing coverage should be surfaced before creating duplicates
+- Binary save/skip keeps decisions fast and avoids half-measures
+- Clear recommendations reduce decision fatigue
diff --git a/AGENTS.md b/AGENTS.md
@@ -210,6 +210,31 @@ This document defines the available commands/skills for AI agents interacting wi
 
 ---
 
+### /scout
+
+**Description:** Evaluate URLs and tools — check vault coverage, assess relevance, recommend save or skip.
+
+**Triggers:**
+- `/scout`
+- "scout this"
+- "evaluate this"
+- "should I save this?"
+- "is this relevant?"
+
+**Purpose:** Lightweight triage that sits between "ignore" and `/url-dump`. Checks existing vault coverage, assesses relevance to your profile and interests, and recommends save or skip.
+
+**What it does:**
+1. Accepts URL(s) or tool name(s)
+2. Searches the entire vault for existing coverage (duplicates, mentions)
+3. If new — fetches content, detects type (tool, article, repo, research, news, reference)
+4. Assesses relevance against your profile (projects, role, tech stack) and interests
+5. Recommends **Save** (hands off to `/url-dump` with pre-filled category) or **Skip** (explains why)
+6. Supports batch mode (multiple URLs in one invocation)
+
+**Boundary with `/url-dump`:** Scout evaluates ("should I save this?"). URL-dump saves ("save this now"). If you already know you want to save, use `/url-dump` directly.
+
+---
+
 ### /update-cog
 
 **Description:** Check for and apply upstream COG framework updates without touching personal content.
@@ -460,11 +485,12 @@ COG-second-brain/
 3. **Morning routine?** Run `/daily-brief` for your intelligence briefing
 4. **End of week?** Use `/weekly-checkin` to reflect
 5. **Save a link?** Use `/url-dump` with the URL
-6. **Build knowledge?** Run `/knowledge-consolidation` periodically
-7. **Create user stories?** Use `/create-user-story` with a problem/solution
-8. **Draft a PRD?** Use `/generate-prd` with your problem context
-9. **Release notes?** Use `/generate-release-notes` with a version
-10. **Strategic research?** Use `/auto-research` with your question
+6. **Evaluate a tool?** Use `/scout` to check relevance before saving
+7. **Build knowledge?** Run `/knowledge-consolidation` periodically
+8. **Create user stories?** Use `/create-user-story` with a problem/solution
+9. **Draft a PRD?** Use `/generate-prd` with your problem context
+10. **Release notes?** Use `/generate-release-notes` with a version
+11. **Strategic research?** Use `/auto-research` with your question
 
 ---
 
PATCH

echo "Gold patch applied."
