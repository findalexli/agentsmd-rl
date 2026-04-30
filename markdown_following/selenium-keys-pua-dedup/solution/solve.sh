#!/usr/bin/env bash
set -euo pipefail

cd /workspace/selenium

KEYS_FILE="java/src/org/openqa/selenium/Keys.java"

# Idempotency: if already patched, exit early
if grep -q 'OPTION(Keys.ALT)' "$KEYS_FILE"; then
    echo "Already patched."
    exit 0
fi

python3 <<'PYEOF'
from pathlib import Path

p = Path("/workspace/selenium/java/src/org/openqa/selenium/Keys.java")
src = p.read_text()

old_javadoc = (
    " * not currently part of the W3C spec. Others (e.g., OPTION, FN) are symbolic and reserved for\n"
    " * possible future mapping."
)
new_javadoc = (
    " * not currently part of the W3C specification. Others (e.g., OPTION) are symbolic aliases for\n"
    " * existing keys."
)
assert old_javadoc in src, "old javadoc block not found"
src = src.replace(old_javadoc, new_javadoc, 1)

old_block = (
    "  // Symbolic macOS keys not yet standardized\n"
    "  OPTION('\\uE052'),\n"
    "  FN('\\uE051'), // TODO: symbolic only; confirm or remove in future\n"
)
new_block = (
    "  // macOS-friendly alias (do NOT introduce new codes)\n"
    "  OPTION(Keys.ALT),\n"
    "\n"
    "  /**\n"
    "   * @deprecated The FN key is not part of the W3C WebDriver specification and does not have a\n"
    "   *     standardized Unicode mapping. Its behavior is not guaranteed across drivers/platforms.\n"
    "   */\n"
    "  @Deprecated\n"
    "  FN(Keys.RIGHT_CONTROL),\n"
)
assert old_block in src, "old enum block not found"
src = src.replace(old_block, new_block, 1)

p.write_text(src)
print("Patch applied.")
PYEOF
