#!/usr/bin/env bash
set -euo pipefail

cd /workspace/homematicip-local

# Idempotency guard
if grep -qF "- **aiohomematic** (v2025.12.17) - Core async library for Homematic device commu" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -6,7 +6,7 @@ This document provides comprehensive guidance for AI assistants working with the
 
 **Project Name:** Homematic(IP) Local for OpenCCU
 **Type:** Home Assistant Custom Integration
-**Version:** 1.91.0
+**Version:** 2.0.0
 **Primary Language:** Python 3.13+
 **Domain:** `homematicip_local`
 
@@ -88,17 +88,17 @@ homematicip_local/
 ## Key Technologies & Dependencies
 
 ### Runtime Dependencies
-- **aiohomematic** (v2025.12.1) - Core async library for Homematic device communication
-- **Home Assistant Core** - Minimum version: 2025.8.0+
+- **aiohomematic** (v2025.12.17) - Core async library for Homematic device communication
+- **Home Assistant Core** - Minimum version: 2025.10.0+
 - **Python 3.13+** (target version for development)
 
 ### Development Dependencies
-- **pytest-homeassistant-custom-component** (0.13.297) - HA test framework
+- **pytest-homeassistant-custom-component** (0.13.300) - HA test framework
 - **mypy** (1.18.2) - Static type checker (strict mode)
-- **pylint** (4.0.3) - Code linting
-- **ruff** (0.14.5) - Fast Python linter and formatter
+- **pylint** (4.0.4) - Code linting
+- **ruff** (0.14.8) - Fast Python linter and formatter
 - **pre-commit** (4.5.0) - Git hooks manager
-- **aiohomematic-test-support** (2025.12.1) - Mock test data
+- **aiohomematic-test-support** (2025.12.17) - Mock test data
 - **async-upnp-client** (0.46.0) - UPnP discovery
 - **uv** - Fast Python package installer (preferred over pip)
 
@@ -431,8 +431,8 @@ Events fired by the integration:
 
 1. **`manifest.json`**
    - Integration metadata
-   - Version: 1.91.0
-   - Dependencies: aiohomematic==2025.12.1
+   - Version: 2.0.0
+   - Dependencies: aiohomematic==2025.12.17
    - Integration type: hub
    - IoT class: local_push
 
@@ -713,7 +713,7 @@ Devices have parameters that can be:
 
 Config entry migrations (`async_migrate_entry` in `__init__.py`) are **only needed** when the **data structure** stored in config entries changes.
 
-**Current version:** 10 (as of 2025-11)
+**Current version:** 12 (as of 2025-12)
 
 **Migration is required when:**
 - ✅ Adding new keys to config entry data
@@ -781,10 +781,10 @@ entry.data = {
 
 ## Version Information
 
-- **Current Version:** 1.91.0
-- **Minimum HA Version:** 2025.8.0+
+- **Current Version:** 2.0.0
+- **Minimum HA Version:** 2025.10.0+
 - **Python Target:** 3.13+ (CI tests on 3.13, 3.14)
-- **aiohomematic Version:** 2025.12.1
+- **aiohomematic Version:** 2025.12.17
 
 ## External Resources
 
@@ -866,7 +866,7 @@ When working with this codebase:
 12. **Understand migration requirements**:
     - ✅ Migration needed: Data structure changes (add/remove/modify keys)
     - ❌ No migration needed: UI/UX changes, flow reorganization, translation updates
-    - Current version: 10 - always increment when migrating
+    - Current version: 12 - always increment when migrating
 
 13. **Config flow best practices**:
     - Validate early (immediately after credential entry)
PATCH

echo "Gold patch applied."
