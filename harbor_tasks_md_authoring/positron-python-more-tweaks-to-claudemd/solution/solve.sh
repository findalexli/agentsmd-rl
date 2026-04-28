#!/usr/bin/env bash
set -euo pipefail

cd /workspace/positron

# Idempotency guard
if grep -qF "- Before running Python-related commands, if a virtual environment exists at `ex" "extensions/positron-python/CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/extensions/positron-python/CLAUDE.md b/extensions/positron-python/CLAUDE.md
@@ -14,19 +14,17 @@ Python language support for the Positron IDE. Fork of Microsoft's Python extensi
 ## Code Style
 
 - In this extension, use 4 spaces for indentation in TypeScript/JavaScript, not tabs. (This is different from the rest of the repository!)
-- Never use em-dashes, en-dashes, smart quotes, or other non-ASCII punctuation. Use ASCII hyphens and straight quotes
 
 ## Testing
 
-- Before running commands, if a virtual environment exists at `extensions/positron-python/.venv`, activate it
+- Before running Python-related commands, if a virtual environment exists at `extensions/positron-python/.venv`, activate it
 - **Python**: Run pytest from `extensions/positron-python/python_files/posit`
 - **TypeScript**: `npm run test-extension -- -l positron-python --grep "pattern"`
 - Never use `if __name__ == "__main__"` in test files
 - Use parametrized tests (`@pytest.mark.parametrize`) for comprehensive coverage
 
 ## Code Quality
 
-- Before running commands, if a virtual environment exists at `extensions/positron-python/.venv`, activate it
 - **Check Python**: `./scripts/check-python-quality.sh`
 - **Fix Python**: `./scripts/fix-python-format.sh`
 - **Check/Fix TypeScript**: `npm run format-fix`
PATCH

echo "Gold patch applied."
