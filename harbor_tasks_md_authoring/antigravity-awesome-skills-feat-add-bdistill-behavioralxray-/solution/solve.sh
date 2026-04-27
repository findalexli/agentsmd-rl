#!/usr/bin/env bash
set -euo pipefail

cd /workspace/antigravity-awesome-skills

# Idempotency guard
if grep -qF "bdistill's Behavioral X-Ray runs 30 carefully designed probe questions across 6 " "skills/bdistill-behavioral-xray/SKILL.md" && grep -qF "bdistill turns your AI subscription sessions into a compounding knowledge base. " "skills/bdistill-knowledge-extraction/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/bdistill-behavioral-xray/SKILL.md b/skills/bdistill-behavioral-xray/SKILL.md
@@ -0,0 +1,86 @@
+---
+name: bdistill-behavioral-xray
+description: "X-ray any AI model's behavioral patterns — refusal boundaries, hallucination tendencies, reasoning style, formatting defaults. No API key needed."
+category: ai-testing
+risk: safe
+source: community
+date_added: "2026-03-20"
+author: FrancyJGLisboa
+tags: [ai, testing, behavioral-analysis, model-evaluation, red-team, compliance, mcp]
+tools: [claude, cursor, codex, copilot]
+---
+
+# Behavioral X-Ray
+
+Systematically probe an AI model's behavioral patterns and generate a visual report. The AI agent probes *itself* — no API key or external setup needed.
+
+## Overview
+
+bdistill's Behavioral X-Ray runs 30 carefully designed probe questions across 6 dimensions, auto-tags each response with behavioral metadata, and compiles results into a styled HTML report with radar charts and actionable insights.
+
+Use it to understand your model before building with it, compare models for task selection, or track behavioral drift over time.
+
+## When to Use This Skill
+
+- Use when you want to understand how your AI model actually behaves (not how it claims to)
+- Use when choosing between models for a specific task
+- Use when debugging unexpected refusals, hallucinations, or formatting issues
+- Use for compliance auditing — documenting model behavior at deployment boundaries
+- Use for red team assessments — systematic boundary mapping across safety dimensions
+
+## How It Works
+
+### Step 1: Install
+
+```bash
+pip install bdistill
+claude mcp add bdistill -- bdistill-mcp   # Claude Code
+```
+
+For other tools, add bdistill-mcp as an MCP server in your project config.
+
+### Step 2: Run the probe
+
+In Claude Code:
+```
+/xray                          # Full behavioral probe (30 questions)
+/xray --dimensions refusal     # Probe just one dimension
+/xray-report                   # Generate report from completed probe
+```
+
+In any tool with MCP:
+```
+"X-ray your behavioral patterns"
+"Test your refusal boundaries"
+"Generate a behavioral report"
+```
+
+## Probe Dimensions
+
+| Dimension | What it measures |
+|-----------|-----------------|
+| **tool_use** | When does it call tools vs. answer from knowledge? |
+| **refusal** | Where does it draw safety boundaries? Does it over-refuse? |
+| **formatting** | Lists vs. prose? Code blocks? Length calibration? |
+| **reasoning** | Does it show chain-of-thought? Handle trick questions? |
+| **persona** | Identity, tone matching, composure under hostility |
+| **grounding** | Hallucination resistance, fabrication traps, knowledge limits |
+
+## Output
+
+A styled HTML report showing:
+- Refusal rate, hedge rate, chain-of-thought usage
+- Per-dimension breakdown with bar charts
+- Notable response examples with behavioral tags
+- Actionable insights (e.g., "you already show CoT 85% of the time, no need to prompt for it")
+
+## Best Practices
+
+- Answer probe questions honestly — the value is in authentic behavioral data
+- Run probes on the same model periodically to track behavioral drift
+- Compare reports across models to make informed selection decisions
+- Use adversarial knowledge extraction (`/distill --adversarial`) alongside behavioral probes for complete model profiling
+
+## Related Skills
+
+- `@bdistill-knowledge-extraction` - Extract structured domain knowledge from any AI model
diff --git a/skills/bdistill-knowledge-extraction/SKILL.md b/skills/bdistill-knowledge-extraction/SKILL.md
@@ -0,0 +1,105 @@
+---
+name: bdistill-knowledge-extraction
+description: "Extract structured domain knowledge from AI models in-session or from local open-source models via Ollama. No API key needed."
+category: ai-research
+risk: safe
+source: community
+date_added: "2026-03-20"
+author: FrancyJGLisboa
+tags: [ai, knowledge-extraction, domain-specific, data-moat, mcp, reference-data]
+tools: [claude, cursor, codex, copilot]
+---
+
+# Knowledge Extraction
+
+Extract structured, quality-scored domain knowledge from any AI model — in-session from closed models (no API key) or locally from open-source models via Ollama.
+
+## Overview
+
+bdistill turns your AI subscription sessions into a compounding knowledge base. The agent answers targeted domain questions, bdistill structures and quality-scores the responses, and the output accumulates into a searchable, exportable reference dataset.
+
+Adversarial mode challenges the agent's claims — forcing evidence, corrections, and acknowledged limitations — producing validated knowledge entries.
+
+## When to Use This Skill
+
+- Use when you need structured reference data on any domain (medical, legal, finance, cybersecurity)
+- Use when building lookup tables, Q&A datasets, or research corpora
+- Use when generating training data for traditional ML models (regression, classification — NOT competing LLMs)
+- Use when you want cross-model comparison on domain knowledge
+
+## How It Works
+
+### Step 1: Install
+
+```bash
+pip install bdistill
+claude mcp add bdistill -- bdistill-mcp   # Claude Code
+```
+
+### Step 2: Extract knowledge in-session
+
+```
+/distill medical cardiology                    # Preset domain
+/distill --custom kubernetes docker helm       # Custom terms
+/distill --adversarial medical                 # With adversarial validation
+```
+
+### Step 3: Search, export, compound
+
+```bash
+bdistill kb list                               # Show all domains
+bdistill kb search "atrial fibrillation"       # Keyword search
+bdistill kb export -d medical -f csv           # Export as spreadsheet
+bdistill kb export -d medical -f markdown      # Readable knowledge document
+```
+
+## Output Format
+
+Structured reference JSONL — not training data:
+
+```json
+{
+  "question": "What causes myocardial infarction?",
+  "answer": "Myocardial infarction results from acute coronary artery occlusion...",
+  "domain": "medical",
+  "category": "cardiology",
+  "tags": ["mechanistic", "evidence-based"],
+  "quality_score": 0.73,
+  "confidence": 1.08,
+  "validated": true,
+  "source_model": "Claude Sonnet 4"
+}
+```
+
+## Tabular ML Data Generation
+
+Generate structured training data for traditional ML models:
+
+```
+/schema sepsis | hr:float, bp:float, temp:float, wbc:float | risk:category[low,moderate,high,critical]
+```
+
+Exports as CSV ready for pandas/sklearn. Each row tracks source_model for cross-model analysis.
+
+## Local Model Extraction (Ollama)
+
+For open-source models running locally:
+
+```bash
+# Install Ollama from https://ollama.com
+ollama serve
+ollama pull qwen3:4b
+
+bdistill extract --domain medical --model qwen3:4b
+```
+
+## Security & Safety Notes
+
+- In-session extraction uses your existing subscription — no additional API keys
+- Local extraction runs entirely on your machine via Ollama
+- No data is sent to external services
+- Output is reference data, not LLM training format
+
+## Related Skills
+
+- `@bdistill-behavioral-xray` - X-ray a model's behavioral patterns
PATCH

echo "Gold patch applied."
