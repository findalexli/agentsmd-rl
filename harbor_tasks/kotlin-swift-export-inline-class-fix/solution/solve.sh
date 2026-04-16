#!/bin/bash
set -e

# Fix for Swift Export inline class with ref type crash
# PR: JetBrains/kotlin#5758

cd /workspace/kotlin

# 1. Fix the main source file SirInitFromKtSymbol.kt
# Add the import for containingDeclaration after containingSymbol import
sed -i 's/import org.jetbrains.kotlin.analysis.api.components.containingSymbol/import org.jetbrains.kotlin.analysis.api.components.containingDeclaration\nimport org.jetbrains.kotlin.analysis.api.components.containingSymbol/' \
    native/swift/sir-light-classes/src/org/jetbrains/sir/lightclasses/nodes/SirInitFromKtSymbol.kt

# Add the isInline conditional cast - replace the line that ends with }>(${args.joinToString()})"
# We need to replace the entire expression with the conditional
sed -i 's/}>(${args.joinToString()})"$/}>(${args.joinToString()})${\n                        if ((ktSymbol.containingDeclaration as KaNamedClassSymbol).isInline) " as Any?" else ""\n                    }"/' \
    native/swift/sir-light-classes/src/org/jetbrains/sir/lightclasses/nodes/SirInitFromKtSymbol.kt

# 2. Update golden result files to include the 'as Any?' cast for inline classes
# classes/golden_result/main/main.kt
sed -i 's/kotlin.native.internal.createUninitializedInstance<INLINE_CLASS_WITH_REF>()/kotlin.native.internal.createUninitializedInstance<INLINE_CLASS_WITH_REF>() as Any?/g' \
    native/swift/swift-export-standalone-integration-tests/simple/testData/generation/classes/golden_result/main/main.kt

sed -i 's/kotlin.native.internal.createUninitializedInstance<INLINE_CLASS>()/kotlin.native.internal.createUninitializedInstance<INLINE_CLASS>() as Any?/g' \
    native/swift/swift-export-standalone-integration-tests/simple/testData/generation/classes/golden_result/main/main.kt

# type_reference/golden_result/main/main.kt
sed -i 's/kotlin.native.internal.createUninitializedInstance<ignored.VALUE_CLASS>()/kotlin.native.internal.createUninitializedInstance<ignored.VALUE_CLASS>() as Any?/g' \
    native/swift/swift-export-standalone-integration-tests/simple/testData/generation/type_reference/golden_result/main/main.kt

# typealiases/golden_result/main/main.kt
sed -i 's/kotlin.native.internal.createUninitializedInstance<INLINE_CLASS_WITH_REF>()/kotlin.native.internal.createUninitializedInstance<INLINE_CLASS_WITH_REF>() as Any?/g' \
    native/swift/swift-export-standalone-integration-tests/simple/testData/generation/typealiases/golden_result/main/main.kt

sed -i 's/kotlin.native.internal.createUninitializedInstance<INLINE_CLASS>()/kotlin.native.internal.createUninitializedInstance<INLINE_CLASS>() as Any?/g' \
    native/swift/swift-export-standalone-integration-tests/simple/testData/generation/typealiases/golden_result/main/main.kt

# 3. Create new test data files for value class execution test
mkdir -p native/swift/swift-export-standalone-integration-tests/simple/testData/execution/valueClass

cat > native/swift/swift-export-standalone-integration-tests/simple/testData/execution/valueClass/valueClass.kt << 'EOF'
// KIND: STANDALONE
// FREE_COMPILER_ARGS: -opt-in=kotlin.native.internal.InternalForKotlinNative
// MODULE: ValueClass
// FILE: ValueClass.kt

class Foo(val x: Int)
value class Bar(val foo: Foo)
EOF

cat > native/swift/swift-export-standalone-integration-tests/simple/testData/execution/valueClass/valueClass.swift << 'EOF'
import ValueClass
import KotlinRuntime
import Testing

@Test
func inlineClassWithRef() throws {
    let foo = Foo(x: 1)
    let bar = Bar(foo: foo)
    try #require(bar.foo.x == 1)
}
EOF

# 4. Update the generated test class to add the testValueClass() method
# Using Python to insert the new test method before testVararg
python3 << 'PYEOF'
import re

file_path = "native/swift/swift-export-standalone-integration-tests/simple/tests-gen/org/jetbrains/kotlin/swiftexport/standalone/test/SwiftExportExecutionTestGenerated.java"

with open(file_path, 'r') as f:
    content = f.read()

# Find the position right before testVararg and insert the new test
new_test = '''  @Test
  @TestMetadata("valueClass")
  public void testValueClass() {
    runTest("native/swift/swift-export-standalone-integration-tests/simple/testData/execution/valueClass/");
  }

  @Test
  @TestMetadata("vararg")'''

content = content.replace(
    '''  @Test
  @TestMetadata("vararg")''',
    new_test
)

with open(file_path, 'w') as f:
    f.write(content)

print("Updated SwiftExportExecutionTestGenerated.java")
PYEOF

# Idempotency check: verify the distinctive line is present
if ! grep -q '(ktSymbol.containingDeclaration as KaNamedClassSymbol).isInline' \
    native/swift/sir-light-classes/src/org/jetbrains/sir/lightclasses/nodes/SirInitFromKtSymbol.kt; then
    echo "ERROR: Fix was not applied correctly"
    exit 1
fi

echo "Fix applied successfully"
