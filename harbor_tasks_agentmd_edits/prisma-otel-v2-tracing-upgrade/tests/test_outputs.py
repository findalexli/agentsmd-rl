"""
Task: prisma-otel-v2-tracing-upgrade
Repo: prisma/prisma @ 423b58507879080bdc1273ca5d30b3de87e5b766
PR:   28268

Upgrade OpenTelemetry SDK from v1 to v2 in tracing test files and update
the @prisma/instrumentation README example code to match the new APIs.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

from pathlib import Path

REPO = "/workspace/prisma"

# The four tracing test files that must be updated
TRACING_TEST_FILES = [
    "packages/client/tests/functional/tracing-disabled/tests.ts",
    "packages/client/tests/functional/tracing-filtered-spans/tests.ts",
    "packages/client/tests/functional/tracing-no-sampling/tests.ts",
    "packages/client/tests/functional/tracing/tests.ts",
]

README_PATH = "packages/instrumentation/README.md"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """All modified TypeScript files exist and are non-empty."""
    for rel in TRACING_TEST_FILES + [README_PATH]:
        p = Path(REPO) / rel
        assert p.exists(), f"Missing file: {rel}"
        content = p.read_text()
        assert len(content) > 100, f"File too small (likely empty/corrupt): {rel}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code migration tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_resource_from_attributes_in_test_files():
    """All tracing test files must use resourceFromAttributes (OTel SDK v2)
    instead of new Resource (v1)."""
    for rel in TRACING_TEST_FILES:
        content = (Path(REPO) / rel).read_text()
        assert "resourceFromAttributes" in content, (
            f"{rel}: must use resourceFromAttributes (OTel v2), not new Resource"
        )
        assert "new Resource(" not in content, (
            f"{rel}: must not use deprecated new Resource() constructor"
        )


# [pr_diff] fail_to_pass
def test_semantic_conventions_v2_in_test_files():
    """Test files that previously used SEMRESATTRS_* must use ATTR_SERVICE_NAME
    and ATTR_SERVICE_VERSION (the OTel v2 semantic convention constants)."""
    # These two files specifically had the old SEMRESATTRS_ constants
    files_with_old_constants = [
        "packages/client/tests/functional/tracing-disabled/tests.ts",
        "packages/client/tests/functional/tracing-no-sampling/tests.ts",
    ]
    for rel in files_with_old_constants:
        content = (Path(REPO) / rel).read_text()
        assert "ATTR_SERVICE_NAME" in content, (
            f"{rel}: must use ATTR_SERVICE_NAME (v2), not SEMRESATTRS_SERVICE_NAME"
        )
        assert "ATTR_SERVICE_VERSION" in content, (
            f"{rel}: must use ATTR_SERVICE_VERSION (v2)"
        )
        assert "SEMRESATTRS_" not in content, (
            f"{rel}: must not contain deprecated SEMRESATTRS_ constants"
        )


# [pr_diff] fail_to_pass
def test_set_global_tracer_provider_in_test_files():
    """All tracing test files must use trace.setGlobalTracerProvider() (v2)
    instead of basicTracerProvider.register() (v1)."""
    for rel in TRACING_TEST_FILES:
        content = (Path(REPO) / rel).read_text()
        assert "setGlobalTracerProvider" in content, (
            f"{rel}: must use trace.setGlobalTracerProvider() (OTel v2 pattern)"
        )
        assert ".register()" not in content, (
            f"{rel}: must not use deprecated .register() method"
        )


# [pr_diff] fail_to_pass
def test_span_processors_constructor_option():
    """All tracing test files must pass spanProcessors in the BasicTracerProvider
    constructor options (v2) instead of calling addSpanProcessor (v1)."""
    for rel in TRACING_TEST_FILES:
        content = (Path(REPO) / rel).read_text()
        assert "spanProcessors" in content, (
            f"{rel}: must pass spanProcessors in BasicTracerProvider constructor"
        )
        assert "addSpanProcessor" not in content, (
            f"{rel}: must not call deprecated addSpanProcessor()"
        )


# [pr_diff] fail_to_pass
def test_parent_span_context_property():
    """tracing/tests.ts must use parentSpanContext?.spanId (v2)
    instead of parentSpanId (v1) for filtering root spans and building trees."""
    content = (Path(REPO) / "packages/client/tests/functional/tracing/tests.ts").read_text()
    assert "parentSpanContext" in content, (
        "tracing/tests.ts: must use parentSpanContext?.spanId (OTel SDK v2)"
    )
    # Ensure old pattern is gone — parentSpanId as a direct property access
    # (but not inside 'parentSpanContext' which contains it as substring)
    lines = content.split("\n")
    for line in lines:
        stripped = line.strip()
        if "parentSpanId" in stripped and "parentSpanContext" not in stripped:
            assert False, (
                f"tracing/tests.ts: still uses deprecated parentSpanId directly: {stripped}"
            )


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — README documentation update
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """Test files retain their full test logic (not stubbed out)."""
    content = (Path(REPO) / "packages/client/tests/functional/tracing/tests.ts").read_text()
    assert "BasicTracerProvider" in content, "tracing/tests.ts must create a BasicTracerProvider"
    assert "InMemorySpanExporter" in content, "tracing/tests.ts must use InMemorySpanExporter"
    assert "buildTree" in content, "tracing/tests.ts must have buildTree function"
    assert "getFinishedSpans" in content, "tracing/tests.ts must call getFinishedSpans"
    assert len(content.split("\n")) > 100, "tracing/tests.ts appears truncated"
