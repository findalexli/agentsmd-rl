# Fix AWS S3 (Minio) Endpoint URL Handling for Feature Branches

## Problem Description

The AWS Event Service in OpenHands does not properly handle custom S3/Minio endpoint URLs for feature branch deployments. The S3 client's endpoint URL is currently read directly from `os.getenv('AWS_S3_ENDPOINT')`, which lacks:

1. HTTP/HTTPS protocol conversion based on the `AWS_S3_SECURE` environment variable
2. Per-instance override capability (the URL is fixed at module load time)

## File to Modify

`openhands/app_server/event/aws_event_service.py`

## Symptoms

The `AwsEventServiceInjector` class currently passes `os.getenv('AWS_S3_ENDPOINT')` directly to `boto3.client('s3', endpoint_url=...)`. This causes issues because:

- When `AWS_S3_SECURE` is set to `false`, the endpoint may still use HTTPS (or vice versa)
- When the endpoint URL lacks a protocol prefix, the S3 client may fail or behave unexpectedly
- The endpoint cannot be overridden per injector instance

## Required Behavior

### Endpoint URL computation

A function should compute the default endpoint URL with the following logic:

- Read `AWS_S3_ENDPOINT` via `os.getenv('AWS_S3_ENDPOINT')`. Return `None` if not set.
- Read `AWS_S3_SECURE` via `os.getenv('AWS_S3_SECURE', 'true')`. Default is `'true'`.
- When secure is true: the returned URL must start with `https://`. If the raw endpoint starts with `http://`, replace that prefix with `https://`. If the raw endpoint has no protocol prefix, prepend `https://`.
- When secure is false: the returned URL must start with `http://`. If the raw endpoint starts with `https://`, replace that prefix with `http://`. If the raw endpoint has no protocol prefix, prepend `http://`.

### Pydantic field on the injector

The injector class should expose an `endpoint_url` field of type `str | None`, using Pydantic's `Field` with a `default_factory` pointing to the endpoint URL computation function. This enables per-instance endpoint override while computing the default from the environment at model instantiation time.

### S3 client endpoint sourcing

The boto3 S3 client within the injector should use the instance's `endpoint_url` attribute as its `endpoint_url` parameter, rather than calling `os.getenv` directly.

## Behavioral examples

Given `AWS_S3_ENDPOINT='https://minio.example.com:9000'` and `AWS_S3_SECURE='true'`, the function should return `'https://minio.example.com:9000'`.

Given `AWS_S3_ENDPOINT='minio.example.com:9000'` and `AWS_S3_SECURE='true'`, the function should return `'https://minio.example.com:9000'`.

Given `AWS_S3_ENDPOINT='minio.example.com:9000'` and `AWS_S3_SECURE='false'`, the function should return `'http://minio.example.com:9000'`.

Given `AWS_S3_ENDPOINT='http://minio.example.com:9000'` and `AWS_S3_SECURE='true'`, the function should return `'https://minio.example.com:9000'`.

Given `AWS_S3_ENDPOINT='https://minio.example.com:9000'` and `AWS_S3_SECURE='false'`, the function should return `'http://minio.example.com:9000'`.

Given `AWS_S3_ENDPOINT='minio.example.com:9000'` with `AWS_S3_SECURE` unset, the function should return `'https://minio.example.com:9000'` (secure defaults to true).

With no environment variables set, the function should return `None`.
