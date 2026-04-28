#!/usr/bin/env bash
set -euo pipefail

cd /workspace/airweave

# Idempotency guard
if grep -qF "This is the **master guide** for building a complete, production-ready source co" ".cursor/rules/connector-development-end-to-end.mdc" && grep -qF "**Monke** is Airweave's end-to-end testing framework for source connectors. It c" ".cursor/rules/monke-testing-guide.mdc" && grep -qF "A **source connector** in Airweave is a Python module that extracts data from an" ".cursor/rules/source-connector-implementation.mdc" && grep -qF ".cursor/rules/source-integration-rules.mdc" ".cursor/rules/source-integration-rules.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/connector-development-end-to-end.mdc b/.cursor/rules/connector-development-end-to-end.mdc
@@ -0,0 +1,725 @@
+# Building and Testing a Source Connector: End-to-End Guide
+
+## Overview
+
+This is the **master guide** for building a complete, production-ready source connector for Airweave. It combines source implementation with comprehensive E2E testing using the Monke framework.
+
+**Use this guide with your AI coding assistant** to build connectors systematically.
+
+---
+
+## Prerequisites
+
+**Note:** The human has already completed these setup steps:
+- ✅ OAuth credentials configured in `backend/airweave/platform/auth/yaml/dev.integrations.yaml`
+- ✅ Monke authentication configured in `monke/configs/{short_name}.yaml` (Composio or direct)
+- ✅ API documentation loaded into context
+
+Your task is to write the code. The human will handle testing and running commands.
+
+---
+
+## Phase 1: Research & Planning
+
+### Step 1: Understand the API
+
+**Questions to answer:**
+
+1. What is the **entity hierarchy**?
+   - Example: Asana has `Workspace → Project → Section → Task → Comment/File`
+   - Example: GitHub has `Repository → Issue → Comment`  and `Repository → Folder1 → Folder2 → codefile.go`
+
+2. What **entities should be searchable**?
+   - Primary entities (tasks, documents, tickets)
+   - Secondary entities (comments, messages, threads)
+   - Attachments (files, images, PDFs)
+
+3. What **authentication** does it use?
+   - OAuth2 with refresh tokens?
+   - OAuth2 without refresh tokens?
+   - API key / Personal Access Token?
+
+4. Does it support **incremental sync**?
+   - Can you filter by `modified_since` or `updated_at`?
+   - Does each entity have `created_at` and `modified_at` timestamps?
+
+5. Does it support **deletion detection**?
+   - Can you detect when entities are deleted?
+   - Or do you need full re-sync to detect deletions?
+
+6. How does **pagination** work?
+   - Cursor-based? Page-based? Offset-based?
+   - What's the max page size?
+
+### Step 2: Define Your Entity Model
+
+Create a document listing:
+
+```
+Entity Hierarchy:
+- Workspace (top-level)
+  - Project
+    - Section (optional grouping)
+      - Task
+        - Comment (nested, many per task)
+        - File (nested, many per task)
+
+Searchable Fields per Entity:
+- Task: name, description, notes, assignee, tags
+- Comment: text, author
+- File: name, extracted text content
+
+Timestamps:
+- All entities have created_at
+- Task, Project have modified_at
+- Comments are immutable (no modified_at)
+```
+
+### Step 3: Plan Your Test Strategy
+
+Decide:
+- How many test entities to create (3-5 recommended)
+- What types of content to generate (tasks, comments, files)
+- Where to create them (need a dedicated test workspace/project?)
+- How to clean them up after testing
+
+---
+
+## Phase 2: Implementation
+
+### Step 4: Note on OAuth Configuration
+
+**File:** `backend/airweave/platform/auth/yaml/dev.integrations.yaml`
+
+**Note:** The human has already set up OAuth credentials here. This configuration exists and is ready to use.
+
+### Step 5: Implement Entity Schemas
+
+**File:** `backend/airweave/platform/entities/{short_name}.py`
+
+**Reference:** See `source-connector-implementation.mdc` Part 1
+
+**Implementation order:**
+
+1. Start with the **top-level entity** (workspace, repository, etc.)
+2. Add **primary entities** (tasks, documents, issues)
+3. Add **nested entities** (comments, messages)
+4. Add **file entities** if the API supports attachments
+
+**Key principles:**
+- Use `AirweaveField(..., embeddable=True)` for searchable text
+- Always include `created_at` and `modified_at` with proper flags
+- Use `Field(...)` for non-searchable metadata
+- Inherit from `ChunkEntity` or `FileEntity`
+
+**Example structure:**
+
+```python
+"""Entity schemas for {Connector Name}."""
+
+from datetime import datetime
+from typing import Optional
+from pydantic import Field
+from airweave.platform.entities._airweave_field import AirweaveField
+from airweave.platform.entities._base import ChunkEntity, FileEntity
+
+
+class MyConnectorTaskEntity(ChunkEntity):
+    """Primary task entity."""
+
+    name: str = AirweaveField(..., embeddable=True)
+    description: Optional[str] = AirweaveField(None, embeddable=True)
+    created_at: Optional[datetime] = AirweaveField(
+        None, embeddable=True, is_created_at=True
+    )
+    modified_at: Optional[datetime] = AirweaveField(
+        None, embeddable=True, is_updated_at=True
+    )
+    # ... more fields
+
+
+class MyConnectorCommentEntity(ChunkEntity):
+    """Comment on a task."""
+
+    task_id: str = Field(...)
+    text: str = AirweaveField(..., embeddable=True)
+    author: dict = AirweaveField(..., embeddable=True)
+    created_at: datetime = AirweaveField(..., embeddable=True, is_created_at=True)
+    # ... more fields
+
+
+class MyConnectorFileEntity(FileEntity):
+    """File attachment on a task."""
+
+    task_id: str = Field(...)
+    created_at: Optional[datetime] = AirweaveField(
+        None, embeddable=True, is_created_at=True
+    )
+    # FileEntity provides: file_id, name, mime_type, size, download_url
+```
+
+### Step 6: Implement Source Connector
+
+**File:** `backend/airweave/platform/sources/{short_name}.py`
+
+**Reference:** See `source-connector-implementation.mdc` Part 2
+
+**Implementation order:**
+
+1. Create the class skeleton with `@source` decorator
+2. Implement `create()` classmethod
+3. Implement `validate()` method
+4. Implement `_get_with_auth()` with token refresh handling
+5. Implement entity generation methods in hierarchical order:
+   - `_generate_workspaces()`
+   - `_generate_projects()`
+   - `_generate_tasks()`
+   - `_generate_comments()`
+   - `_generate_files()`
+6. Wire them together in `generate_entities()`
+7. Test locally
+
+**Key principles:**
+- Generate entities hierarchically (parents before children)
+- Track breadcrumbs for relationships
+- Handle pagination properly
+- Implement rate limiting
+- Use retry logic with exponential backoff
+- Handle 401 errors with token refresh
+- Use `process_file_entity()` for file attachments
+
+**Basic structure:**
+
+```python
+from airweave.platform.decorators import source
+from airweave.platform.sources._base import BaseSource
+from airweave.platform.entities._base import Breadcrumb, ChunkEntity
+from airweave.platform.entities.{short_name} import *
+
+
+@source(
+    name="{Display Name}",
+    short_name="{short_name}",
+    auth_methods=[AuthenticationMethod.OAUTH_BROWSER, ...],
+    oauth_type=OAuthType.WITH_REFRESH,
+    auth_config_class=None,
+    config_class="{ConnectorName}Config",
+    labels=["Category"],
+    supports_continuous=False,
+)
+class MyConnectorSource(BaseSource):
+    """Source connector for {Connector Name}."""
+
+    @classmethod
+    async def create(cls, access_token: str, config: Optional[Dict[str, Any]] = None):
+        instance = cls()
+        instance.access_token = access_token
+        # Parse config...
+        return instance
+
+    async def generate_entities(self) -> AsyncGenerator[ChunkEntity, None]:
+        async with self.http_client() as client:
+            # Generate hierarchically with breadcrumbs
+            async for parent in self._generate_parents(client):
+                yield parent
+
+                breadcrumb = Breadcrumb(
+                    entity_id=parent.entity_id,
+                    name=parent.name,
+                    type="parent"
+                )
+
+                async for child in self._generate_children(client, parent, [breadcrumb]):
+                    yield child
+
+    async def validate(self) -> bool:
+        return await self._validate_oauth2(
+            ping_url="https://api.example.com/me",
+            headers={"Accept": "application/json"},
+            timeout=10.0,
+        )
+    # This can also be a very simple list method, to make sure we have a
+```
+
+### Step 7: Checkpoint - Ready for Human Testing
+
+**Inform the human:** The source connector code is complete and ready for manual testing.
+
+The human will now:
+- Test the connector via UI
+- Verify entities sync correctly
+- Report any issues for you to fix
+
+Wait for human feedback before proceeding to Monke tests.
+
+---
+
+## Phase 3: E2E Testing with Monke
+
+### Step 8: Note on Monke Authentication
+
+**File:** `monke/configs/{short_name}.yaml`
+
+**Note:** The human has already set up the authentication portion of this config (either Composio or direct auth).
+
+You will now add the test flow configuration to this file:
+
+```yaml
+# Authentication section already exists (set by human)
+
+config_fields:
+  openai_model: "gpt-4.1-mini"
+  max_concurrency: 3
+
+test_flow:
+  steps:
+    - cleanup
+    - create
+    - sync
+    - verify
+    - update
+    - sync
+    - verify
+    - partial_delete
+    - sync
+    - verify_partial_deletion
+    - verify_remaining_entities
+    - complete_delete
+    - sync
+    - verify_complete_deletion
+    - cleanup
+    - collection_cleanup
+
+deletion:
+  partial_delete_count: 2
+  verify_partial_deletion: true  # Set false if API doesn't detect deletions
+  verify_remaining_entities: true
+  verify_complete_deletion: true
+
+entity_count: 3  # Number of parent entities to create
+
+collection:
+  name: {Connector Name} Test Collection
+
+verification:
+  retry_attempts: 5
+  retry_delay_seconds: 10
+  score_threshold: 0.0
+  expected_fields:
+    - name
+    - entity_id
+```
+
+### Step 9: Implement Generation Schemas
+
+**File:** `monke/generation/schemas/{short_name}.py`
+
+**Reference:** See `monke-testing-guide.mdc` Part 2
+
+Define Pydantic schemas for LLM-generated content:
+
+```python
+from typing import List
+from pydantic import BaseModel, Field
+
+
+class TaskContent(BaseModel):
+    """Content for generated task."""
+    description: str = Field(..., description="Task description with token")
+    objectives: List[str] = Field(..., description="List of objectives")
+    # ... more fields
+
+
+class TaskSpec(BaseModel):
+    """Metadata for task generation."""
+    title: str = Field(..., description="Task title")
+    token: str = Field(..., description="Verification token")
+
+
+class MyConnectorTask(BaseModel):
+    """Complete task structure."""
+    spec: TaskSpec
+    content: TaskContent
+
+
+class CommentContent(BaseModel):
+    """Content for generated comment."""
+    text: str = Field(..., description="Comment text with token")
+
+
+class FileContent(BaseModel):
+    """Content for generated file."""
+    content: str = Field(..., description="File content with token")
+    filename: str = Field(..., description="Filename")
+```
+
+### Step 10: Implement Generation Adapter
+
+**File:** `monke/generation/{short_name}.py`
+
+**Reference:** See `monke-testing-guide.mdc` Part 3
+
+Implement LLM-powered content generation:
+
+```python
+from monke.client.llm import LLMClient
+from monke.generation.schemas.my_connector import *
+
+
+async def generate_task(model: str, token: str) -> dict:
+    """Generate task with embedded verification token."""
+    llm = LLMClient(model_override=model)
+
+    instruction = (
+        f"Generate a realistic task for a software project. "
+        f"You MUST include the literal token '{token}' in the description."
+    )
+
+    task = await llm.generate_structured(MyConnectorTask, instruction)
+    task.spec.token = token
+
+    # Ensure token is in description
+    if token not in task.content.description:
+        task.content.description += f"\n\nToken: {token}"
+
+    return {
+        "title": task.spec.title,
+        "description": task.content.description,
+    }
+
+
+async def generate_comment(model: str, token: str) -> dict:
+    """Generate comment with embedded verification token."""
+    llm = LLMClient(model_override=model)
+
+    instruction = (
+        f"Generate a helpful comment on a task. "
+        f"You MUST include the literal token '{token}' in the text."
+    )
+
+    comment = await llm.generate_structured(CommentContent, instruction)
+
+    if token not in comment.text:
+        comment.text += f"\n\nToken: {token}"
+
+    return {"text": comment.text}
+```
+
+### Step 11: Implement Bongo
+
+**File:** `monke/bongos/{short_name}.py`
+
+**Reference:** See `monke-testing-guide.mdc` Part 1
+
+**This is the most critical file.** It must create ALL entity types.
+
+**Implementation order:**
+
+1. Create the class skeleton
+2. Implement `_ensure_workspace()` and `_ensure_project()` helpers
+3. Implement `create_entities()` - **MUST create all entity types**
+4. Implement `update_entities()`
+5. Implement `delete_specific_entities()`
+6. Implement `delete_entities()`
+7. Implement `cleanup()`
+8. Add rate limiting and error handling
+
+**Critical: Test ALL Entity Types**
+
+```python
+async def create_entities(self) -> List[Dict[str, Any]]:
+    """Create comprehensive test entities.
+
+    CRITICAL: Must create instances of EVERY entity type that
+    the source connector syncs.
+    """
+    all_entities = []
+
+    await self._ensure_workspace()
+    await self._ensure_project()
+
+    async with httpx.AsyncClient() as client:
+        # Create parent entities (tasks)
+        for i in range(self.entity_count):
+            task_token = str(uuid.uuid4())[:8]
+            task_data = await generate_task(self.openai_model, task_token)
+
+            # Create task via API
+            task = await self._create_task(client, task_data)
+            all_entities.append({
+                "type": "task",
+                "id": task["id"],
+                "token": task_token,
+                "expected_content": task_token,
+            })
+
+            # ==========================================
+            # CRITICAL: Create child entities
+            # ==========================================
+
+            # Create 2 comments per task
+            for j in range(2):
+                comment_token = str(uuid.uuid4())[:8]
+                comment_data = await generate_comment(self.openai_model, comment_token)
+
+                comment = await self._create_comment(client, task["id"], comment_data)
+                all_entities.append({
+                    "type": "comment",
+                    "id": comment["id"],
+                    "parent_id": task["id"],
+                    "token": comment_token,
+                    "expected_content": comment_token,
+                })
+
+            # Create 1 file per task
+            file_token = str(uuid.uuid4())[:8]
+            file_content, filename = await generate_file_attachment(
+                self.openai_model,
+                file_token
+            )
+
+            file = await self._upload_file(client, task["id"], file_content, filename)
+            all_entities.append({
+                "type": "file",
+                "id": file["id"],
+                "parent_id": task["id"],
+                "token": file_token,
+                "expected_content": file_token,
+            })
+
+    self.created_entities = all_entities
+    return all_entities
+```
+
+### Step 12: Checkpoint - Ready for E2E Testing
+
+**Inform the human:** Monke test code is complete and ready to run.
+
+The human will now:
+- Run `./monke.sh {connector_name}`
+- Verify all entity types pass (tasks, comments, files)
+- Report any test failures for you to fix
+
+Wait for human feedback. If tests fail, review the error logs and fix the code.
+
+---
+
+## Phase 4: Debugging & Iteration
+
+### Common Issues
+
+#### Issue 1: Source connector runs but entities aren't appearing in Qdrant
+
+**When human reports this issue, you should:**
+
+1. Add logging to count yielded entities:
+   ```python
+   # Add to your source's generate_entities()
+   async def generate_entities(self):
+       count = 0
+       async for entity in self._generate_all():
+           count += 1
+           self.logger.info(f"Yielded entity {count}: {entity.entity_id}")
+           yield entity
+       self.logger.info(f"Total entities yielded: {count}")
+   ```
+
+2. Verify entity schemas have correct field types
+
+3. Ask human to check worker logs: `docker logs airweave-worker-dev | grep ERROR`
+
+#### Issue 2: Comments/files not found in Monke verification
+
+**When human reports this issue, investigate:**
+
+1. Did bongo create them? Add logging to `create_entities()` to confirm
+2. Did source yield them? Add logging to comment/file generation methods
+3. Is token embedded? Check generation logic includes the token in content
+4. Ask human to search Qdrant manually for the token
+
+#### Issue 3: Token refresh failing (401 errors during sync)
+
+**When human reports this issue:**
+
+1. Ask human to verify `oauth_type` in YAML is correct
+2. Ask human to verify scopes include `offline_access` or equivalent
+3. Check your source uses `await self.get_access_token()`
+4. Verify `_get_with_auth()` handles 401 errors with token refresh
+
+#### Issue 4: Rate limiting (429 errors)
+
+**When human reports this issue:**
+
+1. Add simple rate limiting to source and bongo (see rate limiting section in implementation guide)
+2. Reduce `max_concurrency` in bongo config
+
+#### Issue 5: Monke verification times out
+
+**When human reports this issue:**
+
+1. Increase `retry_attempts` and `retry_delay_seconds` in test config
+2. Ask human to verify sync actually completed (check logs)
+3. Ask human to search Qdrant manually for the token to confirm it exists
+
+---
+
+## Phase 5: Production Readiness
+
+### Checklist
+
+**Source Connector:**
+- [ ] All entity types are implemented
+- [ ] All entities have `created_at` or `modified_at` timestamps
+- [ ] Token refresh is properly handled
+- [ ] Rate limiting is implemented
+- [ ] Pagination is handled correctly
+- [ ] Errors are handled gracefully (don't fail entire sync)
+- [ ] Breadcrumbs track entity hierarchy
+- [ ] File entities use `process_file_entity()`
+- [ ] OAuth config is in `dev.integrations.yaml`
+
+**Monke Tests:**
+- [ ] Bongo creates ALL entity types (not just tasks)
+- [ ] Each entity has unique verification token
+- [ ] Tokens are embedded in searchable content
+- [ ] Generation schemas defined for all types
+- [ ] Test config has comprehensive test flow
+- [ ] All entity types are verified after sync
+- [ ] Update flow tests incremental sync
+- [ ] Deletion flow tests deletion detection
+- [ ] cleanup() removes all test data
+
+**Documentation:**
+- [ ] Source code has docstrings
+- [ ] Entity schemas have field descriptions
+- [ ] Rate limits are documented
+
+### Performance Considerations
+
+1. **Pagination:** Always fetch in batches, don't load everything into memory
+2. **Rate Limiting:** Respect API limits to avoid bans
+3. **Concurrency:** Use semaphores to limit parallel requests
+4. **Incremental Sync:** Use `modified_since` filters when available
+5. **Error Recovery:** Don't fail entire sync on one entity error
+
+---
+
+## Phase 6: Submission
+
+### Before Submitting PR
+
+1. **Run full test suite:**
+   ```bash
+   ./monke.sh my_connector
+   ```
+
+2. **Verify all entity types sync:**
+   - Manually check Qdrant for tasks, comments, files
+
+3. **Test with real data:**
+   - Connect to your actual account
+   - Sync your real workspace
+   - Verify search works as expected
+
+4. **Check code quality:**
+   - Run linter: `ruff check backend/`
+   - Run formatter: `black backend/`
+   - Add type hints to all methods
+
+5. **Write PR description:**
+   - List all entity types synced
+   - Note any limitations (e.g., "Deletion detection not supported")
+   - Include example search queries
+
+---
+
+## Example Prompts for AI Assistant
+
+When using this guide with an AI coding assistant like Claude or Cursor:
+
+### Initial Prompt
+
+```
+You are an expert connector builder for Airweave.
+
+You must now implement the connector for [CONNECTOR NAME].
+
+The most important entities we must implement from this API are:
+- [ENTITY 1]
+- [ENTITY 2]
+- [ENTITY 3]
+
+I have already completed all prerequisites:
+✅ Added OAuth credentials to `backend/airweave/platform/auth/yaml/dev.integrations.yaml`
+✅ Set up authentication in `monke/configs/[short_name].yaml`
+✅ Loaded API documentation: @[CONNECTOR API DOCS]
+
+Your job is to write the code. I will handle:
+- Starting/stopping services
+- Testing the connector manually
+- Running Monke tests
+
+Follow this guide: @connector-development-end-to-end.mdc
+
+Please start by:
+1. Analyzing the API documentation to understand the entity hierarchy
+2. Creating entity schemas in `backend/airweave/platform/entities/[short_name].py`
+3. Creating the source connector in `backend/airweave/platform/sources/[short_name].py`
+
+Do not write code to trigger syncs or test anything - I will do that manually.
+```
+
+### Follow-up Prompts
+
+```
+Now implement the source connector in `backend/airweave/platform/sources/[short_name].py`.
+
+Make sure to:
+- Generate all entity types hierarchically
+- Handle token refresh properly
+- Implement rate limiting
+- Track breadcrumbs for entity relationships
+- Process file entities if the API supports them
+
+Reference the Asana source as an example: @asana.py
+```
+
+```
+Now implement the Monke tests.
+
+CRITICAL: The bongo MUST create instances of EVERY entity type, including
+comments and files, not just the top-level tasks.
+
+Start with:
+1. Generation schemas in `monke/generation/schemas/[short_name].py`
+2. Generation adapter in `monke/generation/[short_name].py`
+3. Bongo in `monke/bongos/[short_name].py`
+
+Reference the Asana tests but NOTE that they have a bug: they create comments
+but don't verify them. You must verify ALL entity types.
+```
+
+---
+
+## Summary
+
+Building a complete connector requires:
+
+1. **Research:** Understand the API, entity hierarchy, auth, and rate limits
+2. **Entities:** Define schemas for ALL entity types with proper timestamps
+3. **Source:** Implement hierarchical entity generation with token refresh
+4. **Testing:** Create Monke tests that verify EVERY entity type
+5. **Validation:** Run E2E tests and verify all entities appear in search
+6. **Refinement:** Debug issues, optimize performance, handle edge cases
+
+**The key to success:** Test comprehensively. Don't just test tasks—test comments, files, and all nested entities. If your connector syncs it, your tests should verify it.
+
+---
+
+## Reference Documents
+
+- **Source Implementation:** `source-connector-implementation.mdc`
+- **Monke Testing:** `monke-testing-guide.mdc`
+- **Example Connector:** Asana (see attached files)
+
+Good luck building your connector! 🚀
diff --git a/.cursor/rules/monke-testing-guide.mdc b/.cursor/rules/monke-testing-guide.mdc
@@ -0,0 +1,1055 @@
+# Building Monke Tests for Source Connectors
+
+## Overview
+
+**Monke** is Airweave's end-to-end testing framework for source connectors. It creates real test data in external systems, triggers syncs, and verifies data appears correctly in the search index.
+
+This guide shows you how to build comprehensive tests that verify **every entity type** your connector supports.
+
+---
+
+## Why Test Every Entity Type?
+
+**Problem:** Many connector tests only verify top-level entities (e.g., tasks) but ignore nested entities (e.g., comments, files).
+
+**Impact:**
+- Comments might not sync properly → Silent failures in production
+- File attachments might not be indexed → Missing searchable content
+- Entity relationships might be broken → Poor search results
+
+**Solution:** Create test entities for **every entity type** your connector syncs, and verify each one appears in Qdrant.
+
+---
+
+## Core Components
+
+Every Monke test requires four components:
+
+1. **Bongo implementation** (`monke/bongos/{short_name}.py`)
+2. **Generation schemas** (`monke/generation/schemas/{short_name}.py`)
+3. **Generation adapter** (`monke/generation/{short_name}.py`)
+4. **Test configuration** (`monke/configs/{short_name}.yaml`)
+
+---
+
+## Part 1: Bongo Implementation
+
+The **Bongo** is a class that creates, updates, and deletes test data via the external API.
+
+### File Location
+```
+monke/bongos/{short_name}.py
+```
+
+### Basic Structure
+
+```python
+"""{Connector Name} bongo implementation.
+
+Creates, updates, and deletes test entities via the real {Connector Name} API.
+"""
+
+import asyncio
+import time
+import uuid
+from typing import Any, Dict, List, Optional
+
+import httpx
+from monke.bongos.base_bongo import BaseBongo
+from monke.utils.logging import get_logger
+
+
+class MyConnectorBongo(BaseBongo):
+    """Bongo for {Connector Name} that creates test entities for E2E testing.
+
+    Key responsibilities:
+    - Create test entities (including nested types like comments/files)
+    - Embed verification tokens in content
+    - Update entities to test incremental sync
+    - Delete entities to test deletion detection
+    - Clean up all test data
+    """
+
+    connector_type = "{short_name}"  # Must match source short_name
+
+    API_BASE = "https://api.example.com/v1"
+
+    def __init__(self, credentials: Dict[str, Any], **kwargs):
+        """Initialize the bongo.
+
+        Args:
+            credentials: Dict with "access_token" or other auth
+            **kwargs: Configuration from test config file
+        """
+        super().__init__(credentials)
+        self.access_token: str = credentials["access_token"]
+
+        # Test configuration
+        self.entity_count: int = int(kwargs.get("entity_count", 3))
+        self.openai_model: str = kwargs.get("openai_model", "gpt-4.1-mini")
+        self.max_concurrency: int = int(kwargs.get("max_concurrency", 3))
+
+        # Simple rate limiting (optional, add if needed)
+        self.last_request_time = 0.0
+        self.min_delay = 0.2  # 200ms between requests
+
+        # Runtime state - track ALL created entities
+        self._workspace_id: Optional[str] = None
+        self._project_id: Optional[str] = None
+        self._tasks: List[Dict[str, Any]] = []
+        self._comments: List[Dict[str, Any]] = []
+        self._files: List[Dict[str, Any]] = []
+
+        self.logger = get_logger(f"{self.connector_type}_bongo")
+
+    async def create_entities(self) -> List[Dict[str, Any]]:
+        """Create ALL types of test entities.
+
+        This is critical: You must create instances of EVERY entity type
+        that your source connector syncs.
+
+        Returns:
+            List of entity descriptors with verification tokens
+        """
+        raise NotImplementedError("Implement in subclass")
+
+    async def update_entities(self) -> List[Dict[str, Any]]:
+        """Update a subset of entities to test incremental sync.
+
+        Returns:
+            List of updated entity descriptors
+        """
+        raise NotImplementedError("Implement in subclass")
+
+    async def delete_entities(self) -> List[str]:
+        """Delete all created test entities.
+
+        Returns:
+            List of deleted entity IDs
+        """
+        raise NotImplementedError("Implement in subclass")
+
+    async def delete_specific_entities(self, entities: List[Dict[str, Any]]) -> List[str]:
+        """Delete specific entities by ID.
+
+        Args:
+            entities: List of entity descriptors to delete
+
+        Returns:
+            List of successfully deleted entity IDs
+        """
+        raise NotImplementedError("Implement in subclass")
+
+    async def cleanup(self):
+        """Comprehensive cleanup of ALL test data.
+
+        This should:
+        1. Delete current session entities
+        2. Find orphaned test entities from failed runs
+        3. Delete test projects/workspaces
+        """
+        raise NotImplementedError("Implement in subclass")
+
+    def _headers(self) -> Dict[str, str]:
+        """Return auth headers for API requests."""
+        return {
+            "Authorization": f"Bearer {self.access_token}",
+            "Accept": "application/json",
+            "Content-Type": "application/json",
+        }
+
+    async def _rate_limit(self):
+        """Simple rate limiting (use if API requires it)."""
+        now = time.time()
+        elapsed = now - self.last_request_time
+        if elapsed < self.min_delay:
+            await asyncio.sleep(self.min_delay - elapsed)
+        self.last_request_time = time.time()
+```
+
+### Implementing `create_entities()` - The Critical Method
+
+**Key principle:** Create at least one instance of **every entity type** your connector syncs.
+
+```python
+async def create_entities(self) -> List[Dict[str, Any]]:
+    """Create comprehensive test entities.
+
+    Strategy:
+    1. Create parent entities (projects, tasks, etc.)
+    2. For EACH parent, create child entities (comments, files)
+    3. Track all created entities with verification tokens
+    4. Return entity descriptors for verification
+    """
+    self.logger.info(f"🥁 Creating {self.entity_count} comprehensive test entities")
+
+    # Ensure prerequisites (workspace, project, etc.)
+    await self._ensure_workspace()
+    await self._ensure_project()
+
+    from monke.generation.my_connector import (
+        generate_task,
+        generate_comment,
+        generate_file_attachment,
+    )
+
+    all_entities: List[Dict[str, Any]] = []
+    semaphore = asyncio.Semaphore(self.max_concurrency)
+
+    async with httpx.AsyncClient() as client:
+
+        # Create parent entities (tasks)
+        for i in range(self.entity_count):
+            async with semaphore:
+                # Generate unique token for this task
+                task_token = str(uuid.uuid4())[:8]
+
+                self.logger.info(f"Creating task {i+1}/{self.entity_count} with token {task_token}")
+
+                # Generate content
+                task_data = await generate_task(self.openai_model, task_token)
+
+                # Create via API
+                await self._rate_limit()
+                resp = await client.post(
+                    f"{self.API_BASE}/tasks",
+                    headers=self._headers(),
+                    json={
+                        "title": task_data["title"],
+                        "description": task_data["description"],
+                        "project_id": self._project_id,
+                    },
+                )
+                resp.raise_for_status()
+                task = resp.json()
+
+                # Track the task
+                task_descriptor = {
+                    "type": "task",
+                    "id": task["id"],
+                    "name": task["title"],
+                    "token": task_token,
+                    "expected_content": task_token,
+                    "path": f"my_connector/task/{task['id']}",
+                }
+                self._tasks.append(task_descriptor)
+                all_entities.append(task_descriptor)
+
+                # ========================================
+                # CRITICAL: Create child entities
+                # ========================================
+
+                # 1. Create comments for this task
+                for comment_idx in range(2):  # 2 comments per task
+                    comment_token = str(uuid.uuid4())[:8]
+
+                    self.logger.info(
+                        f"  Creating comment {comment_idx+1}/2 for task {task['id']} "
+                        f"with token {comment_token}"
+                    )
+
+                    comment_data = await generate_comment(self.openai_model, comment_token)
+
+                    await self._rate_limit()
+                    resp = await client.post(
+                        f"{self.API_BASE}/tasks/{task['id']}/comments",
+                        headers=self._headers(),
+                        json={"text": comment_data["text"]},
+                    )
+                    resp.raise_for_status()
+                    comment = resp.json()
+
+                    # Track the comment
+                    comment_descriptor = {
+                        "type": "comment",
+                        "id": comment["id"],
+                        "parent_id": task["id"],
+                        "token": comment_token,
+                        "expected_content": comment_token,
+                        "path": f"my_connector/comment/{comment['id']}",
+                    }
+                    self._comments.append(comment_descriptor)
+                    all_entities.append(comment_descriptor)
+
+                # 2. Create file attachment for this task
+                file_token = str(uuid.uuid4())[:8]
+
+                self.logger.info(
+                    f"  Creating file attachment for task {task['id']} "
+                    f"with token {file_token}"
+                )
+
+                # Generate a test file
+                file_content, file_name = await generate_file_attachment(
+                    self.openai_model,
+                    file_token
+                )
+
+                await self._rate_limit()
+
+                # Upload the file
+                files = {"file": (file_name, file_content, "text/plain")}
+                resp = await client.post(
+                    f"{self.API_BASE}/tasks/{task['id']}/attachments",
+                    headers={"Authorization": f"Bearer {self.access_token}"},
+                    files=files,
+                )
+                resp.raise_for_status()
+                attachment = resp.json()
+
+                # Track the file
+                file_descriptor = {
+                    "type": "file",
+                    "id": attachment["id"],
+                    "parent_id": task["id"],
+                    "name": file_name,
+                    "token": file_token,
+                    "expected_content": file_token,
+                    "path": f"my_connector/file/{attachment['id']}",
+                }
+                self._files.append(file_descriptor)
+                all_entities.append(file_descriptor)
+
+        self.logger.info(
+            f"✅ Created {len(self._tasks)} tasks, "
+            f"{len(self._comments)} comments, "
+            f"{len(self._files)} files"
+        )
+
+    self.created_entities = all_entities
+    return all_entities
+```
+
+### Key Principles for `create_entities()`
+
+1. **Create nested entities** - Don't just create tasks; create comments ON those tasks, files ATTACHED to those tasks
+2. **Unique tokens per entity** - Each comment, file, task gets its own verification token
+3. **Track everything** - Store descriptors for all created entities
+4. **Parallel creation** - Use `asyncio.Semaphore` for efficient bulk creation
+5. **Error handling** - Log failures but continue creating other entities
+
+### Implementing `update_entities()`
+
+```python
+async def update_entities(self) -> List[Dict[str, Any]]:
+    """Update entities to test incremental sync.
+
+    Strategy:
+    - Update a subset of tasks (to test modified_at tracking)
+    - Update some comments
+    - Optionally add new comments to existing tasks
+    """
+    self.logger.info("🥁 Updating test entities for incremental sync")
+
+    if not self._tasks:
+        return []
+
+    from monke.generation.my_connector import generate_task, generate_comment
+
+    updated_entities: List[Dict[str, Any]] = []
+    count = min(2, len(self._tasks))  # Update first 2 tasks
+
+    async with httpx.AsyncClient() as client:
+        # Update tasks
+        for i in range(count):
+            task = self._tasks[i]
+
+            # Generate new content with SAME token
+            task_data = await generate_task(self.openai_model, task["token"])
+
+            await self._rate_limit()
+            resp = await client.put(
+                f"{self.API_BASE}/tasks/{task['id']}",
+                headers=self._headers(),
+                json={
+                    "title": task_data["title"],
+                    "description": task_data["description"],
+                },
+            )
+            resp.raise_for_status()
+
+            updated_entities.append({
+                **task,
+                "name": task_data["title"],
+            })
+
+        # Add new comments to updated tasks
+        for i in range(count):
+            task = self._tasks[i]
+            comment_token = str(uuid.uuid4())[:8]
+
+            comment_data = await generate_comment(self.openai_model, comment_token)
+
+            await self._rate_limit()
+            resp = await client.post(
+                f"{self.API_BASE}/tasks/{task['id']}/comments",
+                headers=self._headers(),
+                json={"text": comment_data["text"]},
+            )
+            resp.raise_for_status()
+            comment = resp.json()
+
+            comment_descriptor = {
+                "type": "comment",
+                "id": comment["id"],
+                "parent_id": task["id"],
+                "token": comment_token,
+                "expected_content": comment_token,
+                "path": f"my_connector/comment/{comment['id']}",
+            }
+            self._comments.append(comment_descriptor)
+            updated_entities.append(comment_descriptor)
+
+    return updated_entities
+```
+
+### Implementing `cleanup()`
+
+**Critical:** Clean up ALL test data, including orphaned entities from failed test runs.
+
+```python
+async def cleanup(self):
+    """Comprehensive cleanup of all test data."""
+    self.logger.info("🧹 Starting comprehensive workspace cleanup")
+
+    await self._ensure_workspace()
+
+    cleanup_stats = {
+        "tasks_deleted": 0,
+        "comments_deleted": 0,
+        "files_deleted": 0,
+        "projects_deleted": 0,
+        "errors": 0,
+    }
+
+    try:
+        # 1. Clean up current session
+        if self._files:
+            for file in self._files:
+                try:
+                    await self._delete_file(file["id"])
+                    cleanup_stats["files_deleted"] += 1
+                except Exception as e:
+                    self.logger.warning(f"Failed to delete file {file['id']}: {e}")
+                    cleanup_stats["errors"] += 1
+
+        if self._comments:
+            for comment in self._comments:
+                try:
+                    await self._delete_comment(comment["id"])
+                    cleanup_stats["comments_deleted"] += 1
+                except Exception as e:
+                    self.logger.warning(f"Failed to delete comment {comment['id']}: {e}")
+                    cleanup_stats["errors"] += 1
+
+        if self._tasks:
+            for task in self._tasks:
+                try:
+                    await self._delete_task(task["id"])
+                    cleanup_stats["tasks_deleted"] += 1
+                except Exception as e:
+                    self.logger.warning(f"Failed to delete task {task['id']}: {e}")
+                    cleanup_stats["errors"] += 1
+
+        if self._project_id:
+            await self._delete_project(self._project_id)
+            cleanup_stats["projects_deleted"] += 1
+
+        # 2. Find and clean up orphaned test data
+        orphaned_projects = await self._find_test_projects()
+        for project in orphaned_projects:
+            try:
+                await self._delete_project(project["id"])
+                cleanup_stats["projects_deleted"] += 1
+            except Exception as e:
+                cleanup_stats["errors"] += 1
+
+        self.logger.info(
+            f"🧹 Cleanup completed: {cleanup_stats['tasks_deleted']} tasks, "
+            f"{cleanup_stats['comments_deleted']} comments, "
+            f"{cleanup_stats['files_deleted']} files, "
+            f"{cleanup_stats['projects_deleted']} projects deleted, "
+            f"{cleanup_stats['errors']} errors"
+        )
+
+    except Exception as e:
+        self.logger.error(f"❌ Error during cleanup: {e}")
+        # Don't re-raise - cleanup is best-effort
+```
+
+---
+
+## Part 2: Generation Schemas
+
+Define Pydantic schemas for structured content generation.
+
+### File Location
+```
+monke/generation/schemas/{short_name}.py
+```
+
+### Structure
+
+```python
+"""Pydantic schemas for {Connector Name} test content generation."""
+
+from typing import List
+from pydantic import BaseModel, Field
+
+
+class TaskContent(BaseModel):
+    """Content structure for a generated task."""
+
+    description: str = Field(
+        ...,
+        description="Detailed task description with verification token embedded"
+    )
+
+    objectives: List[str] = Field(
+        ...,
+        description="List of objectives for this task"
+    )
+
+    technical_details: str = Field(
+        ...,
+        description="Technical implementation details"
+    )
+
+    acceptance_criteria: List[str] = Field(
+        ...,
+        description="Checklist of acceptance criteria"
+    )
+
+    comments: List[str] = Field(
+        default_factory=list,
+        description="Suggested comments/discussions"
+    )
+
+
+class TaskSpec(BaseModel):
+    """Metadata for task generation."""
+
+    title: str = Field(..., description="Task title")
+    token: str = Field(..., description="Verification token to embed")
+    priority: str = Field(default="medium", description="Priority level")
+    tags: List[str] = Field(default_factory=list, description="Tags to apply")
+
+
+class MyConnectorTask(BaseModel):
+    """Complete task structure for generation."""
+
+    spec: TaskSpec
+    content: TaskContent
+
+
+class CommentContent(BaseModel):
+    """Content structure for a comment."""
+
+    text: str = Field(
+        ...,
+        description="Comment text with verification token embedded"
+    )
+
+    author_name: str = Field(
+        default="Test User",
+        description="Name of comment author"
+    )
+
+
+class FileContent(BaseModel):
+    """Content structure for a file attachment."""
+
+    content: str = Field(
+        ...,
+        description="File content with verification token embedded"
+    )
+
+    filename: str = Field(
+        ...,
+        description="Name of the file"
+    )
+```
+
+---
+
+## Part 3: Generation Adapter
+
+Implement the LLM-powered content generation.
+
+### File Location
+```
+monke/generation/{short_name}.py
+```
+
+### Structure
+
+```python
+"""{Connector Name} content generation adapter.
+
+Generates realistic test content using LLM.
+"""
+
+from typing import List, Tuple
+
+from monke.generation.schemas.my_connector import (
+    MyConnectorTask,
+    CommentContent,
+    FileContent,
+)
+from monke.client.llm import LLMClient
+
+
+async def generate_task(model: str, token: str) -> dict:
+    """Generate task content with embedded verification token.
+
+    Args:
+        model: LLM model to use
+        token: Unique token to embed in content
+
+    Returns:
+        Dict with title and description
+    """
+    llm = LLMClient(model_override=model)
+
+    instruction = (
+        f"Generate a realistic task for a software development project. "
+        f"You MUST include the literal token '{token}' in the description. "
+        f"The task should be technical but believable. "
+        f"Create meaningful objectives and acceptance criteria."
+    )
+
+    task = await llm.generate_structured(MyConnectorTask, instruction)
+    task.spec.token = token
+
+    # Ensure token appears in description
+    if token not in task.content.description:
+        task.content.description += f"\n\n**Verification Token**: {token}"
+
+    return {
+        "title": task.spec.title,
+        "description": task.content.description,
+        "objectives": task.content.objectives,
+        "acceptance_criteria": task.content.acceptance_criteria,
+    }
+
+
+async def generate_comment(model: str, token: str) -> dict:
+    """Generate comment content with embedded verification token.
+
+    Args:
+        model: LLM model to use
+        token: Unique token to embed in content
+
+    Returns:
+        Dict with comment text
+    """
+    llm = LLMClient(model_override=model)
+
+    instruction = (
+        f"Generate a helpful comment on a software development task. "
+        f"You MUST include the literal token '{token}' in the comment text. "
+        f"The comment should add value, like a question, suggestion, or update."
+    )
+
+    comment = await llm.generate_structured(CommentContent, instruction)
+
+    # Ensure token is present
+    if token not in comment.text:
+        comment.text += f"\n\nToken: {token}"
+
+    return {"text": comment.text}
+
+
+async def generate_file_attachment(model: str, token: str) -> Tuple[bytes, str]:
+    """Generate file attachment content with embedded verification token.
+
+    Args:
+        model: LLM model to use
+        token: Unique token to embed in content
+
+    Returns:
+        Tuple of (file_bytes, filename)
+    """
+    llm = LLMClient(model_override=model)
+
+    instruction = (
+        f"Generate content for a technical document or specification. "
+        f"You MUST include the literal token '{token}' in the content. "
+        f"Make it look like a real technical document."
+    )
+
+    file_data = await llm.generate_structured(FileContent, instruction)
+
+    # Ensure token is present
+    if token not in file_data.content:
+        file_data.content += f"\n\nVerification Token: {token}"
+
+    # Convert to bytes
+    content_bytes = file_data.content.encode("utf-8")
+
+    return content_bytes, file_data.filename
+```
+
+---
+
+## Part 4: Test Configuration
+
+Define the test flow and parameters.
+
+### File Location
+```
+monke/configs/{short_name}.yaml
+```
+
+### Complete Structure
+
+**Note:** The human must set up the authentication section first. The AI agent implements the rest.
+
+```yaml
+name: my_connector_test
+description: End-to-end test for {Connector Name} source
+
+connector:
+  name: {Connector Display Name}
+  type: {short_name}
+
+  # ===== HUMAN SETS THIS UP =====
+  auth_mode: composio  # or direct
+  composio_config:  # If using Composio
+    account_id: ca_xxxxx  # Human obtains from Composio
+    auth_config_id: ac_xxxxx  # Human obtains from Composio
+  # If using direct auth, human adds token to monke/.env
+  # ==============================
+
+  config_fields:
+    openai_model: "gpt-4.1-mini"
+    max_concurrency: 3
+
+test_flow:
+  steps:
+    - cleanup              # Clean up any leftover test data
+    - create               # Create all entity types
+    - sync                 # Trigger Airweave sync
+    - verify               # Verify ALL entities appear in Qdrant
+    - update               # Update some entities
+    - sync                 # Sync again
+    - verify               # Verify updates appear
+    - partial_delete       # Delete subset of entities
+    - sync                 # Sync again
+    - verify_partial_deletion  # Verify deletions (if supported)
+    - verify_remaining_entities  # Verify non-deleted entities still exist
+    - complete_delete      # Delete all remaining entities
+    - sync                 # Final sync
+    - verify_complete_deletion  # Verify all gone
+    - cleanup              # Final cleanup
+    - collection_cleanup   # Delete test collection
+
+deletion:
+  partial_delete_count: 2  # Number of entities to delete in partial_delete step
+  verify_partial_deletion: true  # Set false if API doesn't support deletion detection
+  verify_remaining_entities: true
+  verify_complete_deletion: true
+
+entity_count: 5  # Number of parent entities to create (each gets children)
+
+collection:
+  name: {Connector Name} Test Collection
+
+verification:
+  retry_attempts: 5  # Retry verification this many times
+  retry_delay_seconds: 10  # Wait between retries
+  score_threshold: 0.0  # Minimum similarity score for verification
+  expected_fields:  # Fields that should exist on indexed entities
+    - name
+    - content
+    - entity_id
+    - created_at
+```
+
+### Test Flow Steps Explained
+
+1. **`cleanup`** - Remove any leftover test data from failed runs
+2. **`create`** - Calls `bongo.create_entities()` to create ALL entity types
+3. **`sync`** - Triggers Airweave sync job via API
+4. **`verify`** - Searches Qdrant for each created entity using its token
+5. **`update`** - Calls `bongo.update_entities()` to modify some entities
+6. **`verify_partial_deletion`** - Verifies deleted entities are gone from Qdrant
+7. **`verify_remaining_entities`** - Verifies non-deleted entities still exist
+8. **`verify_complete_deletion`** - Verifies all entities are gone
+
+---
+
+## Part 5: Verification Deep Dive
+
+### How Verification Works
+
+After sync, Monke searches Qdrant for each entity using its embedded token:
+
+```python
+# In monke/core/steps.py
+
+async def verify_entity(entity: Dict[str, Any], collection_id: str):
+    """Search Qdrant for an entity by its verification token."""
+
+    search_results = await qdrant_client.search(
+        collection_id=collection_id,
+        query_text=entity["expected_content"],  # The token
+        limit=5
+    )
+
+    # Check if any result matches
+    for result in search_results:
+        if entity["token"] in result["content"]:
+            return True  # Found it!
+
+    return False  # Not found
+```
+
+### Verifying ALL Entity Types
+
+The key is to return entity descriptors for EVERY created entity:
+
+```python
+# In your bongo's create_entities()
+
+all_entities = []
+
+# Create tasks
+for task in tasks:
+    all_entities.append({
+        "type": "task",
+        "id": task["id"],
+        "token": task_token,
+        "expected_content": task_token,
+    })
+
+    # Create comments FOR THIS TASK
+    for comment in comments:
+        all_entities.append({
+            "type": "comment",
+            "id": comment["id"],
+            "parent_id": task["id"],
+            "token": comment_token,
+            "expected_content": comment_token,
+        })
+
+    # Create file FOR THIS TASK
+    all_entities.append({
+        "type": "file",
+        "id": file["id"],
+        "parent_id": task["id"],
+        "token": file_token,
+        "expected_content": file_token,
+    })
+
+return all_entities  # Monke will verify EACH of these
+```
+
+### Custom Verification (Advanced)
+
+If you need custom verification logic:
+
+```python
+# In monke/core/steps.py - extend the verification step
+
+async def verify_my_connector_entities(entities, collection_id):
+    """Custom verification for MyConnector entities."""
+
+    verified = []
+    failed = []
+
+    for entity in entities:
+        if entity["type"] == "task":
+            # Standard token search
+            found = await verify_entity(entity, collection_id)
+
+        elif entity["type"] == "comment":
+            # Custom: Verify comment is linked to parent task
+            found = await verify_comment_with_parent(entity, collection_id)
+
+        elif entity["type"] == "file":
+            # Custom: Verify file content was extracted
+            found = await verify_file_content(entity, collection_id)
+
+        if found:
+            verified.append(entity)
+        else:
+            failed.append(entity)
+
+    return verified, failed
+```
+
+---
+
+## Part 6: Best Practices
+
+### 1. Test Entity Relationships
+
+Verify that breadcrumbs are preserved:
+
+```python
+# After sync, search for task and check its breadcrumbs
+result = await search_qdrant(task_token)
+
+assert "workspace" in result["breadcrumbs"]
+assert "project" in result["breadcrumbs"]
+```
+
+### 2. Test File Content Extraction
+
+For file entities, verify the TEXT was extracted:
+
+```python
+# Search for token that was in the file content
+result = await search_qdrant(file_token)
+
+# Should find it in the extracted text chunks
+assert result["entity_type"] == "file"
+assert file_token in result["content"]
+```
+
+### 3. Test Incremental Sync
+
+```python
+# 1. Create entities with token "abc123"
+await bongo.create_entities()
+await sync()
+await verify()  # Should find "abc123"
+
+# 2. Update entities with NEW content but SAME token
+await bongo.update_entities()
+await sync()
+await verify()  # Should still find "abc123" but with updated content
+```
+
+### 4. Test Deletion Detection (if supported)
+
+```python
+# 1. Create and sync entities
+entities = await bongo.create_entities()
+await sync()
+await verify()  # All found
+
+# 2. Delete some entities
+deleted = await bongo.delete_specific_entities(entities[:2])
+await sync()
+
+# 3. Verify deleted entities are gone
+for entity_id in deleted:
+    result = await search_qdrant(entity_id)
+    assert result is None  # Should not be found
+
+# 4. Verify remaining entities still exist
+for entity in entities[2:]:
+    result = await search_qdrant(entity["token"])
+    assert result is not None  # Should still be found
+```
+
+### 5. Handle Rate Limits (If Needed)
+
+Most APIs don't need rate limiting in tests. Add only if you encounter 429 errors:
+
+```python
+async def _rate_limit(self):
+    """Simple rate limiting."""
+    now = time.time()
+    elapsed = now - self.last_request_time
+    if elapsed < self.min_delay:
+        await asyncio.sleep(self.min_delay - elapsed)
+    self.last_request_time = time.time()
+
+# Use before API calls if needed
+await self._rate_limit()
+response = await client.post(...)
+```
+
+---
+
+## Part 7: Running Tests
+
+### Running Tests (Human Task)
+
+**The human runs these commands, not the AI agent:**
+
+```bash
+# Run single connector test
+cd airweave
+./monke.sh my_connector
+
+# Run with verbose logging (for debugging)
+MONKE_VERBOSE=1 ./monke.sh my_connector
+```
+
+### Debugging Failed Tests (Human Task)
+
+**The human debugs test failures:**
+
+```bash
+# Enable detailed logging
+MONKE_VERBOSE=1 ./monke.sh my_connector
+
+# Check logs for:
+# - Entity creation failures
+# - Sync errors
+# - Verification mismatches
+```
+
+**Then ask the AI agent to fix code issues found.**
+
+### Common Failure Modes
+
+1. **Entity not found in Qdrant**
+   - Token might not be embedded in content
+   - Entity might not have synced (check source logs)
+   - Search might be timing out (increase retry attempts)
+
+2. **Comments not found**
+   - Comments might not be generated in bongo
+   - Source might not be yielding comment entities
+   - Comment entity schema might be wrong
+
+3. **Files not found**
+   - File download might be failing
+   - Text extraction might be failing
+   - File entity might not have `download_url` set
+
+---
+
+## Complete Example
+
+See the Asana tests for a complete example:
+- Bongo: `monke/bongos/asana.py`
+- Schemas: `monke/generation/schemas/asana.py`
+- Generation: `monke/generation/asana.py`
+- Config: `monke/configs/asana.yaml`
+
+**Note:** The Asana example creates comments but does NOT verify them. This is a bug that should be fixed. Your implementation should verify ALL entity types.
+
+---
+
+## Checklist
+
+- [ ] Bongo creates ALL entity types (not just top-level)
+- [ ] Each entity gets a unique verification token
+- [ ] Tokens are embedded in searchable content
+- [ ] Entity descriptors include type, id, token, parent_id (if nested)
+- [ ] Generation schemas defined for all entity types
+- [ ] Generation adapters use LLMClient
+- [ ] Test config includes comprehensive test_flow
+- [ ] Verification settings are appropriate (retries, delays)
+- [ ] cleanup() removes ALL test data
+- [ ] Rate limiting added (only if API requires it)
+- [ ] File attachments are created and verified (if supported)
+- [ ] Comments/discussions are created and verified (if supported)
+- [ ] Update flow tests incremental sync
+- [ ] Deletion flow tests deletion detection (if supported)
+
+---
+
+## Next Steps
+
+1. Implement the bongo, schemas, generation, and config
+2. Run the test locally: `./monke.sh {short_name}`
+3. Debug any failures by checking logs
+4. Verify ALL entity types appear in Qdrant after sync
+5. If any entity type is missing, check your source connector's `generate_entities()` method
diff --git a/.cursor/rules/source-connector-implementation.mdc b/.cursor/rules/source-connector-implementation.mdc
@@ -0,0 +1,870 @@
+# Building a Source Connector in Airweave
+
+## Overview
+
+A **source connector** in Airweave is a Python module that extracts data from an external service and transforms it into searchable entities. This guide covers everything you need to build a production-ready connector.
+
+## Core Components
+
+Every source connector requires three main components:
+
+1. **Source implementation** (`backend/airweave/platform/sources/{short_name}.py`)
+2. **Entity schemas** (`backend/airweave/platform/entities/{short_name}.py`)
+3. **OAuth configuration** (`backend/airweave/platform/auth/yaml/dev.integrations.yaml`)
+
+---
+
+## Part 1: Entity Schemas
+
+Start with entities because they define your data model.
+
+### File Location
+```
+backend/airweave/platform/entities/{short_name}.py
+```
+
+### Entity Types
+
+There are two base entity types:
+
+1. **ChunkEntity** - Text-based entities (tasks, messages, documents, etc.)
+2. **FileEntity** - File attachments (PDFs, images, etc.)
+
+### Basic Structure
+
+```python
+"""Entity schemas for {Connector Name}."""
+
+from datetime import datetime
+from typing import Any, Dict, List, Optional
+
+from pydantic import Field
+
+from airweave.platform.entities._airweave_field import AirweaveField
+from airweave.platform.entities._base import ChunkEntity, FileEntity
+
+
+class MyConnectorEntity(ChunkEntity):
+    """Schema for primary entity type."""
+
+    # Required fields
+    name: str = AirweaveField(
+        ...,
+        description="Display name of the entity",
+        embeddable=True  # This field will be embedded for search
+    )
+
+    # Timestamps (critical for incremental sync)
+    created_at: Optional[datetime] = AirweaveField(
+        None,
+        description="When this entity was created",
+        embeddable=True,
+        is_created_at=True  # Marks this as the creation timestamp
+    )
+
+    modified_at: Optional[datetime] = AirweaveField(
+        None,
+        description="When this entity was last modified",
+        embeddable=True,
+        is_updated_at=True  # Marks this as the update timestamp
+    )
+
+    # Content fields
+    content: Optional[str] = AirweaveField(
+        None,
+        description="The main text content",
+        embeddable=True  # Make searchable
+    )
+
+    # Metadata fields (not embeddable)
+    external_id: str = Field(
+        ...,
+        description="Unique ID from the external system"
+    )
+
+    permalink_url: Optional[str] = Field(
+        None,
+        description="Direct link to view in external system"
+    )
+```
+
+### Key Principles
+
+#### 1. Use AirweaveField for Searchable Content
+
+```python
+# Searchable text
+description: str = AirweaveField(
+    ...,
+    description="Task description",
+    embeddable=True
+)
+
+# Searchable structured data
+assignee: Optional[Dict] = AirweaveField(
+    None,
+    description="User assigned to this task",
+    embeddable=True
+)
+
+# Non-searchable metadata
+external_id: str = Field(
+    ...,
+    description="ID in external system"
+)
+```
+
+#### 2. Always Include Timestamps
+
+Every entity should have `created_at` and/or `modified_at` with proper flags:
+
+```python
+created_at: Optional[datetime] = AirweaveField(
+    None,
+    description="Creation time",
+    embeddable=True,
+    is_created_at=True  # System uses this for incremental sync
+)
+
+modified_at: Optional[datetime] = AirweaveField(
+    None,
+    description="Last modification time",
+    embeddable=True,
+    is_updated_at=True  # System uses this for incremental sync
+)
+```
+
+#### 3. Model Entity Hierarchies
+
+If your connector has parent-child relationships, create separate entity classes:
+
+```python
+class WorkspaceEntity(ChunkEntity):
+    """Top-level container."""
+    name: str = AirweaveField(..., embeddable=True)
+    # ...
+
+class ProjectEntity(ChunkEntity):
+    """Belongs to workspace."""
+    name: str = AirweaveField(..., embeddable=True)
+    workspace_id: str = Field(...)
+    workspace_name: str = AirweaveField(..., embeddable=True)
+    # ...
+
+class TaskEntity(ChunkEntity):
+    """Belongs to project."""
+    name: str = AirweaveField(..., embeddable=True)
+    project_id: str = Field(...)
+    section_id: Optional[str] = Field(None)
+    # ...
+```
+
+#### 4. File Entities
+
+For attachments, inherit from `FileEntity`:
+
+```python
+class MyConnectorFileEntity(FileEntity):
+    """Schema for file attachments."""
+
+    # FileEntity provides: file_id, name, mime_type, size, download_url
+    # Add connector-specific fields:
+
+    parent_task_id: str = Field(
+        ...,
+        description="ID of the task this file is attached to"
+    )
+
+    created_at: Optional[datetime] = AirweaveField(
+        None,
+        description="Upload time",
+        embeddable=True,
+        is_created_at=True
+    )
+```
+
+---
+
+## Part 2: Source Implementation
+
+### File Location
+```
+backend/airweave/platform/sources/{short_name}.py
+```
+
+### Basic Structure
+
+```python
+"""{Connector Name} source implementation."""
+
+from typing import Any, AsyncGenerator, Dict, List, Optional
+
+import httpx
+from tenacity import retry, stop_after_attempt, wait_exponential
+
+from airweave.core.exceptions import TokenRefreshError
+from airweave.platform.decorators import source
+from airweave.platform.entities._base import Breadcrumb, ChunkEntity
+from airweave.platform.entities.{short_name} import (
+    MyConnectorEntity,
+    MyConnectorFileEntity,
+)
+from airweave.platform.sources._base import BaseSource
+from airweave.schemas.source_connection import AuthenticationMethod, OAuthType
+
+
+@source(
+    name="{Connector Display Name}",
+    short_name="{short_name}",
+    auth_methods=[
+        AuthenticationMethod.OAUTH_BROWSER,
+        AuthenticationMethod.OAUTH_TOKEN,
+        AuthenticationMethod.AUTH_PROVIDER,
+    ],
+    oauth_type=OAuthType.WITH_REFRESH,  # or WITH_ROTATING_REFRESH, ACCESS_ONLY
+    auth_config_class=None,
+    config_class="{ConnectorName}Config",  # Must match schema name
+    labels=["Category"],  # e.g., "Project Management", "CRM", "Storage"
+    supports_continuous=False,  # Set to True if you support webhook-based sync
+)
+class MyConnectorSource(BaseSource):
+    """{Connector Name} source connector.
+
+    Syncs {list of entity types} from {Connector Name}.
+    """
+
+    @classmethod
+    async def create(
+        cls, access_token: str, config: Optional[Dict[str, Any]] = None
+    ) -> "MyConnectorSource":
+        """Create and configure the source.
+
+        Args:
+            access_token: OAuth access token or API key
+            config: Optional configuration (e.g., workspace filters)
+
+        Returns:
+            Configured source instance
+        """
+        instance = cls()
+        instance.access_token = access_token
+
+        # Store config as instance attributes
+        if config:
+            instance.workspace_id = config.get("workspace_id")
+            instance.exclude_pattern = config.get("exclude_pattern", "")
+        else:
+            instance.workspace_id = None
+            instance.exclude_pattern = ""
+
+        return instance
+
+    async def generate_entities(self) -> AsyncGenerator[ChunkEntity, None]:
+        """Generate all entities from the source.
+
+        This is the main entry point called by the sync engine.
+        """
+        async with self.http_client() as client:
+            # Generate entities hierarchically
+            async for top_level in self._generate_top_level(client):
+                yield top_level
+
+                # Generate children with breadcrumb tracking
+                async for child in self._generate_children(client, top_level):
+                    yield child
+
+    async def validate(self) -> bool:
+        """Verify credentials by pinging the API.
+
+        Returns:
+            True if credentials are valid, False otherwise
+        """
+        return await self._validate_oauth2(
+            ping_url="https://api.example.com/v1/me",
+            headers={"Accept": "application/json"},
+            timeout=10.0,
+        )
+```
+
+### Critical Methods
+
+#### 1. The `create()` Classmethod
+
+This is called once when a sync starts:
+
+```python
+@classmethod
+async def create(
+    cls, access_token: str, config: Optional[Dict[str, Any]] = None
+) -> "MyConnectorSource":
+    """Create and configure the source."""
+    instance = cls()
+    instance.access_token = access_token
+
+    # Parse config fields
+    if config:
+        # Store as instance attributes for use in generate_entities()
+        instance.workspace_filter = config.get("workspace_filter", "")
+        instance.include_archived = config.get("include_archived", False)
+    else:
+        instance.workspace_filter = ""
+        instance.include_archived = False
+
+    return instance
+```
+
+#### 2. The `generate_entities()` Method
+
+This is an async generator that yields entities:
+
+```python
+async def generate_entities(self) -> AsyncGenerator[ChunkEntity, None]:
+    """Generate all entities from the source.
+
+    Key principles:
+    - Generate hierarchically (parents before children)
+    - Track breadcrumbs for relationships
+    - Handle pagination
+    - Use rate limiting
+    """
+    async with self.http_client() as client:
+        # Top-level entities
+        async for workspace in self._generate_workspaces(client):
+            yield workspace
+
+            workspace_breadcrumb = Breadcrumb(
+                entity_id=workspace.entity_id,
+                name=workspace.name,
+                type="workspace"
+            )
+
+            # Child entities
+            async for project in self._generate_projects(client, workspace):
+                yield project
+
+                project_breadcrumb = Breadcrumb(
+                    entity_id=project.entity_id,
+                    name=project.name,
+                    type="project"
+                )
+                breadcrumbs = [workspace_breadcrumb, project_breadcrumb]
+
+                # Grandchild entities
+                async for task in self._generate_tasks(client, project, breadcrumbs):
+                    yield task
+```
+
+#### 3. Making API Requests with Token Refresh
+
+Always use this pattern for authenticated requests:
+
+```python
+@retry(
+    stop=stop_after_attempt(3),
+    wait=wait_exponential(multiplier=1, min=2, max=10),
+    reraise=True
+)
+async def _get_with_auth(
+    self,
+    client: httpx.AsyncClient,
+    url: str,
+    params: Optional[Dict[str, Any]] = None
+) -> Dict:
+    """Make authenticated GET request with automatic token refresh.
+
+    This method handles:
+    - Token refresh on 401 errors
+    - Retries with exponential backoff
+    - Proper error logging
+    """
+    # Get a valid token (will refresh if needed)
+    access_token = await self.get_access_token()
+    if not access_token:
+        raise ValueError("No access token available")
+
+    headers = {"Authorization": f"Bearer {access_token}"}
+
+    try:
+        response = await client.get(url, headers=headers, params=params)
+
+        # Handle 401 Unauthorized - token might have expired
+        if response.status_code == 401:
+            self.logger.warning(f"Received 401 for {url}, refreshing token...")
+
+            if self.token_manager:
+                try:
+                    # Force refresh the token
+                    new_token = await self.token_manager.refresh_on_unauthorized()
+                    headers = {"Authorization": f"Bearer {new_token}"}
+
+                    # Retry with new token
+                    self.logger.info(f"Retrying with refreshed token: {url}")
+                    response = await client.get(url, headers=headers, params=params)
+
+                except TokenRefreshError as e:
+                    self.logger.error(f"Failed to refresh token: {str(e)}")
+                    response.raise_for_status()
+            else:
+                self.logger.error("No token manager available")
+                response.raise_for_status()
+
+        response.raise_for_status()
+        return response.json()
+
+    except httpx.HTTPStatusError as e:
+        self.logger.error(f"HTTP error: {e.response.status_code} for {url}")
+        raise
+    except Exception as e:
+        self.logger.error(f"Unexpected error: {url}, {str(e)}")
+        raise
+```
+
+### Handling Hierarchical Data
+
+Use breadcrumbs to track entity relationships:
+
+```python
+async def _generate_projects(
+    self,
+    client: httpx.AsyncClient,
+    workspace: WorkspaceEntity,
+    workspace_breadcrumb: Breadcrumb
+) -> AsyncGenerator[ChunkEntity, None]:
+    """Generate projects within a workspace."""
+
+    data = await self._get_with_auth(
+        client,
+        f"https://api.example.com/workspaces/{workspace.entity_id}/projects"
+    )
+
+    for project_data in data.get("projects", []):
+        yield ProjectEntity(
+            entity_id=project_data["id"],
+            breadcrumbs=[workspace_breadcrumb],  # Parent relationship
+            name=project_data["name"],
+            workspace_id=workspace.entity_id,
+            workspace_name=workspace.name,
+            # ... other fields
+        )
+```
+
+### Handling File Entities
+
+Use the `process_file_entity()` helper:
+
+```python
+async def _generate_file_entities(
+    self,
+    client: httpx.AsyncClient,
+    task: TaskEntity,
+    task_breadcrumbs: List[Breadcrumb]
+) -> AsyncGenerator[ChunkEntity, None]:
+    """Generate file attachments for a task."""
+
+    data = await self._get_with_auth(
+        client,
+        f"https://api.example.com/tasks/{task.entity_id}/attachments"
+    )
+
+    for attachment in data.get("attachments", []):
+        # Create the file entity
+        file_entity = MyConnectorFileEntity(
+            entity_id=attachment["id"],
+            breadcrumbs=task_breadcrumbs,
+            file_id=attachment["id"],
+            name=attachment["name"],
+            mime_type=attachment.get("mime_type"),
+            size=attachment.get("size"),
+            total_size=attachment.get("size"),
+            download_url=attachment["download_url"],
+            created_at=attachment.get("created_at"),
+            parent_task_id=task.entity_id,
+        )
+
+        # Prepare auth headers if needed
+        headers = None
+        if file_entity.download_url.startswith("https://api.example.com/"):
+            token = await self.get_access_token()
+            headers = {"Authorization": f"Bearer {token}"}
+
+        # Process the file (downloads, extracts text, chunks)
+        processed_entity = await self.process_file_entity(
+            file_entity=file_entity,
+            headers=headers,
+        )
+
+        yield processed_entity
+```
+
+### Pagination
+
+Handle paginated APIs properly:
+
+```python
+async def _get_all_pages(
+    self,
+    client: httpx.AsyncClient,
+    url: str,
+    params: Optional[Dict[str, Any]] = None
+) -> List[Dict]:
+    """Fetch all pages of a paginated endpoint."""
+    all_items = []
+    next_page_token = None
+
+    while True:
+        request_params = {**(params or {})}
+        if next_page_token:
+            request_params["page_token"] = next_page_token
+
+        response = await self._get_with_auth(client, url, request_params)
+
+        all_items.extend(response.get("items", []))
+
+        # Check for next page
+        next_page_token = response.get("next_page_token")
+        if not next_page_token:
+            break
+
+    return all_items
+```
+
+### Rate Limiting (Optional)
+
+If the API has strict rate limits, add simple rate limiting:
+
+```python
+import time
+import asyncio
+
+class MyConnectorSource(BaseSource):
+    def __init__(self):
+        super().__init__()
+        self.last_request_time = 0.0
+        self.min_request_interval = 0.2  # 200ms between requests
+
+    async def _rate_limit(self):
+        """Simple rate limiting."""
+        now = time.time()
+        elapsed = now - self.last_request_time
+        if elapsed < self.min_request_interval:
+            await asyncio.sleep(self.min_request_interval - elapsed)
+        self.last_request_time = time.time()
+
+    async def _get_with_auth(self, client, url, params=None):
+        await self._rate_limit()
+        # ... rest of request logic
+```
+
+Most APIs don't need this initially. Add it if you encounter 429 errors.
+
+---
+
+## Part 3: OAuth Configuration
+
+### File Location
+```
+backend/airweave/platform/auth/yaml/dev.integrations.yaml
+```
+
+**Note:** The human has already set up OAuth credentials here. This configuration exists and contains the client_id, client_secret, and scopes for your connector.
+
+### OAuth Types (For Reference)
+
+The existing configuration will have one of these `oauth_type` values:
+
+1. **`with_refresh`** - Standard OAuth2 with non-rotating refresh tokens (Gmail, Asana, Dropbox)
+2. **`with_rotating_refresh`** - OAuth2 with rotating refresh tokens (Outlook, Jira, Confluence)
+3. **`access_only`** - OAuth2 without refresh tokens (Notion, Linear, Slack)
+
+---
+
+## Part 3.5: Auth Configuration Class
+
+### File Location
+```
+backend/airweave/platform/configs/auth.py
+```
+
+**Add your connector's auth configuration class** to match the OAuth type from the YAML:
+
+### For OAuth2 with Refresh Tokens
+
+```python
+class MyConnectorAuthConfig(OAuth2WithRefreshAuthConfig):
+    """MyConnector authentication credentials schema."""
+
+    # Inherits refresh_token and access_token from OAuth2WithRefreshAuthConfig
+```
+
+### For OAuth2 without Refresh (Access Only)
+
+```python
+class MyConnectorAuthConfig(OAuth2AuthConfig):
+    """MyConnector authentication credentials schema."""
+
+    # Inherits access_token from OAuth2AuthConfig
+```
+
+### For OAuth2 with BYOC (Bring Your Own Credentials)
+
+If users need to provide their own client_id/client_secret:
+
+```python
+class MyConnectorAuthConfig(OAuth2BYOCAuthConfig):
+    """MyConnector authentication credentials schema."""
+
+    # Inherits client_id, client_secret, refresh_token, and access_token
+```
+
+### For API Key Authentication
+
+```python
+class MyConnectorAuthConfig(AuthConfig):
+    """MyConnector authentication credentials schema."""
+
+    api_key: str = Field(
+        title="API Key",
+        description="The API key for MyConnector"
+    )
+```
+
+### Add to Source Decorator
+
+Reference the auth config in your source decorator:
+
+```python
+@source(
+    name="MyConnector",
+    short_name="my_connector",
+    auth_methods=[...],
+    oauth_type=OAuthType.WITH_REFRESH,
+    auth_config_class="MyConnectorAuthConfig",  # ← Add this
+    config_class="MyConnectorConfig",
+    labels=["Category"],
+)
+```
+
+---
+
+## Part 4: Advanced Topics
+
+### Custom Configuration Schema
+
+If your connector needs user-provided config (workspace IDs, filters, etc.), create a config schema:
+
+```python
+# backend/airweave/schemas/source_configs/{short_name}.py
+
+from typing import Optional
+from pydantic import BaseModel, Field
+
+
+class MyConnectorConfig(BaseModel):
+    """Configuration for MyConnector source."""
+
+    workspace_id: Optional[str] = Field(
+        None,
+        description="Specific workspace to sync (leave empty for all)"
+    )
+
+    include_archived: bool = Field(
+        False,
+        description="Include archived items in sync"
+    )
+
+    exclude_pattern: Optional[str] = Field(
+        None,
+        description="Skip items whose name contains this text"
+    )
+```
+
+Then reference it in the `@source` decorator:
+
+```python
+@source(
+    name="MyConnector",
+    short_name="my_connector",
+    # ...
+    config_class="MyConnectorConfig",  # Must match the class name
+)
+```
+
+### Handling Comments and Discussions
+
+If your API has comments or discussions, create a separate entity:
+
+```python
+class MyConnectorCommentEntity(ChunkEntity):
+    """Comments/replies on tasks or documents."""
+
+    parent_id: str = Field(..., description="ID of parent task/document")
+    author: Dict = AirweaveField(..., embeddable=True)
+    text: str = AirweaveField(..., embeddable=True)
+    created_at: datetime = AirweaveField(..., embeddable=True, is_created_at=True)
+```
+
+Then generate them as children:
+
+```python
+async for task in self._generate_tasks(client, project, breadcrumbs):
+    yield task
+
+    task_breadcrumb = Breadcrumb(
+        entity_id=task.entity_id,
+        name=task.name,
+        type="task"
+    )
+    task_breadcrumbs = [*breadcrumbs, task_breadcrumb]
+
+    # Generate comments for this task
+    async for comment in self._generate_comments(client, task, task_breadcrumbs):
+        yield comment
+```
+
+### Logging Best Practices
+
+Use appropriate log levels:
+
+```python
+async def generate_entities(self):
+    """Generate all entities from the source."""
+    # INFO: High-level operation milestones
+    self.logger.info(f"Starting sync for {self.connector_name}")
+
+    async with self.http_client() as client:
+        # INFO: Major steps
+        self.logger.info("Fetching workspaces...")
+        async for workspace in self._generate_workspaces(client):
+            # DEBUG: Detailed progress
+            self.logger.debug(f"Processing workspace: {workspace.entity_id}")
+            yield workspace
+
+            # INFO: Progress updates
+            self.logger.debug(f"Fetching projects for workspace {workspace.name}...")
+            async for project in self._generate_projects(client, workspace):
+                # DEBUG: Individual entity details
+                self.logger.debug(f"Generated project entity: {project.entity_id}")
+                yield project
+
+    # INFO: Completion summary
+    self.logger.info("Sync completed successfully")
+```
+
+**Log Level Guidelines:**
+- **INFO**: Sync start/end, major phase transitions, progress summaries
+- **DEBUG**: Individual entity processing, API calls, detailed progress
+- **WARNING**: Recoverable errors, skipped entities, permission issues
+- **ERROR**: Unrecoverable errors that stop the sync
+
+### Error Handling Best Practices
+
+```python
+async def _generate_projects(self, client, workspace):
+    """Generate projects with graceful error handling."""
+
+    try:
+        data = await self._get_with_auth(
+            client,
+            f"https://api.example.com/workspaces/{workspace.entity_id}/projects"
+        )
+    except httpx.HTTPStatusError as e:
+        if e.response.status_code == 404:
+            self.logger.warning(f"Workspace {workspace.entity_id} not found, skipping")
+            return
+        elif e.response.status_code == 403:
+            self.logger.warning(f"No access to workspace {workspace.entity_id}, skipping")
+            return
+        else:
+            # Re-raise other errors
+            self.logger.error(f"HTTP error {e.response.status_code} for workspace {workspace.entity_id}")
+            raise
+
+    for project_data in data.get("projects", []):
+        try:
+            yield ProjectEntity(
+                entity_id=project_data["id"],
+                # ...
+            )
+        except Exception as e:
+            self.logger.error(f"Failed to create project entity: {e}")
+            # Continue with other projects
+            continue
+```
+
+---
+
+## Part 5: Testing Your Connector
+
+### Local Development
+
+1. **Start the development environment:**
+   ```bash
+   cd docker
+   docker-compose -f docker-compose.dev.yml up -d
+   ```
+
+2. **Set up OAuth credentials:**
+   - Add your `client_id` and `client_secret` to `dev.integrations.yaml`
+
+3. **Create a test connection:**
+   - Use the frontend UI or API to create a source connection
+   - Complete the OAuth flow
+
+4. **Trigger a sync:**
+   - Monitor logs for entity generation
+   - Check Qdrant for indexed data
+
+### Validation Checklist
+
+- [ ] All entity types are defined in `entities/{short_name}.py`
+- [ ] All entities have `created_at` or `modified_at` timestamps
+- [ ] All searchable fields use `AirweaveField(..., embeddable=True)`
+- [ ] Auth config class added to `platform/configs/auth.py`
+- [ ] Auth config referenced in source `@source` decorator
+- [ ] Source implements `create()`, `generate_entities()`, and `validate()`
+- [ ] Token refresh is handled via `_get_with_auth()` pattern
+- [ ] Hierarchical relationships use breadcrumbs
+- [ ] File entities use `process_file_entity()`
+- [ ] Logging uses proper levels (INFO for milestones, DEBUG for details)
+- [ ] OAuth config is in `dev.integrations.yaml` (human already set this up)
+- [ ] Pagination is handled properly
+- [ ] Rate limiting added if API requires it (most don't need it initially)
+- [ ] Error handling is graceful (don't fail entire sync on one error)
+
+### Common Pitfalls
+
+1. **Forgetting timestamps** - Without `is_created_at` or `is_updated_at`, incremental sync won't work
+2. **Not using `embeddable=True`** - Content won't be searchable
+3. **Not handling token refresh** - Syncs will fail after tokens expire
+4. **Not tracking breadcrumbs** - Entity relationships will be lost
+5. **Blocking the event loop** - Always use `async`/`await` for I/O
+6. **Not handling pagination** - You'll only get first page of results
+7. **Not respecting rate limits** - Your connector will get throttled or banned
+
+---
+
+## Complete Example
+
+See the Asana connector for a complete, production-ready example:
+- Source: `backend/airweave/platform/sources/asana.py`
+- Entities: `backend/airweave/platform/entities/asana.py`
+- OAuth: `backend/airweave/platform/auth/yaml/dev.integrations.yaml` (asana section)
+
+The Asana connector demonstrates:
+- ✅ Hierarchical entity generation (workspaces → projects → sections → tasks)
+- ✅ Token refresh handling
+- ✅ File attachment processing
+- ✅ Comment entity generation
+- ✅ Proper timestamp handling
+- ✅ Breadcrumb tracking
+- ✅ Rate limiting
+- ✅ Error handling
+
+---
+
+## Next Steps
+
+After implementing the source connector:
+1. Inform the human that the source code is ready for testing
+2. Proceed to implement Monke tests using `monke-testing-guide.mdc`
+3. Fix any issues the human reports from testing
diff --git a/.cursor/rules/source-integration-rules.mdc b/.cursor/rules/source-integration-rules.mdc
@@ -1,293 +0,0 @@
----
-description: Use if you're writing a new source connection.
-globs:
-alwaysApply: false
----
-
-# Airweave Source Integration Generator
-
-You are an expert Python developer tasked with creating a new source integration for Airweave. Airweave is an open-source platform that makes any app searchable for agents by syncing data from various sources into vector and graph databases.
-
-#### Real Examples
-
-- **Slack**: Multi-resource API with channels, users, and messages [slack.py](mdc:backend/airweave/platform/sources/slack.py) [slack.py](mdc:backend/airweave/platform/entities/slack.py)
-- **Stripe**: Complex pagination with many resource types [stripe.py](mdc:backend/airweave/platform/sources/stripe.py) [stripe.py](mdc:backend/airweave/platform/entities/stripe.py)
-- **Asana**: Hierarchical data with file handling capabilities [asana.py](mdc:backend/airweave/platform/sources/asana.py) [asana.py](mdc:backend/airweave/platform/entities/asana.py)
-
-## Your Task
-
-Create a complete source integration for {your source} in the following steps
-
-1. Extract necessary information from the docs.
-2. Define entity schemas
-3. Implement source connector
-4. Run, test and debug with the `Local Sync Test` MCP Tool server
-5. Conclude
-
-Do not edit code other than the files you were prompted to create or edit.
-
-
-## 1. Extract necessary information
-
-1. Find out which authentication type is best for this type of source integration, if OAuth2, which type? You can choose between: `oauth2`, `oauth2_with_refresh` and `oauth2_with_refresh_rotating`?
-2. Find out which entities are most important. List them, along with their (optional and primary key) attributes
-3. Find out the relations between these entities. List them along with named foreign key relations.
-
-## 2. Define Entity Schemas
-
-For each data type from your API, create a corresponding entity schema in `backend/airweave/platform/entities/your_service.py`:
-
-It extends from [_base.py](mdc:backend/airweave/platform/entities/_base.py) the BaseEntity, ChunkyEntity or FileEntity.
-
-```python
-class Breadcrumb(BaseModel):
-    """Breadcrumb for tracking ancestry."""
-
-    entity_id: str
-    name: str
-    type: str
-
-
-class BaseEntity(BaseModel):
-    """Base entity schema."""
-
-    # Set in source connector
-    entity_id: str = Field(
-        ..., description="ID of the entity this entity represents in the source."
-
-    )
-    breadcrumbs: list[Breadcrumb] = Field(
-        default_factory=list, description="List of breadcrumbs for this entity."
-    )
-    ...
-
-class ChunkEntity(BaseEntity):
-    """Base class for entities that are storable and embeddable chunks of data."""
-
-class FileEntity(BaseEntity):
-    """Base schema for file entities."""
-
-    # Set in source connector
-    file_id: str = Field(..., description="ID of the file in the source system")
-    name: str = Field(..., description="Name of the file")
-    mime_type: Optional[str] = Field(None, description="MIME type of the file")
-    size: Optional[int] = Field(None, description="Size of the file in bytes")
-    download_url: str = Field(..., description="URL to download the file")
-
-```
-
-## AirweaveField
-
-An enhanced Pydantic Field with Airweave-specific metadata for entity processing.
-
-**Key Features:**
-1. **Embeddable fields** - Mark fields for inclusion in neural embedding with `embeddable=True`
-2. **Timestamp harmonization** - Designate creation/update timestamps with `is_created_at=True` or `is_updated_at=True`
-
-**Example:**
-```python
-name: str = AirweaveField(..., embeddable=True)
-created_at: datetime = AirweaveField(None, is_created_at=True)
-description: str = AirweaveField(.., embeddable=True)
-```
-
-**Benefits:**
-- Type-safe metadata colocated with field definitions
-- Replaces class-level `embeddable_fields` lists
-- Allows `build_embeddable_text()` to build better chunkable body of text
-
-**Helper Methods:**
-- `_get_embeddable_fields()` - Returns list of embeddable field names
-- `get_harmonized_timestamps()` - Returns standardized timestamp mapping
-
-This approach makes entity field configuration more explicit and maintainable by keeping all field metadata in one place.
-
-
-**What you will need to implement, based on the API object described in docs:**
-
-```python
-class YourServiceEntity(ChunkEntity):
-    """Schema for your service entity."""
-
-    name: Optional[str] = None                  # Entity name
-    some_count: int                             # Some count in entity
-    created_at: datetime                        # created_at field
-```
-
-The `entity_id` usually is just the id of the item in the API. If not, find a primary key in the object.
-
-
-## 3. Implement Source Connector
-
-Create your source implementation in `backend/airweave/platform/sources/your_service.py`:
-
-```python
-@source("Display Name", "your_service", AuthType.oauth2)
-class YourServiceSource(BaseSource):
-    """Your service source implementation."""
-
-    BASE_URL = "https://api.yourservice.com/v1"
-
-    @classmethod
-    async def create(cls, access_token: str) -> "YourServiceSource":
-        """Create a new source instance with authentication."""
-        instance = cls()
-        instance.access_token = access_token
-        return instance
-    @tenacity.retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
-    async def _get_with_auth(self, client: httpx.AsyncClient, url: str, params: Optional[dict] = None) -> dict:
-        """Make authenticated API request."""
-        headers = {"Authorization": f"Bearer {self.access_token}"}
-        response = await client.get(url, headers=headers, params=params)
-        response.raise_for_status()
-        return response.json()
-
-    async def _generate_resource_entities(self, client: httpx.AsyncClient) -> AsyncGenerator[ChunkEntity, None]:
-        """Generate entities from a specific resource type."""
-        url = f"{self.BASE_URL}/resources"
-
-        # Handle pagination (if needed)
-        next_cursor = None
-        while True:
-            params = {"limit": 100}
-            if next_cursor:
-                params["cursor"] = next_cursor
-
-            response = await self._get_with_auth(client, url, params)
-
-            for item in response.get("items", []):
-                yield YourServiceEntity(
-                    entity_id=item["id"],
-                    name=item.get("name"),
-                    created_at=datetime.fromisoformat(item.get("created", "")),
-                    content=item.get("description", ""),
-                )
-
-            # Check if there are more pages
-            next_cursor = response.get("next_cursor")
-            if not next_cursor:
-                break
-
-    async def generate_entities(self) -> AsyncGenerator[ChunkEntity, None]:
-        """Main entry point to generate all entities."""
-        async with httpx.AsyncClient() as client:
-            # Generate entities for each resource type
-            async for entity in self._generate_resource_entities(client):
-                yield entity
-
-            # Add additional resource generators as needed
-            # async for entity in self._generate_other_resource_entities(client):
-            #     yield entity
-```
-
-### Source Writing Best Practices
-
-- **Error Handling and Retries**: Use Async Tenacity for robust retry mechanisms
-  ```python
-  async def _get_with_auth(self, client: httpx.AsyncClient, url: str) -> Dict:
-      """Make authenticated GET request to API."""
-      retryer = AsyncRetrying(
-          retry=retry_if_exception_type(httpx.HTTPError),
-          wait=wait_exponential(multiplier=1, min=2, max=10),
-          stop=stop_after_attempt(3),
-      )
-
-      async for attempt in retryer:
-          with attempt:
-              try:
-                  response = await client.get(
-                      url,
-                      headers={"Authorization": f"Bearer {self.access_token}"},
-                  )
-                  response.raise_for_status()
-                  return response.json()
-              except Exception as e:
-                  logger.warning(f"Error calling endpoint: {str(e)}")
-                  raise
-  ```
-
-- **Modular Entity Generation**: Create separate methods for different entity types
-  ```python
-  async def generate_entities(self) -> AsyncGenerator[ChunkEntity, None]:
-      """Main entry point to generate all entities."""
-      async with httpx.AsyncClient() as client:
-          # First generate parent entities
-          async for workspace_entity in self._generate_workspace_entities(client):
-              yield workspace_entity
-
-              # Then generate child entities with breadcrumbs
-              async for project_entity in self._generate_project_entities(
-                  client,
-                  {"gid": workspace_entity.entity_id},
-                  workspace_breadcrumb
-              ):
-                  yield project_entity
-  ```
-
-- **Breadcrumb Management**: Build breadcrumb hierarchies for nested resources
-  ```python
-  # Create breadcrumb for the parent entity
-  workspace_breadcrumb = Breadcrumb(
-      entity_id=workspace_entity.entity_id,
-      name=workspace_entity.name,
-      type="workspace",
-  )
-
-  # Pass parent breadcrumbs to child entities
-  project_breadcrumbs = [workspace_breadcrumb, project_breadcrumb]
-  ```
-
-- **File Handling**: Use dedicated streaming methods with proper error handling
-  ```python
-  async def _stream_file(self, client: httpx.AsyncClient, url: str) -> AsyncGenerator[bytes, None]:
-      """Stream a file with authentication."""
-      retryer = AsyncRetrying(
-          retry=retry_if_exception_type(httpx.HTTPError),
-          wait=wait_exponential(multiplier=1, min=2, max=10),
-          stop=stop_after_attempt(3),
-      )
-
-      async for attempt in retryer:
-          with attempt:
-              try:
-                  async with client.stream("GET", url, headers=headers) as response:
-                      response.raise_for_status()
-                      async for chunk in response.aiter_bytes():
-                          yield chunk
-              except Exception as e:
-                  logger.warning(f"Error streaming file: {str(e)}")
-                  raise
-  ```
-
-- **File Processing**: Use the file manager to process file entities
-  ```python
-  file_entity = YourServiceFileEntity(
-      source_name="your_service",
-      entity_id=file_data["id"],
-      file_id=file_data["id"],
-      name=file_data.get("name"),
-      mime_type=file_data.get("mime_type"),
-      size=file_data.get("size"),
-      download_url=file_data.get("download_url"),
-  )
-
-  # Stream the file and hand off the stream.
-  file_stream = self._stream_file(client, file_entity.download_url)
-  yield await handle_file_entity(file_entity, file_stream)
-  ```
-
-## 4. Run, test and debug with the `Local Sync Test` MCP Tool server
-
-Once the source is set up, you must test the MCP server.
-
-There are two tools
-- Check Connection (arg: short_name)
-- Run Sync (arg: short_name)
-
-There are essentially three outcomes:
-
-1. You test the connection and it returns that the user must still handle something. Pause the execution and prompt the user to fix it. If the problem is about the integrations yaml, check out [integrations-yaml.mdc](mdc:.cursor/rules/integrations-yaml.mdc). In case of OAuth2: look into the docs which scoped we need. Add the yaml instance. to `dev.integrations.yaml`. Then `docker-compose down && docker-compose up -d` as there is no hot reload for non-python files. If the problem is that there is no connection, ask the user to add one. Once done, retest the connection using mcp!
-
-2. The connection works, and you try the sync, but it fails. You will receive a stacktrace from the problem. You must now fix it, and retry to sync, until it works.
-
-3. The sync works! You can now create a branch, commit and push.
PATCH

echo "Gold patch applied."
