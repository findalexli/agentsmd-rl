#!/usr/bin/env bash
set -euo pipefail

cd /workspace/antigravity-awesome-skills

# Idempotency guard
if grep -qF "This skill transforms the agent into a senior strategic consultant specializing " "skills/kotler-macro-analyzer/SKILL.md" && grep -qF "A specialized architectural tool for designing and auditing business models usin" "skills/osterwalder-canvas-architect/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/kotler-macro-analyzer/SKILL.md b/skills/kotler-macro-analyzer/SKILL.md
@@ -0,0 +1,48 @@
+---
+name: kotler-macro-analyzer
+description: "Professional PESTEL/SWOT analysis agent based on Kotler's methodology for strategic market audits."
+category: business-strategy
+risk: safe
+source: self
+source_type: self
+date_added: "2026-04-17"
+author: justmiroslav
+tags: [marketing, economics, strategy, kotler, pestel]
+tools: [claude, cursor]
+---
+
+# Kotler Macro-Environment Analyzer
+
+## Overview
+This skill transforms the agent into a senior strategic consultant specializing in Philip Kotler’s macro-marketing environment analysis. It systematically evaluates PESTEL factors and synthesizes them into a high-impact SWOT matrix.
+
+## When to Use This Skill
+- Use when conducting market entry research or a periodic strategic audit.
+- Use to validate business assumptions against real-time macro-economic indicators (GDP, inflation, regulations).
+- Use when preparing for high-level business planning sessions.
+
+## How It Works
+### Step 1: Real-time Data Retrieval
+The agent uses search tools to gather the latest economic, political, and legal data for the target region.
+### Step 2: PESTEL Mapping
+Findings are categorized into Political, Economic, Social, Technological, Environmental, and Legal dimensions.
+### Step 3: SWOT Synthesis
+Macro-trends are mapped to Opportunities and Threats, while internal user data is mapped to Strengths and Weaknesses.
+
+## Examples
+
+### Example 1: Regional Market Entry
+"Conduct a Kotler-style strategic audit for a renewable energy startup planning to enter the Eastern European market in 2026. Focus on regulatory shifts and green energy subsidies."
+
+### Example 2: Competitive Resilience
+"Analyze the current macro-environment for a retail chain in Ukraine. Identify threats from inflation and opportunities from shifting consumer displacement trends."
+
+## Best Practices
+- ✅ Always use search tools to verify specific economic indicators (e.g., current central bank rates).
+- ✅ Link SWOT points directly to the PESTEL findings for logical continuity.
+- ❌ Do not provide generic analysis without region-specific data or numerical evidence.
+
+## Limitations
+- **Expert Review Required**: This skill provides strategic frameworks but does not substitute for professional financial, legal, or management consulting.
+- **Data Freshness**: The quality of the output depends on the real-time availability of data from search tools; results may vary in rapidly shifting economic environments.
+- **Scope**: The analysis focuses on macro-level factors and does not include detailed internal operational auditing.
diff --git a/skills/osterwalder-canvas-architect/SKILL.md b/skills/osterwalder-canvas-architect/SKILL.md
@@ -0,0 +1,48 @@
+---
+name: osterwalder-canvas-architect
+description: "Iterative consultant agent for building and validating logically consistent 9-block Business Model Canvases."
+category: business-strategy
+risk: safe
+source: self
+source_type: self
+date_added: "2026-04-17"
+author: justmiroslav
+tags: [business-model, osterwalder, strategy, bmc]
+tools: [claude, cursor, gemini]
+---
+
+# Osterwalder Business Model Canvas Architect
+
+## Overview
+A specialized architectural tool for designing and auditing business models using Alexander Osterwalder’s 9-block framework. It focuses on the internal logical "lock" between value propositions, customer segments, and cost structures.
+
+## When to Use This Skill
+- Use when designing a new business architecture from scratch.
+- Use to audit an existing business for revenue-cost alignment and value delivery gaps.
+- Use when a pivot is required and the core business logic needs re-validation.
+
+## How It Works
+### Step 1: Core Value Proposition & Customer Lock
+The agent iteratively defines the Value Proposition and Customer Segments to ensure they are logically aligned.
+### Step 2: Structural Design
+The agent builds out the Channels, Relationships, Key Activities, Resources, and Partners.
+### Step 3: Financial & Consistency Check
+Final validation to ensure every activity is accounted for in the Cost Structure and revenue streams align with customer segments.
+
+## Examples
+
+### Example 1: Subscription-based SaaS (Runnable)
+"Draft a Business Model Canvas for an AI-powered agri-tech platform that provides soil analysis for large-scale farmers on a subscription basis. Focus on how the Key Resources (IoT/AI) drive the Cost Structure."
+
+### Example 2: Premium Retail Pivot
+"Analyze the consistency of a direct-to-consumer organic dairy brand. Ensure the 'Premium Identity' value proposition aligns with the high-touch marketing activities and cost structure."
+
+## Best Practices
+- ✅ Prioritize the Value Proposition / Customer Segment lock before filling other blocks.
+- ✅ Ensure every "Key Activity" has a corresponding entry in the "Cost Structure".
+- ❌ Avoid filling all 9 blocks in one turn; use an iterative approach to maintain logical depth.
+
+## Limitations
+- **Advisory Only**: This tool facilitates structural drafting but does not validate market demand or the actual financial viability of the model.
+- **Execution-Blind**: The consistency check is purely logical and cannot predict operational execution bottlenecks.
+- **Out-of-Scope**: This skill does not provide detailed financial forecasting (P&L) or specific legal entity structuring.
PATCH

echo "Gold patch applied."
