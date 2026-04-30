#!/usr/bin/env bash
set -euo pipefail

cd /workspace/fabric-cicd

# Idempotency guard
if grep -qF "Valid values for `item_type_in_scope` are defined in the `ItemType` enum in `src" ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -1,38 +1,125 @@
 # Fabric CICD
 
-fabric-cicd is a Python library for Microsoft Fabric CI/CD automation. It supports code-first Continuous Integration/Continuous Deployment automations to seamlessly integrate Source Controlled workspaces into a deployment framework.
+fabric-cicd is a Python library for Microsoft Fabric CI/CD automation. It supports code-first Continuous Integration/Continuous Deployment automations to integrate Source Controlled workspaces into a deployment framework.
 
 Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.
 
-## Working Effectively
-
--   Bootstrap and set up the development environment:
-    -   Ensure Python 3.9+ is installed
-    -   `pip install uv`
-    -   `uv sync --dev` -- NEVER CANCEL. Set timeout to 120+ seconds.
--   Run tests:
-    -   `uv run pytest -v` -- NEVER CANCEL. Set timeout to 120+ seconds.
--   Code formatting and linting:
-    -   `uv run ruff format` -- Apply formatting fixes.
-    -   `uv run ruff check` -- Check for linting issues.
-    -   `uv run ruff format --check` -- Check if formatting is needed.
--   Documentation:
-    -   `uv run mkdocs build --clean` -- Build documentation.
-    -   `uv run mkdocs serve` -- starts local documentation server.
-
-## Validation
-
--   ALWAYS test library import functionality: `uv run python -c "from fabric_cicd import FabricWorkspace; print('Import successful')"`
--   ALWAYS run through the complete test suite after making changes: `uv run pytest -v`
--   ALWAYS run `uv run ruff format` and `uv run ruff check` before committing or the CI (.github/workflows/validate.yml) will fail
--   The library requires Azure authentication (DefaultAzureCredential) for actual functionality - imports work without auth
+## Quick Command Reference
+
+**Prerequisites**: Requires Python 3.9+
+
+| Task         | Command                                                                                  | Timeout |
+| ------------ | ---------------------------------------------------------------------------------------- | ------- |
+| Setup        | `pip install uv && uv sync --dev` (NEVER CANCEL)                                         | 120+s   |
+| Test         | `uv run pytest -v` (NEVER CANCEL)                                                        | 120+s   |
+| Import check | `uv run python -c "from fabric_cicd import FabricWorkspace; print('Import successful')"` | 30s     |
+| Format       | `uv run ruff format` (Fix formatting issues)                                             | 60s     |
+| Lint check   | `uv run ruff check` (Check for linting issues)                                           | 60s     |
+| Format check | `uv run ruff format --check` (Verify formatting is correct)                              | 60s     |
+| Docs build   | `uv run mkdocs build --clean` (Build documentation)                                      | 60s     |
+| Docs serve   | `uv run mkdocs serve` (Start local documentation server)                                 | 60s     |
+
+**Mandatory Validation (ALWAYS):**
+
+1. Import check → 2. Run tests → 3. Format code → 4. Check linting → 5. Commit
+
+**Critical**: NEVER cancel build/test commands. CI (`.github/workflows/validate.yml`) will fail if validation workflow incomplete.
+
+## Authentication
+
+Must provide explicit `token_credential` parameter to `FabricWorkspace`.
+
+**Methods:**
+
+- **Local development**: `AzureCliCredential()` or `AzurePowerShellCredential()`
+- **CI/CD pipelines**: `ClientSecretCredential()` with service principal
+- **Testing/imports**: No authentication needed
+
+**Example:**
+
+```python
+from azure.identity import AzureCliCredential
+from fabric_cicd import FabricWorkspace
+
+token_credential = AzureCliCredential()
+workspace = FabricWorkspace(
+    workspace_id="your-id",
+    repository_directory="/path/to/workspace/items",
+    token_credential=token_credential
+)
+```
+
+## Basic Usage
+
+### Programmatic API
+
+```python
+from azure.identity import AzureCliCredential
+from fabric_cicd import FabricWorkspace, publish_all_items, unpublish_all_orphan_items
+
+token_credential = AzureCliCredential()
+# Initialize workspace (supports either workspace_id OR workspace_name)
+workspace = FabricWorkspace(
+    workspace_id="your-workspace-id",  # Alternative: workspace_name="your-workspace-name"
+    environment="DEV",
+    repository_directory="/path/to/workspace/items",
+    item_type_in_scope=["Notebook", "DataPipeline", "Environment"],
+    token_credential=token_credential
+)
+
+# Deploy items
+publish_all_items(workspace)
+
+# Clean up orphaned items
+unpublish_all_orphan_items(workspace)
+```
+
+### Config-Based Deployment
+
+Alternative: `deploy_with_config()` centralizes deployment settings in YAML.
+
+```python
+from azure.identity import AzureCliCredential
+from fabric_cicd import deploy_with_config
+token_credential = AzureCliCredential()
+result = deploy_with_config(
+    config_file_path="config.yml",
+    environment="dev",
+    token_credential=token_credential
+)
+```
+
+**Implementation files:**
+
+- Entry points: `deploy_with_config()`, `publish_all_items()`, `unpublish_all_orphan_items()` in `src/fabric_cicd/publish.py`
+- Config utilities: `src/fabric_cicd/_common/_config_utils.py` (loading, extraction)
+- Config validation: `src/fabric_cicd/_common/_config_validator.py`
+- Documentation: `docs/how_to/config_deployment.md`
+- Tests: `tests/test_deploy_with_config.py`, `tests/test_config_validator.py`
+
+### Public API Exports
+
+Only import from the top-level package (`src/fabric_cicd/__init__.py`). Do not import internal modules directly.
+
+**Exported symbols:**
+
+- `FabricWorkspace` - Main workspace management class
+- `publish_all_items` - Deploy all items in scope
+- `unpublish_all_orphan_items` - Remove orphaned items
+- `deploy_with_config` - Config-based deployment
+- `DeploymentResult`, `DeploymentStatus` - Deployment result types
+- `ItemType` - Enum of supported Fabric item types
+- `FeatureFlag` - Enum of feature flags
+- `append_feature_flag` - Add feature flags programmatically
+- `change_log_level`, `configure_external_file_logging`, `disable_file_logging` - Logging utilities
 
 ## Project Structure
 
 ```
 /
 ├── .github/workflows/    # CI/CD pipelines (test.yml, validate.yml, bump.yml)
 ├── docs/                # Documentation source files
+├── docs/example/        # CI/CD scenario patterns (Azure DevOps, GitHub Actions, local development)
 ├── sample/              # Example workspace structure and items
 ├── src/fabric_cicd/     # Main library source code
 ├── tests/               # Test files
@@ -43,104 +130,114 @@ Always reference these instructions first and fallback to search or bash command
 └── uv.lock            # Dependency lock file
 ```
 
