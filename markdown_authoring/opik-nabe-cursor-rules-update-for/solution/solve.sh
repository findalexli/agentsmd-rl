#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opik

# Idempotency guard
if grep -qF "**Rule**: Always use existing utility classes and helper methods instead of re-i" "apps/opik-backend/.cursor/rules/code_style.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/apps/opik-backend/.cursor/rules/code_style.mdc b/apps/opik-backend/.cursor/rules/code_style.mdc
@@ -96,11 +96,113 @@ public void processUsers(com.external.lib.User externalUser, User internalUser)
 }
 ```
 
+## Prefer Shared Helpers
+
+**Rule**: Always use existing utility classes and helper methods instead of re-implementing common patterns. This ensures consistency, reduces duplication, and leverages properly configured shared instances.
+
+### String Validation
+
+Use Apache Commons `StringUtils` for null-safe string checks:
+
+```java
+// ❌ BAD: Manual null checks and empty string validation
+if (value == null || value.isEmpty() || value.trim().isEmpty()) {
+    // handle blank
+}
+
+// ✅ GOOD: Use StringUtils for null-safe checks
+import org.apache.commons.lang3.StringUtils;
+
+if (StringUtils.isBlank(value)) {
+    // handle blank
+}
+
+if (StringUtils.isNotBlank(provider)) {
+    // use provider
+}
+```
+
+**When to use**:
+- `StringUtils.isBlank()`: Checks for null, empty, or whitespace-only strings
+- `StringUtils.isNotBlank()`: Inverse of `isBlank()` - returns true for non-null, non-empty, non-whitespace strings
+- Use throughout the codebase for mode/provider parsing, field validation, and conditional logic
+
+### JSON Processing
+
+Use `JsonUtils` for all JSON operations instead of creating new `ObjectMapper` instances:
+
+```java
+// ❌ BAD: Creating new ObjectMapper instances
+ObjectMapper mapper = new ObjectMapper();
+JsonNode node = mapper.readTree(jsonString);
+
+// ✅ GOOD: Use shared JsonUtils
+import com.comet.opik.utils.JsonUtils;
+
+JsonNode node = JsonUtils.getJsonNodeFromString(jsonString);
+String json = JsonUtils.writeValueAsString(object);
+ObjectNode objNode = JsonUtils.createObjectNode();
+```
+
+**Why**: `JsonUtils` provides a centrally configured `ObjectMapper` that:
+- Matches Dropwizard's configuration (snake_case naming, date handling, etc.)
+- Respects `config.yml` settings for stream read constraints
+- Includes custom deserializers (BigDecimal, Message, Duration)
+- Ensures consistent JSON processing across the application
+
+**Exceptions**:
+- **Tests**: Creating `new ObjectMapper()` in test classes is acceptable when testing serialization/deserialization behavior
+- **Infrastructure classes**: Classes like `JsonNodeArgumentFactory` that need isolated instances for specific use cases
+
+### Factory Methods for Default Values
+
+When classes need default or "empty" instances, provide static factory methods:
+
+```java
+// ✅ GOOD: Factory method for empty/default instance
+@Builder(toBuilder = true)
+public record ModelPrice(
+    @NonNull BigDecimal inputPrice,
+    @NonNull BigDecimal outputPrice,
+    // ... other fields
+) {
+    public static ModelPrice empty() {
+        return new ModelPrice(
+            BigDecimal.ZERO,
+            BigDecimal.ZERO,
+            // ... zeroed values
+        );
+    }
+}
+
+// Usage
+ModelPrice price = ModelPrice.empty();
+```
+
 **Benefits**:
-- Improves code readability
-- Makes dependencies clear at the top of the file
-- Follows Java conventions
-- Easier to maintain and refactor
+- Single source of truth for default values
+- Clear intent when creating empty instances
+- Easier to maintain if default values change
+- Works well with `@Builder(toBuilder = true)` for immutable updates
+
+### Other Utility Classes
+
+The codebase provides several utility classes for common operations:
+
+- **`ValidationUtils`**: Validation constants and patterns (e.g., `NULL_OR_NOT_BLANK`, `COMMIT_PATTERN`)
+- **`ErrorUtils`**: Standardized error creation (e.g., `failWithNotFound()`)
+- **`TruncationUtils`**: JSON node processing with truncation handling
+- **`PaginationUtils`**: Pagination-related utilities
+
+Always check existing utilities before implementing similar functionality.
+
+## Benefits
+
+- **Consistency**: Shared helpers ensure uniform behavior across the codebase
+- **Maintainability**: Changes to common patterns only need to be made in one place
+- **Configuration**: Shared instances (like `JsonUtils.getMapper()`) respect application configuration
+- **Readability**: Utility methods have clear, descriptive names that improve code clarity
+- **Performance**: Reusing configured instances avoids unnecessary object creation
 
 ## Related Rules
 
PATCH

echo "Gold patch applied."
