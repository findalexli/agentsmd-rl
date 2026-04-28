"""Behavioral checks for analytics-toolbox-core-chore-optimize-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/analytics-toolbox-core")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/bigquery.md')
    assert '- Modules: h3, quadbin, s2, placekey, constructors, transformations, processing, clustering, random' in text, "expected to find: " + '- Modules: h3, quadbin, s2, placekey, constructors, transformations, processing, clustering, random'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/bigquery.md')
    assert 'Create a `.env` file in `clouds/bigquery/` (template: `clouds/bigquery/.env.template`):' in text, "expected to find: " + 'Create a `.env` file in `clouds/bigquery/` (template: `clouds/bigquery/.env.template`):'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/bigquery.md')
    assert '- Uses JavaScript libraries (built with `build_modules.js`) and Jest for testing' in text, "expected to find: " + '- Uses JavaScript libraries (built with `build_modules.js`) and Jest for testing'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/ci-cd.md')
    assert 'When passing file lists through Make targets, **proper quoting is critical** to prevent Make from interpreting space-separated filenames as multiple targets.' in text, "expected to find: " + 'When passing file lists through Make targets, **proper quoting is critical** to prevent Make from interpreting space-separated filenames as multiple targets.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/ci-cd.md')
    assert '- **Publish**: Triggered by `publish-release.yml` on push to `stable`. Creates GitHub Release, publishes packages to GCS, deploys to production.' in text, "expected to find: " + '- **Publish**: Triggered by `publish-release.yml` on push to `stable`. Creates GitHub Release, publishes packages to GCS, deploys to production.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/ci-cd.md')
    assert 'The Python CLI automatically detects infrastructure changes and deploys all functions when these paths are modified:' in text, "expected to find: " + 'The Python CLI automatically detects infrastructure changes and deploys all functions when these paths are modified:'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/cloud-sql-testing.md')
    assert '- **JavaScript**: `clouds/{cloud}/common/test-utils.js` — provides `runQuery()`, `loadTable()`, `deleteTable()`, `readJSONFixture()`' in text, "expected to find: " + '- **JavaScript**: `clouds/{cloud}/common/test-utils.js` — provides `runQuery()`, `loadTable()`, `deleteTable()`, `readJSONFixture()`'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/cloud-sql-testing.md')
    assert '- **Python**: `clouds/{cloud}/common/test_utils/__init__.py` — provides `run_query()`, `run_queries()`, `get_cursor()`' in text, "expected to find: " + '- **Python**: `clouds/{cloud}/common/test_utils/__init__.py` — provides `run_query()`, `run_queries()`, `get_cursor()`'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/cloud-sql-testing.md')
    assert '- Test values should match canonical outputs from the reference cloud (Databricks for Quadbin, BigQuery for H3)' in text, "expected to find: " + '- Test values should match canonical outputs from the reference cloud (Databricks for Quadbin, BigQuery for H3)'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/databricks.md')
    assert 'Create a `.env` file in `clouds/databricks/` (template: `clouds/databricks/.env.template`):' in text, "expected to find: " + 'Create a `.env` file in `clouds/databricks/` (template: `clouds/databricks/.env.template`):'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/databricks.md')
    assert 'DB_PREFIX=yourname_            # Schema prefix (e.g., "yourname_" -> "yourname_carto")' in text, "expected to find: " + 'DB_PREFIX=yourname_            # Schema prefix (e.g., "yourname_" -> "yourname_carto")'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/databricks.md')
    assert '- Deploy scripts in `clouds/databricks/common/`: `run_query.py`, `create_schema.py`' in text, "expected to find: " + '- Deploy scripts in `clouds/databricks/common/`: `run_query.py`, `create_schema.py`'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/extending-clouds.md')
    assert 'The gateway uses a registry pattern for cloud-specific type mappings, allowing new clouds to be added without modifying core code.' in text, "expected to find: " + 'The gateway uses a registry pattern for cloud-specific type mappings, allowing new clouds to be added without modifying core code.'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/extending-clouds.md')
    assert '- Provides unified interface: `TypeMapperRegistry.map_type("string", "redshift")` -> `"VARCHAR(MAX)"`' in text, "expected to find: " + '- Provides unified interface: `TypeMapperRegistry.map_type("string", "redshift")` -> `"VARCHAR(MAX)"`'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/extending-clouds.md')
    assert 'from .type_mappings import BigQueryTypeMappings  # Triggers auto-registration' in text, "expected to find: " + 'from .type_mappings import BigQueryTypeMappings  # Triggers auto-registration'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/function-dev.md')
    assert 'Place reusable code in `gateway/functions/_shared/python/<lib_name>/` and reference via `shared_libs` in function.yaml. The build system copies these to `lib/<lib_name>/` in the Lambda package.' in text, "expected to find: " + 'Place reusable code in `gateway/functions/_shared/python/<lib_name>/` and reference via `shared_libs` in function.yaml. The build system copies these to `lib/<lib_name>/` in the Lambda package.'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/function-dev.md')
    assert "**Critical Rule**: Only create shared libraries when code is used by **multiple functions** (2+). Single-function code should live in the function's own `code/lambda/python/lib/` directory." in text, "expected to find: " + "**Critical Rule**: Only create shared libraries when code is used by **multiple functions** (2+). Single-function code should live in the function's own `code/lambda/python/lib/` directory."[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/function-dev.md')
    assert 'For CI/CD prefixes (e.g., `ci_12345678_123456_`), function names should be <=18 chars to stay within the 64-character total AWS Lambda name limit.' in text, "expected to find: " + 'For CI/CD prefixes (e.g., `ci_12345678_123456_`), function names should be <=18 chars to stay within the 64-character total AWS Lambda name limit.'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/gateway.md')
    assert "Core's packaging system supports extensibility through a **try/except import pattern** that allows external repositories (like premium) to customize packages without modifying core code." in text, "expected to find: " + "Core's packaging system supports extensibility through a **try/except import pattern** that allows external repositories (like premium) to customize packages without modifying core code."[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/gateway.md')
    assert "This ensures packages contain `@@RS_SCHEMA@@` as a literal template, which the installer then replaces with the user's chosen schema name." in text, "expected to find: " + "This ensures packages contain `@@RS_SCHEMA@@` as a literal template, which the installer then replaces with the user's chosen schema name."[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/gateway.md')
    assert 'All gateway deployment logic is in `gateway/logic/` and is designed to be cloud and platform agnostic.' in text, "expected to find: " + 'All gateway deployment logic is in `gateway/logic/` and is designed to be cloud and platform agnostic.'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/oracle.md')
    assert '**Note**: Oracle uses wallet-based authentication, unique among all supported clouds. Schemas use UPPERCASE naming convention (e.g., `DEV_CARTO`).' in text, "expected to find: " + '**Note**: Oracle uses wallet-based authentication, unique among all supported clouds. Schemas use UPPERCASE naming convention (e.g., `DEV_CARTO`).'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/oracle.md')
    assert '`H3_KEY`, `H3_BOUNDARY`, `H3_CENTER`, `H3_RESOLUTION`, `H3_PARENT`, `H3_IS_VALID_CELL`, `H3_IS_PENTAGON`, `H3_BASE_CELL`, `H3_NUM_CELLS`, `H3_MBR`' in text, "expected to find: " + '`H3_KEY`, `H3_BOUNDARY`, `H3_CENTER`, `H3_RESOLUTION`, `H3_PARENT`, `H3_IS_VALID_CELL`, `H3_IS_PENTAGON`, `H3_BASE_CELL`, `H3_NUM_CELLS`, `H3_MBR`'[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/oracle.md')
    assert '- Pure SQL functions: `CREATE OR REPLACE FUNCTION ... RETURN ... IS BEGIN ... END;` with `/` terminator' in text, "expected to find: " + '- Pure SQL functions: `CREATE OR REPLACE FUNCTION ... RETURN ... IS BEGIN ... END;` with `/` terminator'[:80]


def test_signal_24():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/packaging.md')
    assert '**IMPORTANT**: The `--non-interactive` flag is **required** to skip all prompts. Without it, the installer will prompt interactively even if all parameters are provided.' in text, "expected to find: " + '**IMPORTANT**: The `--non-interactive` flag is **required** to skip all prompts. Without it, the installer will prompt interactively even if all parameters are provided.'[:80]


def test_signal_25():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/packaging.md')
    assert "Core's packaging supports extensibility through a **try/except import pattern** that lets external repos (like premium) customize packages without modifying core code." in text, "expected to find: " + "Core's packaging supports extensibility through a **try/except import pattern** that lets external repos (like premium) customize packages without modifying core code."[:80]


def test_signal_26():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/packaging.md')
    assert 'BigQuery, Snowflake, Databricks, Oracle, Postgres: use `make deploy` directly — deploys SQL UDFs without Lambda or installer.' in text, "expected to find: " + 'BigQuery, Snowflake, Databricks, Oracle, Postgres: use `make deploy` directly — deploys SQL UDFs without Lambda or installer.'[:80]


def test_signal_27():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/postgres.md')
    assert '- Modules: h3, quadbin, s2, placekey, constructors, transformations, processing, clustering, random' in text, "expected to find: " + '- Modules: h3, quadbin, s2, placekey, constructors, transformations, processing, clustering, random'[:80]


def test_signal_28():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/postgres.md')
    assert 'Create a `.env` file in `clouds/postgres/` (template: `clouds/postgres/.env.template`):' in text, "expected to find: " + 'Create a `.env` file in `clouds/postgres/` (template: `clouds/postgres/.env.template`):'[:80]


def test_signal_29():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/postgres.md')
    assert '- JS libraries: `clouds/postgres/libraries/javascript/`' in text, "expected to find: " + '- JS libraries: `clouds/postgres/libraries/javascript/`'[:80]


def test_signal_30():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/redshift.md')
    assert '- Modules: h3, quadbin, s2, placekey, constructors, transformations, processing, clustering, random' in text, "expected to find: " + '- Modules: h3, quadbin, s2, placekey, constructors, transformations, processing, clustering, random'[:80]


def test_signal_31():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/redshift.md')
    assert 'RS_LAMBDA_PREFIX=yourname-at-dev  # Prefix for Lambda functions (max 46 chars, total name <=64)' in text, "expected to find: " + 'RS_LAMBDA_PREFIX=yourname-at-dev  # Prefix for Lambda functions (max 46 chars, total name <=64)'[:80]


def test_signal_32():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/redshift.md')
    assert 'Create a `.env` file in the repository root or `gateway/` (template: `gateway/.env.template`):' in text, "expected to find: " + 'Create a `.env` file in the repository root or `gateway/` (template: `gateway/.env.template`):'[:80]


def test_signal_33():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/snowflake.md')
    assert '- Modules: h3, quadbin, s2, placekey, constructors, transformations, processing, clustering, random' in text, "expected to find: " + '- Modules: h3, quadbin, s2, placekey, constructors, transformations, processing, clustering, random'[:80]


def test_signal_34():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/snowflake.md')
    assert 'Create a `.env` file in `clouds/snowflake/` (template: `clouds/snowflake/.env.template`):' in text, "expected to find: " + 'Create a `.env` file in `clouds/snowflake/` (template: `clouds/snowflake/.env.template`):'[:80]


def test_signal_35():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/snowflake.md')
    assert 'SF_ENDPOINT=<url>                # Optional AT Gateway Cloud Run service URL' in text, "expected to find: " + 'SF_ENDPOINT=<url>                # Optional AT Gateway Cloud Run service URL'[:80]


def test_signal_36():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/testing.md')
    assert '> This rule covers **gateway-specific** testing (Lambda handlers, Python unit/integration tests). For cloud SQL testing patterns (pytest, Jest, fixtures), see the cloud-sql-testing rule which loads au' in text, "expected to find: " + '> This rule covers **gateway-specific** testing (Lambda handlers, Python unit/integration tests). For cloud SQL testing patterns (pytest, Jest, fixtures), see the cloud-sql-testing rule which loads au'[:80]


def test_signal_37():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/testing.md')
    assert 'Integration tests connect to real Redshift clusters and test deployed functions. They require proper `.env` configuration and deployed functions.' in text, "expected to find: " + 'Integration tests connect to real Redshift clusters and test deployed functions. They require proper `.env` configuration and deployed functions.'[:80]


def test_signal_38():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/testing.md')
    assert '- `from_lib_module` - Access functions from `lib/submodule.py` (dict of `{module_name: [func_names]}`)' in text, "expected to find: " + '- `from_lib_module` - Access functions from `lib/submodule.py` (dict of `{module_name: [func_names]}`)'[:80]


def test_signal_39():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/versioning.md')
    assert '- `.github/workflows/publish-release.yml` detects which version files changed to determine which clouds to publish' in text, "expected to find: " + '- `.github/workflows/publish-release.yml` detects which version files changed to determine which clouds to publish'[:80]


def test_signal_40():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/versioning.md')
    assert '- `make create-package` reads `clouds/{cloud}/version` to name packages (`carto-at-{cloud}-VERSION.zip`)' in text, "expected to find: " + '- `make create-package` reads `clouds/{cloud}/version` to name packages (`carto-at-{cloud}-VERSION.zip`)'[:80]


def test_signal_41():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/versioning.md')
    assert 'Each cloud has independent versions in plain text files: `clouds/{cloud}/version` (e.g., `1.2.7`).' in text, "expected to find: " + 'Each cloud has independent versions in plain text files: `clouds/{cloud}/version` (e.g., `1.2.7`).'[:80]


def test_signal_42():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Cloud-specific configuration, gateway architecture, testing, function development, CI/CD, versioning, and extending cloud support are in `.claude/rules/`. Loaded automatically when working on matching' in text, "expected to find: " + 'Cloud-specific configuration, gateway architecture, testing, function development, CI/CD, versioning, and extending cloud support are in `.claude/rules/`. Loaded automatically when working on matching'[:80]


def test_signal_43():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**CARTO Analytics Toolbox Core** is a multi-cloud spatial analytics platform providing UDFs and Stored Procedures for BigQuery, Snowflake, Redshift, Postgres, Databricks, and Oracle. Two parallel syst' in text, "expected to find: " + '**CARTO Analytics Toolbox Core** is a multi-cloud spatial analytics platform providing UDFs and Stored Procedures for BigQuery, Snowflake, Redshift, Postgres, Databricks, and Oracle. Two parallel syst'[:80]


def test_signal_44():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Clouds** (`clouds/{cloud}/`): Native SQL UDFs per platform (6 clouds, each with `modules/sql/`, `modules/test/`, `libraries/`, `common/`, `version`)' in text, "expected to find: " + '- **Clouds** (`clouds/{cloud}/`): Native SQL UDFs per platform (6 clouds, each with `modules/sql/`, `modules/test/`, `libraries/`, `common/`, `version`)'[:80]

