#!/bin/bash
set -e

cd /workspace/kotlin

# Use Python to fix the Cursor.kt file
python3 << 'PYTHON'
import re

# Read the file
with open('compiler/util-klib-abi/src/org/jetbrains/kotlin/library/abi/parser/Cursor.kt', 'r') as f:
    content = f.read()

# The actual content shows: ^((=(?!	*\.\.\.)|[^;... 
# We need to change it to: ^((?!\.\.\.)(=(?!	*\.\.\.)|[^;...
# Add (?!\.\.\.) after (( and move the )+ to be ))+

# Find and replace the validIdentifierWithDotRegex pattern
old_line = '    ^((=(?!	*\.\.\.)|[^;\\[\\]/<>:\\\\(){}?=,&])+)'
new_line = '    ^((?!\.\.\.)(=(?!	*\.\.\.)|[^;\\[\\]/<>:\\\\(){}?=,&]))+'

if old_line in content:
    content = content.replace(old_line, new_line)
    print("Fix applied successfully")
else:
    print("WARNING: Pattern not found exactly, trying alternative...")
    # The file might have \s instead of a literal tab
    old_line2 = '    ^((=(?!\\s?\\.\\.\\.)|[^;\\[\\]/<>:\\\\(){}?=,&])+)'
    new_line2 = '    ^((?!\\.\\.\\.)(=(?!\\s?\\.\\.\\.)|[^;\\[\\]/<>:\\\\(){}?=,&]))+'
    if old_line2 in content:
        content = content.replace(old_line2, new_line2)
        print("Fix applied with alternative pattern")
    else:
        print("ERROR: Could not find pattern to fix")
        print("Looking for:")
        print(repr(old_line))
        print("Or:")
        print(repr(old_line2))
        exit(1)

# Write the file
with open('compiler/util-klib-abi/src/org/jetbrains/kotlin/library/abi/parser/Cursor.kt', 'w') as f:
    f.write(content)
PYTHON

# Add the new test case for vararg without type params
cat > /tmp/test_fix.patch << 'EOF'
--- a/compiler/util-klib-abi/test/org/jetbrains/kotlin/library/abi/parser/KlibParsingCursorExtensionsTest.kt
+++ b/compiler/util-klib-abi/test/org/jetbrains/kotlin/library/abi/parser/KlibParsingCursorExtensionsTest.kt
@@ -477,6 +477,17 @@ class KlibParsingCursorExtensionsTest {
         assertTrue(valueParam.isVararg)
     }

+    @Test
+    fun parseValueParamVarargWithoutTypeParams() {
+        val input = "kotlin/DoubleArray..."
+        val cursor = Cursor(input)
+        val valueParam = cursor.parseValueParameter()!!
+        assertEquals("kotlin/DoubleArray", valueParam.type.className.toString())
+        assertFalse(valueParam.hasDefaultArg)
+        assertFalse(valueParam.isCrossinline)
+        assertTrue(valueParam.isVararg)
+    }
+
     @Test
     fun parseValueParametersWithTypeArgs() {
         val input = "kotlin/Array<out #A>..."
EOF

patch -p1 < /tmp/test_fix.patch

# Verify the fix was applied
if ! grep -q '(?!\\.\\.\\.)' compiler/util-klib-abi/src/org/jetbrains/kotlin/library/abi/parser/Cursor.kt; then
    echo "ERROR: Cursor.kt patch was not applied correctly"
    cat compiler/util-klib-abi/src/org/jetbrains/kotlin/library/abi/parser/Cursor.kt | tail -20
    exit 1
fi

if ! grep -q 'fun parseValueParamVarargWithoutTypeParams()' compiler/util-klib-abi/test/org/jetbrains/kotlin/library/abi/parser/KlibParsingCursorExtensionsTest.kt; then
    echo "ERROR: Test patch was not applied correctly"
    exit 1
fi

echo "Patch applied successfully"
