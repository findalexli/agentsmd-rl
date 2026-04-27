#!/usr/bin/env bash
set -euo pipefail

cd /workspace/skills

# Idempotency guard
if grep -qF "Use when: you have a retrieval pipeline in place but results aren't getting bett" "skills/qdrant-search-quality/search-strategies/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/qdrant-search-quality/search-strategies/SKILL.md b/skills/qdrant-search-quality/search-strategies/SKILL.md
@@ -39,19 +39,19 @@ Use when: top results are redundant, near-duplicates, or lack diversity. Common
 - MMR is slower than standard search. Only use when redundancy is an actual problem.
 
 
-## Want to Steer Search with Feedback
+## Results Don't Improve Between Iterations
 
-Use when: you have a retrieval pipeline in place and want to use feedback signals to guide the next retrieval iteration.
+Use when: you have a retrieval pipeline in place but results aren't getting better across search iterations.
 
 - Use Relevance Feedback Query (v1.17+) to adjust retrieval based on relevance scores [Relevance Feedback](https://qdrant.tech/documentation/concepts/search-relevance/#relevance-feedback)
 - Customize strategy parameters for your data with [qdrant-relevance-feedback package](https://pypi.org/project/qdrant-relevance-feedback/)
 - Verify it actually helps with the built-in evaluator before deploying
 - End-to-end tutorial [Using Relevance Feedback](https://qdrant.tech/documentation/tutorials-search-engineering/using-relevance-feedback/)
 
 
-## Have Examples of Good and Bad Results
+## Know What Good Results Look Like But Can't Get Them
 
-Use when: you can provide positive and negative example points to steer search, but don't have a feedback model.
+Use when: you can provide positive and negative example points but don't have a feedback model.
 
 - Recommendation API: positive/negative examples to find similar vectors [Recommendation API](https://qdrant.tech/documentation/concepts/explore/#recommendation-api)
   - Best score strategy: better for diverse examples, supports negative-only [Best score](https://qdrant.tech/documentation/concepts/explore/#best-score-strategy)
PATCH

echo "Gold patch applied."
