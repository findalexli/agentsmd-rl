# Fix AWS S3 (Minio) Endpoint URL Configuration

## Problem

The `AwsEventServiceInjector` class in `openhands/app_server/event/aws_event_service.py` currently reads the S3 endpoint URL directly from the `AWS_S3_ENDPOINT` environment variable at runtime using `os.getenv()`. This approach has limitations:

1. The endpoint URL protocol (HTTP vs HTTPS) is not properly handled based on the `AWS_S3_SECURE` setting
2. The configuration cannot be easily customized per-instance
3. Feature branches cannot properly use custom S3/Minio endpoints for event storage

## Your Task

Modify `openhands/app_server/event/aws_event_service.py` to:

1. **Create a helper function** `_get_default_aws_endpoint_url()` that:
   - Reads from `AWS_S3_ENDPOINT` environment variable
   - Handles the `AWS_S3_SECURE` setting (defaults to `true` if not set)
   - Properly sets the protocol (`https://` when secure, `http://` when insecure)
   - Converts between protocols if the endpoint URL doesn't match the secure setting
   - Returns `None` if `AWS_S3_ENDPOINT` is not set

2. **Add an `endpoint_url` field** to the `AwsEventServiceInjector` class:
   - Use Pydantic's `Field` with a `default_factory` pointing to `_get_default_aws_endpoint_url`
   - The field should be optional (`str | None`)
   - This allows the endpoint URL to be configurable per-instance while defaulting from environment

3. **Update the S3 client creation** in `AwsEventServiceInjector.inject()` to use `self.endpoint_url` instead of `os.getenv('AWS_S3_ENDPOINT')`

## Key Files

- `openhands/app_server/event/aws_event_service.py` - Main file to modify
  - Look for the `AwsEventServiceInjector` class
  - Find where `boto3.client('s3', ...)` is called

## Testing

Your changes should allow feature branches to properly configure S3/Minio endpoints through:
- Environment variables (`AWS_S3_ENDPOINT`, `AWS_S3_SECURE`)
- Direct constructor parameter (`endpoint_url`)

The implementation should correctly handle:
- Endpoints with or without protocol prefixes
- Protocol conversion based on the secure setting
- Default secure=true behavior when `AWS_S3_SECURE` is not set
