#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-skills

# Idempotency guard
if grep -qF "**Smaller models (Haiku-class):** Templates provide the most value. On CVE-2026-" "reasoning-semiformally/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/reasoning-semiformally/SKILL.md b/reasoning-semiformally/SKILL.md
@@ -27,6 +27,22 @@ Skip when:
 - Change is trivial (docs, formatting, version bumps)
 - No execution paths cross scope boundaries
 
+## Model-Tier Considerations
+
+Template value is model-capability-dependent, not just reasoning-distance-dependent.
+
+**Smaller models (Haiku-class):** Templates provide the most value. On CVE-2026-29000 (383-line JWT auth bypass), Haiku went from 80% → 100% fault localization with the template (+20pp). The template forces execution tracing that the model wouldn't do unprompted.
+
+**Larger models (Sonnet-class):** Templates can add overhead on bugs the model already handles. Same CVE, Sonnet scored 100% standard but 80% with the template (-20pp). The structured format consumed tokens that the model would have used for reasoning.
+
+**Cost optimization:** Haiku + semi-formal ≈ Sonnet standard, at ~1/10th the cost. When using sub-agents for verification (e.g., verify_patch), consider Haiku + template instead of Sonnet + standard prompting.
+
+**Decision framework:**
+- Bug seems hard (cross-scope, cross-file, architectural) + using a smaller model → apply template
+- Bug seems hard + using a frontier model → apply template (net positive expected)
+- Bug seems tractable + using a frontier model → skip template (overhead may hurt)
+- Cost-sensitive workflow → use smaller model + template
+
 ## Templates
 
 Three templates for different tasks. Each follows the certificate pattern: premises → mandatory traces → formal conclusion.
@@ -134,4 +150,5 @@ Each template output feeds the next as premises.
 
 - Paper: Ugare & Chandra, "Agentic Code Reasoning with Semi-Formal Certificates" (arXiv:2603.01896, March 2026)
 - Replication: Validated on Django name-shadowing (0%→100% fault localization) and 3 real bugs from private repos (+11pp aggregate)
+- CVE validation: CVE-2026-29000 (pac4j-jwt, CVSS 10.0, 383 lines). Haiku: +20pp with template. Sonnet: -20pp (template overhead). Finding: value is model-tier-dependent.
 - Blog: austegard.com/blog/replicating-agentic-code-reasoning/
PATCH

echo "Gold patch applied."
