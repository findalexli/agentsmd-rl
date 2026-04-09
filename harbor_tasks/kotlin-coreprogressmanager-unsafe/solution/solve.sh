#!/bin/bash
set -e

cd /workspace/kotlin

FILE="compiler/cli/src/com/intellij/openapi/progress/impl/CoreProgressManager.java"

# Check if already patched (idempotency check)
# If ConcurrentLongObjectMap is NOT found, the patch was already applied
if ! grep -q "ConcurrentLongObjectMap" "$FILE"; then
    echo "Patch already applied, skipping."
    exit 0
fi

# Write and run the Python modification script
python3 << 'PYTHON_SCRIPT'
import sys

file_path = "compiler/cli/src/com/intellij/openapi/progress/impl/CoreProgressManager.java"

with open(file_path, 'r') as f:
    content = f.read()

# 1. Remove Java11Shim import
content = content.replace("import com.intellij.util.Java11Shim;\n", "")

# 2. Remove ConcurrentLongObjectMap import  
content = content.replace("import com.intellij.util.containers.ConcurrentLongObjectMap;\n", "")

# 3. Replace field declarations and initializations
content = content.replace(
    "private static final ConcurrentLongObjectMap<ProgressIndicator> currentIndicators =\n" +
    "    Java11Shim.Companion.getINSTANCE().createConcurrentLongObjectMap();",
    "private static final ConcurrentMap<Long, ProgressIndicator> currentIndicators =\n" +
    "    new ConcurrentHashMap<>();"
)

content = content.replace(
    "private static final ConcurrentLongObjectMap<ProgressIndicator> threadTopLevelIndicators =\n" +
    "    Java11Shim.Companion.getINSTANCE().createConcurrentLongObjectMap();",
    "private static final ConcurrentMap<Long, ProgressIndicator> threadTopLevelIndicators =\n" +
    "    new ConcurrentHashMap<>();"
)

# 4. Update JavaDoc - use "sun.misc.Unsafe-based map" instead of naming the class
old_javadoc = """ * This class is a simplified version of the original one, which tries to avoid loading a specific class
 * kotlinx/coroutines/internal/intellij/IntellijCoroutine from kotlinx.coroutines fork in a CLI environment.
 *
 * After IJPL-207644 has been fixed, since 253 we can hopefully remove the workaround, via setting
 * `ide.can.use.coroutines.fork` property to false."""

new_javadoc = """ * This class is a simplified version of the original one, which applies two workarounds:
 *
 * 1. Try to avoid loading a specific class
 * kotlinx/coroutines/internal/intellij/IntellijCoroutine from kotlinx.coroutines fork in a CLI environment.
 *
 * After IJPL-207644 has been fixed, since 253 we can hopefully remove the workaround, via setting
 * `ide.can.use.coroutines.fork` property to false.
 *
 * 2. Replace sun.misc.Unsafe-based map with ConcurrentHashMap: sun.misc.Unsafe is
 * being phased out in modern JDK versions (JEP 471).
 * The original version of this class is already fixed in 253 (IJPL-191435)."""

content = content.replace(old_javadoc, new_javadoc)

with open(file_path, 'w') as f:
    f.write(content)

print("Modifications complete")
PYTHON_SCRIPT

echo "Patch applied successfully!"
