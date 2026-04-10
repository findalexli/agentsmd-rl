"""
Task: beam-iceberg-addfiles-manifest-batching
Repo: beam @ d6e04d11c64c70b30916a86303a6d3e3db746073
PR:   38096

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/beam"
ADDFILES = (
    f"{REPO}/sdks/java/io/iceberg/src/main/java"
    "/org/apache/beam/sdk/io/iceberg/AddFiles.java"
)
SCHEMA_TRANSFORM = (
    f"{REPO}/sdks/java/io/iceberg/src/main/java"
    "/org/apache/beam/sdk/io/iceberg/AddFilesSchemaTransformProvider.java"
)

_compile_result = None


def _ensure_compiled():
    """Run Gradle compilation once, caching the result across tests."""
    global _compile_result
    if _compile_result is not None:
        return _compile_result
    _compile_result = subprocess.run(
        [
            "./gradlew",
            ":sdks:java:io:iceberg:clean",
            ":sdks:java:io:iceberg:compileJava",
            "--no-daemon",
        ],
        cwd=REPO,
        capture_output=True,
        timeout=600,
    )
    return _compile_result


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — compilation check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_compilation():
    """Modified files must compile without errors."""
    r = _ensure_compiled()
    assert r.returncode == 0, (
        f"Compilation failed:\n{r.stderr.decode()[-3000:]}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — repo's CI/CD checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_spotbugs():
    """Repo's SpotBugs static analysis passes (pass_to_pass)."""
    r = subprocess.run(
        [
            "./gradlew",
            ":sdks:java:io:iceberg:spotbugsMain",
            "--no-daemon",
        ],
        cwd=REPO,
        capture_output=True,
        timeout=120,
    )
    assert r.returncode == 0, (
        f"SpotBugs analysis failed:\n{r.stderr.decode()[-500:]}"
    )


# [repo_tests] pass_to_pass
def test_repo_spotless():
    """Repo's Spotless code formatting check passes (pass_to_pass)."""
    r = subprocess.run(
        [
            "./gradlew",
            ":sdks:java:io:iceberg:spotlessCheck",
            "--no-daemon",
        ],
        cwd=REPO,
        capture_output=True,
        timeout=120,
    )
    assert r.returncode == 0, (
        f"Spotless check failed:\n{r.stderr.decode()[-500:]}"
    )


# [repo_tests] pass_to_pass
def test_repo_checkstyle():
    """Repo's Checkstyle validation passes (pass_to_pass)."""
    r = subprocess.run(
        [
            "./gradlew",
            ":sdks:java:io:iceberg:checkstyleMain",
            "--no-daemon",
        ],
        cwd=REPO,
        capture_output=True,
        timeout=120,
    )
    assert r.returncode == 0, (
        f"Checkstyle validation failed:\n{r.stderr.decode()[-500:]}"
    )



# [repo_tests] pass_to_pass
def test_repo_unit_tests():
    """Repo's unit tests for iceberg module pass (pass_to_pass)."""
    r = subprocess.run(
        [
            "./gradlew",
            ":sdks:java:io:iceberg:test",
            "--no-daemon",
        ],
        cwd=REPO,
        capture_output=True,
        timeout=600,
    )
    assert r.returncode == 0, (
        f"Unit tests failed:\n{r.stderr.decode()[-1000:]}"
    )


# [repo_tests] pass_to_pass
def test_repo_build():
    """Repo's Gradle build for iceberg module passes (pass_to_pass)."""
    r = subprocess.run(
        [
            "./gradlew",
            ":sdks:java:io:iceberg:build",
            "-PdisableSpotlessCheck=true",
            "-PdisableCheckStyle=true",
            "--no-daemon",
        ],
        cwd=REPO,
        capture_output=True,
        timeout=600,
    )
    assert r.returncode == 0, (
        f"Build failed:\n{r.stderr.decode()[-1000:]}"
    )


# [repo_tests] pass_to_pass
def test_repo_addfiles_unit_test():
    """Unit tests for AddFiles (modified class) pass (pass_to_pass)."""
    r = subprocess.run(
        [
            "./gradlew",
            ":sdks:java:io:iceberg:test",
            "--tests",
            "org.apache.beam.sdk.io.iceberg.AddFilesTest",
            "--no-daemon",
        ],
        cwd=REPO,
        capture_output=True,
        timeout=600,
    )
    assert r.returncode == 0, (
        f"AddFilesTest failed:\n{r.stderr.decode()[-1000:]}"
    )


