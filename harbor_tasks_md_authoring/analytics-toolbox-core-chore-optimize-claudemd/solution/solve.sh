#!/usr/bin/env bash
set -euo pipefail

cd /workspace/analytics-toolbox-core

# Idempotency guard
if grep -qF "- Modules: h3, quadbin, s2, placekey, constructors, transformations, processing," ".claude/rules/bigquery.md" && grep -qF "When passing file lists through Make targets, **proper quoting is critical** to " ".claude/rules/ci-cd.md" && grep -qF "- **JavaScript**: `clouds/{cloud}/common/test-utils.js` \u2014 provides `runQuery()`," ".claude/rules/cloud-sql-testing.md" && grep -qF "Create a `.env` file in `clouds/databricks/` (template: `clouds/databricks/.env." ".claude/rules/databricks.md" && grep -qF "The gateway uses a registry pattern for cloud-specific type mappings, allowing n" ".claude/rules/extending-clouds.md" && grep -qF "Place reusable code in `gateway/functions/_shared/python/<lib_name>/` and refere" ".claude/rules/function-dev.md" && grep -qF "Core's packaging system supports extensibility through a **try/except import pat" ".claude/rules/gateway.md" && grep -qF "**Note**: Oracle uses wallet-based authentication, unique among all supported cl" ".claude/rules/oracle.md" && grep -qF "**IMPORTANT**: The `--non-interactive` flag is **required** to skip all prompts." ".claude/rules/packaging.md" && grep -qF "- Modules: h3, quadbin, s2, placekey, constructors, transformations, processing," ".claude/rules/postgres.md" && grep -qF "- Modules: h3, quadbin, s2, placekey, constructors, transformations, processing," ".claude/rules/redshift.md" && grep -qF "- Modules: h3, quadbin, s2, placekey, constructors, transformations, processing," ".claude/rules/snowflake.md" && grep -qF "> This rule covers **gateway-specific** testing (Lambda handlers, Python unit/in" ".claude/rules/testing.md" && grep -qF "- `.github/workflows/publish-release.yml` detects which version files changed to" ".claude/rules/versioning.md" && grep -qF "Cloud-specific configuration, gateway architecture, testing, function developmen" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/rules/bigquery.md b/.claude/rules/bigquery.md
@@ -0,0 +1,41 @@
+---
+paths:
+  - "clouds/bigquery/**"
+---
+
+# BigQuery
+
+## Configuration
+
+Create a `.env` file in `clouds/bigquery/` (template: `clouds/bigquery/.env.template`):
+
+```bash
+BQ_PROJECT=<project>             # GCP project ID
+BQ_BUCKET=gs://<bucket>          # GCS bucket for staging
+BQ_REGION=<region>               # GCP region
+GOOGLE_APPLICATION_CREDENTIALS=<path> # Path to service account JSON
+BQ_PREFIX=<prefix>               # Optional schema prefix
+BQ_ENDPOINT=<url>                # Optional AT Gateway Cloud Run service URL
+BQ_CONNECTION=<connection>       # Optional BQ connection for remote functions
+BQ_API_BASE_URL=<url>            # Optional CARTO API base URL
+BQ_API_ACCESS_TOKEN=<token>      # Optional CARTO API access token
+BQ_PERMISSIONS=<permissions>     # Optional permissions to grant
+```
+
+## Commands
+
+```bash
+cd clouds/bigquery
+make deploy   # deploy modules
+make test     # run tests (Jest)
+make build    # build JS libraries + SQL modules
+```
+
+## Key Details
+
+- Uses JavaScript libraries (built with `build_modules.js`) and Jest for testing
+- The tiler module requires emscripten (`emcc` 2.0.13)
+- JS libraries: `clouds/bigquery/libraries/javascript/`
+- Test/build utilities: `clouds/bigquery/common/`
+- Schema placeholder: `@@BQ_DATASET@@`, `@@BQ_PREFIX@@`
+- Modules: h3, quadbin, s2, placekey, constructors, transformations, processing, clustering, random
diff --git a/.claude/rules/ci-cd.md b/.claude/rules/ci-cd.md
@@ -0,0 +1,100 @@
+---
+paths:
+  - ".github/**"
+---
+
+# CI/CD
+
+## CI Naming
+
+For CI/CD environments, use short prefixes to avoid AWS naming limits:
+- Pattern: `ci_{8-char-sha}_{6-digit-run-id}_`
+- Example: `ci_a1b2c3d4_123456_getisord`
+- Total length: <=64 characters
+
+## Workflows
+
+Each cloud has its own CI/CD workflows in `.github/workflows/`:
+
+| Cloud | Main Workflow | Dedicated Env |
+|-------|--------------|---------------|
+| BigQuery | `bigquery.yml` | `bigquery-ded.yml` |
+| Snowflake | `snowflake.yml` | `snowflake-ded.yml` |
+| Redshift | `redshift.yml` | `redshift-ded.yml` |
+| Databricks | `databricks.yml` | - |
+| Postgres | `postgres.yml` | `postgres-ded.yml` |
+| Oracle | `oracle.yml` | `oracle-ded.yml` |
+
+- **Main workflows**: Triggered on PRs and pushes to main. Run lint, deploy to CI env, test, cleanup.
+- **Dedicated (`-ded`) workflows**: PR-triggered, deploy to isolated environment for testing.
+- **Publish**: Triggered by `publish-release.yml` on push to `stable`. Creates GitHub Release, publishes packages to GCS, deploys to production.
+
+## Diff Parameter Handling in Makefiles
+
+When passing file lists through Make targets, **proper quoting is critical** to prevent Make from interpreting space-separated filenames as multiple targets.
+
+### Problem
+
+```makefile
+# WRONG - Each filename becomes a separate target
+$(if $(diff),diff=$(diff),)
+
+# If diff=".github/workflows/redshift.yml Makefile README.md"
+# Make interprets this as three separate targets and fails with:
+# make: *** No rule to make target '.github/workflows/redshift.yml'
+```
+
+### Solution
+
+```makefile
+# CORRECT - Entire string passed as single quoted value
+$(if $(diff),diff='$(diff)',)
+
+# Properly passes: diff='.github/workflows/redshift.yml Makefile README.md'
+```
+
+### Where This Matters
+
+1. **Core Root Makefile** (`Makefile`, line 148):
+   ```makefile
+   cd gateway && $(MAKE) deploy cloud=$(cloud) \
+       $(if $(diff),diff='$(diff)',)
+   ```
+
+2. **Gateway Makefile** (`gateway/Makefile`, lines 154, 163):
+   ```makefile
+   # Converts to boolean flag (not the value)
+   $(if $(diff),--diff,)
+   ```
+
+### Architecture Flow
+
+```
+CI Workflow / External Caller
+  | diff="file1 file2 file3"
+Core Root Makefile
+  | diff='$(diff)' (quoted!)
+Gateway Makefile
+  | --diff (flag only)
+Python CLI (gateway/logic/clouds/redshift/cli.py)
+  | reads $GIT_DIFF from environment
+  | detects infrastructure changes
+  | decides: deploy ALL or deploy CHANGED
+```
+
+### Infrastructure Change Detection
+
+The Python CLI automatically detects infrastructure changes and deploys all functions when these paths are modified:
+- `.github/workflows/` - CI/CD configuration
+- `Makefile` - Build system changes
+- `logic/` - Deployment logic changes
+- `platforms/` - Platform code changes
+- `requirements.txt` - Dependency changes
+
+### Key Points
+
+- Root Makefile must quote: `diff='$(diff)'`
+- Gateway Makefile uses flag: `--diff` (no value)
+- Python CLI reads `$GIT_DIFF` environment variable directly
+- Infrastructure files trigger full deployment automatically
+- Clouds Makefiles don't use diff (always deploy all SQL UDFs)
diff --git a/.claude/rules/cloud-sql-testing.md b/.claude/rules/cloud-sql-testing.md
@@ -0,0 +1,54 @@
+---
+paths:
+  - "clouds/**/test/**"
+---
+
+# Cloud SQL Testing
+
+## Test Frameworks by Cloud
+
+- **pytest**: Oracle, Redshift, Databricks, Postgres — test files named `test_FUNCTION_NAME.py`
+- **Jest**: BigQuery, Snowflake — test files named `FUNCTION_NAME.test.js`
+
+## Test File Location
+
+`clouds/{cloud}/modules/test/{module}/test_FUNCTION.py` (or `.test.js`)
+
+## Running Tests
+
+```bash
+cd clouds/{cloud}
+make test                        # all tests
+make test modules=h3             # specific module
+make test functions=H3_POLYFILL  # specific function
+```
+
+## Test Utilities
+
+Each cloud has its own test utilities for database connectivity:
+
+- **Python**: `clouds/{cloud}/common/test_utils/__init__.py` — provides `run_query()`, `run_queries()`, `get_cursor()`
+- **JavaScript**: `clouds/{cloud}/common/test-utils.js` — provides `runQuery()`, `loadTable()`, `deleteTable()`, `readJSONFixture()`
+
+## Schema Placeholders
+
+Tests use `@@SCHEMA@@` placeholders replaced at runtime:
+
+- `@@RS_SCHEMA@@` (Redshift)
+- `@@ORA_SCHEMA@@` (Oracle)
+- `@@BQ_DATASET@@` (BigQuery)
+- `@@BQ_PREFIX@@` (BigQuery)
+
+## Fixtures
+
+Located in `test/{module}/fixtures/`:
+
+- `.txt` files (Oracle, Redshift) — line-by-line expected output
+- `.json` / `.ndjson` / `.csv` files (BigQuery) — structured test data
+
+## Testing Best Practices
+
+- Test values should match canonical outputs from the reference cloud (Databricks for Quadbin, BigQuery for H3)
+- Geometry tolerance: 1e-6 for floating-point coordinate comparison
+- JSON array results: sort before comparison
+- NULL input should always return NULL
diff --git a/.claude/rules/databricks.md b/.claude/rules/databricks.md
@@ -0,0 +1,38 @@
+---
+paths:
+  - "clouds/databricks/**"
+---
+
+# Databricks
+
+## Configuration
+
+Create a `.env` file in `clouds/databricks/` (template: `clouds/databricks/.env.template`):
+
+```bash
+DB_PREFIX=yourname_            # Schema prefix (e.g., "yourname_" -> "yourname_carto")
+DB_CATALOG=<catalog>           # Databricks catalog name
+DB_HOST_NAME=<hostname>        # SQL Warehouse hostname
+DB_HTTP_PATH=<path>            # SQL Warehouse HTTP path
+DB_TOKEN=<token>               # Access token
+DB_CONNECTION=<connection>     # Databricks connection string
+DB_API_BASE_URL=<url>          # CARTO API base URL
+DB_API_ACCESS_TOKEN=<token>    # CARTO API access token
+```
+
+## Commands
+
+```bash
+cd clouds/databricks
+make deploy                    # Deploy SQL UDFs
+make test                      # Run all tests (pytest)
+make test modules=quadbin      # Run tests for specific module
+make build-modules             # Build module packages
+```
+
+## Key Details
+
+- Native SQL UDFs only (no gateway/Lambda)
+- `quadbin` module migrated March 2026 (20 SQL functions)
+- Deploy scripts in `clouds/databricks/common/`: `run_query.py`, `create_schema.py`
+- Schema creation runs automatically during deploy
diff --git a/.claude/rules/extending-clouds.md b/.claude/rules/extending-clouds.md
@@ -0,0 +1,120 @@
+---
+paths:
+  - "gateway/logic/**"
+---
+
+# Extending Cloud Support
+
+The gateway uses a registry pattern for cloud-specific type mappings, allowing new clouds to be added without modifying core code.
+
+## Type Mapping Architecture
+
+**TypeMapperRegistry** (`gateway/logic/common/engine/type_mapper.py`):
+- Cloud-agnostic registry maintaining type mapping providers
+- Each cloud registers its own TypeMappingProvider implementation
+- Provides unified interface: `TypeMapperRegistry.map_type("string", "redshift")` -> `"VARCHAR(MAX)"`
+
+## Adding a New Cloud
+
+To add support for a new cloud (e.g., BigQuery, Snowflake):
+
+### 1. Create cloud-specific type mappings
+
+```python
+# gateway/logic/clouds/bigquery/type_mappings.py
+from ...common.engine.type_mapper import TypeMapperRegistry
+
+class BigQueryTypeMappings:
+    """BigQuery-specific type mapping provider"""
+
+    TYPE_MAPPINGS = {
+        "string": "STRING",
+        "int": "INT64",
+        "bigint": "INT64",
+        "float": "FLOAT64",
+        "double": "FLOAT64",
+        "boolean": "BOOL",
+        "bytes": "BYTES",
+        "object": "JSON",
+        "geometry": "GEOGRAPHY",  # BigQuery uses GEOGRAPHY for spatial
+        "geography": "GEOGRAPHY",
+    }
+
+    def map_type(self, generic_type: str) -> str:
+        """Map generic type to BigQuery SQL type"""
+        generic_lower = generic_type.lower()
+        if generic_lower in self.TYPE_MAPPINGS:
+            return self.TYPE_MAPPINGS[generic_lower]
+        return generic_type  # Already cloud-specific
+
+    def is_generic_type(self, type_str: str) -> bool:
+        """Check if type is generic"""
+        return type_str.lower() in self.TYPE_MAPPINGS
+
+    def get_supported_generic_types(self) -> list[str]:
+        """Get supported generic types"""
+        return list(self.TYPE_MAPPINGS.keys())
+
+# Auto-register when module is imported
+_bigquery_mapper = BigQueryTypeMappings()
+TypeMapperRegistry.register("bigquery", _bigquery_mapper)
+```
+
+### 2. Update CloudType enum
+
+```python
+# gateway/logic/common/engine/models.py
+class CloudType(Enum):
+    """Supported cloud platforms"""
+    REDSHIFT = "redshift"
+    BIGQUERY = "bigquery"  # Add new cloud
+```
+
+### 3. Import the mapping in your cloud CLI
+
+```python
+# gateway/logic/clouds/bigquery/cli.py
+from .type_mappings import BigQueryTypeMappings  # Triggers auto-registration
+```
+
+### 4. Implement cloud-specific deployment logic
+
+- SQL template generator (like `RedshiftSQLTemplateGenerator`)
+- Template renderer for cloud-specific SQL syntax
+- CLI commands for deployment
+- Pre-flight checks and validation
+
+## Current Implementation
+
+**Redshift** (`gateway/logic/clouds/redshift/type_mappings.py`):
+- Implements `RedshiftTypeMappings` class
+- Maps generic types to Redshift SQL types (VARCHAR(MAX), INT8, SUPER, etc.)
+- Auto-registers on import via `TypeMapperRegistry.register("redshift", ...)`
+
+## Future Development Guidelines
+
+**When adding new functions:**
+
+1. Determine if code should be shared or function-specific
+2. Use shared library only if used by 2+ functions
+3. Keep lambda_name <=18 characters
+4. Add comprehensive unit tests
+5. Use generic types in function.yaml when possible
+6. Follow existing handler patterns
+7. Build and test before committing
+
+**When modifying shared libraries:**
+
+1. Consider impact on all dependent functions
+2. Run tests for all dependent functions
+3. Avoid breaking changes
+4. Update shared library documentation
+5. Rebuild all dependent functions
+
+**When refactoring:**
+
+1. Maintain backward compatibility
+2. Keep function signatures unchanged
+3. Update tests to match changes
+4. Verify deployment after refactoring
+5. Document architectural decisions
diff --git a/.claude/rules/function-dev.md b/.claude/rules/function-dev.md
@@ -0,0 +1,291 @@
+---
+paths:
+  - "**/function.yaml"
+  - "**/functions/**"
+---
+
+# Function Development
+
+## Gateway Functions (Lambda-based)
+
+### Directory Structure
+
+```
+gateway/functions/<module>/<function_name>/
+├── function.yaml              # Function metadata
+├── code/
+│   ├── lambda/python/
+│   │   ├── handler.py         # Lambda handler
+│   │   └── requirements.txt   # Python dependencies
+│   └── redshift.sql           # External function SQL template
+└── tests/
+    ├── unit/
+    │   ├── cases.yaml         # Simple test cases
+    │   └── test_*.py          # Complex test scenarios
+    └── integration/
+        └── test_*.py          # Integration tests
+```
+
+## function.yaml Complete Reference
+
+```yaml
+# Optional: name and module are inferred from directory structure
+# Only include if function name differs from folder name
+name: function_name
+module: module_name
+
+# Generic type definitions (hybrid functions)
+parameters:
+  - name: input_data
+    type: string                    # Generic type (maps to VARCHAR(MAX))
+  - name: size
+    type: int                       # Generic type (maps to INT)
+returns: string                     # Return type
+
+clouds:
+  redshift:
+    type: lambda                    # Platform type
+    lambda_name: shortname          # <=18 chars (with prefix)
+    code_file: code/lambda/python/handler.py
+    requirements_file: code/lambda/python/requirements.txt  # Optional
+    external_function_template: code/redshift.sql  # Optional (auto-generated if omitted)
+    shared_libs:                    # Optional - list of _shared/python/ modules
+      - statistics
+      - tiler
+    # Cloud-specific parameter type overrides (optional)
+    parameters:
+      - name: data
+        type: SUPER                 # Redshift-specific type
+    returns: SUPER
+    config:
+      memory_size: 512              # MB (128-10240, default 512)
+      timeout: 300                  # Seconds (3-900, default 300)
+      max_batch_rows: 100           # Batch size (default 100)
+      runtime: python3.10           # Python runtime
+```
+
+### Function Naming Convention
+
+**Function name and module are automatically inferred from directory structure:**
+
+```
+functions/
+  <module>/
+    <function_name>/
+      function.yaml
+```
+
+- **Function name**: From directory name (e.g., `s2_fromtoken`)
+- **Module**: From parent directory name (e.g., `s2`)
+- **SQL function name**: Uppercase version (e.g., `S2_FROMTOKEN`)
+
+**Important**: Do NOT include `name` or `module` fields in `function.yaml` unless the function name needs to differ from the folder name.
+
+## Hybrid Function Definitions (Auto-Generated SQL)
+
+For simple functions, you can eliminate the SQL template file entirely. The system auto-generates SQL from function metadata.
+
+### Key Features
+
+- **Convention over configuration**: Function name and module inferred from directory structure
+- **Generic type mapping**: Define parameters once with generic types (`string`, `int`, `bigint`, etc.)
+- **Cloud-specific overrides**: Override types for specific clouds when needed (e.g., Redshift's `SUPER`)
+- **Automatic SQL generation**: SQL templates generated automatically from metadata
+- **Backward compatible**: Existing functions with SQL templates continue to work
+
+### Pattern 1: Simple Function with Generic Types
+
+For straightforward functions, define parameters and return type at the top level. **No SQL file needed!**
+
+```yaml
+# No 'name' or 'module' fields - inferred from directory structure
+# Function: functions/s2/s2_fromtoken/
+
+parameters:
+  - name: token
+    type: string      # Maps to VARCHAR(MAX) in Redshift
+returns: bigint       # Maps to INT8 in Redshift
+
+clouds:
+  redshift:
+    type: lambda
+    lambda_name: s2_ftok
+    code_file: code/lambda/python/handler.py
+    # NO external_function_template needed!
+    config:
+      max_batch_rows: 10000
+```
+
+**Generated SQL (Redshift):**
+
+```sql
+CREATE OR REPLACE EXTERNAL FUNCTION @@SCHEMA@@.S2_FROMTOKEN(
+    token VARCHAR(MAX)
+)
+RETURNS INT8
+STABLE
+LAMBDA '@@LAMBDA_ARN@@'
+IAM_ROLE '@@IAM_ROLE_ARN@@'
+MAX_BATCH_ROWS 10000;
+```
+
+### Pattern 2: Cloud-Specific Type Overrides
+
+For functions that need cloud-specific types (e.g., Redshift's `SUPER`), define types under the cloud section:
+
+```yaml
+# Function: functions/statistics/getis_ord_quadbin/
+
+clouds:
+  redshift:
+    type: lambda
+    lambda_name: getisord
+    code_file: code/lambda/python/handler.py
+    shared_libs:
+      - statistics
+    # Cloud-specific parameter types
+    parameters:
+      - name: data
+        type: SUPER        # Redshift-specific type
+      - name: k_neighbors
+        type: INT
+    returns: SUPER
+    config:
+      memory_size: 1024
+      max_batch_rows: 50
+```
+
+### Pattern 3: Hybrid (Generic + Cloud-Specific Overrides)
+
+Define generic types at top level for most clouds, then override specific clouds:
+
+```yaml
+# Generic types for most clouds
+parameters:
+  - name: input_data
+    type: object      # Maps to SUPER, JSON, VARIANT, etc.
+  - name: value
+    type: float
+returns: object
+
+clouds:
+  redshift:
+    type: lambda
+    lambda_name: ex_hybrid
+    code_file: code/lambda/python/handler.py
+    # Override for Redshift (use SUPER instead of generic object)
+    parameters:
+      - name: input_data
+        type: SUPER
+      - name: value
+        type: float
+    returns: SUPER
+
+  bigquery:
+    type: cloud_run
+    # Uses generic types (object -> JSON, float -> FLOAT64)
+    code_file: code/cloud_run/main.py
+```
+
+### Pattern 4: Legacy (SQL Template)
+
+Existing functions with SQL templates continue to work unchanged:
+
+```yaml
+name: example_legacy
+module: example
+
+clouds:
+  redshift:
+    type: lambda
+    lambda_name: ex_legacy
+    code_file: code/lambda/python/handler.py
+    external_function_template: code/redshift.sql  # Uses existing template
+```
+
+## Generic Type Mapping
+
+| Generic Type | Redshift | BigQuery | Snowflake | Databricks | Postgres |
+|-------------|----------|----------|-----------|------------|----------|
+| `string` | `VARCHAR(MAX)` | `STRING` | `VARCHAR` | `STRING` | `TEXT` |
+| `int` | `INT` | `INT64` | `INT` | `INT` | `INTEGER` |
+| `bigint` | `INT8` | `INT64` | `BIGINT` | `BIGINT` | `BIGINT` |
+| `float` | `FLOAT4` | `FLOAT64` | `FLOAT` | `FLOAT` | `REAL` |
+| `double` | `FLOAT8` | `FLOAT64` | `DOUBLE` | `DOUBLE` | `DOUBLE PRECISION` |
+| `boolean` | `BOOLEAN` | `BOOL` | `BOOLEAN` | `BOOLEAN` | `BOOLEAN` |
+| `bytes` | `VARBYTE` | `BYTES` | `BINARY` | `BINARY` | `BYTEA` |
+| `object` | `SUPER` | `JSON` | `VARIANT` | `STRING` | `JSONB` |
+| `geometry` | `GEOMETRY` | `GEOGRAPHY` | `GEOMETRY` | `STRING` | `GEOMETRY` |
+| `geography` | `GEOGRAPHY` | `GEOGRAPHY` | `GEOGRAPHY` | `STRING` | `GEOGRAPHY` |
+
+You can also use cloud-specific types directly (e.g., `VARCHAR(MAX)`, `SUPER`), which are passed through unchanged.
+
+## Validation Rules
+
+The system validates function configurations at load time:
+
+- **Error**: Function has neither SQL template nor parameters/returns metadata
+- **Warning**: Function has both SQL template and metadata (template takes precedence)
+- **OK**: Function has either SQL template or complete metadata (parameters + returns)
+
+## Lambda Naming Constraints
+
+**Critical**: Redshift external functions have an undocumented limit of ~18 characters for Lambda function names.
+
+- Keep total name under 18 chars: `len(RS_LAMBDA_PREFIX) + len(function_name) < 18`
+- Use `lambda_name` field in function.yaml for short names
+- Examples:
+  - OK: `v-quadbin_polyfill` = 17 chars (safe)
+  - FAIL: `myname-quadbin_polyfill` = 22 chars (will fail)
+
+For CI/CD prefixes (e.g., `ci_12345678_123456_`), function names should be <=18 chars to stay within the 64-character total AWS Lambda name limit.
+
+## Shared Libraries
+
+Place reusable code in `gateway/functions/_shared/python/<lib_name>/` and reference via `shared_libs` in function.yaml. The build system copies these to `lib/<lib_name>/` in the Lambda package.
+
+**Critical Rule**: Only create shared libraries when code is used by **multiple functions** (2+). Single-function code should live in the function's own `code/lambda/python/lib/` directory.
+
+## Cloud Functions (Native SQL)
+
+SQL UDFs go in `clouds/{cloud}/modules/sql/<module>/` and follow cloud-specific patterns. See cloud-specific READMEs:
+- `clouds/redshift/README.md`
+- `clouds/bigquery/README.md`
+- etc.
+
+## Multi-Cloud Functions
+
+Functions can support multiple clouds in a single `function.yaml`:
+
+```yaml
+clouds:
+  redshift:
+    type: lambda
+    lambda_name: ex_multi
+    code_file: code/lambda/python/handler.py
+  snowflake:
+    type: lambda
+    code_file: code/snowflake/handler.py
+```
+
+## Function Documentation
+
+Documentation lives in `clouds/{cloud}/modules/doc/<module>/`:
+
+- `_INTRO.md` — Module introduction
+- `FUNCTION_NAME.md` — Individual function docs
+
+Follows markdown format with special metadata headers. See `CONTRIBUTING.md` for details.
+
+## Future Development Guidelines
+
+### When adding new functions
+
+1. Determine if code should be shared or function-specific
+2. Use shared library only if used by 2+ functions
+3. Keep lambda_name <=18 characters
+4. Add comprehensive unit tests
+5. Document function in module README
+6. Use generic types in function.yaml when possible
+7. Follow existing handler patterns
+8. Build and test before committing
diff --git a/.claude/rules/gateway.md b/.claude/rules/gateway.md
@@ -0,0 +1,395 @@
+---
+paths:
+  - "gateway/**"
+---
+
+# Gateway Architecture
+
+## Cloud and Platform Agnosticism
+
+All gateway deployment logic is in `gateway/logic/` and is designed to be cloud and platform agnostic.
+
+### Architecture Layers
+
+1. **Common Engine** (`gateway/logic/common/engine/`):
+   - `catalog_loader.py`: Discovers and loads function definitions
+   - `models.py`: Cloud-agnostic data models (CloudType, PlatformType, CloudConfig)
+   - `type_mapper.py`: Generic type mapping system with cloud-specific registrations
+   - `validators.py`: Function configuration validation
+   - `packagers.py`: Package creation for distribution
+
+2. **Platform Layer** (`gateway/logic/platforms/`):
+   - `aws-lambda/`: AWS Lambda-specific deployment logic
+   - Extensible for other platforms (GCP Cloud Run, Snowflake Snowpark, etc.)
+
+3. **Cloud Layer** (`gateway/logic/clouds/`):
+   - `redshift/`: Redshift-specific SQL generation and deployment
+   - `sql_template_generator.py`: Auto-generates SQL from function metadata
+   - Extensible for other clouds (BigQuery, Snowflake, Databricks)
+
+## Shared vs Function-Specific Libraries
+
+**Critical Rule**: Only create shared libraries when code is used by **multiple functions** (2+).
+
+### Shared Libraries (`gateway/functions/_shared/python/`)
+
+- **Purpose**: Code used by multiple functions
+- **Location**: `_shared/python/<module_name>/`
+- **Reference**: Listed in function.yaml `shared_libs` field
+- **Build**: Copied to each function's `lib/<module_name>/` during `make build`
+- **Import**: `from lib.<module_name> import ...`
+
+**Examples:**
+```python
+# gateway/functions/_shared/python/statistics/
+from lib.statistics import get_neighbors  # Used by multiple stat functions
+
+# gateway/functions/_shared/python/tiler/
+from lib.tiler import simple_tiler       # Used by multiple tiler functions
+```
+
+### Function-Specific Libraries (`<function>/code/lambda/python/lib/`)
+
+- **Purpose**: Code used by **only one function**
+- **Location**: `code/lambda/python/lib/` within function directory
+- **Reference**: Not in function.yaml (automatically included)
+- **Build**: Included directly in function package
+- **Import**: `from lib.<module> import ...`
+
+**Examples:**
+```python
+# statistics/__getis_ord_quadbin/code/lambda/python/lib/kernel.py
+from lib.kernel import kernel_weight  # Only used by getis_ord
+
+# statistics/__morans_i_quadbin/code/lambda/python/lib/decay.py
+from lib.decay import distance_decay  # Only used by morans_i
+```
+
+**Why This Matters:**
+- `kernel.py` and `decay.py` are **NOT duplicates** - they're intentionally function-specific
+- This provides **isolation** and **independent versioning** per function
+- Prevents coupling between unrelated functions
+- Allows different functions to evolve independently
+
+## Handler Patterns and Decorators
+
+### Standard Pattern (98% of functions)
+
+```python
+from carto.lambda_wrapper import redshift_handler
+
+@redshift_handler
+def process_row(row):
+    """Process single row from Redshift batch."""
+    # Validation
+    if not row or len(row) < expected_params:
+        return None
+
+    # Extract parameters
+    param1 = row[0]
+    param2 = row[1]
+
+    # Validation
+    if param1 is None or param2 is None:
+        return None
+
+    # Process
+    result = compute_something(param1, param2)
+
+    return result
+
+# Export for AWS Lambda
+lambda_handler = process_row
+```
+
+**What `@redshift_handler` does:**
+- Handles batch processing (receives array of rows from Redshift)
+- Processes each row individually
+- Aggregates results
+- Handles errors and returns proper response format
+- Manages Lambda context
+
+### Alternative Pattern (for complex functions)
+
+```python
+def my_function(param1, param2):
+    """Core function logic."""
+    from lib.shared_module import helper
+    return helper(param1, param2)
+
+@redshift_handler
+def process_row(row):
+    """Wrapper for redshift_handler."""
+    if not row or len(row) < 2:
+        return None
+    return my_function(row[0], row[1])
+
+lambda_handler = process_row
+```
+
+## Build System Details
+
+**What happens during `make build cloud=redshift`:**
+
+### 1. Discovery Phase
+
+```python
+# Scans for function.yaml files in:
+gateway/functions/**/function.yaml
+```
+
+### 2. Validation Phase
+
+```python
+# Validates each function.yaml:
+- Required fields present
+- Lambda name <=18 chars
+- Shared libs exist
+- Code files exist
+```
+
+### 3. Copy Phase
+
+```python
+# For each function with shared_libs:
+for lib in function.shared_libs:
+    copy _shared/python/{lib}/ to {function}/code/lambda/python/lib/{lib}/
+```
+
+### 4. Package Phase
+
+```python
+# Creates deployment package for each function:
+- Copy function code
+- Install requirements.txt dependencies
+- Include shared libraries
+- Create .zip for Lambda deployment
+```
+
+**Why build is required before tests:**
+- Tests import from `lib.*` which doesn't exist until build copies shared libraries
+- Each test runs against the actual Lambda deployment structure
+- Ensures tests match production behavior
+
+## Deployment Flow
+
+**Complete Deployment Process:**
+
+```
+1. Load Function Catalog (gateway/logic/common/engine/catalog_loader.py)
+   |-> Scan gateway/functions/
+   |-> Parse all function.yaml files
+
+2. Validate Functions (gateway/logic/common/engine/validators.py)
+   |-> Check required fields
+   |-> Validate lambda_name length
+   |-> Verify shared_libs exist
+   |-> Validate code files exist
+
+3. Package Functions (gateway/logic/common/engine/packagers.py)
+   |-> Copy function code
+   |-> Copy shared libraries (if specified)
+   |-> Install requirements (if specified)
+   |-> Create deployment package (.zip)
+
+4. Deploy to Lambda (gateway/logic/platforms/aws-lambda/)
+   |-> Upload Lambda package to AWS
+   |-> Set memory, timeout, runtime config
+   |-> Configure IAM role
+   |-> Get Lambda ARN
+
+5. Create External Functions (gateway/logic/clouds/redshift/)
+   |-> Generate SQL from template or auto-generate
+   |-> Replace @@VARIABLES@@ with actual values
+   |-> Execute SQL on Redshift
+   |-> Link external function to Lambda ARN
+
+6. Verify Deployment
+   |-> Test Lambda invocation
+   |-> Test external function call
+```
+
+## Template Variables
+
+SQL templates use `@@VARIABLE@@` syntax that gets replaced at different stages:
+
+```sql
+CREATE OR REPLACE EXTERNAL FUNCTION @@RS_SCHEMA@@.GETIS_ORD_QUADBIN(...)
+LAMBDA '@@RS_LAMBDA_ARN@@'
+IAM_ROLE '@@RS_LAMBDA_INVOKE_ROLE@@';
+```
+
+**Available Variables:**
+- `@@RS_SCHEMA@@`: Schema name (e.g., `dev_carto` or `carto`)
+- `@@RS_LAMBDA_ARN@@`: Lambda function ARN
+- `@@RS_LAMBDA_INVOKE_ROLE@@`: IAM role for Lambda invocation
+- `@@RS_VERSION_FUNCTION@@`: Version function name (e.g., `VERSION_CORE`, `VERSION_ADVANCED`)
+- `@@RS_PACKAGE_VERSION@@`: Package version (e.g., `1.11.2`)
+
+**When Variables Are Replaced:**
+
+**Package Generation Time** (fixed for the package):
+- `@@RS_VERSION_FUNCTION@@` -> Replaced with function name during build
+- `@@RS_PACKAGE_VERSION@@` -> Replaced with version number during build
+
+**Installation Time** (user-specific):
+- `@@RS_SCHEMA@@` -> Preserved in packages, replaced during installation with user's schema
+- Gateway variables (`@@RS_LAMBDA_ARN@@`, etc.) -> Replaced during deployment
+
+**How RS_SCHEMA Preservation Works:**
+
+When creating packages, the build system passes `RS_SCHEMA='@@RS_SCHEMA@@'` to preserve the template:
+
+```makefile
+# Makefile - Package creation
+(cd clouds/redshift && RS_SCHEMA='@@RS_SCHEMA@@' $(MAKE) build-modules ...)
+```
+
+This ensures packages contain `@@RS_SCHEMA@@` as a literal template, which the installer then replaces with the user's chosen schema name.
+
+### SQL Wrapper Pattern for Lambda Functions
+
+For Lambda functions that need to reference the schema in error messages, use a SQL wrapper:
+
+```sql
+-- Internal Lambda function (accepts carto_schema as parameter)
+CREATE OR REPLACE EXTERNAL FUNCTION @@SCHEMA@@.__FUNCTION_NAME_LAMBDA(
+    -- ... other parameters ...
+    carto_schema VARCHAR(MAX)
+)
+RETURNS VARCHAR(MAX)
+LAMBDA '@@LAMBDA_ARN@@'
+IAM_ROLE '@@IAM_ROLE_ARN@@';
+
+-- Public wrapper function (injects @@SCHEMA@@ at deployment time)
+CREATE OR REPLACE FUNCTION @@SCHEMA@@.__FUNCTION_NAME(
+    -- ... other parameters ...
+)
+RETURNS VARCHAR(MAX)
+AS $$
+    SELECT @@SCHEMA@@.__FUNCTION_NAME_LAMBDA(
+        -- ... other parameters ...
+        '@@SCHEMA@@'
+    )
+$$ LANGUAGE sql;
+```
+
+The Lambda Python code receives the schema name as a parameter:
+
+```python
+@redshift_handler
+def process_row(row):
+    # ... extract other parameters ...
+    carto_schema = row[-1]  # Last parameter
+
+    # Can now use carto_schema in error messages
+    raise Exception(f"Error in {carto_schema}.FUNCTION_NAME: ...")
+```
+
+This pattern is used by functions like `__generic_is_configured` and data enrichment functions.
+
+## Gateway Deployment Configuration
+
+**Gateway functions support flexible schema configuration:**
+- **RS_SCHEMA**: Use directly as schema name (e.g., `RS_SCHEMA=yourname_carto` -> "yourname_carto")
+- **RS_PREFIX**: Concatenate with "carto" (e.g., `RS_PREFIX=yourname_` -> "yourname_carto")
+- **Priority**: `RS_SCHEMA` takes precedence if both are set
+- **Consistency**: Using `RS_PREFIX` matches clouds behavior for consistent naming
+- Lambda functions use `RS_LAMBDA_PREFIX` (e.g., `yourname-at-qb_polyfill`)
+- Control Lambda updates with `RS_LAMBDA_OVERRIDE` (1=update existing, 0=skip existing)
+
+## Package Customization (Extensibility Pattern)
+
+Core's packaging system supports extensibility through a **try/except import pattern** that allows external repositories (like premium) to customize packages without modifying core code.
+
+**How Core Enables Extension:**
+
+The core packager (`gateway/logic/clouds/redshift/packager.py`) includes an extension point:
+
+```python
+def create_package(...):
+    """Create base package with core functions."""
+    # ... create base package ...
+
+    # Extension point: Allow external customization
+    try:
+        # Import premium packager if available
+        from gateway.logic.clouds.redshift.packager import customize_package
+        customize_package(package_dir, production, functions)
+    except ImportError:
+        # No premium packager - core-only package
+        pass
+```
+
+**External Customization Interface:**
+
+```python
+def customize_package(package_dir: str, production: bool, functions: dict) -> None:
+    """Customize package with external-specific content.
+
+    Args:
+        package_dir: Path to package directory (full access)
+        production: Whether this is a production build
+        functions: Dictionary of all functions being packaged
+
+    Example use cases:
+        - Add proprietary setup scripts
+        - Generate additional configuration files
+        - Modify package structure for deployment requirements
+    """
+    # Full access to modify package_dir
+    pass
+```
+
+**Key Benefits:**
+- **Core remains generic**: No premium-specific code in open-source core
+- **Convention-based**: Core automatically detects and uses external packager if present
+- **Clean separation**: Extension point is clearly defined and documented
+- **Full flexibility**: External packager has complete access to package directory
+
+**Files Involved:**
+- Core packager: `gateway/logic/clouds/redshift/packager.py` (defines extension point)
+- External packager: Created by external repository at same path
+- Activated during: `make create-package`
+
+## Module Organization
+
+### Core Modules (open source in `gateway/functions/`)
+
+- `quadbin`: Quadbin spatial indexing
+- `quadkey`: Quadkey spatial indexing
+- `s2`: S2 geometry
+- `placekey`: Placekey operations
+- `clustering`: Spatial clustering
+- `constructors`: Geometry constructors
+- `processing`: Geometry processing
+- `transformations`: Coordinate transformations
+- `random`: Random data generation
+
+## Troubleshooting Guide
+
+**Common Issues:**
+
+1. **Import Error: `ModuleNotFoundError: No module named 'lib'`**
+   - **Cause**: Build not run before tests
+   - **Fix**: `make build cloud=redshift`
+
+2. **Lambda Deploy Fails: `ResourceName too long`**
+   - **Cause**: lambda_name + prefix > 64 chars
+   - **Fix**: Shorten lambda_name in function.yaml to <=18 chars
+
+3. **Test Import Error: `No module named 'lib.statistics'`**
+   - **Cause**: shared_libs not specified in function.yaml
+   - **Fix**: Add `shared_libs: [statistics]` to function.yaml, rebuild
+
+4. **Function Not Found During Deploy**
+   - **Cause**: function.yaml missing or invalid
+   - **Fix**: Validate function.yaml structure, check required fields
+
+5. **External Function Error: `Permission denied for Lambda`**
+   - **Cause**: RS_LAMBDA_INVOKE_ROLE not set or incorrect
+   - **Fix**: Verify IAM role ARN in .env file
+
+6. **Build Copies Wrong Library Version**
+   - **Cause**: Old build artifacts
+   - **Fix**: `make clean && make build cloud=redshift`
diff --git a/.claude/rules/oracle.md b/.claude/rules/oracle.md
@@ -0,0 +1,85 @@
+---
+paths:
+  - "clouds/oracle/**"
+---
+
+# Oracle
+
+## Configuration
+
+Create a `.env` file in `clouds/oracle/` (template: `clouds/oracle/.env.template`):
+
+```bash
+ORA_PREFIX=DEV_                # Schema prefix (e.g., "DEV_" -> "DEV_CARTO", empty for production)
+ORA_USER=<user>                # Database user
+ORA_PASSWORD=<password>        # User password
+ORA_WALLET_ZIP=<base64>        # Base64-encoded Oracle wallet ZIP
+ORA_WALLET_PASSWORD=<password> # Wallet password
+ORA_CONNECTION_STRING=<tns>    # Optional TNS alias override (auto-detected from wallet)
+ORA_ENDPOINT=<url>             # AT Gateway Cloud Run service URL
+ORA_API_BASE_URL=<url>         # CARTO API base URL
+ORA_API_ACCESS_TOKEN=<token>   # CARTO API access token
+```
+
+**Note**: Oracle uses wallet-based authentication, unique among all supported clouds. Schemas use UPPERCASE naming convention (e.g., `DEV_CARTO`).
+
+## Commands
+
+```bash
+cd clouds/oracle
+make deploy                    # Deploy SQL UDFs
+make test                      # Run all tests (pytest)
+make test modules=map          # Run tests for specific module
+make lint                      # Run linter
+make lint-fix                  # Auto-fix lint issues
+make remove                    # Drop deployed functions
+make remove drop-schema=1      # Drop entire schema (destructive)
+```
+
+## Key Details
+
+- New cloud (v1.0.0, March 2026), infrastructure in place
+- Schema placeholder: `@@ORA_SCHEMA@@`
+- `ORA_GATEWAY_SERVICE_MOCK=1` to mock gateway (no real Oracle connection)
+- Deploy/test utilities in `clouds/oracle/common/`: `run_query.py`
+
+## Oracle SQL Patterns
+
+- Pure SQL functions: `CREATE OR REPLACE FUNCTION ... RETURN ... IS BEGIN ... END;` with `/` terminator
+- PL/SQL blocks with loops for complex functions (KRING, TOCHILDREN, POLYFILL)
+- No SQL BOOLEAN — use `NUMBER` (1/0) for boolean returns
+- Use `CLOB` instead of `VARCHAR2(32767)` for functions producing large JSON arrays
+- `AUTHID CURRENT_USER` (invoker rights) for all procedures
+- Error codes in `-20100` to `-20199` range for data module errors
+
+## Oracle Type Mapping
+
+| Generic | Oracle | Notes |
+|---------|--------|-------|
+| quadbin index | `NUMBER` | 38-digit precision, safe for 64-bit |
+| h3 index | `VARCHAR2(15)` | Hex string representation |
+| geometry | `SDO_GEOMETRY` | Native spatial type |
+| boolean | `NUMBER` | 1/0 (no SQL BOOLEAN) |
+| JSON struct/array | `VARCHAR2` or `CLOB` | `CLOB` for large results |
+
+## Oracle Native H3 Functions
+
+Oracle AI Database (23ai+) provides `SDO_UTIL.H3_*` functions natively:
+`H3_KEY`, `H3_BOUNDARY`, `H3_CENTER`, `H3_RESOLUTION`, `H3_PARENT`, `H3_IS_VALID_CELL`, `H3_IS_PENTAGON`, `H3_BASE_CELL`, `H3_NUM_CELLS`, `H3_MBR`
+
+These return `RAW(8)` — use `RAWTOHEX`/`HEXTORAW` to bridge to `VARCHAR2` hex strings.
+
+## Dynamic SQL in Procedures
+
+Use Q-literal multiline strings with `REPLACE`-based named placeholders:
+
+```sql
+v_sql := q'[
+    SELECT * FROM #INPUT_TABLE# WHERE #CONDITION#
+]';
+v_sql := REPLACE(v_sql, '#INPUT_TABLE#', p_input_table);
+v_sql := REPLACE(v_sql, '#CONDITION#', v_condition);
+EXECUTE IMMEDIATE v_sql;
+```
+
+Preferred over `UTL_LMS.FORMAT_MESSAGE` (limited to 5 args).
diff --git a/.claude/rules/packaging.md b/.claude/rules/packaging.md
@@ -0,0 +1,86 @@
+---
+paths:
+  - "**/packager*"
+  - "**/install*"
+  - "dist/**"
+---
+
+# Packaging and Installation
+
+## Creating Distribution Packages
+
+```bash
+# From root: create unified package (gateway + clouds)
+make create-package cloud=redshift
+
+# Production package
+make create-package cloud=redshift production=1
+
+# Specific modules only
+make create-package cloud=redshift modules=quadbin
+```
+
+## Installing Packages (Redshift)
+
+Redshift packages include an interactive installer (`scripts/install.py`) for gateway Lambda functions.
+
+### Deployment Phases
+
+- **Phase 0**: IAM Role Setup (auto-creates Lambda execution + Redshift invoke roles) — if needed
+- **Phase 1**: Lambda Deployment (gateway functions)
+- **Phase 2**: External Function Creation (SQL wrappers for Lambdas)
+- **Phase 3**: Native SQL UDF Deployment (clouds functions)
+
+### Interactive Installation
+
+```bash
+cd dist/carto-at-redshift-VERSION
+python3 -m venv .venv && source .venv/bin/activate
+pip install -r scripts/requirements.txt
+python scripts/install.py
+```
+
+### Non-Interactive Installation
+
+**IMPORTANT**: The `--non-interactive` flag is **required** to skip all prompts. Without it, the installer will prompt interactively even if all parameters are provided.
+
+```bash
+python scripts/install.py \
+  --non-interactive \
+  --aws-region us-east-1 \
+  --aws-access-key-id AKIAXXXX \
+  --aws-secret-access-key XXXX \
+  --rs-lambda-prefix myprefix- \
+  --rs-host cluster.redshift.amazonaws.com \
+  --rs-database mydb \
+  --rs-user admin \
+  --rs-password secret \
+  --rs-schema myschema
+```
+
+### Other Clouds
+
+BigQuery, Snowflake, Databricks, Oracle, Postgres: use `make deploy` directly — deploys SQL UDFs without Lambda or installer.
+
+## Package Customization (Extra Packager Pattern)
+
+Core's packaging supports extensibility through a **try/except import pattern** that lets external repos (like premium) customize packages without modifying core code.
+
+```python
+# Core packager: gateway/logic/clouds/redshift/packager.py
+def create_package(...):
+    # ... create base package ...
+    try:
+        from gateway.logic.clouds.redshift.packager import customize_package
+        customize_package(package_dir, production, functions)
+    except ImportError:
+        pass  # No premium packager - core-only package
+```
+
+External repos implement `customize_package(package_dir, production, functions)` at the same path.
+
+## Installer Output Styling
+
+- **Phase headers**: plain `logger.info` (no colors) for consistency across phases
+- **Deployment banner**: only the main banner uses color (`click.secho` with `fg='cyan'`)
+- **Phase list**: don't list phases statically in overview — they vary by configuration
diff --git a/.claude/rules/postgres.md b/.claude/rules/postgres.md
@@ -0,0 +1,34 @@
+---
+paths:
+  - "clouds/postgres/**"
+---
+
+# PostgreSQL
+
+## Configuration
+
+Create a `.env` file in `clouds/postgres/` (template: `clouds/postgres/.env.template`):
+
+```bash
+PG_HOST=<host>       # Database host
+PG_DATABASE=<db>     # Target database
+PG_USER=<user>       # Database user
+PG_PASSWORD=<pass>   # User password
+PG_PREFIX=<prefix>   # Optional schema prefix
+```
+
+## Commands
+
+```bash
+cd clouds/postgres
+make deploy   # deploy modules
+make test     # run tests (pytest)
+make build    # build JS libraries + SQL modules
+```
+
+## Key Details
+
+- Uses JavaScript libraries and pytest for testing
+- Schema creation is automatic
+- JS libraries: `clouds/postgres/libraries/javascript/`
+- Modules: h3, quadbin, s2, placekey, constructors, transformations, processing, clustering, random
diff --git a/.claude/rules/redshift.md b/.claude/rules/redshift.md
@@ -0,0 +1,75 @@
+---
+paths:
+  - "clouds/redshift/**"
+---
+
+# Redshift
+
+## Configuration
+
+Create a `.env` file in the repository root or `gateway/` (template: `gateway/.env.template`):
+
+```bash
+# AWS Configuration
+AWS_REGION=us-east-1
+AWS_ACCESS_KEY_ID=<your-key>
+AWS_SECRET_ACCESS_KEY=<your-secret>
+
+# Lambda Configuration
+RS_LAMBDA_PREFIX=yourname-at-dev  # Prefix for Lambda functions (max 46 chars, total name <=64)
+RS_LAMBDA_OVERRIDE=1              # Override existing Lambdas (1=yes, 0=no)
+
+# Redshift Connection
+RS_SCHEMA=yourname_carto          # Schema name (used directly)
+# OR
+RS_PREFIX=yourname_               # Schema prefix (concatenated with "carto")
+                                  # RS_SCHEMA takes priority if both are set
+RS_HOST=<cluster>.redshift.amazonaws.com
+RS_DATABASE=<database>
+RS_USER=<user>
+RS_PASSWORD=<password>
+RS_LAMBDA_INVOKE_ROLE=arn:aws:iam::<account>:role/<role>
+```
+
+## RS_SCHEMA vs RS_PREFIX
+
+- **RS_SCHEMA**: Use directly as schema name (e.g., `yourname_carto`)
+- **RS_PREFIX**: Concatenated with "carto" (e.g., `yourname_` → `yourname_carto`)
+- **RS_SCHEMA takes priority** if both are set
+
+## Commands
+
+```bash
+cd clouds/redshift
+make test                          # Run all tests (pytest)
+make test modules=h3               # Specific module
+make test functions=H3_POLYFILL    # Specific function
+make deploy                        # Deploy SQL UDFs
+make lint                          # Run linter
+
+# Gateway deployment (from gateway/)
+cd gateway
+make deploy cloud=redshift
+make deploy cloud=redshift diff=1  # Deploy only modified functions
+```
+
+## SQL Naming Conventions
+
+```sql
+-- Definition: parentheses on separate line
+CREATE OR REPLACE FUNCTION @@RS_SCHEMA@@.H3_POLYFILL
+(
+    geom GEOMETRY,
+    resolution INT
+)
+RETURNS VARCHAR ...
+
+-- Invocation: no space before parentheses
+SELECT @@RS_SCHEMA@@.H3_POLYFILL(geom, 5)
+```
+
+## Key Details
+
+- Schema placeholder: `@@RS_SCHEMA@@`
+- Python libraries: `clouds/redshift/libraries/python/`
+- Modules: h3, quadbin, s2, placekey, constructors, transformations, processing, clustering, random
diff --git a/.claude/rules/snowflake.md b/.claude/rules/snowflake.md
@@ -0,0 +1,43 @@
+---
+paths:
+  - "clouds/snowflake/**"
+---
+
+# Snowflake
+
+## Configuration
+
+Create a `.env` file in `clouds/snowflake/` (template: `clouds/snowflake/.env.template`):
+
+```bash
+SF_ACCOUNT=<account>             # Snowflake account identifier
+SF_DATABASE=<database>           # Target database
+SF_USER=<user>                   # Snowflake user
+SF_PASSWORD=<password>           # Password (or use key-pair auth below)
+SF_RSA_KEY=<key>                 # RSA private key (key-pair auth)
+SF_RSA_KEY_PASSWORD=<password>   # RSA key passphrase (key-pair auth)
+SF_PREFIX=<prefix>               # Optional schema prefix
+SF_API_INTEGRATION=<name>        # Optional API integration name
+SF_ENDPOINT=<url>                # Optional AT Gateway Cloud Run service URL
+SF_API_BASE_URL=<url>            # Optional CARTO API base URL
+SF_API_ACCESS_TOKEN=<token>      # Optional CARTO API access token
+```
+
+## Commands
+
+```bash
+cd clouds/snowflake
+make deploy               # deploy modules
+make test                 # run tests (Jest)
+make build                # build JS libraries + SQL modules
+make deploy-native-app    # deploy native app
+make deploy-share         # deploy data share
+```
+
+## Key Details
+
+- Uses JavaScript libraries and Jest for testing
+- Supports native apps and data shares
+- JS libraries: `clouds/snowflake/libraries/javascript/`
+- Build/test utilities: `clouds/snowflake/common/`
+- Modules: h3, quadbin, s2, placekey, constructors, transformations, processing, clustering, random
diff --git a/.claude/rules/testing.md b/.claude/rules/testing.md
@@ -0,0 +1,187 @@
+---
+paths:
+  - "**/test*"
+  - "**/tests/**"
+---
+
+# Testing Standards
+
+> This rule covers **gateway-specific** testing (Lambda handlers, Python unit/integration tests). For cloud SQL testing patterns (pytest, Jest, fixtures), see the cloud-sql-testing rule which loads automatically when working in test directories.
+
+## Test Structure Standards
+
+All gateway function tests follow a standardized structure with clear separation:
+
+### File Structure
+
+```python
+"""
+Unit tests for function_name function.
+
+This file contains:
+- Handler Interface Tests: Validate Lambda handler and batch processing
+- Function Logic Tests: Validate internal algorithms and helpers (if complex)
+"""
+
+# Copyright (c) 2025, CARTO
+
+import json
+from test_utils.unit import load_function_module
+
+# Load handler and functions
+imports = load_function_module(__file__)
+lambda_handler = imports["lambda_handler"]
+
+# For functions with internal helpers to test:
+imports = load_function_module(
+    __file__,
+    {
+        "from_lib": ["function_from_lib"],              # From lib/__init__.py
+        "from_lib_module": {                            # From lib/submodule.py
+            "module_name": ["helper_func"]
+        },
+        "from_handler": ["internal_func"]              # From handler.py itself
+    }
+)
+
+# ============================================================================
+# HANDLER INTERFACE TESTS
+# ============================================================================
+
+class TestLambdaHandler:
+    """Test the Lambda handler interface."""
+    # Tests: empty events, null inputs, batch processing
+
+# ============================================================================
+# FUNCTION LOGIC TESTS (only for complex functions)
+# ============================================================================
+
+class TestHelperFunction:
+    """Test helper_function directly."""
+    # Direct tests of algorithms, edge cases, mathematical correctness
+```
+
+## Testing Tiers
+
+- **Tier 1** (Handler only): Simple functions - validate Lambda interface
+- **Tier 2** (Handler + Logic): Complex functions - also test internal algorithms directly
+- **Tier 3** (Integration): Functions requiring database state validation
+
+## Key Utilities
+
+### load_function_module
+
+`load_function_module(__file__)` - Loads from build directory with shared libs.
+
+Parameters:
+- `from_lib` - Access functions from `lib/__init__.py`
+- `from_lib_module` - Access functions from `lib/submodule.py` (dict of `{module_name: [func_names]}`)
+- `from_handler` - Access internal functions from `handler.py` for direct testing
+
+## Running Tests
+
+**Gateway functions require building before testing** (copies shared libraries):
+
+```bash
+cd gateway
+
+# Build all functions (required before tests)
+make build cloud=redshift
+
+# Run all unit tests
+make test-unit cloud=redshift
+
+# Run specific module tests
+make test-unit cloud=redshift modules=statistics
+
+# Run specific function tests
+make test-unit cloud=redshift functions=getis_ord_quadbin
+
+# Run integration tests
+make test-integration cloud=redshift
+
+# Run linter
+make lint
+```
+
+**Cloud SQL function tests:**
+
+```bash
+cd clouds/redshift
+
+# Run all tests
+make test
+
+# Run specific module tests
+make test modules=h3
+
+# Run specific function tests
+make test functions=H3_POLYFILL
+```
+
+## Unit Test Example
+
+```python
+# gateway/functions/module/function/tests/unit/test_function.py
+
+import pytest
+from test_utils.unit import load_function_module
+
+# Load handler and internal functions using standard utility
+imports = load_function_module(
+    __file__,
+    {
+        "from_handler": ["process_row"],
+        "from_lib": ["get_neighbors"],
+    }
+)
+process_row = imports["process_row"]
+get_neighbors = imports["get_neighbors"]
+
+
+def test_process_row_valid_input():
+    """Test handler with valid input."""
+    row = [{"data": "..."}, 5, "uniform"]
+    result = process_row(row)
+    assert result is not None
+
+
+def test_process_row_invalid_input():
+    """Test handler with invalid input."""
+    row = []
+    result = process_row(row)
+    assert result is None
+```
+
+## Integration Test Example
+
+```python
+# gateway/functions/module/function/tests/integration/test_function.py
+
+import pytest
+import boto3
+
+
+@pytest.mark.integration
+def test_lambda_invocation():
+    """Test actual Lambda function."""
+    client = boto3.client("lambda")
+    response = client.invoke(
+        FunctionName="dev_function_name",
+        Payload=json.dumps({"data": "test"})
+    )
+    assert response["StatusCode"] == 200
+
+
+@pytest.mark.integration
+def test_redshift_external_function():
+    """Test Redshift external function."""
+    import psycopg2
+    conn = psycopg2.connect(...)
+    cursor = conn.cursor()
+    cursor.execute("SELECT dev_carto.function_name(...)")
+    result = cursor.fetchone()
+    assert result is not None
+```
+
+Integration tests connect to real Redshift clusters and test deployed functions. They require proper `.env` configuration and deployed functions.
diff --git a/.claude/rules/versioning.md b/.claude/rules/versioning.md
@@ -0,0 +1,39 @@
+---
+paths:
+  - "**/version"
+  - "**/CHANGELOG*"
+  - "**/RELEASING*"
+---
+
+# Versioning
+
+## Version Files
+
+Each cloud has independent versions in plain text files: `clouds/{cloud}/version` (e.g., `1.2.7`).
+
+## Semver Conventions
+
+- **feat** → minor bump
+- **fix** → patch bump
+- **chore/docs** → no bump
+- **Breaking change** → major bump
+
+## Version Bumping
+
+Manual process — edit the version file directly. No automated tooling.
+
+## How Versions Are Consumed
+
+- `make create-package` reads `clouds/{cloud}/version` to name packages (`carto-at-{cloud}-VERSION.zip`)
+- `.github/workflows/publish-release.yml` detects which version files changed to determine which clouds to publish
+- Installer scripts display version at runtime
+
+## Release Process
+
+See `RELEASING.md` for the full process. Key steps:
+
+1. Create `release/YYYY-MM-DD` branch
+2. Bump version files for affected clouds
+3. Update `CHANGELOG.md` (root + per-cloud)
+4. PR to `stable` branch
+5. Squash-merge triggers CI publish
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -4,1298 +4,56 @@ This file provides guidance to Claude Code (claude.ai/code) when working with co
 
 ## Repository Overview
 
-**CARTO Analytics Toolbox Core** is a multi-cloud spatial analytics platform providing UDFs and Stored Procedures for BigQuery, Snowflake, Redshift, Postgres, Databricks, and Oracle. The repository is organized into:
+**CARTO Analytics Toolbox Core** is a multi-cloud spatial analytics platform providing UDFs and Stored Procedures for BigQuery, Snowflake, Redshift, Postgres, Databricks, and Oracle. Two parallel systems:
 
-1. **Gateway**: Lambda-based Python functions callable via SQL external functions (Redshift)
-2. **Clouds**: Native SQL UDFs specific to each cloud platform
+- **Gateway** (`gateway/`): Lambda-based Python functions for Redshift (build, deploy, test via `gateway/Makefile`)
+- **Clouds** (`clouds/{cloud}/`): Native SQL UDFs per platform (6 clouds, each with `modules/sql/`, `modules/test/`, `libraries/`, `common/`, `version`)
 
-## Repository Structure
-
-```
-core/
-├── gateway/                   # Lambda deployment engine + functions
-│   ├── functions/             # Function definitions by module
-│   │   ├── quadbin/
-│   │   ├── s2/
-│   │   ├── clustering/
-│   │   └── _shared/python/    # Shared libraries
-│   ├── logic/                 # Deployment engine
-│   │   ├── common/engine/     # Catalog, validators, packagers
-│   │   ├── clouds/redshift/   # Redshift CLI and deployers
-│   │   └── platforms/aws-lambda/
-│   └── tools/                 # Build and dependency tools
-│
-└── clouds/{cloud}/            # Native SQL UDFs for each cloud (6 clouds)
-    ├── modules/               # bigquery, snowflake, redshift, postgres, databricks, oracle
-    │   ├── sql/               # SQL function definitions
-    │   ├── doc/               # Function documentation
-    │   └── test/              # Integration tests
-    ├── libraries/             # Cloud-specific libraries (Python/JS)
-    ├── common/                # Cloud-specific build scripts and utilities
-    └── version                # Version file (defines package version)
-```
-
-### Cloud-Specific Modules (core)
-
-| Cloud | Key Modules | Notes |
-|-------|-------------|-------|
-| BigQuery | h3, quadbin, s2, placekey, constructors, transformations, processing, clustering, random | Mature, JS-based libraries |
-| Snowflake | h3, quadbin, s2, placekey, constructors, transformations, processing, clustering, random | Mature, JS-based libraries |
-| Redshift | h3, quadbin, s2, placekey, constructors, transformations, processing, clustering, random | Mature, Python UDFs + Gateway Lambda |
-| Postgres | h3, quadbin, s2, placekey, constructors, transformations, processing, clustering, random | Mature, SQL/PLpgSQL |
-| Databricks | quadbin | Recently migrated (March 2026), 20 SQL functions |
-| Oracle | (none yet) | New cloud (v1.0.0), infrastructure only, SQL modules coming |
-
-## Common Development Commands
-
-### Initial Setup
-
-```bash
-# From gateway directory
-cd gateway
-make venv                      # Create virtual environment
-```
-
-### Configuration
-
-Create a `.env` file in the repository root or `gateway/` directory (template: `gateway/.env.template`):
-
-```bash
-# AWS Configuration
-AWS_REGION=us-east-1
-AWS_ACCESS_KEY_ID=<your-key>
-AWS_SECRET_ACCESS_KEY=<your-secret>
-
-# Lambda Configuration
-RS_LAMBDA_PREFIX=yourname-at-  # Prefix for Lambda functions (max 46 chars, total name ≤64)
-RS_LAMBDA_OVERRIDE=1           # Override existing Lambdas (1=yes, 0=no)
-
-# Redshift Gateway Configuration
-RS_SCHEMA=yourname_carto       # Schema name for gateway functions (use directly)
-# OR use RS_PREFIX (automatically concatenated with "carto")
-RS_PREFIX=yourname_            # Schema prefix (e.g., "yourname_" → "yourname_carto")
-                               # Note: RS_SCHEMA takes priority if both are set
-RS_HOST=<cluster>.redshift.amazonaws.com
-RS_DATABASE=<database>
-RS_USER=<user>
-RS_PASSWORD=<password>
-RS_LAMBDA_INVOKE_ROLE=arn:aws:iam::<account>:role/<role>
-```
-
-### Cloud-Specific Configuration
-
-**Databricks** (`.env` template at `clouds/databricks/.env.template`):
-
-```bash
-DB_PREFIX=yourname_            # Schema prefix (e.g., "yourname_" → "yourname_carto")
-DB_CATALOG=<catalog>           # Databricks catalog name
-DB_HOST_NAME=<hostname>        # SQL Warehouse hostname
-DB_HTTP_PATH=<path>            # SQL Warehouse HTTP path
-DB_TOKEN=<token>               # Access token
-```
-
-**Oracle** (`.env` template at `clouds/oracle/.env.template`):
-
-```bash
-ORA_PREFIX=DEV_                # Schema prefix (e.g., "DEV_" → "DEV_CARTO", empty for production)
-ORA_USER=<user>                # Database user
-ORA_PASSWORD=<password>        # User password
-ORA_WALLET_ZIP=<base64>        # Base64-encoded Oracle wallet ZIP
-ORA_WALLET_PASSWORD=<password> # Wallet password
-ORA_CONNECTION_STRING=<tns>    # Optional TNS alias override (auto-detected from wallet)
-```
-
-**Note**: Oracle uses wallet-based authentication, unique among all supported clouds.
-
-### Building and Testing Gateway Functions
-
-**IMPORTANT**: Gateway functions require building before testing (copies shared libraries):
-
-```bash
-cd gateway
-
-# Build functions (REQUIRED before tests)
-make build cloud=redshift
-
-# Run unit tests (build first!)
-make test-unit cloud=redshift
-
-# Run specific module tests
-make test-unit cloud=redshift modules=quadbin
-
-# Run specific function tests
-make test-unit cloud=redshift functions=quadbin_polyfill
-
-# Run integration tests (requires Redshift connection)
-make test-integration cloud=redshift
-```
-
-### Testing Cloud SQL Functions
-
-```bash
-cd clouds/redshift
-
-# Run all tests
-make test
-
-# Run specific module tests
-make test modules=h3
-
-# Run specific function tests
-make test functions=H3_POLYFILL
-```
-
-### Linting
+## Key Commands
 
 ```bash
-# Lint gateway
+# Gateway (Redshift-only): setup and build REQUIRED before tests
 cd gateway
-make lint
-
-# Auto-fix formatting
-make lint-fix
-
-# Lint from root (both gateway + clouds)
-cd ..
-make lint cloud=redshift
-```
-
-### Deployment
+make venv                                        # First-time setup
+make build cloud=redshift && make test-unit cloud=redshift modules=X
 
-**From root** (deploys both gateway Lambda functions + clouds SQL UDFs):
+# Cloud SQL UDFs
+cd clouds/{cloud}
+make test modules=X                  # Run tests
+make deploy                          # Deploy SQL UDFs
 
-```bash
-# Deploy to dev (with prefixes)
+# Root: combined gateway + clouds
 make deploy cloud=redshift
-
-# Deploy specific modules
-make deploy cloud=redshift modules=quadbin
-
-# Deploy to production (no prefixes)
-make deploy cloud=redshift production=1
-```
-
-**Gateway only** (Lambda functions):
-
-```bash
-cd gateway
-
-# Deploy to dev
-make deploy cloud=redshift
-
-# Deploy specific functions
-make deploy cloud=redshift functions=quadbin_polyfill
-
-# Deploy only modified functions
-make deploy cloud=redshift diff=1
-```
-
-**Clouds only** (native SQL UDFs):
-
-```bash
-cd clouds/redshift
-make deploy
-```
-
-### Creating Distribution Packages
-
-```bash
-# From root: Create unified package (gateway + clouds)
-make create-package cloud=redshift
-
-# Production package
-make create-package cloud=redshift production=1
-
-# Specific modules
-make create-package cloud=redshift modules=quadbin
-```
-
-### Installing Packages
-
-**Redshift Gateway Functions:**
-
-Redshift packages include an interactive installer (`scripts/install.py`) for deploying gateway Lambda functions:
-
-```bash
-cd dist/carto-at-redshift-1.1.3
-python3 -m venv .venv && source .venv/bin/activate
-pip install -r scripts/requirements.txt
-python scripts/install.py
-```
-
-**Deployment phases:**
-1. **Phase 0**: Auto-create IAM roles (Lambda execution + Redshift invoke) - if needed
-2. **Phase 1**: Deploy Lambda functions
-3. **Phase 2**: Create external SQL functions
-4. **Phase 3**: Deploy native SQL UDFs
-
-**Interactive Mode (default):**
-```bash
-python scripts/install.py  # Prompts for all configuration
-```
-
-**Non-Interactive Mode:**
-
-**IMPORTANT**: Use `--non-interactive` flag to skip all prompts (required for automation/CI/CD):
-
-```bash
-python scripts/install.py \
-  --non-interactive \
-  --aws-region us-east-1 \
-  --aws-access-key-id AKIAXXXX \
-  --aws-secret-access-key XXXX \
-  --rs-lambda-prefix myprefix- \
-  --rs-host cluster.redshift.amazonaws.com \
-  --rs-database mydb \
-  --rs-user admin \
-  --rs-password secret \
-  --rs-schema myschema
-```
-
-**Other Clouds (SQL UDFs only):**
-- **BigQuery**: `cd clouds/bigquery && make deploy`
-- **Snowflake**: `cd clouds/snowflake && make deploy`
-- **Databricks**: `cd clouds/databricks && make deploy`
-- **Postgres**: `cd clouds/postgres && make deploy`
-- **Oracle**: `cd clouds/oracle && make deploy`
-
-These clouds deploy native SQL UDFs directly without Lambda or installer.
-
-## Gateway Function Development
-
-### Directory Structure
-
-```
-gateway/functions/<module>/<function_name>/
-├── function.yaml              # Function metadata
-├── code/
-│   ├── lambda/python/
-│   │   ├── handler.py         # Lambda handler
-│   │   └── requirements.txt   # Python dependencies
-│   └── redshift.sql           # External function SQL template
-└── tests/
-    ├── unit/
-    │   ├── cases.yaml         # Simple test cases
-    │   └── test_*.py          # Complex test scenarios
-    └── integration/
-        └── test_*.py          # Integration tests
-```
-
-### function.yaml Example (Legacy with SQL Template)
-
-```yaml
-name: quadbin_polyfill
-module: quadbin
-clouds:
-  redshift:
-    type: lambda
-    lambda_name: qb_polyfill   # Short name (≤18 chars with prefix)
-    code_file: code/lambda/python/handler.py
-    requirements_file: code/lambda/python/requirements.txt
-    external_function_template: code/redshift.sql
-    shared_libs:
-      - quadbin                # Copies _shared/python/quadbin to lib/
-    config:
-      memory_size: 512
-      timeout: 300
-      max_batch_rows: 50
-      runtime: python3.10
-```
-
-### Hybrid Function Definitions (Auto-Generated SQL)
-
-**For simple functions, you can now eliminate the SQL template file entirely!** The system can auto-generate SQL from function metadata.
-
-#### Key Features
-
-- **Convention over configuration**: Function name and module inferred from directory structure
-- **Generic type mapping**: Define parameters once with generic types (`string`, `int`, `bigint`, etc.)
-- **Cloud-specific overrides**: Override types for specific clouds when needed (e.g., Redshift's `SUPER`)
-- **Automatic SQL generation**: SQL templates generated automatically from metadata
-- **Backward compatible**: Existing functions with SQL templates continue to work
-
-#### Function Naming Convention
-
-**Function name and module are automatically inferred from directory structure:**
-
-```
-functions/
-  <module>/
-    <function_name>/
-      function.yaml
-```
-
-- **Function name**: From directory name (e.g., `s2_fromtoken`)
-- **Module**: From parent directory name (e.g., `s2`)
-- **SQL function name**: Uppercase version (e.g., `S2_FROMTOKEN`)
-
-**Important**: Do NOT include `name` or `module` fields in `function.yaml` unless the function name needs to differ from the folder name.
-
-#### Supported Generic Types
-
-| Generic Type | Redshift | BigQuery | Snowflake | Databricks | Postgres |
-|-------------|----------|----------|-----------|------------|----------|
-| `string` | `VARCHAR(MAX)` | `STRING` | `VARCHAR` | `STRING` | `TEXT` |
-| `int` | `INT` | `INT64` | `INT` | `INT` | `INTEGER` |
-| `bigint` | `INT8` | `INT64` | `BIGINT` | `BIGINT` | `BIGINT` |
-| `float` | `FLOAT4` | `FLOAT64` | `FLOAT` | `FLOAT` | `REAL` |
-| `double` | `FLOAT8` | `FLOAT64` | `DOUBLE` | `DOUBLE` | `DOUBLE PRECISION` |
-| `boolean` | `BOOLEAN` | `BOOL` | `BOOLEAN` | `BOOLEAN` | `BOOLEAN` |
-| `bytes` | `VARBYTE` | `BYTES` | `BINARY` | `BINARY` | `BYTEA` |
-| `object` | `SUPER` | `JSON` | `VARIANT` | `STRING` | `JSONB` |
-| `geometry` | `GEOMETRY` | `GEOGRAPHY` | `GEOMETRY` | `STRING` | `GEOMETRY` |
-| `geography` | `GEOGRAPHY` | `GEOGRAPHY` | `GEOGRAPHY` | `STRING` | `GEOGRAPHY` |
-
-You can also use cloud-specific types directly (e.g., `VARCHAR(MAX)`, `SUPER`), which are passed through unchanged.
-
-#### Usage Patterns
-
-**Pattern 1: Simple Function with Generic Types**
-
-For straightforward functions, define parameters and return type at the top level. **No SQL file needed!**
-
-```yaml
-# No 'name' or 'module' fields - inferred from directory structure
-# Function: functions/s2/s2_fromtoken/
-
-parameters:
-  - name: token
-    type: string      # Maps to VARCHAR(MAX) in Redshift
-returns: bigint       # Maps to INT8 in Redshift
-
-clouds:
-  redshift:
-    type: lambda
-    lambda_name: s2_ftok
-    code_file: code/lambda/python/handler.py
-    # NO external_function_template needed!
-    config:
-      max_batch_rows: 10000
-```
-
-**Generated SQL (Redshift):**
-
-```sql
-CREATE OR REPLACE EXTERNAL FUNCTION @@SCHEMA@@.S2_FROMTOKEN(
-    token VARCHAR(MAX)
-)
-RETURNS INT8
-STABLE
-LAMBDA '@@LAMBDA_ARN@@'
-IAM_ROLE '@@IAM_ROLE_ARN@@'
-MAX_BATCH_ROWS 10000;
-```
-
-**Pattern 2: Cloud-Specific Type Overrides**
-
-For functions that need cloud-specific types (e.g., Redshift's `SUPER`), define types under the cloud section:
-
-```yaml
-# Function: functions/statistics/getis_ord_quadbin/
-
-clouds:
-  redshift:
-    type: lambda
-    lambda_name: getisord
-    code_file: code/lambda/python/handler.py
-    shared_libs:
-      - statistics
-    # Cloud-specific parameter types
-    parameters:
-      - name: data
-        type: SUPER        # Redshift-specific type
-      - name: k_neighbors
-        type: INT
-    returns: SUPER
-    config:
-      memory_size: 1024
-      max_batch_rows: 50
-```
-
-**Pattern 3: Hybrid (Generic + Cloud-Specific Overrides)**
-
-Define generic types at top level for most clouds, then override specific clouds:
-
-```yaml
-# Generic types for most clouds
-parameters:
-  - name: input_data
-    type: object      # Maps to SUPER, JSON, VARIANT, etc.
-  - name: value
-    type: float
-returns: object
-
-clouds:
-  redshift:
-    type: lambda
-    lambda_name: ex_hybrid
-    code_file: code/lambda/python/handler.py
-    # Override for Redshift (use SUPER instead of generic object)
-    parameters:
-      - name: input_data
-        type: SUPER
-      - name: value
-        type: float
-    returns: SUPER
-
-  bigquery:
-    type: cloud_run
-    # Uses generic types (object → JSON, float → FLOAT64)
-    code_file: code/cloud_run/main.py
-```
-
-**Pattern 4: Legacy (SQL Template)**
-
-Existing functions with SQL templates continue to work unchanged:
-
-```yaml
-name: example_legacy
-module: example
-
-clouds:
-  redshift:
-    type: lambda
-    lambda_name: ex_legacy
-    code_file: code/lambda/python/handler.py
-    external_function_template: code/redshift.sql  # Uses existing template
-```
-
-#### Validation
-
-The system validates function configurations at load time:
-
-- **Error**: Function has neither SQL template nor parameters/returns metadata
-- **Warning**: Function has both SQL template and metadata (template takes precedence)
-- **OK**: Function has either SQL template or complete metadata (parameters + returns)
-
-### Lambda Handler Pattern
-
-```python
-from carto.lambda_wrapper import redshift_handler
-
-@redshift_handler
-def process_row(row):
-    """Process single row."""
-    if not row or row[0] is None:
-        return None
-
-    # Your logic here
-    return result
-```
-
-### SQL Template Pattern
-
-Templates use `@@VARIABLE@@` syntax:
-
-```sql
-CREATE OR REPLACE EXTERNAL FUNCTION @@SCHEMA@@.QUADBIN_POLYFILL(
-    geom VARCHAR(MAX),
-    resolution INT
-)
-RETURNS VARCHAR(MAX)
-STABLE
-LAMBDA '@@LAMBDA_ARN@@'
-IAM_ROLE '@@IAM_ROLE_ARN@@';
-```
-
-Available variables:
-- `@@SCHEMA@@` - Schema name (e.g., `yourname_carto` or `carto`)
-- `@@LAMBDA_ARN@@` - Lambda function ARN
-- `@@IAM_ROLE_ARN@@` - IAM role for Lambda invocation
-
-### Shared Libraries
-
-Place reusable code in `gateway/functions/_shared/python/<lib_name>/` and reference via `shared_libs` in function.yaml. The build system copies these to `lib/<lib_name>/` in the Lambda package.
-
-## Key Implementation Details
-
-### Lambda Naming Constraints
-
-**Critical**: Redshift external functions have an undocumented limit of ~18 characters for Lambda function names.
-
-- Keep total name under 18 chars: `len(RS_LAMBDA_PREFIX) + len(function_name) < 18`
-- Use `lambda_name` field in function.yaml for short names
-- Examples:
-  - ✓ `v-quadbin_polyfill` = 17 chars (safe)
-  - ✗ `myname-quadbin_polyfill` = 22 chars (will fail)
-
-### Build System
-
-`make build` performs these steps:
-1. Discovers functions from `gateway/functions/`
-2. Installs function-specific dependencies from `requirements.txt`
-3. Copies shared libraries from `_shared/python/` to each function's `lib/` directory
-4. Creates build artifacts in `gateway/build/`
-
-**ALWAYS build before testing gateway functions.**
-
-### Deployment Process
-
-1. **Lambda deployment**: Creates/updates AWS Lambda functions
-2. **External function deployment**: Creates SQL external functions in Redshift
-3. **SQL UDF deployment**: Runs native SQL scripts for cloud-specific UDFs
-
-### Template Variables
-
-SQL templates use `@@VARIABLE@@` syntax that gets replaced at different stages:
-
-**Available Variables:**
-- `@@RS_SCHEMA@@`: Schema name (e.g., `dev_carto` or `carto`)
-- `@@RS_LAMBDA_ARN@@`: Lambda function ARN
-- `@@RS_LAMBDA_INVOKE_ROLE@@`: IAM role for Lambda invocation
-- `@@RS_VERSION_FUNCTION@@`: Version function name (e.g., `VERSION_CORE`)
-- `@@RS_PACKAGE_VERSION@@`: Package version (e.g., `1.1.3`)
-
-**When Variables Are Replaced:**
-
-**Package Generation Time** (fixed for the package):
-- `@@RS_VERSION_FUNCTION@@` → Replaced with function name during build
-- `@@RS_PACKAGE_VERSION@@` → Replaced with version number during build
-
-**Installation Time** (user-specific):
-- `@@RS_SCHEMA@@` → Preserved in packages, replaced during installation with user's schema
-- Gateway variables (`@@RS_LAMBDA_ARN@@`, etc.) → Replaced during deployment
-
-**How RS_SCHEMA Preservation Works:**
-
-When creating packages, the build system passes `RS_SCHEMA='@@RS_SCHEMA@@'` to preserve the template:
-
-```makefile
-# Makefile - Package creation
-(cd clouds/redshift && RS_SCHEMA='@@RS_SCHEMA@@' $(MAKE) build-modules ...)
-```
-
-This ensures packages contain `@@RS_SCHEMA@@` as a literal template, which the installer then replaces with the user's chosen schema name.
-
-**SQL Wrapper Pattern for Lambda Functions:**
-
-For Lambda functions that need to reference the schema in error messages, use a SQL wrapper that passes the schema as a parameter:
-
-```sql
--- Internal Lambda function (accepts carto_schema as parameter)
-CREATE OR REPLACE EXTERNAL FUNCTION @@SCHEMA@@.__FUNCTION_NAME_LAMBDA(
-    -- ... other parameters ...
-    carto_schema VARCHAR(MAX)
-)
-RETURNS VARCHAR(MAX)
-LAMBDA '@@LAMBDA_ARN@@'
-IAM_ROLE '@@IAM_ROLE_ARN@@';
-
--- Public wrapper function (injects @@SCHEMA@@ at deployment time)
-CREATE OR REPLACE FUNCTION @@SCHEMA@@.__FUNCTION_NAME(
-    -- ... other parameters ...
-)
-RETURNS VARCHAR(MAX)
-AS $$
-    SELECT @@SCHEMA@@.__FUNCTION_NAME_LAMBDA(
-        -- ... other parameters ...
-        '@@SCHEMA@@'
-    )
-$$ LANGUAGE sql;
-```
-
-The Lambda Python code receives the schema name as a parameter and can use it in error messages.
-
-### Gateway Deployment
-
-**Gateway functions support flexible schema configuration:**
-- **RS_SCHEMA**: Use directly as schema name (e.g., `RS_SCHEMA=yourname_carto` → "yourname_carto")
-- **RS_PREFIX**: Concatenate with "carto" (e.g., `RS_PREFIX=yourname_` → "yourname_carto")
-- **Priority**: `RS_SCHEMA` takes precedence if both are set
-- **Consistency**: Using `RS_PREFIX` matches clouds behavior for consistent naming
-- Lambda functions use `RS_LAMBDA_PREFIX` (e.g., `yourname-at-qb_polyfill`)
-- Control Lambda updates with `RS_LAMBDA_OVERRIDE` (1=update existing, 0=skip existing)
-
-### Package Customization (Extensibility Pattern)
-
-Core's packaging system supports extensibility through a **try/except import pattern** that allows external repositories (like premium) to customize packages without modifying core code.
-
-**How Core Enables Extension:**
-
-The core packager (`gateway/logic/clouds/redshift/packager.py`) includes an extension point:
-
-```python
-def create_package(...):
-    """Create base package with core functions."""
-    # ... create base package ...
-
-    # Extension point: Allow external customization
-    try:
-        # Import premium packager if available
-        from gateway.logic.clouds.redshift.packager import customize_package
-        customize_package(package_dir, production, functions)
-    except ImportError:
-        # No premium packager - core-only package
-        pass
-```
-
-**External Customization Interface:**
-
-External repositories can create `gateway/logic/clouds/redshift/packager.py` with:
-
-```python
-def customize_package(package_dir: str, production: bool, functions: dict) -> None:
-    """Customize package with external-specific content.
-
-    Args:
-        package_dir: Path to package directory (full access)
-        production: Whether this is a production build
-        functions: Dictionary of all functions being packaged
-
-    Example use cases:
-        - Add proprietary setup scripts
-        - Generate additional configuration files
-        - Modify package structure for deployment requirements
-    """
-    # Full access to modify package_dir
-    pass
-```
-
-**Key Benefits:**
-- **Core remains generic**: No premium-specific code in open-source core
-- **Convention-based**: Core automatically detects and uses external packager if present
-- **Clean separation**: Extension point is clearly defined and documented
-- **Full flexibility**: External packager has complete access to package directory
-
-**Files Involved:**
-- Core packager: `gateway/logic/clouds/redshift/packager.py` (defines extension point)
-- External packager: Created by external repository at same path
-- Activated during: `make create-package`
-
-### Diff Parameter Handling in Makefiles
-
-When passing file lists through Make targets, **proper quoting is critical** to prevent Make from interpreting space-separated filenames as multiple targets.
-
-**Problem:**
-```makefile
-# WRONG - Each filename becomes a separate target
-$(if $(diff),diff=$(diff),)
-
-# If diff=".github/workflows/redshift.yml Makefile README.md"
-# Make interprets this as three separate targets and fails with:
-# make: *** No rule to make target '.github/workflows/redshift.yml'
-```
-
-**Solution:**
-```makefile
-# CORRECT - Entire string passed as single quoted value
-$(if $(diff),diff='$(diff)',)
-
-# Properly passes: diff='.github/workflows/redshift.yml Makefile README.md'
-```
-
-**Where This Matters:**
-
-1. **Core Root Makefile** (`Makefile`, line 148):
-   ```makefile
-   cd gateway && $(MAKE) deploy cloud=$(cloud) \
-       $(if $(diff),diff='$(diff)',)
-   ```
-
-2. **Gateway Makefile** (`gateway/Makefile`, lines 154, 163):
-   ```makefile
-   # Converts to boolean flag (not the value)
-   $(if $(diff),--diff,)
-   ```
-
-**Architecture Flow:**
-
-```
-CI Workflow / External Caller
-  ↓ diff="file1 file2 file3"
-Core Root Makefile
-  ↓ diff='$(diff)' (quoted!)
-Gateway Makefile
-  ↓ --diff (flag only)
-Python CLI (gateway/logic/clouds/redshift/cli.py)
-  ↓ reads $GIT_DIFF from environment
-  ↓ detects infrastructure changes
-  ↓ decides: deploy ALL or deploy CHANGED
-```
-
-**Infrastructure Change Detection:**
-
-The Python CLI automatically detects infrastructure changes and deploys all functions when these paths are modified:
-- `.github/workflows/` - CI/CD configuration
-- `Makefile` - Build system changes
-- `logic/` - Deployment logic changes
-- `platforms/` - Platform code changes
-- `requirements.txt` - Dependency changes
-
-**Key Points:**
-- Root Makefile must quote: `diff='$(diff)'`
-- Gateway Makefile uses flag: `--diff` (no value)
-- Python CLI reads `$GIT_DIFF` environment variable directly
-- Infrastructure files trigger full deployment automatically
-- Clouds Makefiles don't use diff (always deploy all SQL UDFs)
-
-## Cloud SQL Function Development
-
-### Structure (Redshift Example)
-
-```
-clouds/redshift/
-├── modules/
-│   ├── sql/<module>/          # SQL function definitions
-│   ├── doc/<module>/          # Markdown documentation
-│   └── test/<module>/         # pytest integration tests
-├── libraries/python/          # Python UDFs
-└── version                    # Version file
-```
-
-### Common Commands
-
-```bash
-cd clouds/redshift
-
-# Run tests
-make test
-make test modules=h3
-make test functions=H3_POLYFILL
-
-# Deploy
-make deploy
-make deploy modules=h3
-
-# Lint
-make lint
-
-# Build modules
-make build-modules
-make build-modules modules=h3
-```
-
-### SQL Function Naming Conventions
-
-For Redshift/Snowflake/Postgres:
-
-```sql
--- Definition (parentheses on separate line)
-CREATE OR REPLACE FUNCTION @@RS_SCHEMA@@.H3_POLYFILL
-(
-    geom GEOMETRY,
-    resolution INT
-)
-RETURNS VARCHAR
-...
-
--- Invocation (no space before parentheses)
-SELECT @@RS_SCHEMA@@.H3_POLYFILL(geom, 5)
-```
-
-## Testing
-
-### Test Structure Standards
-
-All gateway function tests follow a standardized structure with clear separation:
-
-**File Structure:**
-```python
-"""
-Unit tests for function_name function.
-
-This file contains:
-- Handler Interface Tests: Validate Lambda handler and batch processing
-- Function Logic Tests: Validate internal algorithms and helpers (if complex)
-"""
-
-# Copyright (c) 2025, CARTO
-
-import json
-from test_utils.unit import load_function_module
-
-# Load handler and functions
-imports = load_function_module(__file__)
-lambda_handler = imports["lambda_handler"]
-
-# For functions with internal helpers to test:
-imports = load_function_module(
-    __file__,
-    {
-        "from_lib": ["function_from_lib"],              # From lib/__init__.py
-        "from_lib_module": {                            # From lib/submodule.py
-            "module_name": ["helper_func"]
-        },
-        "from_handler": ["internal_func"]              # From handler.py itself
-    }
-)
-
-# ============================================================================
-# HANDLER INTERFACE TESTS
-# ============================================================================
-
-class TestLambdaHandler:
-    """Test the Lambda handler interface."""
-    # Tests: empty events, null inputs, batch processing
-
-# ============================================================================
-# FUNCTION LOGIC TESTS (only for complex functions)
-# ============================================================================
-
-class TestHelperFunction:
-    """Test helper_function directly."""
-    # Direct tests of algorithms, edge cases, mathematical correctness
-```
-
-**Testing Tiers:**
-- **Tier 1** (Handler only): Simple functions - validate Lambda interface
-- **Tier 2** (Handler + Logic): Complex functions - also test internal algorithms directly
-- **Tier 3** (Integration): Functions requiring database state validation
-
-**Key Utilities:**
-- `load_function_module(__file__)` - Loads from build directory with shared libs
-- `from_handler` parameter - Access internal functions from handler.py for testing
-
-### Running Tests
-
-```bash
-cd gateway
-
-# Build before testing (required)
-make build cloud=redshift
-
-# Run unit tests
-make test-unit cloud=redshift
-
-# Run integration tests
-make test-integration cloud=redshift
-
-# Run linter
-make lint
+make create-package cloud=redshift   # Create distribution package
+make lint cloud=redshift             # Lint both gateway + clouds
 ```
 
-### Integration Tests
-
-- Connect to real Redshift cluster
-- Require proper `.env` configuration
-- Test deployed functions end-to-end
-
-## Multi-Cloud Support
-
-**Supported clouds (6):** BigQuery, Snowflake, Redshift, Postgres, Databricks, Oracle.
-
-**Gateway (Lambda) functions** are currently **Redshift-only**. All other clouds use native SQL UDFs exclusively. The gateway architecture is extensible but no other cloud has been implemented yet.
-
-Functions can support multiple clouds in function.yaml:
-
-```yaml
-clouds:
-  redshift:
-    type: lambda
-    # ... redshift config
-  snowflake:
-    type: lambda
-    # ... snowflake config
-```
-
-## Branching Strategy
-
-- **`main`**: Development branch. All feature PRs merge here.
-- **`stable`**: Production branch. Only release PRs merge here.
-
-Release branches follow `release/YYYY-MM-DD` naming and target `stable`. After merging, CI publishes packages and deploys to production. See `RELEASING.md` in the parent AT repo for full process.
-
-**Release conventions:**
-- Use `git merge --strategy ours stable` to handle divergence
-- Commit: `release: YYYY-MM-DD` with changelog and bumped versions in body
-- PR title: `Release YYYY-MM-DD`, base: `stable`
-- Version bumps: feat → minor, fix → patch, chore/docs → no bump
-
-## CI/CD Workflows
-
-Each cloud has CI/CD workflows in `.github/workflows/`:
-
-| Cloud | Main Workflow | Dedicated Env |
-|-------|--------------|---------------|
-| BigQuery | `bigquery.yml` | `bigquery-ded.yml` |
-| Snowflake | `snowflake.yml` | `snowflake-ded.yml` |
-| Redshift | `redshift.yml` | `redshift-ded.yml` |
-| Databricks | `databricks.yml` | - |
-| Postgres | `postgres.yml` | `postgres-ded.yml` |
-| Oracle | `oracle.yml` | `oracle-ded.yml` |
-
-Publishing is triggered by `publish-release.yml` on push to `stable`.
-
-## Version Management
-
-Versions defined in `clouds/{cloud}/version` files. Used during `make create-package`.
-
-## Documentation
+Environment templates: `gateway/.env.template`, `clouds/{cloud}/.env.template`.
 
-Function documentation in `clouds/{cloud}/modules/doc/<module>/`:
-- `_INTRO.md` - Module introduction
-- `FUNCTION_NAME.md` - Individual function docs
+## Branching & Releases
 
-Follows markdown format with special metadata headers. See CONTRIBUTING.md for details.
+- **`main`**: development, **`stable`**: production
+- Release branches: `release/YYYY-MM-DD` targeting `stable`
+- `git merge --strategy ours stable` before release commits
+- Version bumps: feat → minor, fix → patch, chore/docs → none
 
-## Pull Request Conventions
+## Conventions
 
-Follow [Conventional Commits](https://www.conventionalcommits.org/):
+[Conventional Commits](https://www.conventionalcommits.org/) with scope `(<cloud(s)>|<module(s)>)`.
+Cloud codes: `bq`, `sf`, `rs`, `pg`, `db`, `ora`.
 
 ```
 feat(rs|quadbin): add quadbin_polyfill function
 fix(sf|h3): fix h3_polyfill boundary handling
 ```
 
-Scope format: `(<cloud(s)>|<module(s)>)`
-
-Cloud codes: `bq` (BigQuery), `sf` (Snowflake), `rs` (Redshift), `pg` (Postgres), `db` (Databricks), `ora` (Oracle)
-
 ## Important Notes
 
-- **Always build before testing gateway**: `make build cloud=redshift` before `make test-unit`
-- **Shared libraries are copied during build**: Changes to `_shared/` require rebuilding
-- **Lambda names must be short**: Use `lambda_name` field to keep under 18 chars total
-- **Two parallel systems**: Gateway (Lambda) and Clouds (native SQL) are deployed independently but packaged together
-
----
-
-## Gateway Architecture Deep Dive
-
-### Cloud and Platform Agnosticism
-
-The gateway deployment engine in `gateway/logic/` is designed to be cloud and platform agnostic:
-
-**Architecture Layers:**
-
-1. **Common Engine** (`gateway/logic/common/engine/`):
-   - `catalog_loader.py`: Discovers and loads function definitions
-   - `models.py`: Cloud-agnostic data models (CloudType, PlatformType, CloudConfig)
-   - `type_mapper.py`: Generic type mapping system with cloud-specific registrations
-   - `validators.py`: Function configuration validation
-   - `packagers.py`: Package creation for distribution
-
-2. **Platform Layer** (`gateway/logic/platforms/`):
-   - `aws-lambda/`: AWS Lambda-specific deployment logic
-   - Extensible for other platforms (GCP Cloud Run, Snowflake Snowpark, etc.)
-
-3. **Cloud Layer** (`gateway/logic/clouds/`):
-   - `redshift/`: Redshift-specific SQL generation and deployment
-   - `sql_template_generator.py`: Auto-generates SQL from function metadata
-   - Extensible for other clouds (BigQuery, Snowflake, Databricks)
-
-### Shared vs Function-Specific Libraries
-
-**Critical Rule**: Only create shared libraries when code is used by **multiple functions**.
-
-**Shared Libraries** (`gateway/functions/_shared/python/`):
-
-- **Purpose**: Code used by multiple functions
-- **Location**: `_shared/python/<module_name>/`
-- **Reference**: Listed in function.yaml `shared_libs` field
-- **Build**: Copied to each function's `lib/<module_name>/` during `make build`
-- **Import**: `from lib.<module_name> import ...`
-
-**Function-Specific Libraries** (`<function>/code/lambda/python/lib/`):
-
-- **Purpose**: Code used by **only one function**
-- **Location**: `code/lambda/python/lib/` within function directory
-- **Reference**: Not in function.yaml (automatically included)
-- **Build**: Included directly in function package
-- **Import**: `from lib.<module> import ...`
-
-**Why This Matters:**
-- Provides **isolation** and **independent versioning** per function
-- Prevents coupling between unrelated functions
-- Allows different functions to evolve independently
-
-### Build System Details
-
-**What happens during `make build cloud=redshift`:**
-
-1. **Discovery Phase**:
-   ```python
-   # Scans for function.yaml files in:
-   gateway/functions/**/function.yaml
-   ```
-
-2. **Validation Phase**:
-   ```python
-   # Validates each function.yaml:
-   - Required fields present
-   - Lambda name ≤18 chars
-   - Shared libs exist
-   - Code files exist
-   ```
-
-3. **Copy Phase**:
-   ```python
-   # For each function with shared_libs:
-   for lib in function.shared_libs:
-       copy _shared/python/{lib}/ to {function}/code/lambda/python/lib/{lib}/
-   ```
-
-4. **Package Phase**:
-   ```python
-   # Creates deployment package for each function:
-   - Copy function code
-   - Install requirements.txt dependencies
-   - Include shared libraries
-   - Create .zip for Lambda deployment
-   ```
-
-**Why build is required before tests:**
-- Tests import from `lib.*` which doesn't exist until build copies shared libraries
-- Each test runs against the actual Lambda deployment structure
-- Ensures tests match production behavior
-
-### Function Configuration Deep Dive
-
-**function.yaml Complete Reference:**
-
-```yaml
-name: function_name
-module: module_name
-
-# Generic type definitions (hybrid functions - NEW)
-parameters:
-  - name: input_data
-    type: string                    # Generic type (maps to VARCHAR(MAX))
-  - name: size
-    type: int                       # Generic type (maps to INT)
-returns: string                     # Return type
-
-clouds:
-  redshift:
-    type: lambda                    # Platform type
-    lambda_name: shortname          # ≤18 chars (with prefix)
-    code_file: code/lambda/python/handler.py
-    requirements_file: code/lambda/python/requirements.txt  # Optional
-    external_function_template: code/redshift.sql  # Optional (auto-generated if omitted)
-    shared_libs:                    # Optional - list of _shared/python/ modules
-      - quadbin
-      - utils
-    config:
-      memory_size: 512              # MB (128-10240, default 512)
-      timeout: 300                  # Seconds (3-900, default 300)
-      max_batch_rows: 100           # Batch size (default 100)
-      runtime: python3.10           # Python runtime
-```
-
-**Generic Type Mapping** (auto-converts to cloud-specific):
-
-| Generic Type | Redshift | BigQuery | Snowflake |
-|--------------|----------|----------|-----------|
-| `string` | `VARCHAR(MAX)` | `STRING` | `VARCHAR` |
-| `int` | `INT` | `INT64` | `INTEGER` |
-| `bigint` | `INT8` | `INT64` | `BIGINT` |
-| `float` | `FLOAT8` | `FLOAT64` | `FLOAT` |
-| `boolean` | `BOOLEAN` | `BOOL` | `BOOLEAN` |
-
-### Deployment Flow
-
-**Complete Deployment Process:**
-
-```
-1. Load Function Catalog (gateway/logic/common/engine/catalog_loader.py)
-   ├─> Scan gateway/functions/
-   └─> Parse all function.yaml files
-
-2. Validate Functions (gateway/logic/common/engine/validators.py)
-   ├─> Check required fields
-   ├─> Validate lambda_name length
-   ├─> Verify shared_libs exist
-   └─> Validate code files exist
-
-3. Package Functions (gateway/logic/common/engine/packagers.py)
-   ├─> Copy function code
-   ├─> Copy shared libraries (if specified)
-   ├─> Install requirements (if specified)
-   └─> Create deployment package (.zip)
-
-4. Deploy to Lambda (gateway/logic/platforms/aws-lambda/)
-   ├─> Upload Lambda package to AWS
-   ├─> Set memory, timeout, runtime config
-   ├─> Configure IAM role
-   └─> Get Lambda ARN
-
-5. Create External Functions (gateway/logic/clouds/redshift/)
-   ├─> Generate SQL from template or auto-generate
-   ├─> Replace @@VARIABLES@@ with actual values
-   ├─> Execute SQL on Redshift
-   └─> Link external function to Lambda ARN
-
-6. Verify Deployment
-   ├─> Test Lambda invocation
-   └─> Test external function call
-```
-
-### Testing Best Practices
-
-**Unit Test Structure:**
-
-```python
-# gateway/functions/module/function/tests/unit/test_function.py
-
-import pytest
-from unittest.mock import Mock, patch
-
-# Import from built structure
-from lib.quadbin import to_geojson
-
-
-def test_process_row_valid_input(handler_module):
-    """Test handler with valid input."""
-    row = ["quadbin_string", 5]
-    result = handler_module.process_row(row)
-    assert result is not None
-
-
-def test_process_row_invalid_input(handler_module):
-    """Test handler with invalid input."""
-    row = []
-    result = handler_module.process_row(row)
-    assert result is None
-
-
-@pytest.fixture
-def handler_module():
-    """Load handler module."""
-    import sys
-    sys.path.insert(0, "code/lambda/python")
-    import handler
-    return handler
-```
-
-### Troubleshooting Guide
-
-**Common Issues:**
-
-1. **Import Error: `ModuleNotFoundError: No module named 'lib'`**
-   - **Cause**: Build not run before tests
-   - **Fix**: `make build cloud=redshift`
-
-2. **Lambda Deploy Fails: `ResourceName too long`**
-   - **Cause**: lambda_name + prefix > 64 chars
-   - **Fix**: Shorten lambda_name in function.yaml to ≤18 chars
-
-3. **Test Import Error: `No module named 'lib.quadbin'`**
-   - **Cause**: shared_libs not specified in function.yaml
-   - **Fix**: Add `shared_libs: [quadbin]` to function.yaml, rebuild
-
-4. **Function Not Found During Deploy**
-   - **Cause**: function.yaml missing or invalid
-   - **Fix**: Validate function.yaml structure, check required fields
-
-5. **External Function Error: `Permission denied for Lambda`**
-   - **Cause**: RS_LAMBDA_INVOKE_ROLE not set or incorrect
-   - **Fix**: Verify IAM role ARN in .env file
-
-6. **Build Copies Wrong Library Version**
-   - **Cause**: Old build artifacts
-   - **Fix**: `make clean && make build cloud=redshift`
-
-## Extending Cloud Support
-
-The gateway uses a registry pattern for cloud-specific type mappings, allowing new clouds to be added without modifying core code.
-
-### Type Mapping Architecture
-
-**TypeMapperRegistry** (`core/gateway/logic/common/engine/type_mapper.py`):
-- Cloud-agnostic registry maintaining type mapping providers
-- Each cloud registers its own TypeMappingProvider implementation
-- Provides unified interface: `TypeMapperRegistry.map_type("string", "redshift")` → `"VARCHAR(MAX)"`
-
-### Adding a New Cloud
-
-To add support for a new cloud (e.g., BigQuery, Snowflake):
-
-**1. Create cloud-specific type mappings:**
-
-```python
-# core/gateway/logic/clouds/bigquery/type_mappings.py
-from ...common.engine.type_mapper import TypeMapperRegistry
-
-class BigQueryTypeMappings:
-    """BigQuery-specific type mapping provider"""
-
-    TYPE_MAPPINGS = {
-        "string": "STRING",
-        "int": "INT64",
-        "bigint": "INT64",
-        "float": "FLOAT64",
-        "double": "FLOAT64",
-        "boolean": "BOOL",
-        "bytes": "BYTES",
-        "object": "JSON",
-        "geometry": "GEOGRAPHY",  # BigQuery uses GEOGRAPHY for spatial
-        "geography": "GEOGRAPHY",
-    }
-
-    def map_type(self, generic_type: str) -> str:
-        """Map generic type to BigQuery SQL type"""
-        generic_lower = generic_type.lower()
-        if generic_lower in self.TYPE_MAPPINGS:
-            return self.TYPE_MAPPINGS[generic_lower]
-        return generic_type  # Already cloud-specific
-
-    def is_generic_type(self, type_str: str) -> bool:
-        """Check if type is generic"""
-        return type_str.lower() in self.TYPE_MAPPINGS
-
-    def get_supported_generic_types(self) -> list[str]:
-        """Get supported generic types"""
-        return list(self.TYPE_MAPPINGS.keys())
-
-# Auto-register when module is imported
-_bigquery_mapper = BigQueryTypeMappings()
-TypeMapperRegistry.register("bigquery", _bigquery_mapper)
-```
-
-**2. Update CloudType enum:**
-
-```python
-# core/gateway/logic/common/engine/models.py
-class CloudType(Enum):
-    """Supported cloud platforms"""
-    REDSHIFT = "redshift"
-    BIGQUERY = "bigquery"  # Add new cloud
-```
-
-**3. Import the mapping in your cloud CLI:**
-
-```python
-# core/gateway/logic/clouds/bigquery/cli.py
-from .type_mappings import BigQueryTypeMappings  # Triggers auto-registration
-```
-
-**4. Implement cloud-specific deployment logic:**
-- SQL template generator (like `RedshiftSQLTemplateGenerator`)
-- Template renderer for cloud-specific SQL syntax
-- CLI commands for deployment
-- Pre-flight checks and validation
-
-### Current Implementation
-
-**Redshift** (`core/gateway/logic/clouds/redshift/type_mappings.py`):
-- Implements `RedshiftTypeMappings` class
-- Maps generic types to Redshift SQL types (VARCHAR(MAX), INT8, SUPER, etc.)
-- Auto-registers on import via `TypeMapperRegistry.register("redshift", ...)`
-
-### Future Development Guidelines
-
-**When adding new functions:**
-
-1. Determine if code should be shared or function-specific
-2. Use shared library only if used by 2+ functions
-3. Keep lambda_name ≤18 characters
-4. Add comprehensive unit tests
-5. Use generic types in function.yaml when possible
-6. Follow existing handler patterns
-7. Build and test before committing
-
-**When modifying shared libraries:**
-
-1. Consider impact on all dependent functions
-2. Run tests for all dependent functions
-3. Avoid breaking changes
-4. Update shared library documentation
-5. Rebuild all dependent functions
+- **Build before testing gateway**: `make build` copies shared libs required by tests
+- **Gateway is Redshift-only**: all other clouds use native SQL UDFs exclusively
+- **Lambda names ≤18 chars**: use `lambda_name` field in `function.yaml`
+- **Two independent systems**: Gateway and Clouds deploy separately but package together
 
-**When refactoring:**
+## Detailed Documentation
 
-1. Maintain backward compatibility
-2. Keep function signatures unchanged
-3. Update tests to match changes
-4. Verify deployment after refactoring
-5. Document architectural decisions
+Cloud-specific configuration, gateway architecture, testing, function development, CI/CD, versioning, and extending cloud support are in `.claude/rules/`. Loaded automatically when working on matching file paths.
PATCH

echo "Gold patch applied."
