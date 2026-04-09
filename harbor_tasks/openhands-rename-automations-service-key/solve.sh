#!/bin/bash
set -e

cd /workspace/OpenHands

# Check if patch already applied
if grep -q "AUTOMATIONS_SERVICE_KEY = os.getenv" enterprise/server/routes/service.py; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the gold patch
cat <<'PATCH' | git apply -
diff --git a/enterprise/server/routes/service.py b/enterprise/server/routes/service.py
index 87e470dd7c12..f2bc12849ac8 100644
--- a/enterprise/server/routes/service.py
+++ b/enterprise/server/routes/service.py
@@ -5,7 +5,7 @@
 to perform privileged operations like creating API keys on behalf of users.

 Authentication is via a shared secret (X-Service-API-Key header) configured
-through the AUTOMATIONS_SERVICE_API_KEY environment variable.
+through the AUTOMATIONS_SERVICE_KEY environment variable.
 """

 import os
@@ -20,7 +20,7 @@
 from openhands.core.logger import openhands_logger as logger

 # Environment variable for the service API key
-AUTOMATIONS_SERVICE_API_KEY = os.getenv('AUTOMATIONS_SERVICE_API_KEY', '').strip()
+AUTOMATIONS_SERVICE_KEY = os.getenv('AUTOMATIONS_SERVICE_KEY', '').strip()

 service_router = APIRouter(prefix='/api/service', tags=['Service'])

@@ -70,9 +70,9 @@ async def validate_service_api_key(
         HTTPException: 401 if key is missing or invalid
         HTTPException: 503 if service auth is not configured
     """
