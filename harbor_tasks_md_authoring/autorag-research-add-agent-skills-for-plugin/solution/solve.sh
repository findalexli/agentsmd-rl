#!/usr/bin/env bash
set -euo pipefail

cd /workspace/autorag-research

# Idempotency guard
if grep -qF "**Custom parameters:** Add fields to your config class and pass them via `get_pi" ".agents/skills/create-generation-plugin/SKILL.md" && grep -qF "The generated `pyproject.toml` registers the `autorag_research.ingestors` entry " ".agents/skills/create-ingestor-plugin/SKILL.md" && grep -qF "This is critical for multi-hop queries where multiple evidence pieces are needed" ".agents/skills/create-metric-plugin/SKILL.md" && grep -qF "**Custom parameters:** Add fields to your config class and pass them via `get_pi" ".agents/skills/create-retrieval-plugin/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/create-generation-plugin/SKILL.md b/.agents/skills/create-generation-plugin/SKILL.md
@@ -0,0 +1,79 @@
+---
+name: create-generation-plugin
+description: |
+  Guide developers through creating a custom generation pipeline plugin for AutoRAG-Research.
+  Walks through scaffolding, implementing BaseGenerationPipeline methods, composing with
+  retrieval pipelines, writing YAML configs, testing, and installing. Use when building a
+  new RAG generation strategy (e.g., chain-of-thought RAG, multi-hop RAG).
+allowed-tools:
+  - Bash
+  - Read
+  - Write
+  - Edit
+---
+
+# Create Generation Plugin
+
+## Workflow
+
+### 1. Scaffold
+
+```bash
+autorag-research plugin create my_rag --type=generation
+```
+
+Read the generated `pipeline.py`, `pyproject.toml`, YAML config, and test file to understand the structure.
+
+### 2. Implement
+
+Implement the `_generate(query_id, top_k)` method. This is where your RAG strategy lives.
+
+**Available attributes inside the pipeline:**
+- `self._llm` — LangChain `BaseLanguageModel` (use `await self._llm.ainvoke(prompt)`)
+- `self._retrieval_pipeline` — composed retrieval pipeline (use `await self._retrieval_pipeline._retrieve_by_id(query_id, top_k)`)
+- `self._service` — `GenerationPipelineService` (use `self._service.get_chunk_contents(chunk_ids)`, `self._get_query_text(query_id)`)
+
+Must return a `GenerationResult(text=...)` (from `autorag_research.orm.service.generation_pipeline`).
+
+> **DO NOT add your own `asyncio.gather`, `asyncio.Semaphore`, or any concurrency control.**
+> The base pipeline's `run()` already handles parallel execution of all queries via
+> `run_with_concurrency_limit()` (semaphore + gather), controlled by the `max_concurrency`
+> config parameter. Your `_generate` method is called once per single query — just implement
+> the retrieve-and-generate logic for that one query.
+
+**Custom parameters:** Add fields to your config class and pass them via `get_pipeline_kwargs()` → accept them in the pipeline constructor.
+
+**Inherited config fields** (from `BaseGenerationPipelineConfig`):
+- `llm` — LLM model string (auto-converted to LangChain model instance)
+- `retrieval_pipeline_name` — name of the retrieval pipeline to compose with (Executor injects it)
+
+### 3. Write tests and install
+
+Use `langchain_core.language_models.FakeListLLM` to mock the LLM in tests.
+
+```bash
+cd my_rag_plugin
+pip install -e .   # or: uv pip install -e .
+cd .. && autorag-research plugin sync
+```
+
+Verify: `ls configs/pipelines/generation/my_rag.yaml`
+
+## Key Files
+
+| Purpose | Path |
+|---|---|
+| Base config class | `autorag_research/config.py` → `BaseGenerationPipelineConfig` |
+| Base pipeline class | `autorag_research/pipelines/generation/base.py` → `BaseGenerationPipeline` |
+| Service + GenerationResult | `autorag_research/orm/service/generation_pipeline.py` |
+| Plugin entry point discovery | `autorag_research/plugin_registry.py` |
+
+## Examples
+
+Study these existing implementations for patterns:
+
+- `autorag_research/pipelines/generation/basic_rag.py` — Simple retrieve-then-generate (start here)
+- `autorag_research/pipelines/generation/ircot.py` — Interleaving retrieval with chain-of-thought
+- `autorag_research/pipelines/generation/et2rag.py` — Entity-aware RAG
+- `autorag_research/pipelines/generation/main_rag.py` — Main RAG pipeline
+- YAML configs: `configs/pipelines/generation/basic_rag.yaml`, `configs/pipelines/generation/ircot.yaml`
diff --git a/.agents/skills/create-ingestor-plugin/SKILL.md b/.agents/skills/create-ingestor-plugin/SKILL.md
@@ -0,0 +1,121 @@
+---
+name: create-ingestor-plugin
+description: |
+  Guide developers through creating a custom data ingestor plugin for AutoRAG-Research.
+  Ingestors load external datasets (HuggingFace, local files, APIs) into the database.
+  Uses @register_ingestor decorator for automatic CLI parameter extraction. Use when
+  ingesting a new dataset format into AutoRAG-Research.
+allowed-tools:
+  - Bash
+  - Read
+  - Write
+  - Edit
+---
+
+# Create Ingestor Plugin
+
+## Workflow
+
+### 1. Scaffold
+
+```bash
+autorag-research plugin create my_dataset --type=ingestor
+```
+
+Read the generated `ingestor.py`, `pyproject.toml`, and test file to understand the structure.
+
+The generated `pyproject.toml` registers the `autorag_research.ingestors` entry point. The `@register_ingestor` decorator handles automatic CLI parameter extraction from `__init__` type hints.
+
+### 2. Implement the ingestor
+
+**Required methods:**
+- `__init__(embedding_model, ...)` — accept embedding model + dataset-specific params
+- `detect_primary_key_type()` → `"bigint"` or `"string"`
+- `ingest(subset, query_limit, min_corpus_cnt)` — load data and save via `self.service`
+
+**`__init__` type hints drive CLI generation automatically:**
+
+| Type Hint | CLI Behavior |
+|---|---|
+| `Literal["a", "b"]` | `--param` with choices, required |
+| `str` | `--param`, required |
+| `int = 100` | `--param`, optional with default |
+| `bool = False` | `--param/--no-param` flag |
+
+Parameters named `embedding_model` or `late_interaction_embedding_model` are auto-skipped (injected by CLI).
+
+**`self.service`** is injected after construction via `set_service()`. Read existing ingestors for exact service method signatures.
+
+### 3. Database Schema (critical)
+
+Ingestors must populate the correct entity hierarchy:
+
+```
+Document → Page → Chunk (text)
+                → ImageChunk (images)
+```
+
+- **Document** — top-level container (e.g., a Wikipedia article, a PDF)
+- **Page** — subdivision within a document (linked via `document_id`)
+- **Chunk** — text passage with embedding vector (linked to Page via `PageChunkRelation`)
+- **ImageChunk** — image binary with embedding vector (linked to Page via `PageChunkRelation`)
+- **Query** — search query with `generation_gt: list[str] | None` (ground truth answers)
+
+**RetrievalRelation** — links queries to relevant chunks using AND/OR group structure:
+
+```
+RetrievalRelation(query_id, chunk_id, group_index, group_order, score)
+
+group_index = AND group number
+group_order = OR position within the group
+
+Example: query needs (chunk_A OR chunk_B) AND chunk_C
+  → (query, chunk_A, group_index=0, group_order=0)
+  → (query, chunk_B, group_index=0, group_order=1)
+  → (query, chunk_C, group_index=1, group_order=0)
+```
+
+This AND/OR structure is critical for multi-hop queries. See `ai_instructions/db_schema.md` for the full DBML schema.
+
+### 4. Install and verify
+
+```bash
+cd my_dataset_plugin
+pip install -e .   # or: uv pip install -e .
+```
+
+No `plugin sync` needed — ingestors are discovered automatically via entry points.
+
+```bash
+autorag-research ingest my_dataset --dataset-name subset_a
+```
+
+## Testing
+
+Use `ingestor_test_utils` for integration tests against a real PostgreSQL database:
+
+- `IngestorTestConfig` — declare expected counts (queries, chunks, image_chunks), relation checks, primary key type
+- `create_test_database(config)` — context manager that creates/drops an isolated test DB
+- `IngestorTestVerifier` — runs all configured checks: count verification, format validation, retrieval relation checks, generation_gt checks, content hash verification
+
+See `tests/autorag_research/data/ingestor_test_utils.py` for full API and usage examples in the module docstring.
+
+## Key Files
+
+| Purpose | Path |
+|---|---|
+| Base classes | `autorag_research/data/base.py` → `TextEmbeddingDataIngestor`, `MultiModalEmbeddingDataIngestor` |
+| Registration decorator | `autorag_research/data/registry.py` → `@register_ingestor` |
+| Text ingestion service | `autorag_research/orm/service/text_ingestion.py` |
+| Multi-modal ingestion service | `autorag_research/orm/service/multi_modal_ingestion.py` |
+| DB schema reference | `ai_instructions/db_schema.md` |
+| Test utilities | `tests/autorag_research/data/ingestor_test_utils.py` |
+
+## Examples
+
+Study these existing implementations for patterns:
+
+- `autorag_research/data/beir.py` — BEIR benchmark (simple, good starting point)
+- `autorag_research/data/bright.py` — BRIGHT dataset
+- `autorag_research/data/mrtydi.py` — Mr. TyDi multilingual dataset
+- `autorag_research/data/ragbench.py` — RAGBench dataset
diff --git a/.agents/skills/create-metric-plugin/SKILL.md b/.agents/skills/create-metric-plugin/SKILL.md
@@ -0,0 +1,89 @@
+---
+name: create-metric-plugin
+description: |
+  Guide developers through creating a custom evaluation metric plugin for AutoRAG-Research.
+  Covers both retrieval metrics (recall, precision, etc.) and generation metrics (BLEU, ROUGE, etc.).
+  Walks through scaffolding, implementing metric functions with @metric decorators, writing configs,
+  testing, and installing. Use when building a new evaluation metric.
+allowed-tools:
+  - Bash
+  - Read
+  - Write
+  - Edit
+---
+
+# Create Metric Plugin
+
+## Workflow
+
+### 1. Scaffold
+
+```bash
+# For retrieval metric:
+autorag-research plugin create my_metric --type=metric_retrieval
+
+# For generation metric:
+autorag-research plugin create my_metric --type=metric_generation
+```
+
+Read the generated `metric.py`, `pyproject.toml`, YAML config, and test file to understand the structure.
+
+### 2. Implement the metric function
+
+Use the `@metric` decorator (per-input) or `@metric_loop` decorator (batch) from `autorag_research.evaluation.metrics.util`. Both validate that required fields are non-None before calling.
+
+- `@metric(fields_to_check=[...])` — function receives a single `MetricInput`, returns `float`
+- `@metric_loop(fields_to_check=[...])` — function receives `list[MetricInput]`, returns `list[float]`
+
+See `autorag_research/schema.py` for the full `MetricInput` dataclass definition.
+
+### 3. Understanding `retrieval_gt` (AND/OR group structure)
+
+For retrieval metrics, `metric_input.retrieval_gt` uses a **nested list structure** with AND/OR semantics:
+
+```
+retrieval_gt: list[list[str]]
+
+Example: [["A", "B"], ["C"]]
+  → Means: (A OR B) AND C
+  → Each inner list is an OR group (any item satisfies the group)
+  → Outer list is AND (ALL groups must be satisfied for complete retrieval)
+```
+
+This is critical for multi-hop queries where multiple evidence pieces are needed. Your metric must handle this structure correctly — don't just flatten it into a single set unless your metric semantics allow it.
+
+**Examples:**
+- `[["doc1"]]` — single required document
+- `[["doc1", "doc2"], ["doc3"]]` — need (doc1 OR doc2) AND doc3
+- `[["doc1"], ["doc2"], ["doc3"]]` — need doc1 AND doc2 AND doc3
+
+See `retrieval_ndcg` in `autorag_research/evaluation/metrics/retrieval.py` for a real implementation that handles AND/OR groups with graded relevance.
+
+### 4. Wire up config and install
+
+The generated config class just needs `get_metric_func()` to return your metric function. If your metric takes extra kwargs, override `get_metric_kwargs()`.
+
+```bash
+cd my_metric_plugin
+pip install -e .   # or: uv pip install -e .
+cd .. && autorag-research plugin sync
+```
+
+Verify: `ls configs/metrics/retrieval/my_metric.yaml` (or `metrics/generation/`)
+
+## Key Files
+
+| Purpose | Path |
+|---|---|
+| Base config classes | `autorag_research/config.py` → `BaseRetrievalMetricConfig`, `BaseGenerationMetricConfig` |
+| MetricInput schema | `autorag_research/schema.py` |
+| Metric decorators | `autorag_research/evaluation/metrics/util.py` → `@metric`, `@metric_loop` |
+| Plugin entry point discovery | `autorag_research/plugin_registry.py` |
+
+## Examples
+
+Study these existing implementations for patterns:
+
+- `autorag_research/evaluation/metrics/retrieval.py` — Recall, Precision, F1, NDCG, MRR, MAP (all handle AND/OR groups)
+- `autorag_research/evaluation/metrics/generation.py` — BLEU, ROUGE, BERTScore, SemScore
+- YAML configs: `configs/metrics/retrieval/f1.yaml`, `configs/metrics/generation/rouge.yaml`
diff --git a/.agents/skills/create-retrieval-plugin/SKILL.md b/.agents/skills/create-retrieval-plugin/SKILL.md
@@ -0,0 +1,71 @@
+---
+name: create-retrieval-plugin
+description: |
+  Guide developers through creating a custom retrieval pipeline plugin for AutoRAG-Research.
+  Walks through scaffolding, implementing BaseRetrievalPipeline methods, writing YAML configs,
+  testing, and installing. Use when building a new search/retrieval strategy (e.g., Elasticsearch,
+  ColBERT, custom vector search).
+allowed-tools:
+  - Bash
+  - Read
+  - Write
+  - Edit
+---
+
+# Create Retrieval Plugin
+
+## Workflow
+
+### 1. Scaffold
+
+```bash
+autorag-research plugin create my_search --type=retrieval
+```
+
+Read the generated `pipeline.py`, `pyproject.toml`, YAML config, and test file to understand the structure.
+
+### 2. Implement
+
+Implement the two abstract methods in the pipeline class:
+
+- `_retrieve_by_id(query_id, top_k)` — retrieve using query ID (query exists in DB with stored embedding)
+- `_retrieve_by_text(query_text, top_k)` — retrieve using raw text (may need on-the-fly embedding)
+
+Both must return `list[dict[str, Any]]` with `doc_id` (chunk ID) and `score` keys.
+
+> **DO NOT add your own `asyncio.gather`, `asyncio.Semaphore`, or any concurrency control.**
+> The base pipeline's `run()` already handles parallel execution of all queries via
+> `run_with_concurrency_limit()` (semaphore + gather), controlled by the `max_concurrency`
+> config parameter. Your method is called once per single query — just implement the
+> retrieval logic for that one query.
+
+**Custom parameters:** Add fields to your config class and pass them via `get_pipeline_kwargs()` → accept them in the pipeline constructor. See `bm25.py` for a real example.
+
+### 3. Write tests and install
+
+```bash
+cd my_search_plugin
+pip install -e .   # or: uv pip install -e .
+cd .. && autorag-research plugin sync
+```
+
+Verify: `ls configs/pipelines/retrieval/my_search.yaml`
+
+## Key Files
+
+| Purpose | Path |
+|---|---|
+| Base config class | `autorag_research/config.py` → `BaseRetrievalPipelineConfig` |
+| Base pipeline class | `autorag_research/pipelines/retrieval/base.py` → `BaseRetrievalPipeline` |
+| Service layer | `autorag_research/orm/service/retrieval_pipeline.py` → `RetrievalPipelineService` |
+| Plugin entry point discovery | `autorag_research/plugin_registry.py` |
+
+## Examples
+
+Study these existing implementations for patterns:
+
+- `autorag_research/pipelines/retrieval/bm25.py` — BM25 retrieval (simple)
+- `autorag_research/pipelines/retrieval/vector_search.py` — Vector similarity search
+- `autorag_research/pipelines/retrieval/hybrid.py` — Hybrid (BM25 + vector)
+- `autorag_research/pipelines/retrieval/hyde.py` — HyDE (Hypothetical Document Embeddings)
+- YAML configs: `configs/pipelines/retrieval/bm25.yaml`, `configs/pipelines/retrieval/vector_search.yaml`
PATCH

echo "Gold patch applied."
