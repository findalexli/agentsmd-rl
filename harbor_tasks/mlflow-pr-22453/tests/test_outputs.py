"""
test_outputs.py - mlflow-gemini-bytes-repr-extraction

Tests for Gemini SDK bytes repr format handling in inline_data extraction.
The bug: when Gemini SDK sends bytes as Python repr string (e.g., "b'\\x89PNG...'")
instead of base64, the inline_data attachment is not extracted correctly.
"""
import base64
import os
import subprocess
import sys

REPO = "/workspace/mlflow_repo"

# Add mlflow to path
sys.path.insert(0, REPO)


def _make_live_span(trace_id="tr-test123"):
    from opentelemetry.sdk.trace import TracerProvider

    tracer = TracerProvider().get_tracer("test")
    otel_span = tracer.start_span("test_span")
    from mlflow.entities.span import LiveSpan

    return LiveSpan(otel_span, trace_id=trace_id)


PNG_BYTES = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwADhQGAWjR9awAAAABJRU5ErkJggg=="
)


# ==============================================================================
# Fail-to-pass tests: these MUST fail on base commit, pass on fix
# ==============================================================================


def test_gemini_inline_data_bytes_repr_extracted():
    """
    When inline_data contains a Python bytes repr string (as produced by
    the Gemini SDK's Pydantic serialization), the attachment must be
    extracted and the original bytes must be recoverable.
    """
    span = _make_live_span()

    # Gemini SDK Pydantic serialization produces repr(bytes) instead of base64
    # e.g., repr(b'\x89PNG') = "b'\\x89PNG'"
    bytes_repr = repr(PNG_BYTES)

    span.set_outputs({
        "candidates": [
            {
                "content": {
                    "parts": [
                        {"text": "A small image."},
                        {
                            "inline_data": {
                                "mime_type": "image/png",
                                "data": bytes_repr,
                            }
                        },
                    ]
                }
            }
        ]
    })

    parts = span.outputs["candidates"][0]["content"]["parts"]
    # Text part unchanged
    assert parts[0] == {"text": "A small image."}

    # inline_data reference should be rewritten to mlflow-attachment://
    inline = parts[1]
    assert inline["inline_data"]["data"].startswith("mlflow-attachment://"), \
        f"Expected mlflow-attachment:// prefix, got: {inline['inline_data']['data'][:50]}"

    # Attachment stored and content matches original bytes
    assert len(span._attachments) == 1, f"Expected 1 attachment, got {len(span._attachments)}"
    att = next(iter(span._attachments.values()))
    assert att.content_type == "image/png", f"Expected image/png, got {att.content_type}"
    assert att.content_bytes == PNG_BYTES, f"Extracted bytes don't match original PNG"


def test_gemini_inline_data_bytes_repr_via_set_inputs():
    """
    Same bytes repr handling should work when data arrives via set_inputs.
    """
    span = _make_live_span()

    bytes_repr = repr(PNG_BYTES)

    span.set_inputs({
        "candidates": [
            {
                "content": {
                    "parts": [
                        {"text": "Image input."},
                        {
                            "inline_data": {
                                "mime_type": "image/png",
                                "data": bytes_repr,
                            }
                        },
                    ]
                }
            }
        ]
    })

    parts = span.inputs["candidates"][0]["content"]["parts"]
    inline = parts[1]
    assert inline["inline_data"]["data"].startswith("mlflow-attachment://")
    assert len(span._attachments) == 1
    att = next(iter(span._attachments.values()))
    assert att.content_type == "image/png"
    assert att.content_bytes == PNG_BYTES