-    if not AUTOMATIONS_SERVICE_API_KEY:
+    if not AUTOMATIONS_SERVICE_KEY:
         logger.warning(
-            'Service authentication not configured (AUTOMATIONS_SERVICE_API_KEY not set)'
+            'Service authentication not configured (AUTOMATIONS_SERVICE_KEY not set)'
         )
         raise HTTPException(
             status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
@@ -85,7 +85,7 @@ async def validate_service_api_key(
             detail='X-Service-API-Key header is required',
         )

-    if x_service_api_key != AUTOMATIONS_SERVICE_API_KEY:
+    if x_service_api_key != AUTOMATIONS_SERVICE_KEY:
         logger.warning('Invalid service API key attempted')
         raise HTTPException(
             status_code=status.HTTP_401_UNAUTHORIZED,
@@ -104,7 +104,7 @@ async def service_health() -> dict:
     """
     return {
         'status': 'ok',
-        'service_auth_configured': bool(AUTOMATIONS_SERVICE_API_KEY),
+        'service_auth_configured': bool(AUTOMATIONS_SERVICE_KEY),
     }


diff --git a/enterprise/tests/unit/routes/test_service.py b/enterprise/tests/unit/routes/test_service.py
index a7156ec117f0..a3806b54da2c 100644
--- a/enterprise/tests/unit/routes/test_service.py
+++ b/enterprise/tests/unit/routes/test_service.py
@@ -19,18 +19,14 @@ class TestValidateServiceApiKey:
     @pytest.mark.asyncio
     async def test_valid_service_key(self):
         """Test validation with valid service API key."""
-        with patch(
-            'server.routes.service.AUTOMATIONS_SERVICE_API_KEY', 'test-service-key'
-        ):
+        with patch('server.routes.service.AUTOMATIONS_SERVICE_KEY', 'test-service-key'):
             result = await validate_service_api_key('test-service-key')
         assert result == 'automations-service'

     @pytest.mark.asyncio
     async def test_missing_service_key(self):
         """Test validation with missing service API key header."""
-        with patch(
-            'server.routes.service.AUTOMATIONS_SERVICE_API_KEY', 'test-service-key'
-        ):
+        with patch('server.routes.service.AUTOMATIONS_SERVICE_KEY', 'test-service-key'):
             with pytest.raises(HTTPException) as exc_info:
                 await validate_service_api_key(None)
         assert exc_info.value.status_code == 401
@@ -39,9 +35,7 @@ async def test_missing_service_key(self):
     @pytest.mark.asyncio
     async def test_invalid_service_key(self):
         """Test validation with invalid service API key."""
-        with patch(
-            'server.routes.service.AUTOMATIONS_SERVICE_API_KEY', 'test-service-key'
-        ):
+        with patch('server.routes.service.AUTOMATIONS_SERVICE_KEY', 'test-service-key'):
             with pytest.raises(HTTPException) as exc_info:
                 await validate_service_api_key('wrong-key')
         assert exc_info.value.status_code == 401
@@ -50,7 +44,7 @@ async def test_invalid_service_key(self):
     @pytest.mark.asyncio
     async def test_service_auth_not_configured(self):
         """Test validation when service auth is not configured."""
-        with patch('server.routes.service.AUTOMATIONS_SERVICE_API_KEY', ''):
+        with patch('server.routes.service.AUTOMATIONS_SERVICE_KEY', ''):
             with pytest.raises(HTTPException) as exc_info:
                 await validate_service_api_key('any-key')
         assert exc_info.value.status_code == 503
@@ -112,7 +106,7 @@ class TestCreateUserApiKey:
     @pytest.mark.asyncio
     async def test_user_not_found(self, valid_user_id, valid_org_id, valid_request):
         """Test error when user doesn't exist."""
-        with patch('server.routes.service.AUTOMATIONS_SERVICE_API_KEY', 'test-key'):
+        with patch('server.routes.service.AUTOMATIONS_SERVICE_KEY', 'test-key'):
             with patch(
                 'server.routes.service.UserStore.get_user_by_id', new_callable=AsyncMock
             ) as mock_get_user:
@@ -132,7 +126,7 @@ async def test_user_not_in_org(self, valid_user_id, valid_org_id, valid_request)
         """Test error when user is not a member of the org."""
         mock_user = MagicMock()

-        with patch('server.routes.service.AUTOMATIONS_SERVICE_API_KEY', 'test-key'):
+        with patch('server.routes.service.AUTOMATIONS_SERVICE_KEY', 'test-key'):
             with patch(
                 'server.routes.service.UserStore.get_user_by_id', new_callable=AsyncMock
             ) as mock_get_user:
@@ -164,7 +158,7 @@ async def test_successful_key_creation(
             return_value='sk-oh-test-key-12345678901234567890'
         )

-        with patch('server.routes.service.AUTOMATIONS_SERVICE_API_KEY', 'test-key'):
+        with patch('server.routes.service.AUTOMATIONS_SERVICE_KEY', 'test-key'):
             with patch(
                 'server.routes.service.UserStore.get_user_by_id', new_callable=AsyncMock
             ) as mock_get_user:
@@ -210,7 +204,7 @@ async def test_store_exception_handling(
             side_effect=Exception('Database error')
         )

-        with patch('server.routes.service.AUTOMATIONS_SERVICE_API_KEY', 'test-key'):
+        with patch('server.routes.service.AUTOMATIONS_SERVICE_KEY', 'test-key'):
             with patch(
                 'server.routes.service.UserStore.get_user_by_id', new_callable=AsyncMock
             ) as mock_get_user:
@@ -252,7 +246,7 @@ async def test_successful_delete(self, valid_org_id):
         mock_api_key_store.make_system_key_name.return_value = '__SYSTEM__:automation'
         mock_api_key_store.delete_api_key_by_name = AsyncMock(return_value=True)

-        with patch('server.routes.service.AUTOMATIONS_SERVICE_API_KEY', 'test-key'):
+        with patch('server.routes.service.AUTOMATIONS_SERVICE_KEY', 'test-key'):
             with patch(
                 'server.routes.service.ApiKeyStore.get_instance'
             ) as mock_get_store:
@@ -283,7 +277,7 @@ async def test_delete_key_not_found(self, valid_org_id):
         mock_api_key_store.make_system_key_name.return_value = '__SYSTEM__:nonexistent'
         mock_api_key_store.delete_api_key_by_name = AsyncMock(return_value=False)

-        with patch('server.routes.service.AUTOMATIONS_SERVICE_API_KEY', 'test-key'):
+        with patch('server.routes.service.AUTOMATIONS_SERVICE_KEY', 'test-key'):
             with patch(
                 'server.routes.service.ApiKeyStore.get_instance'
             ) as mock_get_store:
@@ -303,7 +297,7 @@ async def test_delete_key_not_found(self, valid_org_id):
     @pytest.mark.asyncio
     async def test_delete_invalid_service_key(self, valid_org_id):
         """Test error when service API key is invalid."""
-        with patch('server.routes.service.AUTOMATIONS_SERVICE_API_KEY', 'test-key'):
+        with patch('server.routes.service.AUTOMATIONS_SERVICE_KEY', 'test-key'):
             with pytest.raises(HTTPException) as exc_info:
                 await delete_user_api_key(
                     user_id='user-123',
@@ -318,7 +312,7 @@ async def test_delete_invalid_service_key(self, valid_org_id):
     @pytest.mark.asyncio
     async def test_delete_missing_service_key(self, valid_org_id):
         """Test error when service API key header is missing."""
-        with patch('server.routes.service.AUTOMATIONS_SERVICE_API_KEY', 'test-key'):
+        with patch('server.routes.service.AUTOMATIONS_SERVICE_KEY', 'test-key'):
             with pytest.raises(HTTPException) as exc_info:
                 await delete_user_api_key(
                     user_id='user-123',
PATCH

echo "Patch applied successfully"