-## Common Tasks
+## Development Guidelines
 
-Reference these validated outputs instead of running bash commands to save time:
+### Core Concepts
 
-### Import and Basic Usage
+- **Publisher Classes**: Handle deployment logic for each Fabric item type in `src/fabric_cicd/_items/`
+- **Serial Publishing**: Items deploy in dependency order via `SERIAL_ITEM_PUBLISH_ORDER`
+- **Parameterization**: YAML-based environment-specific value replacement
 
-```python
-from fabric_cicd import FabricWorkspace, publish_all_items, unpublish_all_orphan_items
+### Supported Item Types
 
-# Initialize workspace (requires Azure auth)
-workspace = FabricWorkspace(
-    workspace_id="your-workspace-id",
-    repository_directory="/path/to/workspace/items",
-    item_type_in_scope=["Notebook", "DataPipeline", "Environment"],
-    environment="DEV"
-)
+Valid values for `item_type_in_scope` are defined in the `ItemType` enum in `src/fabric_cicd/constants.py`. Always reference that file for the current list — do not hard-code item type strings without verifying them against the enum.
 
-# Deploy items
-publish_all_items(workspace)
+The publish/unpublish dependency order is defined in `SERIAL_ITEM_PUBLISH_ORDER` in the same file.
 
-# Clean up orphaned items
-unpublish_all_orphan_items(workspace)
-```
+### Common Development Patterns
+
+- **Adding constants**: Add to `ItemType` enum + `SERIAL_ITEM_PUBLISH_ORDER` in `src/fabric_cicd/constants.py`
+- **Adding publisher**: Extend `ItemPublisher` + register in `_base_publisher.py` factory
+- **Adding public exports**: Update `__all__` in `src/fabric_cicd/__init__.py`
+
+### Testing Guidelines
+
+**Always add/update tests for:**
+
+- New functionality or features
+- Bug fixes that change behavior
+- Core logic changes in any module
+- Publisher classes and deployment logic
+- Configuration and validation logic
+- API integrations and external calls
+
+**Testing approach**: Mock all external dependencies, use `requests_mock` for Azure APIs, `tmpdir` for file operations. Focus on testing business logic, error handling, and integration points.
+
+**Test file naming**: Follow the conventions in the `tests/` directory. Review existing test files to match the naming pattern before creating new ones.
+
+### Files to Avoid Modifying
+
+- `coverage_report/`, `site/`, `htmlcov/` - Auto-generated
+- `uv.lock` - Managed by uv
+- `.github/workflows/` - Affects CI validation
+
+### Dependencies & Testing
+
+**Runtime:** `azure-identity`, `dpath`, `pyyaml`, `requests`, `packaging`  
+**Development:** `uv`, `ruff`, `pytest`, `mkdocs-material`
+
+**Test Types:** Unit (`tests/test_*.py`), Integration (mocked APIs), Parameter/File Handling, Workspace management
 
