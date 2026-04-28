#!/usr/bin/env bash
set -euo pipefail

cd /workspace/lance

# Idempotency guard
if grep -qF "4. **Indexing**: Supports both vector indices (for similarity search) and scalar" "AGENTS.md" && grep -qF "CLAUDE.md" "CLAUDE.md" && grep -qF "CLAUDE.md" "CLAUDE.md" && grep -qF "format: `./mvnw spotless:apply && cargo fmt --manifest-path ./lance-jni/Cargo.to" "java/AGENTS.md" && grep -qF "java/CLAUDE.md" "java/CLAUDE.md" && grep -qF "java/CLAUDE.md" "java/CLAUDE.md" && grep -qF "All changes should be backwards compatible. Don't re-use field numbers of change" "protos/AGENTS.md" && grep -qF "protos/CLAUDE.md" "protos/CLAUDE.md" && grep -qF "protos/CLAUDE.md" "protos/CLAUDE.md" && grep -qF "* Run single test: `pytest python/tests/<test_file>.py::<test_name>`" "python/AGENTS.md" && grep -qF "python/CLAUDE.md" "python/CLAUDE.md" && grep -qF "python/CLAUDE.md" "python/CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -0,0 +1,127 @@
+# AGENTS.md
+
+This file provides guidance to coding agents collaborating on this repository.
+
+## Project Overview
+
+Lance is a modern columnar data format optimized for ML workflows and datasets. It provides:
+
+- High-performance random access
+- Vector search
+- Zero-copy, automatic versioning
+- Ecosystem integrations
+
+## Project Vision
+
+The de facto standard columnar data format for machine learning and large language models.
+
+## Project Requirements
+
+- Always use English in code, examples, and comments.
+- Features should be implemented concisely, maintainably, and efficiently.
+- Code is not just for execution, but also for readability.
+- Only add meaingful comments and tests.
+
+## Architecture
+
+The project is organized as a Rust workspace with Python and Java bindings:
+
+- `rust/lance/` - Main Lance library implementing the columnar format
+- `rust/lance-arrow/` - Apache Arrow integration layer
+- `rust/lance-core/` - Core types, traits, and utilities
+- `rust/lance-encoding/` - Data encoding and compression algorithms
+- `rust/lance-file/` - File format reading/writing
+- `rust/lance-index/` - Vector and scalar indexing implementations
+- `rust/lance-io/` - I/O operations and object store integration
+- `rust/lance-linalg/` - Linear algebra operations for vector search
+- `rust/lance-table/` - Table format and operations
+- `rust/lance-datafusion/` - DataFusion query engine integration
+- `python/` - Python bindings using PyO3/maturin
+- `java/` - Java bindings using JNI
+
+## Common Development Commands
+
+### Rust Development
+
+* Check for build errors: `cargo check --all --tests --benches`
+* Run tests: `cargo test`
+* Run specific test: `cargo test -p <package> <test_name>`
+* Lint: `cargo clippy --all --tests --benches -- -D warnings`
+* Format: `cargo fmt --all`
+
+### Python Development
+
+Use the makefile for most actions:
+
+* Build: `maturin develop`
+* Test: `make test`
+* Run single test: `pytest python/tests/<test_file>.py::<test_name>`
+* Doctest: `make doctest`
+* Lint: `make lint`
+* Format: `make format`
+
+### Integration Testing
+
+```bash
+# Start required services
+cd test_data && docker compose up -d
+
+# Run S3/DynamoDB tests
+AWS_DEFAULT_REGION=us-east-1 pytest --run-integration python/tests/test_s3_ddb.py
+
+# Performance profiling
+maturin develop --release -m python/Cargo.toml -E benchmarks
+python python/benchmarks/test_knn.py --iterations 100
+```
+
+## Key Technical Details
+
+1. **Async-first Architecture**: Heavy use of tokio and async/await throughout Rust codebase
+2. **Arrow-native**: All data operations work directly with Apache Arrow arrays
+3. **Version Control**: Every write creates a new version with manifest tracking
+4. **Indexing**: Supports both vector indices (for similarity search) and scalar indices (BTree, inverted)
+5. **Encoding**: Custom encodings optimized for ML data patterns
+6. **Object Store**: Unified interface for local, S3, Azure, GCS storage
+
+## Development Notes
+
+- All public APIs should have comprehensive documentation with examples
+- Performance-critical code uses SIMD optimizations where available
+- Always rebuild Python extension after Rust changes using `maturin develop`
+- Integration tests require Docker for local S3/DynamoDB emulation
+- Use feature flags to control dependencies (e.g., `datafusion` for SQL support)
+
+## Development tips
+
+Code standards:
+* Be mindful of memory use:
+  * When dealing with streams of `RecordBatch`, avoid collecting all data into
+    memory whenever possible.
+  * Use `RoaringBitmap` instead `HashSet<u32>`.
+
+Tests:
+* When writing unit tests, prefer using the `memory://` URI instead of creating
+  a temporary directory.
+* Use rstest to generate parameterized tests to cover more cases with fewer lines
+  of code.
+    * Use syntax `#[case::{name}(...)]` to provide human-readable names for each case.
+* For backwards compatibility, use the `test_data` directory to check in datasets
+  written with older library version.
+    * Check in a `datagen.py` that creates the test data. It should assert the
+      version of Lance used as part of the script.
+    * Use `pip install pylance=={version}` and then run `python datagen.py` to
+      create the dataset. The data files should be checked into git.
+    * Use `copy_test_data_to_tmp` to read this data in Lance
+* Avoid using `ignore` in doctests. For APIs with complex inputs, like methods on
+  `Dataset`, instead write Rust doctests that just compile a function. This
+  guarantees that the example code compiles and is in sync with the API. For example:
+
+  ```
+  /// ```
+  /// # use lance::{Dataset, Result};
+  /// # async fn test(dataset: &Dataset) -> Result<()> {
+  /// dataset.delete("id = 25").await?;
+  /// # Ok(())
+  /// # }
+  /// ```
+  ```
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -1,127 +0,0 @@
-# CLAUDE.md
-
-This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
-
-## Project Overview
-
-Lance is a modern columnar data format optimized for ML workflows and datasets. It provides:
-
-- High-performance random access
-- Vector search
-- Zero-copy, automatic versioning
-- Ecosystem integrations
-
-## Project Vision
-
-The de facto standard columnar data format for machine learning and large language models.
-
-## Project Requirements
-
-- Always use English in code, examples, and comments.
-- Features should be implemented concisely, maintainably, and efficiently.
-- Code is not just for execution, but also for readability.
-- Only add meaingful comments and tests.
-
-## Architecture
-
-The project is organized as a Rust workspace with Python and Java bindings:
-
-- `rust/lance/` - Main Lance library implementing the columnar format
-- `rust/lance-arrow/` - Apache Arrow integration layer
-- `rust/lance-core/` - Core types, traits, and utilities
-- `rust/lance-encoding/` - Data encoding and compression algorithms
-- `rust/lance-file/` - File format reading/writing
-- `rust/lance-index/` - Vector and scalar indexing implementations
-- `rust/lance-io/` - I/O operations and object store integration
-- `rust/lance-linalg/` - Linear algebra operations for vector search
-- `rust/lance-table/` - Table format and operations
-- `rust/lance-datafusion/` - DataFusion query engine integration
-- `python/` - Python bindings using PyO3/maturin
-- `java/` - Java bindings using JNI
-
-## Common Development Commands
-
-### Rust Development
-
-* Check for build errors: `cargo check --all --tests --benches`
-* Run tests: `cargo test`
-* Run specific test: `cargo test -p <package> <test_name>`
-* Lint: `cargo clippy --all --tests --benches -- -D warnings`
-* Format: `cargo fmt --all`
-
-### Python Development
-
-Use the makefile for most actions:
-
-* Build: `maturin develop`
-* Test: `make test`
-* Run single test: `pytest python/tests/<test_file>.py::<test_name>`
-* Doctest: `make doctest`
-* Lint: `make lint`
-* Format: `make format`
-
-### Integration Testing
-
-```bash
-# Start required services
-cd test_data && docker compose up -d
-
-# Run S3/DynamoDB tests
-AWS_DEFAULT_REGION=us-east-1 pytest --run-integration python/tests/test_s3_ddb.py
-
-# Performance profiling
-maturin develop --release -m python/Cargo.toml -E benchmarks
-python python/benchmarks/test_knn.py --iterations 100
-```
-
-## Key Technical Details
-
-1. **Async-first Architecture**: Heavy use of tokio and async/await throughout Rust codebase
-2. **Arrow-native**: All data operations work directly with Apache Arrow arrays
-3. **Version Control**: Every write creates a new version with manifest tracking
-4. **Indexing**: Supports both vector indices (for similarity search) and scalar indices (BTree, inverted)
-5. **Encoding**: Custom encodings optimized for ML data patterns
-6. **Object Store**: Unified interface for local, S3, Azure, GCS storage
-
-## Development Notes
-
-- All public APIs should have comprehensive documentation with examples
-- Performance-critical code uses SIMD optimizations where available
-- Always rebuild Python extension after Rust changes using `maturin develop`
-- Integration tests require Docker for local S3/DynamoDB emulation
-- Use feature flags to control dependencies (e.g., `datafusion` for SQL support)
-
-## Development tips
-
-Code standards:
-* Be mindful of memory use:
-  * When dealing with streams of `RecordBatch`, avoid collecting all data into
-    memory whenever possible.
-  * Use `RoaringBitmap` instead `HashSet<u32>`.
-
-Tests:
-* When writing unit tests, prefer using the `memory://` URI instead of creating
-  a temporary directory.
-* Use rstest to generate parameterized tests to cover more cases with fewer lines
-  of code.
-    * Use syntax `#[case::{name}(...)]` to provide human-readable names for each case.
-* For backwards compatibility, use the `test_data` directory to check in datasets
-  written with older library version.
-    * Check in a `datagen.py` that creates the test data. It should assert the
-      version of Lance used as part of the script.
-    * Use `pip install pylance=={version}` and then run `python datagen.py` to
-      create the dataset. The data files should be checked into git.
-    * Use `copy_test_data_to_tmp` to read this data in Lance
-* Avoid using `ignore` in doctests. For APIs with complex inputs, like methods on
-  `Dataset`, instead write Rust doctests that just compile a function. This
-  guarantees that the example code compiles and is in sync with the API. For example:
-
-  ```
-  /// ```
-  /// # use lance::{Dataset, Result};
-  /// # async fn test(dataset: &Dataset) -> Result<()> {
-  /// dataset.delete("id = 25").await?;
-  /// # Ok(())
-  /// # }
-  /// ```
-  ```
\ No newline at end of file
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -0,0 +1 @@
+AGENTS.md
\ No newline at end of file
diff --git a/java/AGENTS.md b/java/AGENTS.md
@@ -0,0 +1,10 @@
+## Structure
+Java code: `core/src`
+Rust JNI bindings: `lance-jni`
+
+## Commands
+Use `./mvnw` instead of `mvn` to ensure the correct version of Maven is used.
+format: `./mvnw spotless:apply && cargo fmt --manifest-path ./lance-jni/Cargo.toml --all`
+lint rust: `cargo clippy --tests --manifest-path ./lance-jni/Cargo.toml`
+compile: `./mvnw compile`
+test: `./mvnw test`
diff --git a/java/CLAUDE.md b/java/CLAUDE.md
@@ -1,10 +0,0 @@
-## Structure
-Java code: `core/src`
-Rust JNI bindings: `lance-jni`
-
-## Commands
-Use `./mvnw` instead of `mvn` to ensure the correct version of Maven is used.
-format: `./mvnw spotless:apply && cargo fmt --manifest-path ./lance-jni/Cargo.toml --all`
-lint rust: `cargo clippy --tests --manifest-path ./lance-jni/Cargo.toml`
-compile: `./mvnw compile`
-test: `./mvnw test`
diff --git a/java/CLAUDE.md b/java/CLAUDE.md
@@ -0,0 +1 @@
+AGENTS.md
\ No newline at end of file
diff --git a/protos/AGENTS.md b/protos/AGENTS.md
@@ -0,0 +1,2 @@
+All changes should be backwards compatible. Don't re-use field numbers of change
+field numbers of existing fields.
\ No newline at end of file
diff --git a/protos/CLAUDE.md b/protos/CLAUDE.md
@@ -1,2 +0,0 @@
-All changes should be backwards compatible. Don't re-use field numbers of change
-field numbers of existing fields.
\ No newline at end of file
diff --git a/protos/CLAUDE.md b/protos/CLAUDE.md
@@ -0,0 +1 @@
+AGENTS.md
\ No newline at end of file
diff --git a/python/AGENTS.md b/python/AGENTS.md
@@ -0,0 +1,8 @@
+Use the makefile for most actions:
+
+* Build: `maturin develop`
+* Test: `make test`
+* Run single test: `pytest python/tests/<test_file>.py::<test_name>`
+* Doctest: `make doctest`
+* Lint: `make lint`
+* Format: `make format`
diff --git a/python/CLAUDE.md b/python/CLAUDE.md
@@ -1,8 +0,0 @@
-Use the makefile for most actions:
-
-* Build: `maturin develop`
-* Test: `make test`
-* Run single test: `pytest python/tests/<test_file>.py::<test_name>`
-* Doctest: `make doctest`
-* Lint: `make lint`
-* Format: `make format`
diff --git a/python/CLAUDE.md b/python/CLAUDE.md
@@ -0,0 +1 @@
+AGENTS.md
\ No newline at end of file
PATCH

echo "Gold patch applied."
