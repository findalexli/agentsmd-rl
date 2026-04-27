#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-code-marketing-skills

# Idempotency guard
if grep -qF "3. Use `update_finding` to merge duplicate findings into one (update the body to" "skills/cogny/SKILL.md" && grep -qF "\"body\": \"Campaign targeting C-suite titles with single image ads. CPC is 55% abo" "skills/linkedin-ads-audit/SKILL.md" && grep -qF "\"body\": \"Pages /pricing, /features, /blog/... lack meta descriptions. Average CT" "skills/seo-audit/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/cogny/SKILL.md b/skills/cogny/SKILL.md
@@ -5,32 +5,31 @@ version: "1.0.0"
 user-invocable: true
 argument-hint: "[status|run|loop|update]"
 allowed-tools:
-  # Built-in Cogny tools (task queue, heartbeat, tickets)
+  # Built-in Cogny tools (task queue, heartbeat, findings)
   - mcp__cogny__get_queue_status
   - mcp__cogny__get_next_task
   - mcp__cogny__complete_task
   - mcp__cogny__heartbeat
   - mcp__cogny__list_findings
   - mcp__cogny__get_finding
   - mcp__cogny__update_finding_status
+  - mcp__cogny__update_finding
   - mcp__cogny__create_finding
-  # Read-only platform tools (auto-approved)
-  - mcp__cogny__google_ads__tool_list_accessible_accounts
-  - mcp__cogny__google_ads__tool_execute_gaql
-  - mcp__cogny__google_ads__tool_get_gaql_doc
-  - mcp__cogny__google_ads__tool_get_reporting_view_doc
-  - mcp__cogny__google_ads__tool_list_audience_segments
-  - mcp__cogny__google_ads__tool_search_geo_targets
-  - mcp__cogny__google_ads__tool_generate_keyword_ideas
-  - mcp__cogny__meta_ads__tool_list_ad_accounts
-  - mcp__cogny__meta_ads__tool_get_campaigns
-  - mcp__cogny__meta_ads__tool_get_ad_sets
-  - mcp__cogny__meta_ads__tool_get_ads
-  - mcp__cogny__meta_ads__tool_get_insights
-  - mcp__cogny__meta_ads__tool_get_pixels
-  - mcp__cogny__meta_ads__tool_get_custom_audiences
-  - mcp__cogny__meta_ads__tool_get_facebook_pages
+  - mcp__cogny__delete_finding
+  - mcp__cogny__delete_findings
+  # Context tree (organizational knowledge)
+  - mcp__cogny__browse_context_tree
+  - mcp__cogny__read_context_node
+  - mcp__cogny__search_context
+  - mcp__cogny__write_context_node
+  - mcp__cogny__archive_context_node
+  - mcp__cogny__get_context_tree_overview
+  # Platform tools — Search Console + LinkedIn Ads (launch MCPs)
   - mcp__cogny__search_console__*
+  - mcp__cogny__linkedin_ads__*
+  # Platform tools — Google Ads + Meta Ads (coming soon)
+  - mcp__cogny__google_ads__*
+  - mcp__cogny__meta_ads__*
   - mcp__cogny__ga4__*
   # Write/mutation tools are NOT listed here — Claude Code will prompt for approval
   # Local tools
@@ -214,7 +213,11 @@ Approve all? Or select specific actions (e.g., "1 and 3 only")
 
 This ensures the user always knows exactly what will be changed and why before any mutation happens. Read-only queries (GAQL, get_campaigns, get_insights, etc.) can be run freely without approval.
 
-## Finding Quality Standards
+## Finding Management
+
+Findings are your primary output — they track actionable opportunities in the dashboard.
+
+### Creating findings
 
 Every finding MUST include:
 - **Specific numbers**: actual spend, CPA, ROAS, impressions, clicks
@@ -225,3 +228,19 @@ Every finding MUST include:
 
 Bad: "Campaign performance could be improved"
 Good: "Campaign 'Brand - US' CPA is $42.50 (68% above $25 target). Top 3 keywords consuming 40% of budget with 0 conversions. Pausing these keywords would save ~$1,200/month."
