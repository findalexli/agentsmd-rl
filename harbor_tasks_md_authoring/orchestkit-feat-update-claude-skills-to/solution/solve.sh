#!/usr/bin/env bash
set -euo pipefail

cd /workspace/orchestkit

# Idempotency guard
if grep -qF "6. Ensure PostgreSQL 18 modern features are used" ".claude/agents/database-engineer.md" && grep -qF "# PostgreSQL 18 generates UUID v7 via server_default=text(\"uuidv7()\")" ".claude/skills/api-design-framework/examples/skillforge-api-design.md" && grep -qF "import uuid_utils  # pip install uuid-utils (UUID v7 for Python < 3.14)" ".claude/skills/langgraph-human-in-loop/SKILL.md" && grep -qF "async def analyze_content(url: str, content: str, db: AsyncSession = Depends(get" ".claude/skills/langgraph-supervisor/examples/skillforge-analysis-workflow.md" && grep -qF "correlation_id = request.headers.get(\"X-Correlation-ID\") or str(uuid_utils.uuid7" ".claude/skills/observability-monitoring/SKILL.md" && grep -qF "correlation_id = request.headers.get(\"X-Correlation-ID\") or str(uuid_utils.uuid7" ".claude/skills/observability-monitoring/checklists/monitoring-implementation-checklist.md" && grep -qF "import uuid_utils  # pip install uuid-utils (UUID v7 for Python < 3.14)" ".claude/skills/pgvector-search/references/metadata-filtering.md" && grep -qF "image: pgvector/pgvector:pg18" ".claude/skills/unit-testing/examples/skillforge-test-strategy.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/agents/database-engineer.md b/.claude/agents/database-engineer.md
@@ -25,7 +25,7 @@ Activates for: schema, migration, database, postgres, pgvector, index, constrain
 3. Optimize slow queries using EXPLAIN ANALYZE
 4. Configure pgvector indexes (HNSW vs IVFFlat selection)
 5. Set up full-text search with tsvector and GIN indexes
-6. Ensure PostgreSQL 17 modern features are used
+6. Ensure PostgreSQL 18 modern features are used
 
 ## Output Format
 Return structured findings:
