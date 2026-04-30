#!/usr/bin/env bash
set -euo pipefail

cd /workspace/skills

# Idempotency guard
if grep -qF "combining-searches/" "AGENTS.md" && grep -qF "Check [Qdrant team recommendations on how to choose an embedding model](https://" "skills/qdrant-search-quality/diagnosis/SKILL.md" && grep -qF "description: \"Guides Qdrant search strategy selection. Use when someone asks 'sh" "skills/qdrant-search-quality/search-strategies/SKILL.md" && grep -qF "description: \"Explains hybrid search in Qdrant. Use when someone asks 'how do I " "skills/qdrant-search-quality/search-strategies/hybrid-search/SKILL.md" && grep -qF "- **[DBSF](https://search.qdrant.tech/md/documentation/search/hybrid-queries/?s=" "skills/qdrant-search-quality/search-strategies/hybrid-search/combining-searches/SKILL.md" && grep -qF "If first, help user to design logic of constructing query or/and filters on appl" "skills/qdrant-search-quality/search-strategies/hybrid-search/search-types/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -33,6 +33,9 @@ skills/
     SKILL.md
     diagnosis/
     search-strategies/
+      hybrid-search/
+        search-types/
+        combining-searches/
   qdrant-monitoring/
     SKILL.md
     debugging/
diff --git a/skills/qdrant-search-quality/diagnosis/SKILL.md b/skills/qdrant-search-quality/diagnosis/SKILL.md
@@ -35,7 +35,9 @@ Binary quantization requires rescore. Without it, quality loss is severe. Use ov
 
 Use when: exact search also returns bad results.
 