def test_gemini_inline_data_bytes_repr_wav_audio():
    """
    Bytes repr format should also work for audio mime types.
    """
    span = _make_live_span()

    audio_bytes = b"RIFF\x00\x00\x00\x00WAVEfmt "
    audio_repr = repr(audio_bytes)

    span.set_outputs({
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "inline_data": {
                                "mime_type": "audio/wav",
                                "data": audio_repr,
                            }
                        },
                    ]
                }
            }
        ]
    })

    inline = span.outputs["candidates"][0]["content"]["parts"][0]
    assert inline["inline_data"]["data"].startswith("mlflow-attachment://")
    assert len(span._attachments) == 1
    att = next(iter(span._attachments.values()))
    assert att.content_type == "audio/wav"
    assert att.content_bytes == audio_bytes


# ==============================================================================
# Pass-to-pass tests: verify existing behavior still works
# ==============================================================================


def test_gemini_inline_data_base64_still_works():
    """
    Normal base64-encoded inline_data (non-repr format) should continue
    to work as before. This is a regression control.
    """
    span = _make_live_span()

    img_b64 = base64.b64encode(PNG_BYTES).decode()

    span.set_outputs({
        "candidates": [
            {
                "content": {
                    "parts": [
                        {"text": "A base64 image."},
                        {
                            "inline_data": {
                                "mime_type": "image/png",
                                "data": img_b64,
                            }
                        },
                    ]
                }
            }
        ]
    })

    parts = span.outputs["candidates"][0]["content"]["parts"]
    inline = parts[1]
    assert inline["inline_data"]["data"].startswith("mlflow-attachment://")
    assert len(span._attachments) == 1
    att = next(iter(span._attachments.values()))
    assert att.content_type == "image/png"
    assert att.content_bytes == PNG_BYTES


def test_gemini_inline_data_invalid_base64_rejected():
    """
    Malformed base64 data should not create an attachment.
    This verifies graceful error handling.
    """
    span = _make_live_span()

    span.set_outputs({
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "inline_data": {
                                "mime_type": "image/png",
                                "data": "!!!not-valid-base64!!!",
                            }
                        },
                    ]
                }
            }
        ]
    })

    inline = span.outputs["candidates"][0]["content"]["parts"][0]
    # Invalid data should be left as-is (not rewritten to attachment ref)
    assert inline["inline_data"]["data"] == "!!!not-valid-base64!!!"
    assert len(span._attachments) == 0


def test_gemini_inline_data_invalid_bytes_repr_rejected():
    """
    Malformed bytes repr (not valid Python literal) should fall back to
    base64 decode attempt, and if that also fails, leave data unchanged.
    """
    span = _make_live_span()

    # Not a valid Python bytes literal
    invalid_repr = "b'incomplete"

    span.set_outputs({
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "inline_data": {
                                "mime_type": "image/png",
                                "data": invalid_repr,
                            }
                        },
                    ]
                }
            }
        ]
    })

    inline = span.outputs["candidates"][0]["content"]["parts"][0]
    # Should be left as-is since neither repr parse nor base64 decode succeeds
    assert inline["inline_data"]["data"] == invalid_repr
    assert len(span._attachments) == 0


# ==============================================================================
# Repo CI/CD pass-to-pass tests
# ==============================================================================


def test_repo_span_entity_tests():
    """Repo's span entity tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-m", "pytest", "tests/entities/test_span.py", "--noconftest", "-q"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Span entity tests failed:\n{r.stdout[-500:]}"


def test_repo_span_attachment_extraction_tests():
    """Repo's span attachment extraction tests pass (pass_to_pass)."""
    r = subprocess.run(
        [
            "python", "-m", "pytest",
            "tests/entities/test_span_auto_extract_attachments.py",
            "--noconftest", "-q",
        ],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Attachment extraction tests failed:\n{r.stdout[-500:]}"


def test_repo_tracing_export_tests():
    """Repo's tracing export tests pass (pass_to_pass)."""
    r = subprocess.run(
        [
            "python", "-m", "pytest",
            "tests/tracing/export/test_mlflow_v3_exporter.py",
            "--noconftest", "-q",
        ],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Tracing export tests failed:\n{r.stdout[-500:]}"


