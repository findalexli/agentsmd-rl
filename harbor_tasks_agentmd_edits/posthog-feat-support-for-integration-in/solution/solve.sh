#!/usr/bin/env bash
set -euo pipefail

cd /workspace/posthog

# Idempotent: skip if already applied
if grep -q 'BigQueryImpersonateServiceAccountTestStep' products/batch_exports/backend/api/destination_tests/bigquery.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
git apply --whitespace=fix - <<'PATCH'
diff --git a/posthog/api/test/batch_exports/test_test.py b/posthog/api/test/batch_exports/test_test.py
index d0ecfb530dd5..5199d93beb51 100644
--- a/posthog/api/test/batch_exports/test_test.py
+++ b/posthog/api/test/batch_exports/test_test.py
@@ -474,6 +474,7 @@ def test_can_run_databricks_test_step_for_new_destination(
                 "server_hostname": "my-server-hostname",
                 "client_id": "my-client-id",
                 "client_secret": "my-client-secret",
+                "integration": databricks_integration,
             }
         )
 
diff --git a/posthog/batch_exports/http.py b/posthog/batch_exports/http.py
index 949acbcfa408..d3281f91a124 100644
--- a/posthog/batch_exports/http.py
+++ b/posthog/batch_exports/http.py
@@ -1130,7 +1130,12 @@ def run_test_step_new(self, request: request.Request, *args, **kwargs) -> respon
         # if we have an integration, add its config and sensitive_config to test_configuration
         integration: Integration | None = serializer.validated_data["destination"].get("integration")
         if integration:
-            test_configuration = {**test_configuration, **integration.config, **integration.sensitive_config}
+            test_configuration = {
+                **test_configuration,
+                **integration.config,
+                **integration.sensitive_config,
+                "integration": integration,
+            }
 
         destination_test.configure(**test_configuration)
 
@@ -1164,7 +1169,12 @@ def run_test_step(self, request: request.Request, *args, **kwargs) -> response.R
         # if we have an integration, add its config and sensitive_config to test_configuration
         integration: Integration | None = serializer.validated_data["destination"].get("integration")
         if integration:
-            test_configuration = {**test_configuration, **integration.config, **integration.sensitive_config}
+            test_configuration = {
+                **test_configuration,
+                **integration.config,
+                **integration.sensitive_config,
+                "integration": integration,
+            }
 
         destination_test.configure(**test_configuration)
 
diff --git a/products/batch_exports/backend/api/destination_tests/bigquery.py b/products/batch_exports/backend/api/destination_tests/bigquery.py
index ce5b92af99cb..23f30330ae48 100644
--- a/products/batch_exports/backend/api/destination_tests/bigquery.py
+++ b/products/batch_exports/backend/api/destination_tests/bigquery.py
@@ -1,11 +1,176 @@
+import typing
 import collections.abc
 
+from google.api_core.exceptions import NotFound, PermissionDenied
+from google.cloud import bigquery, iam_admin_v1
+
+from posthog.models.integration import GoogleCloudServiceAccountIntegration
+
 from products.batch_exports.backend.api.destination_tests.base import (
     DestinationTest,
     DestinationTestStep,
     DestinationTestStepResult,
     Status,
 )
