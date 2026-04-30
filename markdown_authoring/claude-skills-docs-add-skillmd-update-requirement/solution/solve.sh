#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-skills

# Idempotency guard
if grep -qF "- `SKILL.md` - User-facing documentation, version in frontmatter, installation i" "CLAUDE.md" && grep -qF "**Function Signatures**: Extracts parameter lists from Python and partial TypeSc" "mapping-codebases/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -78,6 +78,57 @@ find skill-name/ -name "*.py" -o -name "*.md"
 ls -la .claude/skills/skill-name 2>/dev/null
 ```
 
+### CRITICAL: Skills Have Multiple Documentation Files
+
+**SKILL.md is the source of truth** - it's what users see and what triggers releases.
+
+When updating a skill, you MUST update ALL relevant files:
+- `SKILL.md` - User-facing documentation, version in frontmatter, installation instructions
+- `README.md` - Auto-generated but may exist in development
+- Implementation files (scripts/*.py, etc.)
+- Any other documentation
+
+**Common FAILURE pattern:**
+```bash
+# Update implementation
+Edit codemap.py (✓)
+
+# Update README.md
+Edit README.md (✓)
+
+# Forget SKILL.md (✗ CRITICAL FAILURE)
+# - Users get outdated installation instructions
+# - Version not bumped → no release triggered
+# - Frontmatter description outdated
+```
+
+**CORRECT workflow:**
+```bash
+# 1. Update implementation files
+Edit scripts/codemap.py
+
+# 2. Update README.md (if exists)
+Edit README.md
+
+# 3. Update SKILL.md (REQUIRED)
+Edit SKILL.md:
+  - Bump version in frontmatter
+  - Update installation instructions
+  - Update examples to match new features
+  - Update limitations section
+
+# 4. Verify all files consistent
+grep -n "tree-sitter" skill-name/*.md skill-name/scripts/*.py
+# All should show updated package names
+```
+
+**Version bumping triggers releases:**
+- Change `metadata.version` in SKILL.md frontmatter
+- Semantic versioning: major.minor.patch
+- New features = minor bump (0.2.0 → 0.3.0)
+- Bug fixes = patch bump (0.2.0 → 0.2.1)
+- Breaking changes = major bump (0.2.0 → 1.0.0)
+
 ### CLAUDE.md Files Take Priority
 
 If a skill has a `CLAUDE.md` file:
diff --git a/mapping-codebases/SKILL.md b/mapping-codebases/SKILL.md
@@ -2,7 +2,7 @@
 name: mapping-codebases
 description: Generate navigable code maps for unfamiliar codebases. Use when exploring a new codebase, needing to understand project structure, or before diving into code modifications. Extracts exports/imports via AST (tree-sitter) to create _MAP.md files per directory. Triggers on "map this codebase", "understand this project structure", "generate code map", or when starting work on an unfamiliar repository.
 metadata:
-  version: 0.2.0
+  version: 0.3.0
 ---
 
 # Mapping Codebases
@@ -13,7 +13,7 @@ Generate `_MAP.md` files that provide a hierarchical view of code structure with
 
 ```bash
 # Install dependencies (once per session)
-uv pip install tree-sitter==0.21.3 tree-sitter-languages==1.10.2
+uv pip install tree-sitter-language-pack
 
 # Generate maps for a codebase
 python scripts/codemap.py /path/to/repo
@@ -24,8 +24,9 @@ python scripts/codemap.py /path/to/repo
 Per-directory `_MAP.md` files listing:
 - Directory statistics (file count, subdirectory count)
 - Subdirectories (with links to their maps)
-- Files with exports and imports
-- Counts when lists are truncated (e.g., "exports (23)" when showing 8 of 23)
+- **Symbol hierarchy** with kind markers: (C) class, (m) method, (f) function
+- **Function signatures** extracted from AST (Python, partial TypeScript)
+- Import previews
 
 Example output:
 ```markdown
@@ -36,8 +37,15 @@ Example output:
 - [middleware/](./middleware/_MAP.md)
 
 ## Files
-- **jwt.go** — exports: `Claims, ValidateToken` — imports: `context, jwt`
-- **handlers.py** — exports (12): `login, logout, refresh_token`... — imports (8): `flask, .models`...
+
+### handlers.py
+> Imports: `flask, functools, jwt, .models`...
+- **login** (f) `(username: str, password: str)`
+- **logout** (f) `()`
+- **AuthHandler** (C)
+  - **__init__** (m) `(self, config: dict)`
+  - **validate_token** (m) `(self, token: str)`
+  - **refresh_session** (m) `(self, user_id: int)`
 ```
 
 ## Supported Languages
@@ -77,9 +85,11 @@ Maps use hierarchical disclosure - you only load what you need. Even massive cod
 
 ## Features
 
-**Directory Statistics**: Each map header shows file and subdirectory counts, helping you quickly assess scope.
+**Symbol Hierarchy**: Shows classes with nested methods, not just flat lists. See the structure at a glance with kind markers (C/m/f).
 
-**Export/Import Counts**: When truncated, shows total count (e.g., "exports (23)") so you know how much detail exists without cluttering the view.
+**Function Signatures**: Extracts parameter lists from Python and partial TypeScript, showing what functions expect without reading the source.
+
+**Directory Statistics**: Each map header shows file and subdirectory counts, helping you quickly assess scope.
 
 **Hierarchical Navigation**: Links between maps let you traverse the codebase structure naturally without overwhelming context windows.
 
@@ -98,6 +108,8 @@ git add '*/_MAP.md'
 
 ## Limitations
 
-- Extracts structural info only (exports/imports), not semantic descriptions
+- Extracts structural info only (symbols/imports), not semantic descriptions
+- Method extraction: Full support for Python/TypeScript, partial for other languages
+- Signatures: Python (full), TypeScript (partial), others (not extracted)
 - Skips: `.git`, `node_modules`, `__pycache__`, `venv`, `dist`, `build` (plus user-specified patterns)
-- Private symbols (Python `_prefix`) excluded from exports
+- Private symbols (Python `_prefix`) excluded from top-level exports (methods not filtered yet)
PATCH

echo "Gold patch applied."
