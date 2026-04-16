#!/bin/bash
set -e

cd /workspace/OpenHands

# Apply the gold patch for PR #13579
# This patch adds _get_default_aws_endpoint_url() function and updates
# AwsEventServiceInjector to use Pydantic Field with default_factory

patch -p1 << 'PATCH'
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
diff --git a/tests/unit/app_server/test_aws_event_service.py b/tests/unit/app_server/test_aws_event_service.py
index 1b1f60e80bb6..12daf96d7add 100644
--- a/tests/unit/app_server/test_aws_event_service.py
+++ b/tests/unit/app_server/test_aws_event_service.py
@@ -4,6 +4,7 @@
 focusing on search functionality and S3 operations.
 """

+import importlib
 import json
 from pathlib import Path
 from unittest.mock import MagicMock
@@ -12,6 +13,7 @@ import boto3
 import botocore.exceptions
 import pytest

+from openhands.app_server.event import aws_event_service
 from openhands.app_server.event.aws_event_service import (
     AwsEventService,
     AwsEventServiceInjector,
@@ -211,3 +213,124 @@ def test_injector_has_default_prefix(self):
         """Test that injector has default prefix."""
         injector = AwsEventServiceInjector(bucket_name='my-bucket')
         assert injector.prefix == Path('users')
+
+
+class TestGetDefaultAwsEndpointUrl:
+    """Test cases for _get_default_aws_endpoint_url function."""
+
+    def test_no_env_vars_returns_none(self, monkeypatch):
+        """Test that function returns None when no env vars are set."""
+        monkeypatch.delenv('AWS_S3_ENDPOINT', raising=False)
+        monkeypatch.delenv('AWS_S3_SECURE', raising=False)
+
+        # Need to reload to get fresh default factory
+        importlib.reload(aws_event_service)
+
+        result = aws_event_service._get_default_aws_endpoint_url()
+        assert result is None
+
+    def test_endpoint_with_https_prefix_secure(self, monkeypatch):
+        """Test endpoint with https:// prefix when secure=true."""
+        monkeypatch.setenv('AWS_S3_ENDPOINT', 'https://minio.example.com:9000')
+        monkeypatch.setenv('AWS_S3_SECURE', 'true')
+
+        importlib.reload(aws_event_service)
+
+        result = aws_event_service._get_default_aws_endpoint_url()
+        assert result == 'https://minio.example.com:9000'
+
+    def test_endpoint_without_https_prefix_secure(self, monkeypatch):
+        """Test endpoint without https:// prefix when secure=true adds it."""
+        monkeypatch.setenv('AWS_S3_ENDPOINT', 'minio.example.com:9000')
+        monkeypatch.setenv('AWS_S3_SECURE', 'true')
+
+        importlib.reload(aws_event_service)
+
+        result = aws_event_service._get_default_aws_endpoint_url()
+        assert result == 'https://minio.example.com:9000'
+
+    def test_endpoint_with_http_prefix_insecure(self, monkeypatch):
+        """Test endpoint with http:// prefix when secure=false."""
+        monkeypatch.setenv('AWS_S3_ENDPOINT', 'http://minio.example.com:9000')
+        monkeypatch.setenv('AWS_S3_SECURE', 'false')
+
+        importlib.reload(aws_event_service)
+
+        result = aws_event_service._get_default_aws_endpoint_url()
+        assert result == 'http://minio.example.com:9000'
+
+    def test_endpoint_without_http_prefix_insecure(self, monkeypatch):
+        """Test endpoint without http:// prefix when secure=false adds it."""
+        monkeypatch.setenv('AWS_S3_ENDPOINT', 'minio.example.com:9000')
+        monkeypatch.setenv('AWS_S3_SECURE', 'false')
+
+        importlib.reload(aws_event_service)
+
+        result = aws_event_service._get_default_aws_endpoint_url()
+        assert result == 'http://minio.example.com:9000'
+
+    def test_endpoint_with_http_converted_to_https(self, monkeypatch):
+        """Test http:// is converted to https:// when secure=true."""
+        monkeypatch.setenv('AWS_S3_ENDPOINT', 'http://minio.example.com:9000')
+        monkeypatch.setenv('AWS_S3_SECURE', 'true')
+
+        importlib.reload(aws_event_service)
+
+        result = aws_event_service._get_default_aws_endpoint_url()
+        assert result == 'https://minio.example.com:9000'
+
+    def test_endpoint_with_https_converted_to_http(self, monkeypatch):
+        """Test https:// is converted to http:// when secure=false."""
+        monkeypatch.setenv('AWS_S3_ENDPOINT', 'https://minio.example.com:9000')
+        monkeypatch.setenv('AWS_S3_SECURE', 'false')
+
+        importlib.reload(aws_event_service)
+
+        result = aws_event_service._get_default_aws_endpoint_url()
+        assert result == 'http://minio.example.com:9000'
+
+    def test_secure_default_is_true(self, monkeypatch):
+        """Test that secure defaults to true when not set."""
+        monkeypatch.setenv('AWS_S3_ENDPOINT', 'minio.example.com:9000')
+        monkeypatch.delenv('AWS_S3_SECURE', raising=False)
+
+        importlib.reload(aws_event_service)
+
+        result = aws_event_service._get_default_aws_endpoint_url()
+        assert result == 'https://minio.example.com:9000'
+
+
+class TestAwsEventServiceInjectorEndpointUrl:
+    """Test cases for AwsEventServiceInjector endpoint_url field."""
+
+    def test_injector_endpoint_url_from_env(self, monkeypatch):
+        """Test that endpoint_url is populated from environment variables."""
+        monkeypatch.setenv('AWS_S3_ENDPOINT', 'minio.example.com:9000')
+        monkeypatch.setenv('AWS_S3_SECURE', 'false')
+
+        importlib.reload(aws_event_service)
+
+        injector = aws_event_service.AwsEventServiceInjector(bucket_name='my-bucket')
+        assert injector.endpoint_url == 'http://minio.example.com:9000'
+
+    def test_injector_accepts_custom_endpoint_url(self, monkeypatch):
+        """Test that injector accepts custom endpoint_url parameter."""
+        monkeypatch.delenv('AWS_S3_ENDPOINT', raising=False)
+        monkeypatch.delenv('AWS_S3_SECURE', raising=False)
+
+        importlib.reload(aws_event_service)
+
+        injector = aws_event_service.AwsEventServiceInjector(
+            bucket_name='my-bucket', endpoint_url='https://custom.example.com:9000'
+        )
+        assert injector.endpoint_url == 'https://custom.example.com:9000'
+
+    def test_injector_endpoint_url_none_when_no_env(self, monkeypatch):
+        """Test that endpoint_url is None when no env vars set."""
+        monkeypatch.delenv('AWS_S3_ENDPOINT', raising=False)
+        monkeypatch.delenv('AWS_S3_SECURE', raising=False)
+
+        importlib.reload(aws_event_service)
+
+        injector = aws_event_service.AwsEventServiceInjector(bucket_name='my-bucket')
+        assert injector.endpoint_url is None
PATCH

echo "Patch applied successfully"
