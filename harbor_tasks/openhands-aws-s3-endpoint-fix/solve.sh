#!/bin/bash
set -e

cd /workspace/openhands

# Check if already patched (idempotency)
if grep -q "_get_default_aws_endpoint_url" openhands/app_server/event/aws_event_service.py 2>/dev/null; then
    echo "Patch already applied, skipping..."
    exit 0
fi

# Apply the gold patch
cat <<'PATCH' | git apply -
diff --git a/openhands/app_server/event/aws_event_service.py b/openhands/app_server/event/aws_event_service.py
index fd6cf4017dcc..3fd827dc4820 100644
--- a/openhands/app_server/event/aws_event_service.py
+++ b/openhands/app_server/event/aws_event_service.py
@@ -13,6 +13,7 @@
 import boto3
 import botocore.exceptions
 from fastapi import Request
+from pydantic import Field

 from openhands.app_server.config import get_app_conversation_info_service
 from openhands.app_server.event.event_service import EventService, EventServiceInjector
@@ -75,9 +76,25 @@ def _search_paths(self, prefix: Path, page_id: str | None = None) -> list[Path]:
         return paths


+def _get_default_aws_endpoint_url() -> str | None:
+    """Legacy fallback for aws endpoint url based on V0"""
+    endpoint_url = os.getenv('AWS_S3_ENDPOINT')
+    if not endpoint_url:
+        return None
+    secure = os.getenv('AWS_S3_SECURE', 'true').lower() == 'true'
+    if secure:
+        if not endpoint_url.startswith('https://'):
+            endpoint_url = 'https://' + endpoint_url.removeprefix('http://')
+    else:
+        if not endpoint_url.startswith('http://'):
+            endpoint_url = 'http://' + endpoint_url.removeprefix('https://')
+    return endpoint_url
+
+
 class AwsEventServiceInjector(EventServiceInjector):
     bucket_name: str
     prefix: Path = Path('users')
+    endpoint_url: str | None = Field(default_factory=_get_default_aws_endpoint_url)

     async def inject(
         self, state: InjectorState, request: Request | None = None
@@ -100,7 +117,7 @@ async def inject(
             # use IAM role credentials when running in AWS
             s3_client = boto3.client(
                 's3',
-                endpoint_url=os.getenv('AWS_S3_ENDPOINT'),
+                endpoint_url=self.endpoint_url,
             )

             yield AwsEventService(
PATCH

echo "Patch applied successfully!"