diff --git a/.claude/skills/api-design-framework/examples/skillforge-api-design.md b/.claude/skills/api-design-framework/examples/skillforge-api-design.md
@@ -102,20 +102,22 @@ async def create_analysis(
     # 1. Detect content type
     content_type = detect_content_type(str(request.url))
 
-    # 2. Generate or normalize analysis_id
+    # 2. Normalize custom analysis_id if provided (optional)
     analysis_uuid = (
         normalize_analysis_id_to_uuid(request.analysis_id)
         if request.analysis_id
-        else uuid.uuid4()
+        else None  # Let DB generate UUID v7 via server_default
     )
 
     # 3. Create Analysis record (status: pending)
-    await analysis_repo.create_analysis(
-        analysis_id=analysis_uuid,
+    # PostgreSQL 18 generates UUID v7 via server_default=text("uuidv7()")
+    created_analysis = await analysis_repo.create_analysis(
+        analysis_id=analysis_uuid,  # None → DB generates UUID v7
         url=url_str,
         content_type=content_type,
         status="pending"
     )
+    analysis_uuid = cast("AnalysisID", created_analysis.id)
 
     # 4. Start workflow asynchronously (fire-and-forget)
     task = asyncio.create_task(
diff --git a/.claude/skills/langgraph-human-in-loop/SKILL.md b/.claude/skills/langgraph-human-in-loop/SKILL.md
@@ -72,9 +72,11 @@ app = workflow.compile(interrupt_before=["approval_gate"])
 ## Feedback Loop Pattern
 
 ```python
+import uuid_utils  # pip install uuid-utils (UUID v7 for Python < 3.14)
+
 async def run_with_feedback(initial_state: dict):
     """Run until human approves."""
-    config = {"configurable": {"thread_id": str(uuid4())}}
+    config = {"configurable": {"thread_id": str(uuid_utils.uuid7())}}
 
     while True:
         # Run until interrupt
diff --git a/.claude/skills/langgraph-supervisor/examples/skillforge-analysis-workflow.md b/.claude/skills/langgraph-supervisor/examples/skillforge-analysis-workflow.md
@@ -445,10 +445,14 @@ import uuid
 router = APIRouter(prefix="/api/v1/analysis")
 
 @router.post("/analyze")
-async def analyze_content(url: str, content: str):
+async def analyze_content(url: str, content: str, db: AsyncSession = Depends(get_db)):
     """Start content analysis workflow."""
 
-    analysis_id = str(uuid.uuid4())
+    # Create analysis record - PostgreSQL 18 generates UUID v7 via server_default
+    analysis = Analysis(url=url, content_type="article", status="pending")
+    db.add(analysis)
+    await db.flush()  # Get DB-generated UUID v7
+    analysis_id = str(analysis.id)
 
     app = create_analysis_workflow()
 
diff --git a/.claude/skills/observability-monitoring/SKILL.md b/.claude/skills/observability-monitoring/SKILL.md
@@ -180,14 +180,14 @@ tracer.startActiveSpan('processOrder', async (span) => {
 **Trace requests across services:**
 ```python
 import structlog
-from uuid import uuid4
+import uuid_utils  # pip install uuid-utils (UUID v7 support for Python < 3.14)
 
 logger = structlog.get_logger()
 
 @app.middleware("http")
 async def correlation_middleware(request: Request, call_next):
-    # Get or generate correlation ID
-    correlation_id = request.headers.get("X-Correlation-ID") or str(uuid4())
+    # Get or generate correlation ID (UUID v7 for time-ordering in distributed traces)
+    correlation_id = request.headers.get("X-Correlation-ID") or str(uuid_utils.uuid7())
 
     # Bind to logger context (all logs in this request will include it)
     structlog.contextvars.bind_contextvars(
diff --git a/.claude/skills/observability-monitoring/checklists/monitoring-implementation-checklist.md b/.claude/skills/observability-monitoring/checklists/monitoring-implementation-checklist.md
@@ -60,15 +60,15 @@ def get_logger(name: str):
 
 ```python
 import structlog
-from uuid import uuid4
+import uuid_utils  # pip install uuid-utils (UUID v7 for Python < 3.14)
 from fastapi import Request
 
 @app.middleware("http")
 async def correlation_middleware(request: Request, call_next):
     """Add correlation ID to all logs."""
 
-    # Get or generate correlation ID
-    correlation_id = request.headers.get("X-Correlation-ID") or str(uuid4())
+    # Get or generate correlation ID (UUID v7 for time-ordering in traces)
+    correlation_id = request.headers.get("X-Correlation-ID") or str(uuid_utils.uuid7())
 
     # Bind to logger context
     structlog.contextvars.bind_contextvars(
diff --git a/.claude/skills/pgvector-search/references/metadata-filtering.md b/.claude/skills/pgvector-search/references/metadata-filtering.md
@@ -294,12 +294,13 @@ async def faceted_search(
 ```python
 # backend/tests/unit/services/search/test_boosting.py
 import pytest
+import uuid_utils  # pip install uuid-utils (UUID v7 for Python < 3.14)
 
 def test_section_title_boost():
     """Test section title boosting."""
 
     chunk = Chunk(
-        id=uuid4(),
+        id=uuid_utils.uuid7(),
         content="...",
         section_title="Database Indexing Strategies"
     )
@@ -316,7 +317,7 @@ def test_no_boost_for_non_matching_title():
     """Test no boost when title doesn't match."""
 
     chunk = Chunk(
-        id=uuid4(),
+        id=uuid_utils.uuid7(),
         content="...",
         section_title="API Authentication"
     )
@@ -333,7 +334,7 @@ async def test_combined_boosting():
     """Test that boosts are multiplicative."""
 
     chunk = Chunk(
-        id=uuid4(),
+        id=uuid_utils.uuid7(),
         content="...",
         section_title="API Implementation",  # Matches "API"
         section_path="docs/backend/api/routes.md",  # Matches "API"
diff --git a/.claude/skills/unit-testing/examples/skillforge-test-strategy.md b/.claude/skills/unit-testing/examples/skillforge-test-strategy.md
@@ -572,7 +572,7 @@ jobs:
     runs-on: ubuntu-latest
     services:
       postgres:
-        image: pgvector/pgvector:pg17
+        image: pgvector/pgvector:pg18
         env:
           POSTGRES_PASSWORD: test
         ports:
PATCH

echo "Gold patch applied."