+from products.batch_exports.backend.temporal.destinations.bigquery_batch_export import (
+    BigQueryClient,
+    get_our_google_cloud_credentials,
+    impersonate_service_account,
+)
+
+
+class ServiceAccountInfo(typing.TypedDict):
+    private_key: str
+    private_key_id: str
+    token_uri: str
+    client_email: str
+
+
+def get_client(
+    project_id: str | None,
+    integration: GoogleCloudServiceAccountIntegration | None,
+    service_account_info: ServiceAccountInfo | None,
+) -> BigQueryClient:
+    """Get a `BigQueryClient` from an integration or service account information."""
+    if project_id is None:
+        raise ValueError("Project ID not set")
+
+    if integration is not None:
+        client = BigQueryClient.from_service_account_integration(integration=integration)
+    elif service_account_info is not None:
+        client = BigQueryClient.from_service_account_inputs(project_id=project_id, **service_account_info)
+    else:
+        raise ValueError("Either integration or service account information must be defined")
+
+    return client
+
+
+class BigQueryImpersonateServiceAccountTestStep(DestinationTestStep):
+    """Test whether a BigQuery service account exists and we can impersonate it.
+
+    Attributes:
+        project_id: ID of the BigQuery project containing the service account.
+        integration: Integration with service account configuration.
+    """
+
+    name = "Impersonate BigQuery service account"
+    description = "Confirm we can impersonate a BigQuery service account."
+
+    def __init__(
+        self,
+        project_id: str | None = None,
+        integration: GoogleCloudServiceAccountIntegration | None = None,
+    ) -> None:
+        super().__init__()
+        self.project_id = project_id
+        self.integration = integration
+
+    def _is_configured(self) -> bool:
+        """Ensure required configuration parameters are set."""
+        if self.project_id is None or self.integration is None:
+            return False
+        return True
+
+    async def _run_step(self) -> DestinationTestStepResult:
+        """Run this test step."""
+        assert self.integration is not None
+
+        try:
+            their_credentials = impersonate_service_account(self.integration)
+            client = bigquery.Client(
+                project=self.integration.project_id,
+                credentials=their_credentials,
+            )
+            # This triggers an actual credential refresh
+            list(client.query("SELECT 1").result())
+
+        except NotFound:
+            service_account_email = self.integration.service_account_email
+
+            return DestinationTestStepResult(
+                status=Status.FAILED,
+                message=f"Service account '{service_account_email}' was not found and cannot be impersonated. It may not exist or we may not have sufficient permissions.",
+            )
+        except Exception:
+            service_account_email = self.integration.service_account_email
+
+            return DestinationTestStepResult(
+                status=Status.FAILED,
+                message=f"Failed to impersonate Service account '{service_account_email}'.",
+            )
+
+        return DestinationTestStepResult(status=Status.PASSED)
+
+
+class BigQueryVerifyServiceAccountOwnershipTestStep(DestinationTestStep):
+    """Test whether a BigQuery service account is owned by the current organization.
+
+    We require users to set their organization ID as the service account description so
+    that we can verify they own them at runtime. This test reproduces that verification
+    to help debug incorrect descriptions or missing permissions.
+
+    Attributes:
+        project_id: ID of the BigQuery project containing the service account.
+        integration: Integration with service account configuration.
+    """
+
+    name = "Verify BigQuery service account ownership"
+    description = "Confirm that the current PostHog organization owns a BigQuery service account by ensuring its organization ID is set as part of the service account description."
+
+    def __init__(
+        self,
+        project_id: str | None = None,
+        integration: GoogleCloudServiceAccountIntegration | None = None,
+        organization_id: str | None = None,
+    ) -> None:
+        super().__init__()
+        self.project_id = project_id
+        self.integration = integration
+        self.organization_id = organization_id
+
+    def _is_configured(self) -> bool:
+        """Ensure required configuration parameters are set."""
+        if self.project_id is None or self.integration is None or self.organization_id is None:
+            return False
+        return True
+
+    async def _run_step(self) -> DestinationTestStepResult:
+        """Run this test step."""
+        assert self.integration is not None
+
+        service_account_email = self.integration.service_account_email
+
+        try:
+            our_credentials = get_our_google_cloud_credentials()
+            client = iam_admin_v1.IAMClient(credentials=our_credentials)
+            sa = client.get_service_account(
+                request=iam_admin_v1.GetServiceAccountRequest(
+                    name=f"projects/-/serviceAccounts/{self.integration.service_account_email}"
+                )
+            )
+        except PermissionDenied:
+            return DestinationTestStepResult(
+                status=Status.FAILED,
+                message=f"No permission to read service account's '{service_account_email}' description. Have you granted the PostHog service account a role with `iam.serviceAccounts.get`?",
+            )
+        except NotFound:
+            return DestinationTestStepResult(
+                status=Status.FAILED,
+                message=f"Service account '{service_account_email}' was not found. It may not exist or we may not have sufficient permissions.",
+            )
+        except Exception:
+            return DestinationTestStepResult(
+                status=Status.FAILED,
+                message=f"Failed to verify ownership of service account '{service_account_email}'.",
+            )
+
+        if f"posthog:{self.organization_id}" not in sa.description:
+            return DestinationTestStepResult(
+                status=Status.FAILED,
+                message=f"Organization ID not found in service account's '{service_account_email}' description. Ownership could not be verified.",
+            )
+
+        return DestinationTestStepResult(status=Status.PASSED)
 
 
 class BigQueryProjectTestStep(DestinationTestStep):
