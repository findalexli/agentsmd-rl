#!/usr/bin/env bash
set -euo pipefail

cd /workspace/skills

# Idempotency guard
if grep -qF "description: \"Diagnoses and improves Qdrant search relevance. Use when someone r" "skills/qdrant-search-quality/SKILL.md" && grep -qF "description: \"Diagnoses Qdrant search quality issues. Use when someone reports '" "skills/qdrant-search-quality/diagnosis/SKILL.md" && grep -qF "description: \"Guides Qdrant search strategy selection. Use when someone asks 'sh" "skills/qdrant-search-quality/search-strategies/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/qdrant-search-quality/SKILL.md b/skills/qdrant-search-quality/SKILL.md
@@ -1,41 +1,24 @@
 ---
 name: qdrant-search-quality
-description: "Guidance on how to improve the search quality in Qdrant, including tips on tuning parameters, and applying information retrieval best practices. Use when you want to enhance the relevance and accuracy of search results in your Qdrant deployment."
+description: "Diagnoses and improves Qdrant search relevance. Use when someone reports 'search results are bad', 'wrong results', 'low precision', 'low recall', 'irrelevant matches', 'missing expected results', or asks 'how to improve search quality?', 'which embedding model?', 'should I use hybrid search?', 'should I use reranking?'. Also use when search quality degrades after quantization, model change, or data growth."
 allowed-tools:
   - Read
   - Grep
   - Glob
 ---
 
-
-
 # Qdrant Search Quality
 
-Search quality is a critical aspect of any vector search system, including Qdrant. Qdrant supports a variety of techniques to improve search quality.
-Choice of the right technique depends on the specific use case and requirements of your application.
- This document serves as a navigation hub for different techniques to improve search quality in Qdrant.
-
-
-## Identifying Source of Search Quality Issues
-
-<!-- ToDo -->
-
-## Tuning Vector Index Parameters
-
-<!-- ToDo -->
-
-## Choosing Right Embedding Model
+First determine whether the problem is the embedding model, Qdrant configuration, or the query strategy. Most quality issues come from the model or data, not from Qdrant itself. If search quality is low, inspect how chunks are being passed to Qdrant before tuning any parameters. Splitting mid-sentence can drop quality 30-40%.
 
