# Refactor AWS S3 endpoint URL handling in OpenHands

In the OpenHands repository, the file `openhands/app_server/event/aws_event_service.py` defines the `AwsEventServiceInjector` class. Currently, the boto3 S3 client within this class reads the endpoint URL directly from `os.getenv('AWS_S3_ENDPOINT')`. This approach has two shortcomings: there is no HTTP/HTTPS protocol conversion based on a `AWS_S3_SECURE` environment variable, and the endpoint URL cannot be overridden per injector instance.

## Desired behavior

### Endpoint URL computation

A module-level function `_get_default_aws_endpoint_url` should handle endpoint URL computation with protocol conversion:

- Read `AWS_S3_ENDPOINT` via `os.getenv('AWS_S3_ENDPOINT')`. Return `None` if not set.
- Read `AWS_S3_SECURE` via `os.getenv('AWS_S3_SECURE', 'true')`. Default is `'true'`.
- When secure is true: the returned URL must start with `https://`. If the raw endpoint starts with `http://`, replace that prefix with `https://`. If the raw endpoint has no protocol prefix, prepend `https://`.
- When secure is false: the returned URL must start with `http://`. If the raw endpoint starts with `https://`, replace that prefix with `http://`. If the raw endpoint has no protocol prefix, prepend `http://`.

### Pydantic field on the injector

The `AwsEventServiceInjector` class should expose an `endpoint_url` field of type `str | None`, using `Field` (imported from `pydantic`) with `default_factory=_get_default_aws_endpoint_url`. This enables per-instance endpoint override while computing the default from the environment at model instantiation time.

### S3 client endpoint sourcing

The boto3 S3 client within `AwsEventServiceInjector` should use the instance's `endpoint_url` attribute as its `endpoint_url` parameter, rather than reading from `os.getenv` directly.

### Behavioral examples

Given `AWS_S3_ENDPOINT='https://minio.example.com:9000'` and `AWS_S3_SECURE='true'`, the function should return `'https://minio.example.com:9000'`.

Given `AWS_S3_ENDPOINT='minio.example.com:9000'` and `AWS_S3_SECURE='true'`, the function should return `'https://minio.example.com:9000'`.

Given `AWS_S3_ENDPOINT='minio.example.com:9000'` and `AWS_S3_SECURE='false'`, the function should return `'http://minio.example.com:9000'`.

Given `AWS_S3_ENDPOINT='http://minio.example.com:9000'` and `AWS_S3_SECURE='true'`, the function should return `'https://minio.example.com:9000'`.

Given `AWS_S3_ENDPOINT='https://minio.example.com:9000'` and `AWS_S3_SECURE='false'`, the function should return `'http://minio.example.com:9000'`.

Given `AWS_S3_ENDPOINT='minio.example.com:9000'` with `AWS_S3_SECURE` unset, the function should return `'https://minio.example.com:9000'` (secure defaults to true).

With no environment variables set, the function should return `None`.