@@ -30,34 +195,26 @@ class BigQueryProjectTestStep(DestinationTestStep):
         "Ensure the configured BigQuery project exists and that we have the required permissions to access it."
     )
 
-    def __init__(self, project_id: str | None = None, service_account_info: dict[str, str] | None = None) -> None:
+    def __init__(
+        self,
+        project_id: str | None = None,
+        integration: GoogleCloudServiceAccountIntegration | None = None,
+        service_account_info: ServiceAccountInfo | None = None,
+    ) -> None:
         super().__init__()
         self.project_id = project_id
+        self.integration = integration
         self.service_account_info = service_account_info
 
     def _is_configured(self) -> bool:
         """Ensure required configuration parameters are set."""
-        if (
-            self.project_id is None
-            or self.service_account_info is None
-            or not all(
-                param in self.service_account_info
-                for param in ("private_key", "private_key_id", "token_uri", "client_email")
-            )
-        ):
+        if self.project_id is None or (self.integration is None and self.service_account_info is None):
             return False
         return True
 
     async def _run_step(self) -> DestinationTestStepResult:
         """Run this test step."""
-        from products.batch_exports.backend.temporal.destinations.bigquery_batch_export import BigQueryClient
-
-        # This method should be called by `run()` which ensures this test step is configured
-        # with non-`None` values.
-        assert self.service_account_info is not None
-        assert self.project_id is not None
-
-        client = BigQueryClient.from_service_account_inputs(project_id=self.project_id, **self.service_account_info)
+        client = get_client(self.project_id, self.integration, self.service_account_info)
         projects = {p.project_id for p in client.sync_client.list_projects()}
 
         if self.project_id in projects:
@@ -96,12 +253,14 @@ def __init__(
         self,
         project_id: str | None = None,
         dataset_id: str | None = None,
-        service_account_info: dict[str, str] | None = None,
+        integration: GoogleCloudServiceAccountIntegration | None = None,
+        service_account_info: ServiceAccountInfo | None = None,
     ) -> None:
         super().__init__()
 
         self.dataset_id = dataset_id
         self.project_id = project_id
+        self.integration = integration
         self.service_account_info = service_account_info
 
     def _is_configured(self) -> bool:
@@ -109,11 +268,7 @@ def _is_configured(self) -> bool:
         if (
             self.project_id is None
             or self.dataset_id is None
-            or self.service_account_info is None
-            or not all(
-                param in self.service_account_info
-                for param in ("private_key", "private_key_id", "token_uri", "client_email")
-            )
+            or (self.service_account_info is None and self.integration is None)
         ):
             return False
         return True
@@ -122,16 +277,12 @@ async def _run_step(self) -> DestinationTestStepResult:
         """Run this test step."""
         from google.cloud.exceptions import NotFound
 
-        from products.batch_exports.backend.temporal.destinations.bigquery_batch_export import BigQueryClient
+        client = get_client(self.project_id, self.integration, self.service_account_info)
 
         # This method should be called by `run()` which ensures this test step is configured
         # with non-`None` values.
-        assert self.service_account_info is not None
-        assert self.project_id is not None
         assert self.dataset_id is not None
 