# [repo_tests] pass_to_pass
def test_repo_schema_transform_unit_test():
    """Unit tests for IcebergWriteSchemaTransformProvider pass (pass_to_pass)."""
    r = subprocess.run(
        [
            "./gradlew",
            ":sdks:java:io:iceberg:test",
            "--tests",
            "org.apache.beam.sdk.io.iceberg.IcebergWriteSchemaTransformProviderTest",
            "--no-daemon",
        ],
        cwd=REPO,
        capture_output=True,
        timeout=600,
    )
    assert r.returncode == 0, (
        f"IcebergWriteSchemaTransformProviderTest failed:\n{r.stderr.decode()[-1000:]}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_manifest_creation_stage():
    """DataFiles must be batched into ManifestFiles before committing."""
    src = Path(ADDFILES).read_text()

    # Must use ManifestWriter to create manifest files
    assert "ManifestWriter" in src, (
        "Should use ManifestWriter to batch DataFiles into ManifestFiles"
    )
    # Must write manifests using the Iceberg API
    assert re.search(r"ManifestFiles\.write\(", src), (
        "Should call ManifestFiles.write() to create manifests"
    )
    # Must encode manifests for pipeline serialization between stages
    assert re.search(r"ManifestFiles\.encode\(", src), (
        "Should encode ManifestFiles for passing between pipeline stages"
    )

    # Also verify via compilation that a manifest-related inner class exists
    # Use clean build to ensure new inner classes are compiled (Gradle may skip
    # compilation if old .class files have newer timestamps than modified source)
    r = subprocess.run(
        [
            "./gradlew",
            ":sdks:java:io:iceberg:clean",
            ":sdks:java:io:iceberg:compileJava",
            "--no-daemon",
        ],
        cwd=REPO,
        capture_output=True,
        timeout=600,
    )
    assert r.returncode == 0, f"Compilation failed:\n{r.stderr.decode()[-3000:]}"

    build_dir = (
        Path(REPO)
        / "sdks/java/io/iceberg/build/classes/java/main"
        / "org/apache/beam/sdk/io/iceberg"
    )
    if build_dir.exists():
        # Use ?* pattern to match inner classes (the $ character doesn't work well with glob)
        class_files = [f.name for f in build_dir.glob("AddFiles?*.class") if f.name != "AddFiles.class"]
        has_manifest_class = any(
            "Manifest" in f or "Create" in f for f in class_files
        )
        assert has_manifest_class, (
            f"Expected a new inner class for manifest handling. "
            f"Found: {class_files}"
        )


# [pr_diff] fail_to_pass
def test_two_stage_batching():
    """Pipeline must use two GroupIntoBatches stages for data files and manifests."""
    src = Path(ADDFILES).read_text()

    # Count non-import GroupIntoBatches lines (base has 1 usage, fix needs 2+)
    lines = src.split("\n")
    gib_lines = [
        l for l in lines if "GroupIntoBatches" in l and "import " not in l
    ]
    assert len(gib_lines) >= 2, (
        f"Expected at least 2 GroupIntoBatches usages "
        f"(data files + manifests), found {len(gib_lines)}"
    )

    # Should use sharded keys for parallel data file batching
    assert "ShardedKey" in src, (
        "Should use ShardedKey for parallel data file batching"
    )

    # Static Void key must be gone
    assert "WithKeys.of((Void) null)" not in src, (
        "Static Void key should be replaced with a meaningful grouping key"
    )


# [pr_diff] fail_to_pass
def test_commit_uses_append_manifest():
    """Commit step must use appendManifest() instead of individual appendFile() calls."""
    src = Path(ADDFILES).read_text()

    # Must call appendManifest for bulk loading (not present in base commit)
    assert re.search(r"\.appendManifest\(", src), (
        "Should call appendManifest() for bulk manifest commits"
    )

    # Must decode ManifestFiles from serialized form before committing
    assert re.search(r"ManifestFiles\.decode\(", src), (
        "Should decode ManifestFiles before committing"
    )


# [pr_diff] fail_to_pass
def test_bucket_partition_removed():
    """Bucket partition validation must be removed (matches Spark behavior)."""
    src = Path(ADDFILES).read_text()

    assert "bucketPartitions" not in src, (
        "Bucket partition map should be removed"
    )
    assert "bucket[" not in src, (
        "Bucket transform detection code should be removed"
    )
    assert "ACTIVE_READERS" not in src, (
        "Semaphore-gated reader pool should be removed"
    )
    assert "CloseableIterable<Record>" not in src, (
        "File content reading for bucket validation should be removed"
    )


# [pr_diff] fail_to_pass
def test_schema_manifest_param():
    """Schema transform parameter must be updated from appendBatchSize."""
    src = Path(SCHEMA_TRANSFORM).read_text()

    # Old parameter name must be gone
    assert "AppendBatchSize" not in src, (
        "Old AppendBatchSize parameter should be renamed"
    )
    assert "appendBatchSize" not in src, (
        "Old appendBatchSize reference should be updated"
    )