-### Test Categories
+**GitHub Actions:** `test.yml` (PR tests), `validate.yml` (formatting/linting), `bump.yml` (version bumps - vX.X.X format)
 
--   **Unit Tests**: `tests/test_*.py` - Test individual components
--   **Integration Tests**: Validate API interactions (mocked)
--   **Parameter Tests**: Test parameterization and variable replacement
--   **File Handling Tests**: Test various item type processing
--   **Workspace Tests**: Test folder hierarchy and item management
+**Microsoft Fabric APIs:** https://learn.microsoft.com/en-us/rest/api/fabric/
 
-### Key Dependencies
+## Pull Request Requirements
 
--   `azure-identity` - Azure authentication
--   `dpath` - JSON path manipulation
--   `pyyaml` - YAML parameter file processing
--   `requests` - HTTP API calls
--   `packaging` - Version handling
+**Base branch:** Always target `main` unless otherwise specified.
 
-### Development Dependencies
+**Title format:** "Fixes #123 - Short Description" where #123 is the issue number
 
--   `uv` - Package manager and virtual environment
--   `ruff` - Code formatting and linting
--   `pytest` - Testing framework
--   `mkdocs-material` - Documentation generation
+- Use "Fixes" for bug fixes, "Closes" for features, "Resolves" for other changes
+- Example: "Fixes #520 - Add Python version requirements to documentation"
+- Exception: Version bump PRs use "vX.X.X" format only
 
-### GitHub Actions Workflows
+**Requirements:**
 
--   **test.yml**: Runs `uv run pytest -v` on PR
--   **validate.yml**: Runs `ruff format` and `ruff check` validation
--   **bump.yml**: Handles version bumps (requires PR title format vX.X.X)
+- PR description should be copilot generated summary
+- Pass ruff formatting and linting checks
+- Pass all tests
+- All PRs must be linked to valid GitHub issue
 
-### Authentication Requirements
+## Do Not
 