-        client = BigQueryClient.from_service_account_inputs(project_id=self.project_id, **self.service_account_info)
-
         try:
             _ = client.sync_client.get_dataset(self.dataset_id)
         except NotFound:
@@ -172,12 +323,14 @@ def __init__(
         project_id: str | None = None,
         dataset_id: str | None = None,
         table_id: str | None = None,
-        service_account_info: dict[str, str] | None = None,
+        integration: GoogleCloudServiceAccountIntegration | None = None,
+        service_account_info: ServiceAccountInfo | None = None,
     ) -> None:
         super().__init__()
         self.dataset_id = dataset_id
         self.project_id = project_id
         self.table_id = table_id
+        self.integration = integration
         self.service_account_info = service_account_info
 
     def _is_configured(self) -> bool:
@@ -186,11 +339,7 @@ def _is_configured(self) -> bool:
             self.project_id is None
             or self.dataset_id is None
             or self.table_id is None
-            or self.service_account_info is None
-            or not all(
-                param in self.service_account_info
-                for param in ("private_key", "private_key_id", "token_uri", "client_email")
-            )
+            or (self.service_account_info is None and self.integration is None)
         ):
             return False
         return True
@@ -201,14 +350,12 @@ async def _run_step(self) -> DestinationTestStepResult:
         from google.cloud import bigquery
         from google.cloud.exceptions import NotFound
 
-        from products.batch_exports.backend.temporal.destinations.bigquery_batch_export import BigQueryClient
+        client = get_client(self.project_id, self.integration, self.service_account_info)
 
         # This method should be called by `run()` which ensures this test step is configured
         # with non-`None` values.
-        assert self.service_account_info is not None
-        assert self.project_id is not None
-
-        client = BigQueryClient.from_service_account_inputs(project_id=self.project_id, **self.service_account_info)
+        assert self.table_id is not None
+        assert self.dataset_id is not None
 
         fully_qualified_name = f"{self.project_id}.{self.dataset_id}.{self.table_id}"
         table = bigquery.Table(fully_qualified_name, schema=[bigquery.SchemaField(name="event", field_type="STRING")])
