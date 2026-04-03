# BigQuery destination tests fail when using an integration

## Problem

BigQuery destination tests do not work when a user configures a BigQuery batch export with an integration (e.g., an impersonated service account). The `integration` object is available in the API handler but is never passed through to the destination test configuration, so the BigQuery test steps cannot authenticate using integration-based credentials.

Additionally, the existing BigQuery destination test steps (`BigQueryProjectTestStep`, `BigQueryDatasetTestStep`, `BigQueryTableTestStep`) only accept raw service account info (private key, token URI, etc.) and have no awareness of integrations. There are no test steps to verify impersonation or service account ownership.

## Expected Behavior

1. The `integration` object should be passed through to the destination test's `configure()` method from the API handler (in `posthog/batch_exports/http.py`).
2. Each BigQuery destination test step should accept an optional `integration` parameter and use it for authentication when available (falling back to raw service account info).
3. New test steps should be added for impersonation-specific checks:
   - Verifying that we can impersonate a service account
   - Verifying service account ownership (organization ID in description)
4. A helper function should abstract BigQuery client creation from either integration or service account info.

## Files to Look At

- `posthog/batch_exports/http.py` — API handler that runs destination tests; this is where `integration` needs to be added to `test_configuration`
- `products/batch_exports/backend/api/destination_tests/bigquery.py` — BigQuery destination test steps that need integration support
- `products/batch_exports/backend/api/destination_tests/base.py` — base classes for destination tests
- `products/batch_exports/backend/temporal/destinations/bigquery_batch_export.py` — contains `BigQueryClient`, `impersonate_service_account`, and `get_our_google_cloud_credentials` helpers

After making the code changes, update the relevant test documentation (`products/batch_exports/backend/tests/temporal/README.md`) to reflect the new authentication mechanisms and setup requirements for impersonation testing.
