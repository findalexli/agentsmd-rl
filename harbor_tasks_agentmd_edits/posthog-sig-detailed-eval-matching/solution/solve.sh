#!/usr/bin/env bash
set -euo pipefail

cd /workspace/posthog

# Idempotent: skip if already applied
if grep -q 'correct_match_pre_specificity' products/signals/eval/eval_grouping_e2e.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/products/signals/eval/AGENTS.md b/products/signals/eval/AGENTS.md
index 6d1e188db5ad..c2599eb66eff 100644
--- a/products/signals/eval/AGENTS.md
+++ b/products/signals/eval/AGENTS.md
@@ -78,14 +78,14 @@ Followed by an aggregate results summary table.
 All metrics are captured as `$ai_evaluation` events with source `signals-grouping`.
 Five eval experiments, each with their own metrics:

-| Experiment                     | Granularity | Metrics                                                                                      |
-| ------------------------------ | ----------- | -------------------------------------------------------------------------------------------- |
-| `match-quality`                | Per-signal  | `correct_match` (binary), failure mode: NONE/UNDERGROUP/OVERGROUP/SPECIFICITY_SPLIT          |
-| `{source}-actionability-check` | Per-signal  | `correct_classification` (binary) — did pre-emit filter agree with ground truth              |
-| `grouping-quality`             | Per-report  | `purity`, `is_pure`, `group_recall`                                                          |
-| `report-safety-check`          | Per-report  | `correct_classification` (binary) — safety judge vs ground truth                             |
-| `report-actionability-check`   | Per-report  | `correct_classification` (binary) — actionability judge vs ground truth                      |
-| `grouping-aggregate`           | Global      | `ari`, `homogeneity`, `completeness`, `mean_purity`, `group_recall`, `malicious_leaked_rate` |
+| Experiment                     | Granularity | Metrics                                                                                                                                                                                                 |
+| ------------------------------ | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
+| `match-quality`                | Per-signal  | `correct_match` (binary), `correct_match_pre_specificity` (binary), failure mode: NONE/UNDERGROUP/OVERGROUP, `query_diversity` (numeric, cosine distance), `candidate_diversity` (numeric, 1 − Jaccard) |
+| `{source}-actionability-check` | Per-signal  | `correct_classification` (binary) — did pre-emit filter agree with ground truth                                                                                                                         |
+| `grouping-quality`             | Per-report  | `purity`, `is_pure`, `group_recall`                                                                                                                                                                     |
+| `report-safety-check`          | Per-report  | `correct_classification` (binary) — safety judge vs ground truth                                                                                                                                        |
+| `report-actionability-check`   | Per-report  | `correct_classification` (binary) — actionability judge vs ground truth                                                                                                                                 |
+| `grouping-aggregate`           | Global      | `ari`, `homogeneity`, `completeness`, `mean_purity`, `group_recall`, `malicious_leaked_rate`                                                                                                            |

 ### Aggregate metrics explained

@@ -161,7 +161,6 @@ SELECT
     multiIf(
         properties.$ai_score = 1.0, 'CORRECT',
         properties.$ai_reasoning LIKE '%UNDERGROUP%', 'UNDERGROUP',
-        properties.$ai_reasoning LIKE '%SPECIFICITY_SPLIT%', 'SPECIFICITY_SPLIT',
         properties.$ai_reasoning LIKE '%OVERGROUP%', 'OVERGROUP',
         'UNKNOWN'
     ) AS failure_mode,
