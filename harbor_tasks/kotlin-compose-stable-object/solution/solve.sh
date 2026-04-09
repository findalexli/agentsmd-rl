#!/bin/bash
set -e

cd /workspace/kotlin

# Fix 1: Add isObject check in Stability.kt after the enum check
STABILITY_FILE="plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/analysis/Stability.kt"
sed -i 's/if (declaration.isEnumClass || declaration.isEnumEntry) return Stability.Stable/if (declaration.isEnumClass || declaration.isEnumEntry) return Stability.Stable\n        if (declaration.isObject) return Stability.Stable/' "$STABILITY_FILE"

# Fix 2: Change isCompanion to isObject in AbstractComposeLowering.kt
LOWERING_FILE="plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/lower/AbstractComposeLowering.kt"
sed -i 's/if (symbol.owner.isCompanion) true/if (symbol.owner.isObject) true/' "$LOWERING_FILE"

# Fix 3: Add test method to ComposerParamTransformTests.kt
COMPOSER_TEST_FILE="plugins/compose/compiler-hosted/integration-tests/src/jvmTest/kotlin/androidx/compose/compiler/plugins/kotlin/ComposerParamTransformTests.kt"

# Find the last closing brace of the class and add the test before it
cat >> "$COMPOSER_TEST_FILE" << 'TESTCODE'

    // We expect the type of the receiver of an invocation of a composable method defined within an
    // object to be stable. We validate this by checking that `Object.%stable` does not appear in
    // the golden file.
    @Test
    fun testObjectTypesAreStable() = verifyGoldenComposeIrTransform(
        """
            import androidx.compose.runtime.Composable

            @Composable fun Test() {
                Object.bar()
            }
        """.trimIndent(),
        """
            import androidx.compose.runtime.Composable

            object Object {
                @Composable fun bar() {}
            }
        """.trimIndent(),
    )
}
TESTCODE

# Need to remove the original closing brace first, then add our test + closing brace
# Use a temp file approach
TEMP_FILE=$(mktemp)
head -n -1 "$COMPOSER_TEST_FILE" > "$TEMP_FILE"
cat >> "$TEMP_FILE" << 'TESTCODE2'

    // We expect the type of the receiver of an invocation of a composable method defined within an
    // object to be stable. We validate this by checking that `Object.%stable` does not appear in
    // the golden file.
    @Test
    fun testObjectTypesAreStable() = verifyGoldenComposeIrTransform(
        """
            import androidx.compose.runtime.Composable

            @Composable fun Test() {
                Object.bar()
            }
        """.trimIndent(),
        """
            import androidx.compose.runtime.Composable

            object Object {
                @Composable fun bar() {}
            }
        """.trimIndent(),
    )
}
TESTCODE2

mv "$TEMP_FILE" "$COMPOSER_TEST_FILE"

# Fix 4: Add test method to RunComposableTests.kt
RUN_TEST_FILE="plugins/compose/compiler-hosted/integration-tests/src/jvmTest/kotlin/androidx/compose/compiler/plugins/kotlin/RunComposableTests.kt"

# Find the last closing brace of the class and add the test before it
TEMP_FILE2=$(mktemp)
head -n -1 "$RUN_TEST_FILE" > "$TEMP_FILE2"
cat >> "$TEMP_FILE2" << 'TESTCODE3'

    // This is a regression test against a bug that was causing us to add a `$stable` property to
    // companion objects. This made the JVM bytecode of affected classes contain duplicate `%stable`
    // fields. For more details, see https://issuetracker.google.com/issues/497751457.
    @Test
    fun testNoStablePropertyOnCompanionObjects() {
        runCompose(
            testFunBody = """
                C.bar()
            """.trimIndent(),
            commonFiles = mapOf(
                "C.kt" to """
                    import androidx.compose.runtime.Composable

                    class C {
                        @Composable fun foo() {}

                        companion object {
                            @Composable fun bar() {}
                        }
                    }
                    """,
            ),
            platformFiles = mapOf()
        ) {
            // This test passes as long as loading `C` succeeds without hitting a "Duplicate field
            // name "$stable" with signature "I" in class file C" error.
        }
    }
}
TESTCODE3

mv "$TEMP_FILE2" "$RUN_TEST_FILE"

# Fix 5: Create golden files for testObjectTypesAreStable
GOLDEN_DIR="plugins/compose/compiler-hosted/integration-tests/src/jvmTest/resources/golden"
COMPOSER_GOLDEN_DIR="$GOLDEN_DIR/androidx.compose.compiler.plugins.kotlin.ComposerParamTransformTests"

mkdir -p "$COMPOSER_GOLDEN_DIR"

GOLDEN_CONTENT='//
// Source
// ------------------------------------------

