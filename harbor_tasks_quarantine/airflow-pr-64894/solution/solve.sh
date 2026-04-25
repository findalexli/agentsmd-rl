#!/bin/bash
# Gold solution for airflow task-sdk CommsDecoder thread safety fix
set -e

cd /workspace/airflow

# Check if already patched (idempotency)
if grep -q "^            return self._get_response()$" task-sdk/src/airflow/sdk/execution_time/comms.py; then
    echo "Patch already applied"
    exit 0
fi

# Apply the gold patch
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
PATCH

echo "Patch applied successfully"