@@ -177,6 +176,58 @@ GROUP BY failure_mode
 ORDER BY cnt DESC
 ```

+### Specificity judge impact
+
+Compares pre- and post-specificity correctness to show
+how often the specificity judge helps (prevents overgroup),
+hurts (causes undergroup), or has no effect.
+
+```sql
+SELECT
+    multiIf(
+        pre.score = 1.0 AND post.score = 1.0, 'no_effect_correct',
+        pre.score = 0.0 AND post.score = 0.0 AND pre.reasoning = post.reasoning, 'no_effect_wrong',
+        pre.score = 0.0 AND post.score = 1.0, 'prevented_overgroup',
+        pre.score = 1.0 AND post.score = 0.0, 'caused_undergroup',
+        pre.score = 0.0 AND post.score = 0.0, 'changed_failure_mode',
+        'unknown'
+    ) AS specificity_impact,
+    count() AS cnt
+FROM (
+    SELECT properties.$ai_experiment_item_name AS item, properties.$ai_score AS score, properties.$ai_reasoning AS reasoning
+    FROM events
+    WHERE event = '$ai_evaluation' AND properties.$ai_eval_source = 'signals-grouping' AND properties.$ai_evaluation_type = 'offline'
+      AND properties.$ai_experiment_name = 'signals-grouping/match-quality' AND properties.$ai_metric_name = 'correct_match_pre_specificity'
+) pre
+JOIN (
+    SELECT properties.$ai_experiment_item_name AS item, properties.$ai_score AS score, properties.$ai_reasoning AS reasoning
+    FROM events
+    WHERE event = '$ai_evaluation' AND properties.$ai_eval_source = 'signals-grouping' AND properties.$ai_evaluation_type = 'offline'
+      AND properties.$ai_experiment_name = 'signals-grouping/match-quality' AND properties.$ai_metric_name = 'correct_match'
+) post ON pre.item = post.item
+GROUP BY specificity_impact
+ORDER BY cnt DESC
+```
+
+### Query and candidate diversity
+
+```sql
+SELECT
+    properties.$ai_metric_name AS metric,
+    count() AS n,
+    round(avg(properties.$ai_score), 3) AS mean,
+    round(min(properties.$ai_score), 3) AS min,
+    round(max(properties.$ai_score), 3) AS max
+FROM events
+WHERE event = '$ai_evaluation'
+  AND properties.$ai_eval_source = 'signals-grouping'
+  AND properties.$ai_evaluation_type = 'offline'
+  AND properties.$ai_experiment_name = 'signals-grouping/match-quality'
+  AND properties.$ai_metric_name IN ('query_diversity', 'candidate_diversity')
+GROUP BY metric
+ORDER BY metric
+```
+
 ### Pre-emit actionability by source type

 ```sql
diff --git a/products/signals/eval/eval_grouping_e2e.py b/products/signals/eval/eval_grouping_e2e.py
index 20fa59c03f71..64e09f1d958d 100644
--- a/products/signals/eval/eval_grouping_e2e.py
+++ b/products/signals/eval/eval_grouping_e2e.py
@@ -10,13 +10,17 @@
 injection detection) and actionability (can a coding agent act on it).

 Captures four levels of metrics:
-- Per-signal: correct_match (binary), failure_mode (categorical: NONE,
-  UNDERGROUP, OVERGROUP, SPECIFICITY_SPLIT)
+- Per-signal matching: correct_match (binary), correct_match_pre_specificity
+  (binary, LLM matcher decision before specificity judge),
+  failure_mode (categorical: NONE, UNDERGROUP, OVERGROUP),
+  query_diversity (numeric, avg pairwise cosine distance between query
+  embeddings), candidate_diversity (numeric, avg 1 − Jaccard across
+  query pairs' candidate sets)
 - Per-report grouping: purity, is_pure, group_recall
-- Per-report judges: correct_safety (binary), correct_actionability
-  (binary), actionability_choice (categorical)
-- Aggregate: ARI, homogeneity, completeness, v_measure, mean_purity,
-  mean_group_recall, unsafe_blocked_rate
+- Per-report judges: correct_classification (binary) for both
+  report-safety-check and report-actionability-check
+- Aggregate: ARI, homogeneity, completeness, mean_purity,
+  group_recall, malicious_leaked_rate

 Run:
     pytest products/signals/eval/eval_grouping_e2e.py -xvs
@@ -30,6 +34,7 @@
 import logging
 from dataclasses import dataclass
 from enum import Enum
+from itertools import combinations
 from time import time
 from typing import Any

@@ -57,6 +62,7 @@
     MatchResult,
     NewReportMatch,
     NoMatchMetadata,
+    SignalCandidate,
     SpecificityMetadata,
 )
 from products.signals.eval.capture import EvalMetric, capture_evaluation, deterministic_uuid
