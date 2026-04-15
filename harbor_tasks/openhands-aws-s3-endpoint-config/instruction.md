# Fix AWS S3 (Minio) Endpoint URL Protocol Handling

## Problem

The `AwsEventServiceInjector` class in `openhands/app_server/event/aws_event_service.py` doesn't properly handle custom S3/Minio endpoint URLs for feature branches. Currently, it reads the `AWS_S3_ENDPOINT` environment variable directly inside the `inject()` method, which has two issues:

1. **Protocol handling bug**: When `AWS_S3_ENDPOINT` contains a URL without a protocol (e.g., `minio.example.com:9000`) or with a mismatched protocol (e.g., `http://minio.example.com:9000` when `AWS_S3_SECURE=true`), the endpoint URL isn't properly converted to use HTTP or HTTPS based on the `AWS_S3_SECURE` environment variable.

2. **Improper configuration pattern**: The endpoint URL should be determined at class initialization time using a configurable field rather than being read from environment variables inside the method.

## Expected Behavior

The fix should implement the following runtime behavior:

When `AWS_S3_ENDPOINT=minio.example.com:9000` and `AWS_S3_SECURE=true`:
- The endpoint URL should be `https://minio.example.com:9000`

When `AWS_S3_ENDPOINT=http://minio.example.com:9000` and `AWS_S3_SECURE=true`:
- The endpoint URL should be `https://minio.example.com:9000` (converts http to https)

When `AWS_S3_ENDPOINT=minio.example.com:9000` and `AWS_S3_SECURE=false`:
- The endpoint URL should be `http://minio.example.com:9000`

When `AWS_S3_ENDPOINT=https://minio.example.com:9000` and `AWS_S3_SECURE=false`:
- The endpoint URL should be `http://minio.example.com:9000` (converts https to http)

When `AWS_S3_ENDPOINT` is not set:
- The endpoint URL should be `None`

## Requirements

The implementation must:
1. Add a helper function (suggested name: `_get_default_aws_endpoint_url`) that reads `AWS_S3_ENDPOINT` and `AWS_S3_SECURE` environment variables and returns the properly formatted endpoint URL with correct protocol
2. Add an `endpoint_url` field (type: `str | None`) to `AwsEventServiceInjector` that is initialized using the helper function
3. Update the boto3 client creation to use the class's `endpoint_url` field instead of calling `os.getenv('AWS_S3_ENDPOINT')` directly
4. The `endpoint_url` field should have a default value so it's not required when creating an instance

## Files to Modify

- `openhands/app_server/event/aws_event_service.py`
