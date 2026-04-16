# Fix AWS S3 (Minio) Endpoint URL Handling for Feature Branches

## Problem Description

The AWS Event Service in OpenHands does not properly handle custom S3/Minio endpoint URLs for feature branch deployments. The current implementation reads the endpoint URL from environment variables at module load time in a way that doesn't properly support feature branch configurations.

## Files to Modify

- `openhands/app_server/event/aws_event_service.py` - Main service implementation

## Symptoms

1. The `AwsEventServiceInjector` class needs to properly read and use the `AWS_S3_ENDPOINT` environment variable
2. The endpoint URL should respect the `AWS_S3_SECURE` environment variable to determine HTTP vs HTTPS protocol
3. When `AWS_S3_SECURE=true` (default), the URL should use `https://` protocol
4. When `AWS_S3_SECURE=false`, the URL should use `http://` protocol
5. The protocol prefix should be added automatically if missing, or converted if mismatched with the secure setting
6. The endpoint URL should be configurable as a Pydantic field with proper default factory behavior

## Expected Behavior

- When `AWS_S3_ENDPOINT=https://minio.example.com:9000` and `AWS_S3_SECURE=true`, the endpoint URL should be `https://minio.example.com:9000`
- When `AWS_S3_ENDPOINT=minio.example.com:9000` and `AWS_S3_SECURE=true`, the endpoint URL should be `https://minio.example.com:9000` (https:// added)
- When `AWS_S3_ENDPOINT=http://minio.example.com:9000` and `AWS_S3_SECURE=true`, the endpoint URL should be `https://minio.example.com:9000` (converted to https)
- When `AWS_S3_ENDPOINT=http://minio.example.com:9000` and `AWS_S3_SECURE=false`, the endpoint URL should be `http://minio.example.com:9000`
- When no environment variables are set, the endpoint URL should be `None`
- The `AwsEventServiceInjector` should accept a custom `endpoint_url` parameter that overrides the environment variable default

## Context

The `AwsEventServiceInjector` class is a Pydantic model that provides dependency injection for the AWS Event Service. It currently has `bucket_name` and `prefix` fields. You need to add an `endpoint_url` field that reads from environment variables with the logic described above.

The `AwsEventService` uses this endpoint URL when creating the S3 boto3 client.

## Testing

Run tests with: `pytest tests/unit/app_server/test_aws_event_service.py -v`

The tests use monkeypatch to set/clear environment variables and verify the endpoint URL behavior.