+
+### Compacting findings
+
+The workspace has a limit of 100 findings. When approaching the limit:
+
+1. Use `list_findings` with `status: ["done", "dismissed"]` to find resolved items
+2. Use `delete_findings` to bulk-remove old resolved findings
+3. Use `update_finding` to merge duplicate findings into one (update the body to combine details, then delete the duplicates)
+
+### Recording to context tree
+
+When you discover important, reusable insights about the business (not one-off findings), save them to the context tree:
+
+- `write_context_node` with path like `insights/seo/top-keywords` or `insights/linkedin/audience-profile`
+- This persists knowledge across sessions and helps future analyses
+- The context tree has a limit of 50 nodes — use `archive_context_node` to clean up stale entries
diff --git a/skills/linkedin-ads-audit/SKILL.md b/skills/linkedin-ads-audit/SKILL.md
@@ -0,0 +1,182 @@
+---
+name: linkedin-ads-audit
+description: Full LinkedIn Ads account audit — campaign structure, targeting, creative performance, spend efficiency
+version: "1.0.0"
+author: Cogny AI
+platforms: [linkedin-ads]
+user-invocable: true
+argument-hint: ""
+allowed-tools:
+  - mcp__cogny__linkedin_ads__*
+  - mcp__cogny__create_finding
+  - mcp__cogny__list_findings
+  - mcp__cogny__update_finding
+  - WebFetch
+  - Bash
+  - Read
+  - Write
+---
+
+# LinkedIn Ads Audit
+
+Perform a comprehensive LinkedIn Ads account audit using live data from the connected LinkedIn Ads MCP.
+
+## Usage
+
+`/linkedin-ads-audit` — audit the connected LinkedIn Ads account
+
+## Benchmarks
+
+Use these LinkedIn Ads benchmarks for scoring:
+
+| Metric | Poor | Average | Good |
+|--------|------|---------|------|
+| CTR | <0.3% | 0.4-0.6% | >0.8% |
+| CPC | >$10 | $5-8 | <$4 |
+| CPM | >$40 | $25-35 | <$20 |
+| Conversion Rate | <1% | 2-4% | >5% |
+| Engagement Rate | <0.3% | 0.5-1% | >1.5% |
+
+## Steps
+
+### 1. List accessible ad accounts
+
+Query available ad accounts. If multiple exist, note which is active.
+
+### 2. Campaign overview
+
+Get all campaigns (active + recently paused). For each:
+- Status, objective, budget type (daily/lifetime)
+- Date range and total spend
+- Key metrics: impressions, clicks, CTR, CPC, conversions
+
+Flag:
+- Campaigns spending >30% of budget with CTR below 0.3%
+- Paused campaigns that were performing well (CTR >0.6%)
+- Campaigns running >90 days without optimization
+
+### 3. Spend efficiency analysis
+
+Across all active campaigns:
+- Total monthly spend vs results
+- CPC trend (last 30 vs previous 30 days)
+- Cost per conversion by campaign
+- Budget utilization (actual spend vs allocated)
+
+Flag:
+- Campaigns with CPC >$10 (above LinkedIn average)
+- Budget underspend (<70% utilization) or overspend
+- Rising CPC trends (>20% increase MoM)
+
+### 4. Targeting review
+
+For each active campaign, analyze:
+- Audience size (too narrow <10K or too broad >1M)
+- Job title/function targeting specificity
+- Industry and company size filters
+- Geographic targeting
+- Audience expansion settings
+
+Flag:
+- Overlapping audiences between campaigns
+- Overly broad targeting (no job title/function filters)
+- Missing exclusions (existing customers, competitors)
+
+### 5. Creative performance
+
+Analyze ad creatives across campaigns:
+- Format breakdown (single image, carousel, video, text)
+- Per-creative CTR and engagement rate
+- Ad copy length and CTA effectiveness
+- Creative age (days since launch)
+
+Flag:
+- Creatives running >60 days (fatigue risk)
+- Single-format campaigns (no A/B testing)
+- Low-performing creatives (CTR <0.2%) still active
+- Missing formats (no video if budget >$5K/mo)
+
+### 6. Conversion tracking
+
+Check:
+- Insight Tag installation status
+- Conversion event definitions
+- Attribution window settings
+- Lead gen form completion rates (if using lead gen)
+
+Flag:
+- Missing or misconfigured conversion tracking
+- Low form completion rates (<10%)
+- No offline conversion import
+
+### 7. Budget pacing
+
+For each campaign:
+- Daily/monthly spend rate vs target
+- Projected end-of-month spend
+- Day-of-week performance patterns
+
+Flag:
+- Campaigns pacing >20% over or under budget
+- Weekend spend on B2B campaigns (usually wasteful)
+
+### 8. Report findings
+
+Present as a scored audit:
+
+```
+LinkedIn Ads Audit
+Score: X/100
+
+Campaign Structure: X/20
+- [PASS/FAIL] Campaign organization
+- [PASS/FAIL] Objective alignment
+- [PASS/FAIL] Budget allocation
+
+Targeting: X/20
+- [PASS/FAIL] Audience specificity
+- [PASS/FAIL] Audience overlap
+- [PASS/FAIL] Exclusions
+
+Creative: X/20
+- [PASS/FAIL] Format diversity
+- [PASS/FAIL] Creative freshness
+- [PASS/FAIL] A/B testing
+
+Performance: X/20
+- [PASS/FAIL] CPC vs benchmark
+- [PASS/FAIL] CTR vs benchmark
+- [PASS/FAIL] Conversion rate
+
+Tracking & Budget: X/20
+- [PASS/FAIL] Conversion tracking
+- [PASS/FAIL] Budget pacing
+- [PASS/FAIL] Attribution setup
+
+Top 3 Actions:
+1. [Highest impact fix]
+2. [Second highest]
+3. [Third highest]
+```
+
+### 9. Record findings
+
+For EVERY actionable issue found, call `mcp__cogny__create_finding`:
+
+```json
+{
+  "title": "High CPC on 'Decision Makers' campaign ($12.40 vs $5-8 benchmark)",
+  "body": "Campaign targeting C-suite titles with single image ads. CPC is 55% above LinkedIn average. Recommend: 1) Test carousel format 2) Narrow to VP+ titles only 3) Add company size >500 filter",
+  "action_type": "campaign_optimization",
+  "expected_outcome": "Reduce CPC to <$8 within 2 weeks",
+  "estimated_impact_usd": 800,
+  "priority": "high"
+}
+```
+
+Action types for LinkedIn Ads:
+- `campaign_optimization` — budget, bidding, pacing changes
+- `targeting_refinement` — audience, exclusion, geo changes
+- `creative_refresh` — new ads, format tests, copy updates
+- `conversion_tracking` — pixel, events, attribution fixes
+- `audience_management` — overlap, expansion, exclusion updates
diff --git a/skills/seo-audit/SKILL.md b/skills/seo-audit/SKILL.md
@@ -100,10 +100,24 @@ Top 3 Actions:
 3. [Third highest]
 ```
 
-## Upgrade
+## Recording Findings
+
+If the Cogny MCP is connected (`mcp__cogny__create_finding` available), record each actionable finding:
+
+```json
+{
+  "title": "Missing meta descriptions on 12 pages",
+  "body": "Pages /pricing, /features, /blog/... lack meta descriptions. Average CTR for pages without descriptions is 30% lower.",
+  "action_type": "seo_optimization",
+  "expected_outcome": "Improve CTR by 15-30% on affected pages",
+  "priority": "high"
+}
+```
+
+## Deeper Analysis
 
-Want deeper insights with real Search Console data (actual queries, rankings, click-through rates, indexing status)?
+Want live Search Console data (actual queries, rankings, click-through rates, indexing status)?
 
-Connect Search Console via Cogny Agent ($9/mo): https://cogny.com/agent
+Connect Search Console via Cogny ($9/mo): https://cogny.com/pricing
 
 Then use `/seo-monitor` for live ranking data and automated monitoring.
PATCH

echo "Gold patch applied."