@@ -116,7 +122,6 @@ class MatchFailureMode(Enum):
     NONE = "NONE"  # correct match
     UNDERGROUP = "UNDERGROUP"  # created new report when should have joined existing
     OVERGROUP = "OVERGROUP"  # joined a report belonging to a different ground-truth group
-    SPECIFICITY_SPLIT = "SPECIFICITY_SPLIT"  # specificity check split a correct match


 @dataclass
@@ -223,14 +228,21 @@ async def run_signal_pipeline(self, record_id: int, case: EvalSignalCase):
                 return

             async with self._match_lock:
-                match_result, queries = await self._match(record_id, description, case)
-                await self._persist_signal(record_id, description, case, match_result, queries)
+                match_result, specificity_result, queries, query_embeddings, candidates = await self._match(
+                    record_id, description, case
+                )
+                self._capture_match_quality(
+                    case, match_result, specificity_result, queries, query_embeddings, candidates
+                )
+                await self._persist_signal(record_id, description, case, specificity_result)

             self.progress.signal_done()
         except Exception:
             self.progress.signal_dropped()

-    async def _match(self, record_id: int, description: str, case: EvalSignalCase) -> tuple[MatchResult, list[str]]:
+    async def _match(
+        self, record_id: int, description: str, case: EvalSignalCase
+    ) -> tuple[MatchResult, MatchResult, list[str], list[list[float]], list[list[SignalCandidate]]]:
         """Generate queries, embed, search, LLM-match, and verify specificity. No side effects."""

         queries = await generate_search_queries(
@@ -251,11 +263,12 @@ async def _match(self, record_id: int, description: str, case: EvalSignalCase) -
             query_results=candidates,
             report_contexts=self.report_store.get_contexts(),
         )
+        specificity_match_result = match_result

-        if isinstance(match_result, ExistingReportMatch):
-            report_ctx = self.report_store.get(match_result.report_id)
+        if isinstance(specificity_match_result, ExistingReportMatch):
+            report_ctx = self.report_store.get(specificity_match_result.report_id)
             report_title = report_ctx.context.title if report_ctx else ""
-            group_signals = self.store.get_signals_for_report(match_result.report_id)
+            group_signals = self.store.get_signals_for_report(specificity_match_result.report_id)

             specificity_result = await verify_match_specificity(
                 new_signal_description=description,
@@ -272,9 +285,9 @@ async def _match(self, record_id: int, description: str, case: EvalSignalCase) -
             )

             if specificity_result.specific_enough:
-                match_result.match_metadata.specificity = specificity_meta
+                specificity_match_result.match_metadata.specificity = specificity_meta
             else:
-                match_result = NewReportMatch(
+                specificity_match_result = NewReportMatch(
                     title=description.split("\n")[0],
                     summary=f"Split from group: {report_title}",
                     match_metadata=NoMatchMetadata(
@@ -283,7 +296,7 @@ async def _match(self, record_id: int, description: str, case: EvalSignalCase) -
                     ),
                 )

-        return match_result, queries
+        return match_result, specificity_match_result, queries, query_embeddings, candidates

     async def _persist_signal(
         self,
@@ -291,13 +304,11 @@ async def _persist_signal(
         description: str,
         case: EvalSignalCase,
         match_result: MatchResult,
-        queries: list[str],
     ) -> str:
-        """Write match result to both stores and capture eval metrics."""
+        """Write match result to both stores."""

         report_id = match_result.report_id if isinstance(match_result, ExistingReportMatch) else str(uuid.uuid4())

-        self._capture_match_quality(case, report_id, match_result, queries)
         self.report_store.insert(report_id, match_result, case.group_index)

         signal_embedding = await self.store.embed(description)
@@ -383,47 +394,76 @@ async def _capture_pre_emit_actionability(self, case: EvalSignalCase, thoughts:
         )

     def _capture_match_quality(
-        self, case: EvalSignalCase, report_id: str, match_result: MatchResult, queries: list[str]
+        self,
+        case: EvalSignalCase,
+        match_result: MatchResult,
+        specificity_match_result: MatchResult,
+        queries: list[str],
+        query_embeddings: list[list[float]],
+        candidates: list[list[SignalCandidate]],
     ):
         """Captures whether the matching decision was correct and classifies the failure mode."""
-        is_existing = isinstance(match_result, ExistingReportMatch)
         expected_report = self.report_store.find_report_by_group_index(case.group_index)
         expected_id = expected_report.context.report_id if expected_report else None
-        has_specificity_rejection = (
-            isinstance(match_result, NewReportMatch) and match_result.match_metadata.specificity_rejection is not None
+        expected = "NEW_REPORT" if expected_report is None else "EXISTING_REPORT"
+
+        def evaluate_match_failure(mr: MatchResult) -> MatchFailureMode:
+            is_existing = isinstance(mr, ExistingReportMatch)
+            if expected_report is None:
+                return MatchFailureMode.OVERGROUP if is_existing else MatchFailureMode.NONE
+            if isinstance(mr, ExistingReportMatch) and mr.report_id == expected_id:
+                return MatchFailureMode.NONE
+            if is_existing:
+                return MatchFailureMode.OVERGROUP
+            return MatchFailureMode.UNDERGROUP
+
+        match_failure_mode = evaluate_match_failure(match_result)
+        specificity_failure_mode = evaluate_match_failure(specificity_match_result)
+        correct = specificity_failure_mode == MatchFailureMode.NONE
+        pre_specificity_correct = match_failure_mode == MatchFailureMode.NONE
+
+        specificity_reasoning = (
+            specificity_match_result.match_metadata.reason
+            if hasattr(specificity_match_result.match_metadata, "reason")
+            else ""
         )

-        if expected_report is None:
-            correct = not is_existing
-            expected = "NEW_REPORT"
-            if correct:
-                failure_mode = MatchFailureMode.NONE
-            else:
-                failure_mode = MatchFailureMode.OVERGROUP
+        # Query diversity: average pairwise cosine distance between query embeddings
+        if len(query_embeddings) < 2:
+            query_diversity = 0.0
         else:
-            expected = f"EXISTING_REPORT"
-
-            if isinstance(match_result, ExistingReportMatch) and match_result.report_id == expected_id:
-                failure_mode = MatchFailureMode.NONE
-                correct = True
-            elif is_existing:
-                failure_mode = MatchFailureMode.OVERGROUP
-                correct = False
-            elif has_specificity_rejection:
-                failure_mode = MatchFailureMode.SPECIFICITY_SPLIT
-                correct = False
-            else:
-                failure_mode = MatchFailureMode.UNDERGROUP
-                correct = False
-
-        reasoning = match_result.match_metadata.reason if hasattr(match_result.match_metadata, "reason") else ""
+            distances = [
+                self.store.cosine_distance(query_embeddings[i], query_embeddings[j])
+                for i, j in combinations(range(len(query_embeddings)), 2)
+            ]
+            query_diversity = sum(distances) / len(distances)
+
+        # Candidate diversity
+        if len(candidates) < 2:
+            candidate_diversity = 0.0
+        else:
+            candidate_sets = [{c.signal_id for c in cands} for cands in candidates]
+            jaccards = []
+            for i, j in combinations(range(len(candidate_sets)), 2):
+                union = candidate_sets[i] | candidate_sets[j]
+                if not union:
+                    jaccards.append(0.0)
+                else:
+                    intersection = candidate_sets[i] & candidate_sets[j]
+                    jaccards.append(1.0 - len(intersection) / len(union))
+            candidate_diversity = sum(jaccards) / len(jaccards)
+
+        is_existing = isinstance(specificity_match_result, ExistingReportMatch)
+        report_id = (
+            specificity_match_result.report_id if isinstance(specificity_match_result, ExistingReportMatch) else None
+        )

         output = {
-            "report": f"EXISTING_REPORT" if is_existing else f"NEW_REPORT",
-            "specificity_reasoning": reasoning,
+            "report": "EXISTING_REPORT" if is_existing else "NEW_REPORT",
+            "specificity_reasoning": specificity_reasoning,
             "queries": queries,
             "report_signals": [sig.content for sig in self.store.get_signals_for_report(report_id)]
-            if is_existing
+            if report_id
             else None,
         }

@@ -440,7 +480,27 @@ def _capture_match_quality(
                     score=1.0 if correct else 0.0,
                     score_min=0,
                     score_max=1,
-                    reasoning=None if correct else f"Failure mode: {failure_mode.value}",
+                    reasoning=None if correct else f"Failure mode: {specificity_failure_mode.value}",
+                ),
+                EvalMetric(
+                    name="correct_match_pre_specificity",
+                    result_type="binary",
+                    score=1.0 if pre_specificity_correct else 0.0,
+                    score_min=0,
+                    score_max=1,
+                    reasoning=None if pre_specificity_correct else f"Failure mode: {match_failure_mode.value}",
+                ),
+                EvalMetric(
+                    name="query_diversity",
+                    description="Average pairwise cosine distance between query embeddings (0 = identical, 1 = orthogonal)",
+                    result_type="numeric",
+                    score=query_diversity,
+                ),
+                EvalMetric(
+                    name="candidate_diversity",
+                    description="Average (1 - Jaccard similarity) across query pairs' candidate sets (0 = identical, 1 = disjoint)",
+                    result_type="numeric",
+                    score=candidate_diversity,
                 ),
             ],
             passed=correct,
diff --git a/products/signals/eval/mock.py b/products/signals/eval/mock.py
index 94270f38a34d..f0b33cd99bd8 100644
--- a/products/signals/eval/mock.py
+++ b/products/signals/eval/mock.py
@@ -111,21 +111,28 @@ def store(
             )
         )

+    @staticmethod
+    def cosine_distance(a: list[float], b: list[float]) -> float:
+        """Cosine distance between two vectors: 1 - cosine_similarity."""
+        va = np.array(a, dtype=np.float64)
+        vb = np.array(b, dtype=np.float64)
+        norm_product = np.linalg.norm(va) * np.linalg.norm(vb)
+        if norm_product == 0:
+            return 1.0
+        return 1.0 - float(np.dot(va, vb) / norm_product)
+
     def search(self, query_embedding: list[float], limit: int = 10) -> list[SignalCandidate]:
         """Cosine search against stored signals. Returns SignalCandidate list."""
         searchable = [s for s in self._signals if not s.deleted and s.report_id and np.linalg.norm(s.embedding) > 0]
         if not searchable:
             return []

-        q = np.array(query_embedding, dtype=np.float64)
-        q_norm = np.linalg.norm(q)
-        if q_norm == 0:
+        if np.linalg.norm(query_embedding) == 0:
             return []

         scored: list[tuple[float, StoredSignal]] = []
         for sig in searchable:
-            s = np.array(sig.embedding, dtype=np.float64)
-            dist = 1.0 - float(np.dot(q, s) / (q_norm * np.linalg.norm(s)))
+            dist = self.cosine_distance(query_embedding, sig.embedding)
             scored.append((dist, sig))

         scored.sort(key=lambda x: x[0])
diff --git a/products/signals/eval/reports/2026-03-17.md b/products/signals/eval/reports/2026-03-17.md
new file mode 100644
index 000000000000..7b603af5afe9
--- /dev/null
+++ b/products/signals/eval/reports/2026-03-17.md
@@ -0,0 +1,90 @@
+# 2026-03-17
+
+91 signals, 41 ground-truth groups, 37 reports produced.
+
+## Aggregate metrics
+
+| Metric                | Score        |
+| --------------------- | ------------ |
+| ARI                   | 0.754        |
+| Homogeneity           | 0.990        |
+| Completeness          | 0.932        |
+| Mean purity           | 0.993        |
+| Mean group recall     | 0.775        |
+| Malicious leaked rate | 0.000 (0/24) |
+
+## Match quality
+
+67 signals matched (24 dropped by safety filter).
+
+| Failure mode | Count | % of total |
+| ------------ | ----- | ---------- |
+| CORRECT      | 55    | 82.1%      |
+| UNDERGROUP   | 8     | 11.9%      |
+| OVERGROUP    | 4     | 6.0%       |
+
+### Pre-specificity (LLM matcher before specificity judge)
+
+| Failure mode | Count | % of total |
+| ------------ | ----- | ---------- |
+| CORRECT      | 46    | 68.7%      |
+| OVERGROUP    | 18    | 26.9%      |
+| UNDERGROUP   | 3     | 4.5%       |
+
+The specificity judge converted 14 overgroups into correct matches and
+introduced 5 new undergroups (net: +9 correct, from 68.7% to 82.1%).
+
+## Retrieval diversity
+
+| Metric              | n   | Mean  | Min   | Max   |
+| ------------------- | --- | ----- | ----- | ----- |
+| query_diversity     | 67  | 0.465 | 0.289 | 0.652 |
+| candidate_diversity | 67  | 0.445 | 0.000 | 0.858 |
+
+Queries are moderately diverse (mean cosine distance 0.47),
+and different queries retrieve partially overlapping but distinct
+candidate sets (mean 1 − Jaccard 0.45).
+
+## Pre-emit actionability by source
+
+| Source  | Total | Correct | Failure rate | FP  | FN  |
+| ------- | ----- | ------- | ------------ | --- | --- |
+| Zendesk | 44    | 32      | 27.3%        | 12  | 0   |
+| GitHub  | 29    | 19      | 34.5%        | 10  | 0   |
+| Linear  | 18    | 12      | 33.3%        | 6   | 0   |
+
+All failures are false positives (passed signals that should have been
+filtered). No false negatives — no actionable signals are being dropped.
+
+## Report-level judges
+
+| Judge         | Total | Correct | Accuracy | FP  | FN  |
+| ------------- | ----- | ------- | -------- | --- | --- |
+| Safety        | 37    | 37      | 100.0%   | 0   | 0   |
+| Actionability | 37    | 30      | 81.1%    | 7   | 0   |
+
+Safety judge is now perfect (was 90.7% on 2026-03-16).
+Actionability improved from 64.8% to 81.1%.
+
+## Per-report grouping quality
+
+| Metric       | n   | Mean          | Min   | Max   |
+| ------------ | --- | ------------- | ----- | ----- |
+| Purity       | 37  | 0.993         | 0.750 | 1.000 |
+| Is pure      | 37  | 36/37 (97.3%) | -     | -     |
+| Group recall | 37  | 0.775         | 0.333 | 1.000 |
+
+## Comparison to 2026-03-16
+
+| Metric            | 03-16 | 03-17 | Delta   |
+| ----------------- | ----- | ----- | ------- |
+| ARI               | 0.706 | 0.754 | +0.048  |
+| Homogeneity       | 0.992 | 0.990 | −0.002  |
+| Completeness      | 0.907 | 0.932 | +0.025  |
+| Mean purity       | 0.995 | 0.993 | −0.002  |
+| Mean group recall | 0.679 | 0.775 | +0.096  |
+| Malicious leaked  | 5/24  | 0/24  | −5      |
+| Reports produced  | 54    | 37    | −17     |
+| Match accuracy    | 76.0% | 82.1% | +6.1pp  |
+| Safety accuracy   | 90.7% | 100%  | +9.3pp  |
+| Actionability acc | 64.8% | 81.1% | +16.3pp |

PATCH

echo "Patch applied successfully."