import androidx.compose.runtime.Composable

@Composable fun Test() {
    Object.bar()
}

//
// Transformed IR
// ------------------------------------------

@Composable
fun Test(%composer: Composer?, %changed: Int) {
  %composer = %composer.startRestartGroup(<>)
  sourceInformation(%composer, "C(Test)<bar()>:Test.kt")
  if (%composer.shouldExecute(%changed != 0, %changed and 0b0001)) {
    if (isTraceInProgress()) {
      traceEventStart(<>, %changed, -1, <>)
    }
    Object.bar(%composer, 0b0110)
    if (isTraceInProgress()) {
      traceEventEnd()
    }
  } else {
    %composer.skipToGroupEnd()
  }
  %composer.endRestartGroup()?.updateScope { %composer: Composer?, %force: Int ->
    Test(%composer, updateChangedFlags(%changed or 0b0001))
  }
}'

echo "$GOLDEN_CONTENT" > "$COMPOSER_GOLDEN_DIR/testObjectTypesAreStable[useFir = false].txt"
echo "$GOLDEN_CONTENT" > "$COMPOSER_GOLDEN_DIR/testObjectTypesAreStable[useFir = true].txt"

# Fix 6: Update existing golden files to remove .%stable references
GOLDEN_BASE="plugins/compose/compiler-hosted/integration-tests/src/jvmTest/resources/golden"

# ContextParametersTransformTests - remove BoxScope.%stable and States.A.%stable
sed -i 's/BoxScope.%stable or //g' "$GOLDEN_BASE/androidx.compose.compiler.plugins.kotlin.ContextParametersTransformTests/testMemoizationContextParameters.txt"
sed -i 's/or States.A.%stable//g' "$GOLDEN_BASE/androidx.compose.compiler.plugins.kotlin.ContextParametersTransformTests/testMemoizationContextParameters.txt"

# ControlFlowTransformTests - replace MaterialTheme.%stable with 0b0110
for file in "$GOLDEN_BASE/androidx.compose.compiler.plugins.kotlin.ControlFlowTransformTests/"testComposablePropertyDelegate*.txt; do
    if [ -f "$file" ]; then
        sed -i 's/MaterialTheme.%stable or 0b01110000 and %changed shr 0b0011/0b0110 or 0b01110000 and %changed shr 0b0011/g' "$file"
    fi
done

# DefaultParamTransformTests - replace class.%stable with literal values
for file in "$GOLDEN_BASE/androidx.compose.compiler.plugins.kotlin.DefaultParamTransformTests/"testDefaultArgsOnInvoke*.txt; do
    if [ -f "$file" ]; then
        # HasDefault.%stable shl 0b0011 -> 0b00110000
        sed -i 's/HasDefault.%stable shl 0b0011/0b00110000/g' "$file"
        # 0b0110 or NoDefault.%stable shl 0b0011 -> 0b00110110
        sed -i 's/0b0110 or NoDefault.%stable shl 0b0011/0b00110110/g' "$file"
        # MultipleDefault.%stable shl 0b0110 -> 0b000110000000
        sed -i 's/MultipleDefault.%stable shl 0b0110/0b000110000000/g' "$file"
    fi
done

# LambdaMemoizationTransformTests - replace BottomSheetDefaults.%stable with 0b0110
for file in "$GOLDEN_BASE/androidx.compose.compiler.plugins.kotlin.LambdaMemoizationTransformTests/"composableLambdaInInlineDefaultParam*.txt; do
    if [ -f "$file" ]; then
        sed -i 's/BottomSheetDefaults.%stable/0b0110/g' "$file"
    fi
done

# Verify the patches were applied
if ! grep -q "if (declaration.isObject) return Stability.Stable" "$STABILITY_FILE"; then
    echo "ERROR: Stability.kt patch was not applied correctly"
    exit 1
fi

if ! grep -q "if (symbol.owner.isObject) true" "$LOWERING_FILE"; then
    echo "ERROR: AbstractComposeLowering.kt patch was not applied correctly"
    exit 1
fi

if ! grep -q "fun testObjectTypesAreStable()" "$COMPOSER_TEST_FILE"; then
    echo "ERROR: ComposerParamTransformTests.kt test was not added"
    exit 1
fi

if ! grep -q "fun testNoStablePropertyOnCompanionObjects()" "$RUN_TEST_FILE"; then
    echo "ERROR: RunComposableTests.kt test was not added"
    exit 1
fi

if [ ! -f "$COMPOSER_GOLDEN_DIR/testObjectTypesAreStable[useFir = false].txt" ]; then
    echo "ERROR: Golden file for testObjectTypesAreStable was not created"
    exit 1
fi

echo "Patch applied successfully"
