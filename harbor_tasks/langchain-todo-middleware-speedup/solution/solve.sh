#!/bin/bash
set -e

cd /workspace/langchain

# Check if already patched (idempotency)
if grep -q "WriteTodosInput" libs/langchain_v1/langchain/agents/middleware/todo.py; then
    echo "Patch already applied, skipping..."
    exit 0
fi

# Apply the gold patch
cat <<'PATCH' | git apply -
diff --git a/libs/langchain_v1/langchain/agents/middleware/todo.py b/libs/langchain_v1/langchain/agents/middleware/todo.py
index ba826d553967e..21719e3ba5e8e 100644
--- a/libs/langchain_v1/langchain/agents/middleware/todo.py
+++ b/libs/langchain_v1/langchain/agents/middleware/todo.py
@@ -1,17 +1,13 @@
 """Planning and task management middleware for agents."""

-from __future__ import annotations
-
-from typing import TYPE_CHECKING, Annotated, Any, Literal, cast
-
-if TYPE_CHECKING:
-    from collections.abc import Awaitable, Callable
-
-    from langgraph.runtime import Runtime
+from collections.abc import Awaitable, Callable
+from typing import Annotated, Any, Literal, cast

 from langchain_core.messages import AIMessage, SystemMessage, ToolMessage
-from langchain_core.tools import tool
+from langchain_core.tools import InjectedToolCallId, StructuredTool, tool
+from langgraph.runtime import Runtime
 from langgraph.types import Command
+from pydantic import BaseModel, Field
 from typing_extensions import NotRequired, TypedDict, override

 from langchain.agents.middleware.types import (
@@ -23,7 +19,7 @@
     OmitFromInput,
     ResponseT,
 )
-from langchain.tools import InjectedToolCallId
+from langchain.tools import ToolRuntime


 class Todo(TypedDict):
@@ -47,6 +43,12 @@ class PlanningState(AgentState[ResponseT]):
     """List of todo items for tracking task progress."""


+class WriteTodosInput(BaseModel):
+    """Input schema for the `write_todos` tool."""
+
+    todos: list[Todo] = Field(description="Updated todo items for the current work session.")
+
+
 WRITE_TODOS_TOOL_DESCRIPTION = """Use this tool to create and manage a structured task list for your current work session. This helps you track progress, organize complex tasks, and demonstrate thoroughness to the user.

 Only use this tool if you think it will be helpful in staying organized. If the user's request is trivial and takes less than 3 steps, it is better to NOT use this tool and just do the task directly.
@@ -135,6 +137,21 @@ def write_todos(
     )


+# Dynamically create the write_todos tool with the custom description
+def _write_todos(
+    runtime: ToolRuntime[ContextT, PlanningState[ResponseT]], todos: list[Todo]
+) -> Command[Any]:
+    """Create and manage a structured task list for your current work session."""
+    return Command(
+        update={
+            "todos": todos,
+            "messages": [
+                ToolMessage(f"Updated todo list to {todos}", tool_call_id=runtime.tool_call_id)
+            ],
+        }
+    )
+
+
 class TodoListMiddleware(AgentMiddleware[PlanningState[ResponseT], ContextT, ResponseT]):
     """Middleware that provides todo list management capabilities to agents.

@@ -181,22 +198,15 @@ def __init__(
         self.system_prompt = system_prompt
         self.tool_description = tool_description

-        # Dynamically create the write_todos tool with the custom description
-        @tool(description=self.tool_description)
-        def write_todos(
-            todos: list[Todo], tool_call_id: Annotated[str, InjectedToolCallId]
-        ) -> Command[Any]:
-            """Create and manage a structured task list for your current work session."""
-            return Command(
-                update={
-                    "todos": todos,
-                    "messages": [
-                        ToolMessage(f"Updated todo list to {todos}", tool_call_id=tool_call_id)
-                    ],
-                }
+        self.tools = [
+            StructuredTool.from_function(
+                name="write_todos",
+                description=tool_description,
+                func=_write_todos,
+                args_schema=WriteTodosInput,
+                infer_schema=False,
             )
-
-        self.tools = [write_todos]
+        ]

     def wrap_model_call(
         self,
PATCH

echo "Patch applied successfully!"
