# Fix AWS S3 (Minio) Endpoint URL Configuration

## Problem

The `AwsEventServiceInjector` class reads the S3 endpoint URL directly from the `AWS_S3_ENDPOINT` environment variable at runtime using `os.getenv()`. This causes several issues:

1. The endpoint URL protocol (HTTP vs HTTPS) is not properly handled based on the `AWS_S3_SECURE` setting
2. When `AWS_S3_ENDPOINT` contains a protocol prefix that doesn't match the `AWS_S3_SECURE` setting, the wrong protocol is used
3. The configuration cannot be customized per-instance because it's read directly from environment at client creation time
4. When `AWS_S3_SECURE` is not set, the code doesn't default to secure connections

## Required Behavior

Fix the `AwsEventServiceInjector` class so that:

1. **Endpoint URL field**: The class should have an `endpoint_url` field of type `str | None` that:
   - Defaults to `None` when `AWS_S3_ENDPOINT` environment variable is not set
   - Reads from `AWS_S3_ENDPOINT` and `AWS_S3_SECURE` environment variables
   - Uses `https://` prefix when `AWS_S3_SECURE` is `true` (case-insensitive), or when not set (secure should be the default)
   - Uses `http://` prefix when `AWS_S3_SECURE` is `false` (case-insensitive)
   - Adds the appropriate protocol prefix when the endpoint URL doesn't have one
   - Converts between `http://` and `https://` if the endpoint URL protocol doesn't match the secure setting
   - Allows per-instance customization (not just environment-based)

2. **S3 client usage**: The S3 client creation should use the instance's `endpoint_url` field instead of calling `os.getenv('AWS_S3_ENDPOINT')` directly.

## Specific Requirements

The implementation should correctly handle these environment variable combinations:
- `AWS_S3_ENDPOINT=https://minio.example.com:9000`, `AWS_S3_SECURE=true` → `https://minio.example.com:9000`
- `AWS_S3_ENDPOINT=minio.example.com:9000`, `AWS_S3_SECURE=true` → `https://minio.example.com:9000`
- `AWS_S3_ENDPOINT=http://minio.example.com:9000`, `AWS_S3_SECURE=false` → `http://minio.example.com:9000`
- `AWS_S3_ENDPOINT=minio.example.com:9000`, `AWS_S3_SECURE=false` → `http://minio.example.com:9000`
- `AWS_S3_ENDPOINT=http://minio.example.com:9000`, `AWS_S3_SECURE=true` → `https://minio.example.com:9000`
- `AWS_S3_ENDPOINT=https://minio.example.com:9000`, `AWS_S3_SECURE=false` → `http://minio.example.com:9000`
- `AWS_S3_ENDPOINT` not set → `None`

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
- `mypy (Python type checker)`
