#!/usr/bin/env bash
set -euo pipefail

cd /workspace/magento-lts

# Idempotency guard
if grep -qF "- Ignore support for PHP versions below PHP 8.1 in new code." ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -48,8 +48,10 @@ This project aims to provide a stable and secure version of Magento 1.x, with on
 - Follow PSR-12 coding standards for PHP code.
 - Declare strict types in new PHP files.
 - Use type hints for function parameters and return types for new methods.
+- Use short array syntax `[]` for arrays in new code.
 - Do not use underscores in new method names. Use camelCase instead.
 - Use named parameters in new method calls where applicable.
+- Ignore support for PHP versions below PHP 8.1 in new code.
 - Update docblocks to use proper types and descriptions for new methods and classes.
 - Update comments to reflect changes in code.
 - Update tests to cover new functionality and changes in code.
PATCH

echo "Gold patch applied."
