# Fix AWS S3 (Minio) Endpoint URL Configuration

## Problem

The `AwsEventServiceInjector` class in `openhands/app_server/event/aws_event_service.py` doesn't properly handle custom S3/Minio endpoint URLs for feature branches. Currently, it reads the `AWS_S3_ENDPOINT` environment variable directly inside the `inject()` method, which has two issues:

1. **No protocol handling**: The endpoint URL isn't properly handling HTTP vs HTTPS protocols based on the `AWS_S3_SECURE` environment variable
2. **No configurable field**: The endpoint URL should be a configurable field on the injector class rather than being read from environment variables inside the method

## What Needs to Be Fixed

1. Add a new function `_get_default_aws_endpoint_url()` that:
   - Reads `AWS_S3_ENDPOINT` from environment variables
   - Handles the `AWS_S3_SECURE` setting (defaults to `true`)
   - Properly adds or converts the protocol (http:// or https://) based on the secure setting

2. Add an `endpoint_url` field to `AwsEventServiceInjector` using Pydantic's `Field` with a `default_factory` that calls the new function

3. Update the `inject()` method to use `self.endpoint_url` instead of `os.getenv('AWS_S3_ENDPOINT')`

## Behavior Examples

When `AWS_S3_ENDPOINT=minio.example.com:9000` and `AWS_S3_SECURE=true`:
- Should produce: `https://minio.example.com:9000`

When `AWS_S3_ENDPOINT=http://minio.example.com:9000` and `AWS_S3_SECURE=true`:
- Should produce: `https://minio.example.com:9000` (converts http to https)

When `AWS_S3_ENDPOINT=minio.example.com:9000` and `AWS_S3_SECURE=false`:
- Should produce: `http://minio.example.com:9000`

When `AWS_S3_ENDPOINT=https://minio.example.com:9000` and `AWS_S3_SECURE=false`:
- Should produce: `http://minio.example.com:9000` (converts https to http)

When `AWS_S3_ENDPOINT` is not set:
- Should produce: `None`

## Files to Modify

- `openhands/app_server/event/aws_event_service.py`

## Testing

Write tests that verify:
1. The `_get_default_aws_endpoint_url()` function handles all protocol combinations correctly
2. The `AwsEventServiceInjector` properly gets its `endpoint_url` from environment variables
3. The `endpoint_url` can also be set explicitly when creating an injector instance
4. When no environment variables are set, `endpoint_url` defaults to `None`