@@ -255,35 +402,83 @@ class BigQueryDestinationTest(DestinationTest):
     """
 
     def __init__(self):
-        self.project_id = None
-        self.dataset_id = None
-        self.table_id = None
-        self.service_account_info = None
+        self.project_id: str | None = None
+        self.integration: GoogleCloudServiceAccountIntegration | None = None
+        self.service_account_email: str | None = None
+        self.dataset_id: str | None = None
+        self.table_id: str | None = None
+        self.private_key: str | None = None
+        self.private_key_id: str | None = None
+        self.token_uri: str | None = None
 
     def configure(self, **kwargs):
         """Configure this test with necessary attributes."""
         self.project_id = kwargs.get("project_id", None)
+        self.service_account_email = kwargs.get("service_account_email", None) or kwargs.get("client_email", None)
         self.dataset_id = kwargs.get("dataset_id", None)
         self.table_id = kwargs.get("table_id", None)
-        self.service_account_info = {
-            "private_key": kwargs.get("private_key", None),
-            "private_key_id": kwargs.get("private_key_id", None),
-            "token_uri": kwargs.get("token_uri", None),
-            "client_email": kwargs.get("client_email", None),
+
+        self.private_key = kwargs.get("private_key", None)
+        self.private_key_id = kwargs.get("private_key_id", None)
+        self.token_uri = kwargs.get("token_uri", None)
+
+        integration = kwargs.get("integration", None)
+        if integration is not None:
+            self.integration = GoogleCloudServiceAccountIntegration(integration)
+
+    @property
+    def service_account_info(self) -> ServiceAccountInfo | None:
+        if (
+            self.private_key is None
+            or self.private_key_id is None
+            or self.token_uri is None
+            or self.service_account_email is None
+        ):
+            return None
+
+        return {
+            "private_key": self.private_key,
+            "private_key_id": self.private_key_id,
+            "token_uri": self.token_uri,
+            "client_email": self.service_account_email,
         }
 
     @property
     def steps(self) -> collections.abc.Sequence[DestinationTestStep]:
         """Sequence of test steps that make up this destination test."""
+        if self.integration is not None and self.service_account_info is None:
+            # If no service account information is set, then that's the same as
+            # asserting the integration has no keys, so we can check impersonation and
+            # ownership.
+            base_steps: tuple[DestinationTestStep, ...] = (
+                BigQueryImpersonateServiceAccountTestStep(project_id=self.project_id, integration=self.integration),
+                BigQueryVerifyServiceAccountOwnershipTestStep(
+                    project_id=self.project_id,
+                    integration=self.integration,
+                    organization_id=str(self.integration.integration.team.organization_id),
+                ),
+            )
+        else:
+            base_steps = ()
+
         return [
-            BigQueryProjectTestStep(project_id=self.project_id, service_account_info=self.service_account_info),
+            *base_steps,
+            BigQueryProjectTestStep(
+                project_id=self.project_id,
+                integration=self.integration,
+                service_account_info=self.service_account_info,
+            ),
             BigQueryDatasetTestStep(
-                project_id=self.project_id, dataset_id=self.dataset_id, service_account_info=self.service_account_info
+                project_id=self.project_id,
+                dataset_id=self.dataset_id,
+                integration=self.integration,
+                service_account_info=self.service_account_info,
             ),
             BigQueryTableTestStep(
                 project_id=self.project_id,
                 dataset_id=self.dataset_id,
                 table_id=self.table_id,
+                integration=self.integration,
                 service_account_info=self.service_account_info,
             ),
         ]
diff --git a/products/batch_exports/backend/tests/api/destination_tests/test_bigquery_destination_tests.py b/products/batch_exports/backend/tests/api/destination_tests/test_bigquery_destination_tests.py
index 5257b46f1720..cd2c017ff204 100644
--- a/products/batch_exports/backend/tests/api/destination_tests/test_bigquery_destination_tests.py
+++ b/products/batch_exports/backend/tests/api/destination_tests/test_bigquery_destination_tests.py
@@ -5,15 +5,29 @@
 import warnings
 
 import pytest
+from unittest.mock import patch
 
+import pytest_asyncio
 from google.cloud import bigquery, exceptions
 
+from posthog.models.integration import GoogleCloudServiceAccountIntegration
+
 from products.batch_exports.backend.api.destination_tests.bigquery import (
     BigQueryDatasetTestStep,
+    BigQueryImpersonateServiceAccountTestStep,
     BigQueryProjectTestStep,
     BigQueryTableTestStep,
+    BigQueryVerifyServiceAccountOwnershipTestStep,
     Status,
 )
+from products.batch_exports.backend.tests.temporal.destinations.bigquery.utils import (
+    impersonated_integration,
+    key_file_integration,
+    set_service_account_description_for_integration,
+)
+from products.batch_exports.backend.tests.temporal.destinations.s3.utils import (
+    check_valid_credentials as has_valid_aws_credentials,
+)
 
 SKIP_IF_MISSING_GOOGLE_APPLICATION_CREDENTIALS = pytest.mark.skipif(
     "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ,
@@ -80,10 +94,49 @@ def service_account_info(bigquery_config):
     return {k: v for k, v in bigquery_config.items() if k != "project_id"}
 
 
-async def test_bigquery_check_dataset_exists_test_step(project_id, service_account_info, bigquery_dataset):
+@pytest.fixture
+def service_account_description(aorganization, request) -> str:
+    try:
+        description = request.param
+    except Exception:
+        return f"posthog:{str(aorganization.id)}"
+
+    if description is None:
+        return f"posthog:{str(aorganization.id)}"
+    return description
+
+
+@pytest_asyncio.fixture
+async def integration(
+    request, aorganization, ateam, bigquery_config, service_account_description
+) -> GoogleCloudServiceAccountIntegration | None:
+    try:
+        integration_type = request.param
+    except Exception:
+        return None
+
+    match integration_type:
+        case "impersonated":
+            if not await has_valid_aws_credentials():
+                pytest.skip("AWS credentials not available")
+
+            inner = await impersonated_integration(ateam, bigquery_config)
+            await set_service_account_description_for_integration(inner, service_account_description)
+            integration: GoogleCloudServiceAccountIntegration | None = GoogleCloudServiceAccountIntegration(inner)
+        case "key_file":
+            integration = GoogleCloudServiceAccountIntegration(await key_file_integration(ateam, bigquery_config))
+        case _:
+            integration = None
+
+    return integration
+
+
+@pytest.mark.parametrize("integration", ["impersonated", "key_file", None], indirect=True)
+async def test_bigquery_check_dataset_exists_test_step(project_id, integration, service_account_info, bigquery_dataset):
     test_step = BigQueryDatasetTestStep(
         project_id=project_id,
         dataset_id=bigquery_dataset.dataset_id,
+        integration=integration,
         service_account_info=service_account_info,
     )
     result = await test_step.run()
@@ -92,10 +145,12 @@ async def test_bigquery_check_dataset_exists_test_step(project_id, service_accou
     assert result.message is None
 
 
-async def test_bigquery_check_dataset_exists_test_step_without_dataset(project_id, service_account_info):
+@pytest.mark.parametrize("integration", ["impersonated", "key_file", None], indirect=True)
+async def test_bigquery_check_dataset_exists_test_step_without_dataset(project_id, integration, service_account_info):
     test_step = BigQueryDatasetTestStep(
         project_id=project_id,
         dataset_id="garbage",
+        integration=integration,
         service_account_info=service_account_info,
     )
     result = await test_step.run()
@@ -107,20 +162,24 @@ async def test_bigquery_check_dataset_exists_test_step_without_dataset(project_i
     )
 
 
-async def test_bigquery_check_project_exists_test_step(project_id, service_account_info):
+@pytest.mark.parametrize("integration", ["impersonated", "key_file", None], indirect=True)
+async def test_bigquery_check_project_exists_test_step(project_id, integration, service_account_info):
     test_step = BigQueryProjectTestStep(
         project_id=project_id,
+        integration=integration,
         service_account_info=service_account_info,
     )
     result = await test_step.run()
 
-    assert result.status == Status.PASSED
+    assert result.status == Status.PASSED, result.message
     assert result.message is None
 
 
-async def test_bigquery_check_project_exists_test_step_without_project(service_account_info):
+@pytest.mark.parametrize("integration", ["impersonated", "key_file", None], indirect=True)
+async def test_bigquery_check_project_exists_test_step_without_project(integration, service_account_info):
     test_step = BigQueryProjectTestStep(
         project_id="garbage",
+        integration=integration,
         service_account_info=service_account_info,
     )
     result = await test_step.run()
@@ -132,7 +191,10 @@ async def test_bigquery_check_project_exists_test_step_without_project(service_a
     )
 
 
-async def test_bigquery_check_table_test_step(project_id, bigquery_client, bigquery_dataset, service_account_info):
+@pytest.mark.parametrize("integration", ["impersonated", "key_file", None], indirect=True)
+async def test_bigquery_check_table_test_step(
+    project_id, bigquery_client, bigquery_dataset, integration, service_account_info
+):
     table_id = f"destination_test_{uuid.uuid4()}"
     fully_qualified_table_id = f"{project_id}.{bigquery_dataset.dataset_id}.{table_id}"
 
@@ -143,6 +205,7 @@ async def test_bigquery_check_table_test_step(project_id, bigquery_client, bigqu
         project_id=project_id,
         dataset_id=bigquery_dataset.dataset_id,
         table_id=table_id,
+        integration=integration,
         service_account_info=service_account_info,
     )
     result = await test_step.run()
@@ -154,8 +217,9 @@ async def test_bigquery_check_table_test_step(project_id, bigquery_client, bigqu
         bigquery_client.get_table(fully_qualified_table_id)
 
 
+@pytest.mark.parametrize("integration", ["impersonated", "key_file", None], indirect=True)
 async def test_bigquery_check_table_test_step_with_invalid_identifier(
-    project_id, bigquery_client, bigquery_dataset, service_account_info
+    project_id, bigquery_client, bigquery_dataset, integration, service_account_info
 ):
     table_id = f"$destination_test_{uuid.uuid4()}"
     fully_qualified_table_id = f"{project_id}.{bigquery_dataset.dataset_id}.{table_id}"
@@ -167,6 +231,7 @@ async def test_bigquery_check_table_test_step_with_invalid_identifier(
         project_id=project_id,
         dataset_id=bigquery_dataset.dataset_id,
         table_id=table_id,
+        integration=integration,
         service_account_info=service_account_info,
     )
     result = await test_step.run()
@@ -179,7 +244,73 @@ async def test_bigquery_check_table_test_step_with_invalid_identifier(
         bigquery_client.get_table(fully_qualified_table_id)
 
 
-@pytest.mark.parametrize("step", [BigQueryTableTestStep(), BigQueryProjectTestStep(), BigQueryDatasetTestStep()])
+@pytest.mark.parametrize("integration", ["impersonated"], indirect=True)
+async def test_bigquery_impersonate_service_account_test_step(project_id, integration):
+    test_step = BigQueryImpersonateServiceAccountTestStep(
+        project_id=project_id,
+        integration=integration,
+    )
+    result = await test_step.run()
+
+    assert result.status == Status.PASSED, result.message
+    assert result.message is None
+
+
+@pytest.mark.parametrize("integration", ["impersonated"], indirect=True)
+async def test_bigquery_impersonate_service_account_test_step_with_unknown_account(project_id, integration):
+    with patch.dict(
+        integration.integration.config,
+        service_account_email=f"garbage@{integration.project_id}.iam.gserviceaccount.com",
+    ):
+        test_step = BigQueryImpersonateServiceAccountTestStep(
+            project_id=project_id,
+            integration=integration,
+        )
+        result = await test_step.run()
+
+    assert result.status == Status.FAILED
+    assert result.message is not None
+
+
+@pytest.mark.parametrize("integration", ["impersonated"], indirect=True)
+async def test_bigquery_verify_service_account_ownership_test_step(project_id, integration, aorganization):
+    test_step = BigQueryVerifyServiceAccountOwnershipTestStep(
+        project_id=project_id,
+        integration=integration,
+        organization_id=str(aorganization.id),
+    )
+    result = await test_step.run()
+
+    assert result.status == Status.PASSED, result.message
+    assert result.message is None
+
+
+@pytest.mark.parametrize("integration", ["impersonated"], indirect=True)
+@pytest.mark.parametrize("service_account_description", ["garbage"], indirect=True)
+async def test_bigquery_verify_service_account_ownership_test_step_with_garbage_description(
+    project_id, integration, aorganization
+):
+    test_step = BigQueryVerifyServiceAccountOwnershipTestStep(
+        project_id=project_id,
+        integration=integration,
+        organization_id=str(aorganization.id),
+    )
+    result = await test_step.run()
+
+    assert result.status == Status.FAILED
+    assert result.message is not None
+
+
+@pytest.mark.parametrize(
+    "step",
+    [
+        BigQueryImpersonateServiceAccountTestStep(),
+        BigQueryVerifyServiceAccountOwnershipTestStep(),
+        BigQueryTableTestStep(),
+        BigQueryProjectTestStep(),
+        BigQueryDatasetTestStep(),
+    ],
+)
 async def test_test_steps_fail_if_not_configured(step):
     result = await step.run()
     assert result.status == Status.FAILED
diff --git a/products/batch_exports/backend/tests/temporal/README.md b/products/batch_exports/backend/tests/temporal/README.md
index 6f3d5571411f..2a2e752e18ba 100644
--- a/products/batch_exports/backend/tests/temporal/README.md
+++ b/products/batch_exports/backend/tests/temporal/README.md
@@ -4,17 +4,34 @@ This module contains unit tests covering activities, workflows, and helper funct
 
 ## Testing BigQuery batch exports
 
-BigQuery batch exports can be tested against a real BigQuery instance, but doing so requires additional setup. For this reason, these tests are skipped unless an environment variable pointing to a BigQuery credentials file (`GOOGLE_APPLICATION_CREDENTIALS=/path/to/my/project-credentials.json`) is set.
+BigQuery batch exports can be tested against a real BigQuery instance, but doing so requires additional setup. BigQuery currently supports multiple authentication mechanisms:
+
+1. Authenticating directly with a JSON key file
+2. Using an integration populated with a JSON key file
+3. Using an integration without any keys to impersonate the account using our own credentials
+
+All tests still require a JSON key file for setup so, regardless of which authentication method is being tested, all these tests are skipped unless an environment variable pointing to a BigQuery credentials file (`GOOGLE_APPLICATION_CREDENTIALS=/path/to/my/project-credentials.json`) is set.
+
+Additionally, any tests that are specific to the 3rd authentication method in the list (impersonation) require AWS credentials to be available to `boto3`, and the following settings to be configured:
+
+- `BATCH_EXPORT_BIGQUERY_SERVICE_ACCOUNT`
+- `BATCH_EXPORT_BIGQUERY_STS_AUDIENCE_FIELD`
+
+For PostHog employees, development values for these settings are available in the PostHog password manager.
 
 > [!WARNING]
 > Since BigQuery batch export tests require additional setup, we skip them by default and will not be ran by automated CI pipelines. Please ensure these tests pass when making changes that affect BigQuery batch exports.
 
-To enable testing for BigQuery batch exports, we require:
+When starting from scratch, to enable testing for BigQuery batch exports, we require:
 
-1. A BigQuery project and dataset
-2. A BigQuery ServiceAccount with access to said project and dataset. See the [BigQuery batch export documentation](https://posthog.com/docs/cdp/batch-exports/bigquery#setting-up-bigquery-access) on detailed steps to setup a ServiceAccount.
+1. A BigQuery project
+2. A Google Cloud service account with BigQuery access in said project. See the [BigQuery batch export documentation](https://posthog.com/docs/cdp/batch-exports/bigquery#setting-up-bigquery-access) on detailed steps to setup a service account.
+3. A [JSON key file](https://cloud.google.com/iam/docs/keys-create-delete#creating) for the service account, saved to a local file.
+4. If testing impersonation:
+   - Another Google Cloud service account that can be used to impersonate the service account from the previous step is required.
+   - A workload identity federation provider and pool setup to grant access to this other service account.
 
-Then, a [key](https://cloud.google.com/iam/docs/keys-create-delete#creating) can be created for the BigQuery ServiceAccount and saved to a local file. For PostHog employees, this file should already be available under the PostHog password manager.
+For PostHog employees, all of this is already setup for you. You can obtain a JSON key file, and the necessary values for the settings detailed above from the PostHog password manager.
 
 Tests for BigQuery batch exports can be then run from the root of the `posthog` repo:
 
diff --git a/products/batch_exports/backend/tests/temporal/destinations/bigquery/conftest.py b/products/batch_exports/backend/tests/temporal/destinations/bigquery/conftest.py
index 5f283ce7c9ff..52b31e34ed78 100644
--- a/products/batch_exports/backend/tests/temporal/destinations/bigquery/conftest.py
+++ b/products/batch_exports/backend/tests/temporal/destinations/bigquery/conftest.py
@@ -92,7 +92,7 @@ async def integration(
     match integration_type:
         case "impersonated":
             if not await has_valid_aws_credentials():
-                pytest.skip("AWS credentials not available")
+                pytest.skip("AWS credentials not available. Credentials are required to impersonate a service account")
 
             integration = await impersonated_integration(ateam, bigquery_config)
             await set_service_account_description_for_integration(integration, service_account_description)

PATCH

echo "Patch applied successfully."