-Test top 3 MTEB models on 100-1000 sample queries, measure recall@10. Domain-specific models often outperform general models. [Hosted inference](https://search.qdrant.tech/md/documentation/inference/)
+Check [Qdrant team recommendations on how to choose an embedding model](https://search.qdrant.tech/md/articles/how-to-choose-an-embedding-model/).
+
+Test top 3 MTEB models on 100-1000 sample queries. [Hosted Qdrant inference](https://search.qdrant.tech/md/documentation/inference/)
 
 ## Unoptimized Search Pipeline
 
diff --git a/skills/qdrant-search-quality/search-strategies/SKILL.md b/skills/qdrant-search-quality/search-strategies/SKILL.md
@@ -1,31 +1,29 @@
 ---
 name: qdrant-search-strategies
-description: "Guides Qdrant search strategy selection. Use when someone asks 'should I use hybrid search?', 'BM25 or sparse vectors?', 'how to rerank?', 'results are not relevant', 'I don't get needed results from my dataset but they're there', 'retrieval quality is not good enough', 'results too similar', 'need diversity', 'MMR', 'relevance feedback', 'recommendation API', 'discovery API', 'ColBERT reranking', or 'missing keyword matches'"
+description: "Guides Qdrant search strategy selection. Use when someone asks 'should I use hybrid search?', 'how to rerank?', 'results are not relevant', 'I don't get needed results from my dataset but they're there', 'retrieval quality is not good enough', 'results too similar', 'need diversity', 'MMR', 'relevance feedback', 'recommendation API', 'discovery API', or 'missing keyword matches'"
+allowed-tools:
+  - Read
+  - Grep
+  - Glob
 ---
 
 # How to Improve Search Results with Advanced Strategies
 
 These strategies complement basic vector search. Use them after confirming the embedding model is fitting the task and HNSW config is correct. If exact search returns bad results, verify the selection of the embedding model (retriever) first.
 If the user wants to use a weaker embedding model because it is small, fast, and cheap, use reranking or relevance feedback to improve search quality.
 
-## Missing Obvious Keyword Matches
+## Missing Keyword Matches or Need to Combine Multiple Search Signals
 
-Use when: pure vector search misses results that contain obvious keyword matches. Domain terminology not in embedding training data, exact keyword matching critical (brand names, SKUs), acronyms common. Skip when: pure semantic queries, all data in training set, latency budget very tight.
+Use when: pure vector search misses keyword/domain term matches, or the use case benefits from combining searches on multiple representations (including languages and modalities) of the same item.
 
-- Dense + sparse with `prefetch` and fusion [Hybrid search](https://search.qdrant.tech/md/documentation/search/hybrid-queries/?s=hybrid-search)
-- Prefer learned sparse ([miniCOIL](https://search.qdrant.tech/md/documentation/fastembed/fastembed-minicoil/), SPLADE, GTE) over raw BM25 if applicable (when user needs smart keywords matching and learned sparse models know the vocabulary of the domain)
-- For non-English languages, [configure sparse BM25 parameters accordingly](https://search.qdrant.tech/md/documentation/search/text-search/?s=language-specific-settings)
-- RRF: good default, supports weighted (v1.17+) [RRF](https://search.qdrant.tech/md/documentation/search/hybrid-queries/?s=reciprocal-rank-fusion-rrf)
-- DBSF with asymmetric limits (sparse_limit=250, dense_limit=100) can outperform RRF for technical docs [DBSF](https://search.qdrant.tech/md/documentation/search/hybrid-queries/?s=distribution-based-score-fusion-dbsf)
-- Fusion can also be done through reranking
+See how to use [hybrid search](hybrid-search/SKILL.md)
 
-## Right Documents Found But Wrong Order
+## Right Documents Found But Not in the Top Results
 
 Use when: good recall but poor precision (right docs in top-100, not top-10).
 
+- See how to use [Multistage queries](https://search.qdrant.tech/md/documentation/search/hybrid-queries/?s=multi-stage-queries), for example with late interaction rerankers through [Multivectors](https://search.qdrant.tech/md/documentation/manage-data/vectors/?s=multivectors).
 - Cross-encoder rerankers via FastEmbed [Rerankers](https://search.qdrant.tech/md/documentation/fastembed/fastembed-rerankers/)
-- See how to use [Multistage queries](https://search.qdrant.tech/md/documentation/search/hybrid-queries/?s=multi-stage-queries) in Qdrant
-- ColBERT and ColPali/ColQwen reranking is especially precise due to late interaction mechanisms, but it is heavy. It is important to configure and store multivectors without building HNSW for them to save resources. See [Multivector representation](https://search.qdrant.tech/md/documentation/tutorials-search-engineering/using-multivector-representations/)
 
 ## Right Documents Not Found But They Are There
 
@@ -50,21 +48,21 @@ Use when: top results are redundant, near-duplicates, or lack diversity. Common
 - Start with `diversity=0.5`, lower for more precision, higher for more exploration
 - MMR is slower than standard search. Only use when redundancy is an actual problem.
 
-## Know What Good Results Could Look Like But Can't Get Them
+## Want to improve search results based on examples (positive and negative)
 
 Use when: you can provide positive and negative example points to steer search closer to positive and further from negative.
 
 - Recommendation API: positive/negative examples to recommend fitting vectors [Recommendation API](https://search.qdrant.tech/md/documentation/search/explore/?s=recommendation-api)
   - Best score strategy: better for diverse examples, supports negative-only [Best score](https://search.qdrant.tech/md/documentation/search/explore/?s=best-score-strategy)
 - Discovery API: context pairs (positive/negative) to constrain search regions without a request target [Discovery](https://search.qdrant.tech/md/documentation/search/explore/?s=discovery-api)
 
-## Have Business Logic Behind Relevance
+## Have Business Logic Behind Results Relevance
+
 Use when: results should be additionally ranked according to some business logic based on data, like recency or distance.
 
 Check how to set up in [Score Boosting docs](https://search.qdrant.tech/md/documentation/search/search-relevance/?s=score-boosting)
 
 ## What NOT to Do
 
-- Use hybrid search before verifying pure vector quality (adds complexity, may mask model issues)
-- Use BM25 on non-English text without correctly configuring language-specific stop-word removal (severely degraded results)
+- Use hybrid search before verifying pure vector search quality (adds complexity, may mask model issues)
 - Skip evaluation when adding relevance feedback (it's good to check on real queries that it actually could help)
diff --git a/skills/qdrant-search-quality/search-strategies/hybrid-search/SKILL.md b/skills/qdrant-search-quality/search-strategies/hybrid-search/SKILL.md
@@ -0,0 +1,39 @@
+---
+name: qdrant-hybrid-search
+description: "Explains hybrid search in Qdrant. Use when someone asks 'how do I setup hybrid search?', 'how to combine keyword and semantic search?', 'sparse plus dense vectors?', 'missing keyword matches', 'how to combine results from multiple searches?' and 'combining multiple representations'"
+allowed-tools:
+  - Read
+  - Grep
+  - Glob
+---
+
+# Hybrid Search in Qdrant
+
+Hybrid search means running two or more different searches in parallel and combining their results into one. 
+
+In Qdrant this is powered by the Query API via `prefetch`: each `prefetch` runs exactly one type of search independently, and the outer `query` combines results from parallel prefetches.  
+Prefetches can be nested and searches can be multi-stage, all pipeline happening in one request through Query API. See [Universal Query API](https://search.qdrant.tech/md/course/essentials/day-5/universal-query-api/) for examples.
+
+Identify the user's problem and pick building blocks:
+- What can go into one prefetch, e.g. power one search, in [Search Types](search-types/SKILL.md)
+- How to combine results of these searches (RRF, DBSF, FormulaQuery, reranking) in [Combining Searches](combining-searches/SKILL.md)
+
+Based on what you've picked, test your approach:
+1. Configure Qdrant collection with [named vectors](https://search.qdrant.tech/md/documentation/manage-data/vectors/?s=named-vectors), where each named vector usually corresponds to one representation (different embedding models or different vector types) of a data point.
+2. Construct a hybrid search request with Query API from your building blocks. You can search independently among one type of vectors, with `prefetch` + `using`, like shown in examples in [Hybrid Queries documentation](https://search.qdrant.tech/md/documentation/search/hybrid-queries).
+3. Evaluate hybrid search quality on real user data and provide user with improvements and tradeoffs (speed/resources).
+
+## How Isolated Are Parallel Searches?
+
+Use when: different tenants share one collection and you need to understand hybrid search isolation guarantees.
+
+If user wants to isolate/share hybrid search pipelines between tenants, consider that:
+
+- Indexes (sparse, payload and dense) and [IDF modifier](https://search.qdrant.tech/md/documentation/manage-data/indexing/?s=idf-modifier) for sparse vectors are computed independently **per shard**, not per **tenant**.
+- Prefetch runs independently per shard to retrieve #limit results, so for collection-level prefetches if collection has several shards, Qdrant will always prefetch under the hood #limit * #shard results. Final results are merged based on scores.
+- In nested prefetches (deeper than 1 level), methods described in "Combining Searches" might be done on a shard level first, then per-shards results once again will be merged based on scores.
+
+## What NOT to Do
+
+- Choose a hybrid search pattern based on "vibes" without any [hybrid search quality evaluation](https://search.qdrant.tech/md/articles/hybrid-search/?s=how-effective-is-your-search-system) in-place.
+- Create too many named vectors without a need. An unfilled named vector might take as much resources as a filled one.
\ No newline at end of file
diff --git a/skills/qdrant-search-quality/search-strategies/hybrid-search/combining-searches/SKILL.md b/skills/qdrant-search-quality/search-strategies/hybrid-search/combining-searches/SKILL.md
@@ -0,0 +1,49 @@
+---
+name: qdrant-hybrid-search-combining
+description: "Use when someone asks 'RRF or DBSF?', 'how to combine sparse and dense', 'how to combine scores from multiple searches?', 'custom fusion', or 'fusion is not producing good results'"
+---
+
+# Combining Prefetch Results
+
+The outer query fuses ranked candidate lists from all parallel prefetches into one ranked list of results. Fusion methods differ in whether they use rank, score or directly vector representations of candidates (their similarity to the outer query) and whether final score incorporates payload metadata. All methods support flat (one fusion step) and nested (multi-stage) prefetch structures.
+
+## Scores Are Not Comparable Across Prefetches & You Want Some Easy Baseline
+
+Use when: searches produce scores on different scales, like BM25 and cosine on dense embeddings.
+
+### RRF
+- **[RRF](https://search.qdrant.tech/md/documentation/search/hybrid-queries/?s=reciprocal-rank-fusion-rrf)** (Reciprocal Rank Fusion) — rank-based, ignores scores magnitude, a decent default to start with.
+- Tune `k` to [control rank sensitivity in RRF fusion](https://search.qdrant.tech/md/documentation/search/hybrid-queries/?s=setting-rrf-constant-k).
+- Add per-prefetch **weights** when one search should dominate, using [Weighted RRF](https://search.qdrant.tech/md/documentation/search/hybrid-queries/?s=weighted-rrf). Weights should be customized per collection and retrievers' score distributions!
+
+### DBSF
+- **[DBSF](https://search.qdrant.tech/md/documentation/search/hybrid-queries/?s=distribution-based-score-fusion-dbsf)** (Distribution-Based Score Fusion) — normalizes score distributions per prefetch before fusing them, for that, instead of min-max, uses mean +- 3 deviations on prefetched list of scores. Avoid relying on resulting absolute scores, as scores in DBSF are normalized per prefetch (aka per a retrieved list of search results), and might be uncomparable across queries.
+
+## Need Custom Fusion
+
+Use when: recency, popularity or other payload values should affect the merged ranking alongside candidate scores or you need a custom fusion.
+
+**[With formula query](https://search.qdrant.tech/md/documentation/search/search-relevance/?s=score-boosting)**, access `score` of each prefetch and, if desired, payload field values.
+
+If you want to implement custom fusion on `score` of each prefetch:
+- Use decay or any other available expressions for normalizing score distributions before fusing them. 
+- Parameters of these expressions should be based on the collection & retriever score distributions (for example, adjusting these parameters on a subsample of real queries). 
+- Formula query is unable to provide ranks for custom fusions 
+
+## Need Good Ranking of Fused Candidates and Ready To Spend More Resources
+
+Use when: you want to use similarity between query and candidates' vector representations as the prefetches combiner and simultaneously ranker. 
+More resource heavy than score/rank based fusions, but might be necessary due to use case requirements or need in a high top-K precision of results (when parallel prefetches have overall a good recall of retrieved candidates).
+
+You can use any type of vector as an outer query over the prefetches, to perform the fusion on the server-side in one QueryAPI request: sparse, dense, multivector. For that, same type of vector representations for documents need to be stored as named vectors per point.
+
+Instead of using client-side fusion through cross-encoders, a popular option is **Late interaction models-based fusion**, through reranking on multivectors (e.g. ColBERT for text, ColPali and ColQwen for images).
+- Most precise but highest compute/resource usage.
+- Configure multivectors used for fusion through reranking with HNSW disabled like in [Hybrid Search with Reranking tutorial](https://search.qdrant.tech/md/documentation/tutorials-search-engineering/reranking-hybrid-search/).
+
+## What NOT to Do
+
+- Use linear weighted fusion on incomparable score ranges. [Why not](https://search.qdrant.tech/md/articles/hybrid-search/?s=why-not-a-linear-combination).
+- Use "vibe" defined weights in weighted RRF. Weights should be fine-tuned per dataset and retrieval pipelines.
+- Pick any fusion type without comparative experiments.
+- Use late interaction multivectors for fusion without evaluating cheaper analogues, for example, MUVERA. More in [multi-vector Qdrant search course](https://search.qdrant.tech/md/course/multi-vector-search/)
diff --git a/skills/qdrant-search-quality/search-strategies/hybrid-search/search-types/SKILL.md b/skills/qdrant-search-quality/search-strategies/hybrid-search/search-types/SKILL.md
@@ -0,0 +1,62 @@
+---
+name: qdrant-hybrid-search-prefetches
+description: "Use when someone asks 'how to combine lexical and semantic retrieval', 'dense and sparse in one search?', 'how to combine multiple fields for retrieval?', 'payloads or sparse vectors for lexical?', 'which sparse embedding model to use?', 'BM25 vs SPLADE?'"
+---
+
+# Different Searches in One Query API Request
+
+Each `prefetch` runs exactly one search per one query. 
+
+Understand if user wants to run several parallel searches on:
+1. The same vector representations but different queries or filters.
+2. Different vector representations but the same raw query.
+
+If first, help user to design logic of constructing query or/and filters on application side and then check [Combining Searches](../combining-searches/SKILL.md). Don't forget to create [indices on filterable payload fields](https://search.qdrant.tech/md/documentation/manage-data/indexing/?s=payload-index), immediately after collection creation, prior to building HNSW, so filterable HNSW could be constructed.
+
+If second, use [named vectors](https://search.qdrant.tech/md/documentation/manage-data/vectors/?s=named-vectors), which allow to store multiple vector types per point in one collection. Beware that named vectors currently can be configured only at collection creation. To choose vectors, check following recommendations.
+
+## Missed Keyword Matches
+
+Use when: pure vector search misses exact term or keyword matches and you need lexical retrieval alongside semantic search.
+
+Most likely you need a sparse vector for exact text search alongside the dense one. Qdrant uses sparse vectors for lexical searches, as [payload filtering doesn't provide any ranking score](https://search.qdrant.tech/md/documentation/search/text-search/?s=filtering-versus-querying).
+
+### Choose a Sparse Vector for Text
+- **BM25** statistical representations, built into Qdrant core (computed server-side). Good baseline, works out-of-domain, usually for long texts. Can be used for non-English content, but needs to be configured per language (tokenization, stemming, stopwords, etc) at indexing and retrieval time. More in [Text Search Guide](https://search.qdrant.tech/md/documentation/search/text-search/?s=bm25)
+- **BM42** learned sparse, based on BM25, but better for small chunks of text & with meaning understanding. Works only on English. Requires fine-tuning for domain-specific retrieval. Requires FastEmbed (Python/REST only, not available in all SDKs). Not maintained. 
+- **miniCOIL** learned sparse, BM25 with additional understanding of words meaning in context. Works only on English. Requires fine-tuning for domain-specific retrieval. Requires FastEmbed. Usage shown in [FastEmbed miniCOIL documentation](https://search.qdrant.tech/md/documentation/fastembed/fastembed-minicoil/).
+- **SPLADE++** learned sparse with term expansion. Heavier inference and resources usage but better performance due to term expansion. Requires fine-tuning for domain-specific retrieval. Provided in Qdrant Cloud Inference and FastEmbed versions work only on English. To use with FastEmbed, check [FastEmbed SPLADE documentation](https://search.qdrant.tech/md/documentation/fastembed/fastembed-splade/).
+- **External learned sparse embeddings**, for example BAAI/bge-m3.
+
+What to remember when using sparse vectors for lexical search:
+- tokenization and stemming affect exact matches, especially on custom codes, terms, etc.
+
+What to remember when using Qdrant BM25 and miniCOIL (based on BM25):
+- avg_len in formula is not computed server-side, it is a user responsibility and passed as a parameter
+- BM25 might be not good for small chunks of text, as BM25 algorithm was initially created for search on long documents; consider adjusting document statistics in sparse vectors (TF & IDF, k, b).
+- Qdrant BM25 vectors are configured per language, so consider customizing stop words, stemming & tokenization when users documents mix several languages or carefully configure vectors per point when they are monolingual.
+
+More on [Sparse Vectors for Text Search](https://search.qdrant.tech/md/course/essentials/day-3/sparse-retrieval-demo/)
+
+## Need to Combine Multiple Representations of the Same Item
+
+Use when: the same item is embedded in multiple ways (e.g. different models, languages, or modalities) and you want to search across different representations in one request (don't have to be all of them, can be even one).
+
+Use multiple named vector prefetches, each prefetch covers one representation.
+
+- If you have groups and subgroups of representations (document -> chunk, image -> patch), you could use [searching in groups](https://search.qdrant.tech/md/documentation/search/search/?s=search-groups). To not store identical payloads several times, check [Lookup in Groups](https://search.qdrant.tech/md/documentation/search/search/#lookup-in-groups)
+
+You can also search directly on [multivectors](https://search.qdrant.tech/md/documentation/manage-data/vectors/?s=multivectors), a matrix of dense vectors, in a prefetch.
+
+However, it comes with several considerations, as multivectors were designed to support late interaction models using max similarity metric, so it's impossible to retrieve the list of individual max similarity scores for each query vector.
+
+Moreover, multivectors are rarely a good pick for prefetch:
+- max similarity metric is not symmetric, so [using HNSW index with it could be problematic](https://search.qdrant.tech/md/course/multi-vector-search/module-1/maxsim-distance/#the-hnsw-challenge)
+- [multivector representations are very heavy, as search process on them](https://search.qdrant.tech/md/course/multi-vector-search/module-1/problems-multi-vector). 
+
+There are ways to make multivector retrieval cheaper (MUVERA, pooling), you can see more in ["Evaluating Tradeoffs of Multi-stage Multi-vector Search"](https://search.qdrant.tech/md/course/multi-vector-search/module-3/evaluating-pipelines/)
+
+## What NOT to Do
+- Choose any search method (for example, BM25) without evaluation of its quality & resources used.
+- Use any search method (for example, BM25) without paying attention to the specifics of their configuration and applicability to the use case.
+
PATCH

echo "Gold patch applied."
