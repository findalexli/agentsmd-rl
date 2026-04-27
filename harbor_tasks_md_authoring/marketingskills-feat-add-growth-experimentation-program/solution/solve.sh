#!/usr/bin/env bash
set -euo pipefail

cd /workspace/marketingskills

# Idempotency guard
if grep -qF "description: When the user wants to plan, design, or implement an A/B test or ex" "skills/ab-test-setup/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/ab-test-setup/SKILL.md b/skills/ab-test-setup/SKILL.md
@@ -1,8 +1,8 @@
 ---
 name: ab-test-setup
-description: When the user wants to plan, design, or implement an A/B test or experiment. Also use when the user mentions "A/B test," "split test," "experiment," "test this change," "variant copy," "multivariate test," "hypothesis," "should I test this," "which version is better," "test two versions," "statistical significance," or "how long should I run this test." Use this whenever someone is comparing two approaches and wants to measure which performs better. For tracking implementation, see analytics-tracking. For page-level conversion optimization, see page-cro.
+description: When the user wants to plan, design, or implement an A/B test or experiment, or build a growth experimentation program. Also use when the user mentions "A/B test," "split test," "experiment," "test this change," "variant copy," "multivariate test," "hypothesis," "should I test this," "which version is better," "test two versions," "statistical significance," "how long should I run this test," "growth experiments," "experiment velocity," "experiment backlog," "ICE score," "experimentation program," or "experiment playbook." Use this whenever someone is comparing two approaches and wants to measure which performs better, or when they want to build a systematic experimentation practice. For tracking implementation, see analytics-tracking. For page-level conversion optimization, see page-cro.
 metadata:
-  version: 1.1.0
+  version: 1.2.0
 ---
 
 # A/B Test Setup
@@ -229,6 +229,93 @@ Document every test with:
 
 ---
 
+## Growth Experimentation Program
+
+Individual tests are valuable. A continuous experimentation program is a compounding asset. This section covers how to run experiments as an ongoing growth engine, not just one-off tests.
+
+### The Experiment Loop
+
+```
+1. Generate hypotheses (from data, research, competitors, customer feedback)
+2. Prioritize with ICE scoring
+3. Design and run the test
+4. Analyze results with statistical rigor
+5. Promote winners to a playbook
+6. Generate new hypotheses from learnings
+→ Repeat
+```
+
+### Hypothesis Generation
+
+Feed your experiment backlog from multiple sources:
+
+| Source | What to Look For |
+|--------|-----------------|
+| Analytics | Drop-off points, low-converting pages, underperforming segments |
+| Customer research | Pain points, confusion, unmet expectations |
+| Competitor analysis | Features, messaging, or UX patterns they use that you don't |
+| Support tickets | Recurring questions or complaints about conversion flows |
+| Heatmaps/recordings | Where users hesitate, rage-click, or abandon |
+| Past experiments | "Significant loser" tests often reveal new angles to try |
+
+### ICE Prioritization
+
+Score each hypothesis 1-10 on three dimensions:
+
+| Dimension | Question |
+|-----------|----------|
+| **Impact** | If this works, how much will it move the primary metric? |
+| **Confidence** | How sure are we this will work? (Based on data, not gut.) |
+| **Ease** | How fast and cheap can we ship and measure this? |
+
+**ICE Score** = (Impact + Confidence + Ease) / 3
+
+Run highest-scoring experiments first. Re-score monthly as context changes.
+
+### Experiment Velocity
+
+Track your experimentation rate as a leading indicator of growth:
+
+| Metric | Target |
+|--------|--------|
+| Experiments launched per month | 4-8 for most teams |
+| Win rate | 20-30% is common for mature programs (sustained higher rates may indicate conservative hypotheses) |
+| Average test duration | 2-4 weeks |
+| Backlog depth | 20+ hypotheses queued |
+| Cumulative lift | Compound gains from all winners |
+
+### The Experiment Playbook
+
+When a test wins, don't just implement it — document the pattern:
+
+```
+## [Experiment Name]
+**Date**: [date]
+**Hypothesis**: [the hypothesis]
+**Sample size**: [n per variant]
+**Result**: [winner/loser/inconclusive] — [primary metric] changed by [X%] (95% CI: [range], p=[value])
+**Guardrails**: [any guardrail metrics and their outcomes]
+**Segment deltas**: [notable differences by device, segment, or cohort]
+**Why it worked/failed**: [analysis]
+**Pattern**: [the reusable insight — e.g., "social proof near pricing CTAs increases plan selection"]
+**Apply to**: [other pages/flows where this pattern might work]
+**Status**: [implemented / parked / needs follow-up test]
+```
+
+Over time, your playbook becomes a library of proven growth patterns specific to your product and audience.
+
+### Experiment Cadence
+
+**Weekly (30 min)**: Review running experiments for technical issues and guardrail metrics. Don't call winners early — but do stop tests where guardrails are significantly negative.
+
+**Bi-weekly**: Conclude completed experiments. Analyze results, update playbook, launch next experiment from backlog.
+
+**Monthly (1 hour)**: Review experiment velocity, win rate, cumulative lift. Replenish hypothesis backlog. Re-prioritize with ICE.
+
+**Quarterly**: Audit the playbook. Which patterns have been applied broadly? Which winning patterns haven't been scaled yet? What areas of the funnel are under-tested?
+
+---
+
 ## Common Mistakes
 
 ### Test Design
PATCH

echo "Gold patch applied."
