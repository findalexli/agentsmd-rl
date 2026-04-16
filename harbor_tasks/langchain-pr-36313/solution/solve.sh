#!/bin/bash
set -e

cd /workspace/langchain

# Apply the gold patch
git apply <<'PATCH'
diff --git a/libs/langchain_v1/langchain/agents/middleware/todo.py b/libs/langchain_v1/langchain/agents/middleware/todo.py
index 21719e3ba5e8e..813e059c1df3d 100644
--- a/libs/langchain_v1/langchain/agents/middleware/todo.py
+++ b/libs/langchain_v1/langchain/agents/middleware/todo.py
@@ -152,6 +152,13 @@ def _write_todos(
     )


+async def _awrite_todos(
+    runtime: ToolRuntime[ContextT, PlanningState[ResponseT]], todos: list[Todo]
+) -> Command[Any]:
+    """Create and manage a structured task list for your current work session."""
+    return _write_todos(runtime, todos)
+
+
 class TodoListMiddleware(AgentMiddleware[PlanningState[ResponseT], ContextT, ResponseT]):
     """Middleware that provides todo list management capabilities to agents.

@@ -203,6 +210,7 @@ def __init__(
                 name="write_todos",
                 description=tool_description,
                 func=_write_todos,
+                coroutine=_awrite_todos,
                 args_schema=WriteTodosInput,
                 infer_schema=False,
             )
diff --git a/libs/langchain_v1/tests/unit_tests/agents/middleware/implementations/test_todo.py b/libs/langchain_v1/tests/unit_tests/agents/middleware/implementations/test_todo.py
index eb37700f4a6d7..6da56153256e5 100644
--- a/libs/langchain_v1/tests/unit_tests/agents/middleware/implementations/test_todo.py
+++ b/libs/langchain_v1/tests/unit_tests/agents/middleware/implementations/test_todo.py
@@ -649,6 +649,45 @@ def test_single_write_todos_call_allowed() -> None:
     assert result is None


+async def test_todo_middleware_agent_creation_with_middleware_async() -> None:
+    """Test async agent execution with the planning middleware."""
+    model = FakeToolCallingModel(
+        tool_calls=[
+            [
+                {
+                    "args": {"todos": [{"content": "Task 1", "status": "pending"}]},
+                    "name": "write_todos",
+                    "type": "tool_call",
+                    "id": "test_call",
+                }
+            ],
+            [
+                {
+                    "args": {"todos": [{"content": "Task 1", "status": "in_progress"}]},
+                    "name": "write_todos",
+                    "type": "tool_call",
+                    "id": "test_call",
+                }
+            ],
+            [
+                {
+                    "args": {"todos": [{"content": "Task 1", "status": "completed"}]},
+                    "name": "write_todos",
+                    "type": "tool_call",
+                    "id": "test_call",
+                }
+            ],
+            [],
+        ]
+    )
+    middleware = TodoListMiddleware()
+    agent = create_agent(model=model, middleware=[middleware])
+
+    result = await agent.ainvoke({"messages": [HumanMessage("Hello")]})
+    assert result["todos"] == [{"content": "Task 1", "status": "completed"}]
+    assert len(result["messages"]) == 8
+
+
 async def test_parallel_write_todos_calls_rejected_async() -> None:
     """Test async version - parallel write_todos calls are rejected with error messages."""
     middleware = TodoListMiddleware()
PATCH

echo "Patch applied successfully"

# Idempotency check: verify the distinctive line exists
grep -q "coroutine=_awrite_todos" libs/langchain_v1/langchain/agents/middleware/todo.py || {
    echo "Idempotency check failed: coroutine=_awrite_todos not found"
    exit 1
}

echo "Solve complete"