--   Uses Azure DefaultAzureCredential by default
--   Requires Azure CLI (`az login`) or Az.Accounts PowerShell module for local development
--   Service principal authentication supported for CI/CD pipelines
--   No authentication needed for basic library imports or testing
+- Do not modify `uv.lock` manually — it is managed by `uv`
+- Do not import from internal modules (e.g., `fabric_cicd._items`) — only use the public API from `fabric_cicd`
+- Do not add `print()` statements — use the standard `logging` module
+- Do not create PRs without a linked GitHub issue
+- Do not modify `.github/workflows/` files unless explicitly required
 
-### Microsoft Fabric APIs
+## Agent Troubleshooting
 
--   The library primarily integrates with Microsoft Fabric Core APIs
--   API documentation: https://learn.microsoft.com/en-us/rest/api/fabric/
--   Common API operations include workspace management, item publishing, and artifact deployment
+**Common Failures:**
 
-### Timing Expectations and Timeouts
+- **Import errors**: Use `uv run python` prefix to ensure virtual environment
+- **Test pollution**: Azure credentials interfering - ensure proper mocking
+- **Setup failures**: Run `uv sync --dev` if modules missing
+- **Formatting issues**: Run `uv run ruff format` to auto-fix most issues
+- **CI failures**: Missing format/lint step in validation workflow
 
--   **CRITICAL**: NEVER CANCEL any build or test commands. Always use adequate timeouts:
-    -   uv sync: 120+ seconds
-    -   pytest: 120+ seconds
-    -   All other commands: 60+ seconds
+**Authentication Strategy for Agents:**
 
-### Pull Request Requirements
+1. For testing/imports: No auth needed
+2. For publish operations: Use `AzureCliCredential()` (If `CredentialUnavailableError` occurs, user needs to run `az login` first)
+3. Context: Import check works without auth, but publish operations require credentials
 
--   **PR Title MUST follow this exact format**: "Fixes #123 - Short Description" where #123 is the issue number
-    -   Use "Fixes" for bug fixes, "Closes" for features, "Resolves" for other changes
-    -   Example: "Fixes #520 - Add Python version requirements to documentation"
-    -   Version bump PRs are an exception: title must be "vX.X.X" format only
--   PR description should be a copilot generated summary
--   MUST pass ruff formatting and linting checks
--   MUST pass all tests
--   All PRs must be linked to a valid GitHub issue - no PRs without associated issues
+## Key Files to Monitor
 
-### Common Troubleshooting
+**Core System Files:**
 
--   **Import errors**: Use `uv run python` instead of direct `python` to ensure virtual environment
--   **Test failures**: Check if Azure credentials are interfering with mocked tests
--   **Formatting issues**: Run `uv run ruff format` to auto-fix most issues
--   **CI failures**: Usually due to missing `ruff format` or failing tests
+- `src/fabric_cicd/constants.py` - Version and configuration constants
+- `src/fabric_cicd/fabric_workspace.py` - Main workspace management class
+- `src/fabric_cicd/publish.py` - Main deployment entry points
+- `src/fabric_cicd/_items/` - Publisher classes for all item types
+- `src/fabric_cicd/_common/` - Config utilities, validation, and exceptions
 
-### Repository Examples
+**Configuration Files:**
 
-See `sample/workspace/` for example Microsoft Fabric item structures and `docs/example/` for usage patterns in different CI/CD scenarios (Azure DevOps, GitHub Actions, local development).
+- `pyproject.toml` - Project dependencies and configuration
+- `sample/workspace/parameter.yml` - Environment-specific parameter template
 
-### Key Files to Monitor
+**Project Structure:**
 
--   `src/fabric_cicd/constants.py` - Version and configuration constants
--   `src/fabric_cicd/fabric_workspace.py` - Main workspace management class
--   `pyproject.toml` - Project dependencies and configuration
--   `parameter.yml` - Environment-specific parameter template (in sample/)
+- `sample/workspace/` - Example Microsoft Fabric item structures
PATCH

echo "Gold patch applied."
