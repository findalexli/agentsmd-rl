#!/bin/bash
set -e
cd /workspace/prefect

# Apply the fix patch
git apply <<'PATCH'
diff --git a/src/prefect/task_runners.py b/src/prefect/task_runners.py
index 1c2ac99894bf..e897e53f36a2 100644
--- a/src/prefect/task_runners.py
+++ b/src/prefect/task_runners.py
@@ -755,7 +755,7 @@ def __init__(
     def duplicate(self) -> Self:
         duplicate_runner = type(self)(max_workers=self._max_workers)
         duplicate_runner.subprocess_message_processor_factories = (
-            self._subprocess_message_processor_factories
+            self.subprocess_message_processor_factories
         )
         return duplicate_runner

@@ -763,7 +763,7 @@ def duplicate(self) -> Self:
     def subprocess_message_processor_factories(
         self,
     ) -> tuple[_SubprocessMessageProcessorFactory, ...]:
-        return self._subprocess_message_processor_factories
+        return getattr(self, "_subprocess_message_processor_factories", ())

     @subprocess_message_processor_factories.setter
     def subprocess_message_processor_factories(
PATCH

# Verify patch applied
grep -q "getattr(self, \"_subprocess_message_processor_factories\", ())" src/prefect/task_runners.py
