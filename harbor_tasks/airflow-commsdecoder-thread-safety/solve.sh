#!/bin/bash
set -e

cd /workspace/airflow

# Apply the gold patch for the thread-safety fix in CommsDecoder
patch -p1 <<'PATCH'
diff --git a/task-sdk/src/airflow/sdk/execution_time/comms.py b/task-sdk/src/airflow/sdk/execution_time/comms.py
index a47554249775d..f4d83baef6d74 100644
--- a/task-sdk/src/airflow/sdk/execution_time/comms.py
+++ b/task-sdk/src/airflow/sdk/execution_time/comms.py
@@ -216,7 +216,7 @@ def send(self, msg: SendMsgType) -> ReceiveMsgType | None:
                 # always be in the return type union
                 return resp  # type: ignore[return-value]

-        return self._get_response()
+            return self._get_response()

     async def asend(self, msg: SendMsgType) -> ReceiveMsgType | None:
         """
PATCH'

# Verify the patch was applied (idempotency check)
if ! grep -q "            return self._get_response()" task-sdk/src/airflow/sdk/execution_time/comms.py; then
    echo "ERROR: Patch was not applied correctly"
    exit 1
fi

echo "Gold patch applied successfully"
