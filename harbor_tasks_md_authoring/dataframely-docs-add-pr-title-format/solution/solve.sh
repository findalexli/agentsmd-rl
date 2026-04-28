#!/usr/bin/env bash
set -euo pipefail

cd /workspace/dataframely

# Idempotency guard
if grep -qF "- `style`: Changes that do not affect the meaning of the code (white-space, form" ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -206,6 +206,29 @@ validated_df: dy.DataFrame[MySchema] = MySchema.validate(df, cast=True)
 4. **Documentation**: Update docstrings
 5. **API changes**: Ensure backward compatibility or document migration path
 
+### Pull request titles (required)
+
+Pull request titles must follow the Conventional Commits format: `<type>[!]: <Subject>`
+
+Allowed `type` values:
+
+- `feat`: A new feature
+- `fix`: A bug fix
+- `docs`: Documentation only changes
+- `style`: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)
+- `refactor`: A code change that neither fixes a bug nor adds a feature
+- `perf`: A code change that improves performance
+- `test`: Adding missing tests or correcting existing tests
+- `build`: Changes that affect the build system or external dependencies
+- `ci`: Changes to our CI configuration files and scripts
+- `chore`: Other changes that don't modify src or test files
+- `revert`: Reverts a previous commit
+
+Additional rules:
+
+- Use `!` only for **breaking changes**
+- `Subject` must start with an **uppercase** letter and must **not** end with `.` or a trailing space
+
 ## Performance Considerations
 
 - Validation uses native polars expressions for performance
PATCH

echo "Gold patch applied."
