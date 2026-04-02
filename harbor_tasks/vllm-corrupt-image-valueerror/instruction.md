# Bug: Corrupt/Truncated Image Inputs Return HTTP 500 Instead of 400

## Context

The vLLM server's multimodal image handling code is in `vllm/multimodal/media/image.py`. The `ImageMediaIO` class provides methods for loading image data from bytes and files, processing them via PIL, and returning the result for downstream use.

## Problem

When a client sends a base64-encoded image that is syntactically valid base64 but contains **truncated or corrupted image data** (e.g., a JPEG file with the last 128 bytes chopped off), the server returns an HTTP 500 Internal Server Error instead of HTTP 400 Bad Request.

This is incorrect — the client sent invalid input, so the response should be a 4xx client error, not a 5xx server error. Other forms of invalid input (e.g., malformed base64, random non-image bytes that fail immediately) already correctly return 400.

The inconsistency is specifically with images that have valid headers but corrupted/incomplete data streams — these slip past initial parsing but fail during actual pixel decoding.

## Reproduction

- A truncated JPEG/PNG/WebP file (real image with bytes removed from the end) → HTTP 500
- Completely garbage bytes that don't match any image format → HTTP 400 (already correct)
- Malformed base64 encoding → HTTP 400 (already correct)

## Files to Investigate

- `vllm/multimodal/media/image.py` — specifically the `load_bytes()` and `load_file()` methods in `ImageMediaIO`
