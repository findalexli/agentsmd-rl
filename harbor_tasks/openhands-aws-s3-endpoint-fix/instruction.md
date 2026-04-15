# Fix AWS S3 (Minio) Endpoint URL Configuration

## Problem

The `AwsEventServiceInjector` class in `openhands/app_server/event/aws_event_service.py` reads the S3 endpoint URL directly from the `AWS_S3_ENDPOINT` environment variable at runtime using `os.getenv()`. This causes several issues:

1. The endpoint URL protocol (HTTP vs HTTPS) is not properly handled based on the `AWS_S3_SECURE` setting
2. When `AWS_S3_ENDPOINT` contains a protocol prefix that doesn't match the `AWS_S3_SECURE` setting, the wrong protocol is used
3. The configuration cannot be customized per-instance because it's read directly from environment at client creation time
4. When `AWS_S3_SECURE` is not set, the code doesn't default to secure connections

Specifically, the expected behavior should be:

1. A helper function named `_get_default_aws_endpoint_url()` that:
   - Returns `None` if `AWS_S3_ENDPOINT` environment variable is not set
   - Reads the `AWS_S3_SECURE` environment variable (defaults to `true` when not set)
   - Returns a URL with `https://` prefix when `AWS_S3_SECURE` is `true` (case-insensitive)
   - Returns a URL with `http://` prefix when `AWS_S3_SECURE` is `false` (case-insensitive)
   - Converts between `http://` and `https://` if the endpoint URL protocol doesn't match the secure setting
   - Preserves URLs that already have the correct protocol prefix

2. An `endpoint_url` field on the `AwsEventServiceInjector` class:
   - Type: `str | None`
   - Should use Pydantic's `Field` with `default_factory=_get_default_aws_endpoint_url`
   - This allows per-instance customization while defaulting from environment

3. The S3 client creation in `AwsEventServiceInjector.inject()` should use the instance's `endpoint_url` field instead of calling `os.getenv('AWS_S3_ENDPOINT')` directly.

The implementation should correctly handle:
- Endpoints without protocol prefixes (adds `https://` when secure, `http://` when insecure)
- Endpoints with `https://` prefix preserved when secure
- Endpoints with `http://` prefix preserved when insecure
- Protocol conversion: `http://` → `https://` when secure=true
- Protocol conversion: `https://` → `http://` when secure=false
- Returns `None` when `AWS_S3_ENDPOINT` is not set
- Defaults to secure=true when `AWS_S3_SECURE` is not set
