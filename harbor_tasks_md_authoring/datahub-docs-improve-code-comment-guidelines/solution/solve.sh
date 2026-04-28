#!/usr/bin/env bash
set -euo pipefail

cd /workspace/datahub

# Idempotency guard
if grep -qF "- What the code does when it's self-evident (`# Loop through items`, `// Set var" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -93,6 +93,39 @@ Each Python module has a gradle setup similar to `metadata-ingestion/` (document
   - **Error Handling**: Robust error handling with layers of protection for known failure points
 - **TypeScript**: Use Prettier formatting, strict types (no `any`), React Testing Library
 
+### Code Comments
+
+Only add comments that provide real value beyond what the code already expresses.
+
+**Do NOT** add comments for:
+
+- Obvious operations (`# Get user by ID`, `// Create connection`)
+- What the code does when it's self-evident (`# Loop through items`, `// Set variable to true`)
+- Restating parameter names or return types already in signatures
+- Basic language constructs (`# Import modules`, `// End of function`)
+
+**DO** add comments for:
+
+- **Why** something is done, especially non-obvious business logic or workarounds
+- **Context** about external constraints, API quirks, or domain knowledge
+- **Warnings** about gotchas, performance implications, or side effects
+- **References** to tickets, RFCs, or external documentation that explain decisions
+- **Complex algorithms** or mathematical formulas that aren't immediately clear
+- **Temporary solutions** with TODOs and context for future improvements
+
+Examples:
+
+```python
+# Good: Explains WHY and provides context
+# Use a 30-second timeout because Snowflake's query API can hang indefinitely
+# on large result sets. See issue #12345.
+connection_timeout = 30
+
+# Bad: Restates what's obvious from code
+# Set connection timeout to 30 seconds
+connection_timeout = 30
+```
+
 ### Testing Strategy
 
 - Python: Tests go in the `tests/` directory alongside `src/`, use `assert` statements
PATCH

echo "Gold patch applied."