-<!-- ToDo -->
+- Start by testing with exact search to isolate the problem [Search API](https://qdrant.tech/documentation/concepts/search/#search-api)
 
-## Whether to use hybrid search
 
-<!-- ToDo -->
+## Diagnosis and Tuning
 
-## Whether to use reranking
+Isolate the source of quality issues, tune HNSW parameters, and choose the right embedding model. [Diagnosis and Tuning](diagnosis/SKILL.md)
 
-<!-- ToDo -->
 
-## Whether to use relevance feedback
+## Search Strategies
 
-<!-- ToDo -->
\ No newline at end of file
+Hybrid search, reranking, relevance feedback, and exploration APIs for improving result quality. [Search Strategies](search-strategies/SKILL.md)
diff --git a/skills/qdrant-search-quality/diagnosis/SKILL.md b/skills/qdrant-search-quality/diagnosis/SKILL.md
@@ -0,0 +1,51 @@
+---
+name: qdrant-search-quality-diagnosis
+description: "Diagnoses Qdrant search quality issues. Use when someone reports 'results are bad', 'wrong results', 'missing matches', 'recall is low', 'approximate search worse than exact', 'which embedding model', or 'quality dropped after quantization'. Also use when search quality degrades without obvious changes."
+---
+
+# How to Diagnose Bad Search Quality
+
+Before tuning, establish baselines. Use exact KNN as ground truth, compare against approximate HNSW. Target >95% recall@K for production.
+
+
+## Don't Know What's Wrong Yet
+
+Use when: results are irrelevant or missing expected matches and you need to isolate the cause.
+
+- Test with `exact=true` to bypass HNSW approximation [Search API](https://qdrant.tech/documentation/concepts/search/#nearest-neighbors-search)
+- Exact search bad = model problem. Exact good, approximate bad = tune HNSW.
+- Check if quantization degrades quality (compare with and without)
+- Check if filters are too restrictive
+- If duplicate results from chunked documents, use Grouping API to deduplicate [Grouping](https://qdrant.tech/documentation/concepts/search/#grouping-api)
+
+Payload filtering and sparse vector search are different things. Metadata (dates, categories, tags) goes in payload for filtering. Text content goes in vectors for search. Do not embed metadata.
+
+
+## Approximate Search Worse Than Exact
+
+Use when: exact search returns good results but HNSW approximation misses them.
+
+- Increase `hnsw_ef` at query time [Search params](https://qdrant.tech/documentation/guides/optimize/#fine-tuning-search-parameters)
+- Increase `ef_construct` (200+ for high quality) [HNSW config](https://qdrant.tech/documentation/concepts/indexing/#vector-index)
+- Increase `m` (16 default, 32 for high recall) [HNSW config](https://qdrant.tech/documentation/concepts/indexing/#vector-index)
+- Enable oversampling + rescore with quantization [Search with quantization](https://qdrant.tech/documentation/guides/quantization/#searching-with-quantization)
+- ACORN for filtered queries (v1.16+) [ACORN](https://qdrant.tech/documentation/concepts/search/#acorn-search-algorithm)
+
+Binary quantization requires rescore. Without it, quality loss is severe. Use oversampling (3-5x minimum for binary) to recover recall. Always test quantization impact on your data before production. [Quantization](https://qdrant.tech/documentation/guides/quantization/)
+
+
+## Wrong Embedding Model
+
+Use when: exact search also returns bad results.
+
+Test top 3 MTEB models on 100-1000 sample queries, measure recall@10. Domain-specific models outperform general models. [Hosted inference](https://qdrant.tech/documentation/concepts/inference/)
+
+
+## What NOT to Do
+
+- Tune Qdrant before verifying the model is right (most quality issues are model issues)
+- Use binary quantization without rescore (severe quality loss)
+- Set `hnsw_ef` lower than results requested (guaranteed bad recall)
+- Skip payload indexes on filtered fields then blame quality (HNSW can't traverse filtered-out nodes)
+- Deploy without baseline recall metrics (no way to measure regressions)
+- Confuse payload filtering with sparse vector search (different things, different config)
diff --git a/skills/qdrant-search-quality/search-strategies/SKILL.md b/skills/qdrant-search-quality/search-strategies/SKILL.md
@@ -0,0 +1,67 @@
+---
+name: qdrant-search-strategies
+description: "Guides Qdrant search strategy selection. Use when someone asks 'should I use hybrid search?', 'BM25 or sparse vectors?', 'how to rerank?', 'results too similar', 'need diversity', 'MMR', 'relevance feedback', 'recommendation API', 'discovery API', 'ColBERT reranking', or 'missing keyword matches'. Also use when initial retrieval quality is acceptable but result ordering needs improvement."
+---
+
+# How to Improve Search Results with Advanced Strategies
+
+These strategies complement basic vector search. Use them after confirming the embedding model and HNSW config are correct. If exact search returns bad results, fix the model first.
+
+
+## Missing Obvious Keyword Matches
+
+Use when: pure vector search misses results that contain obvious keyword matches.
+
+Use hybrid when: domain terminology not in embedding training data, exact keyword matching critical (brand names, SKUs), acronyms common. Skip when: pure semantic queries, all data in training set, latency budget very tight.
+
+- Dense + sparse with `prefetch` and fusion [Hybrid search](https://qdrant.tech/documentation/concepts/hybrid-queries/#hybrid-search)
+- Prefer learned sparse (Splade, GTE) over raw BM25
+- RRF: good default, supports weighted (v1.17+) [RRF](https://qdrant.tech/documentation/concepts/hybrid-queries/#reciprocal-rank-fusion-rrf)
+- DBSF with asymmetric limits (sparse_limit=250, dense_limit=100) can outperform RRF for technical docs [DBSF](https://qdrant.tech/documentation/concepts/hybrid-queries/#distribution-based-score-fusion-dbsf)
+
+For non-English languages, sparse BM25 without stop-word removal produces severely degraded results. Pre-process text before generating sparse vectors.
+
+
+## Right Documents Found But Wrong Order
+
+Use when: good recall but poor precision (right docs in top-100, not top-10).
+
+- Cross-encoder rerankers via FastEmbed [Rerankers](https://qdrant.tech/documentation/fastembed/fastembed-rerankers/)
+- ColBERT reranking can promote documents from mid-list to #1. Does not require GPU at query time. [Multi-stage](https://qdrant.tech/documentation/concepts/hybrid-queries/#multi-stage-queries)
+
+
+## Results Too Similar
+
+Use when: top results are redundant, near-duplicates, or lack diversity. Common in dense content domains (academic papers, product catalogs).
+
+- Use MMR (v1.15+) as a query parameter with `diversity` to balance relevance and diversity [MMR](https://qdrant.tech/documentation/search/search-relevance/#maximal-marginal-relevance-mmr)
+- Start with `diversity=0.5`, lower for more precision, higher for more exploration
+- MMR is slower than standard search. Only use when redundancy is an actual problem.
+
+
+## Want to Steer Search with Feedback
+
+Use when: you have a retrieval pipeline in place and want to use feedback signals to guide the next retrieval iteration.
+
+- Use Relevance Feedback Query (v1.17+) to adjust retrieval based on relevance scores [Relevance Feedback](https://qdrant.tech/documentation/concepts/search-relevance/#relevance-feedback)
+- Customize strategy parameters for your data with [qdrant-relevance-feedback package](https://pypi.org/project/qdrant-relevance-feedback/)
+- Verify it actually helps with the built-in evaluator before deploying
+- End-to-end tutorial [Using Relevance Feedback](https://qdrant.tech/documentation/tutorials-search-engineering/using-relevance-feedback/)
+
+
+## Have Examples of Good and Bad Results
+
+Use when: you can provide positive and negative example points to steer search, but don't have a feedback model.
+
+- Recommendation API: positive/negative examples to find similar vectors [Recommendation API](https://qdrant.tech/documentation/concepts/explore/#recommendation-api)
+  - Best score strategy: better for diverse examples, supports negative-only [Best score](https://qdrant.tech/documentation/concepts/explore/#best-score-strategy)
+- Discovery API: context pairs to constrain search regions without a target [Discovery](https://qdrant.tech/documentation/concepts/explore/#discovery-api)
+
+
+## What NOT to Do
+
+- Use hybrid search before verifying pure vector quality (adds complexity, may mask model issues)
+- Use BM25 on non-English text without stop-word removal (severely degraded results)
+- Skip evaluation when adding relevance feedback (measure that it actually helps)
+- Confuse Relevance Feedback Query with Recommendation API (different mechanisms, different use cases)
+- Rerank without oversampling (if you only retrieve 10 candidates, reranking 10 items is pointless)
PATCH

echo "Gold patch applied."
