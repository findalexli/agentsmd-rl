#!/bin/bash
set -e

cd /workspace/kotlin

# Check if already patched in the first SearchPathType section (line ~404)
# We check for "map" on the line after joinToString in the first SearchPathType block
if sed -n '404,412p' compiler/build-tools/kotlin-build-tools-options-generator/src/org/jetbrains/kotlin/buildtools/options/generator/BtaImplGenerator.kt | grep -q "absolutePathStringOrThrow"; then
    echo "Already patched"
    exit 0
fi

# Fix the generator file - BtaImplGenerator.kt
# The first SearchPathType section is around line 404-410
# Change it to map through absolutePathStringOrThrow before joinToString
sed -i '404,410s/maybeGetNullabilitySign(argument) + ".%M(%T.pathSeparator)",/maybeGetNullabilitySign(argument) + ".%M { it.%M() }" + maybeGetNullabilitySign(argument) + ".%M(%T.pathSeparator)",\n                    MemberName(KOTLIN_COLLECTIONS, "map"),\n                    MemberName(targetPackage, "absolutePathStringOrThrow", true),/' \
    compiler/build-tools/kotlin-build-tools-options-generator/src/org/jetbrains/kotlin/buildtools/options/generator/BtaImplGenerator.kt

# Apply fixes to the generated files using sed
# Fix kotlin-build-tools-compat JvmCompilerArgumentsImpl.kt
sed -i 's/get(X_KLIB)?\.joinToString(File.pathSeparator)/get(X_KLIB)?.map { it.absolutePathStringOrThrow() }?.joinToString(File.pathSeparator)/g' \
    compiler/build-tools/kotlin-build-tools-compat/gen/org/jetbrains/kotlin/buildtools/internal/compat/arguments/JvmCompilerArgumentsImpl.kt

sed -i 's/get(X_MODULE_PATH)?\.joinToString(File.pathSeparator)/get(X_MODULE_PATH)?.map { it.absolutePathStringOrThrow() }?.joinToString(File.pathSeparator)/g' \
    compiler/build-tools/kotlin-build-tools-compat/gen/org/jetbrains/kotlin/buildtools/internal/compat/arguments/JvmCompilerArgumentsImpl.kt

sed -i 's/get(CLASSPATH)?\.joinToString(File.pathSeparator)/get(CLASSPATH)?.map { it.absolutePathStringOrThrow() }?.joinToString(File.pathSeparator)/g' \
    compiler/build-tools/kotlin-build-tools-compat/gen/org/jetbrains/kotlin/buildtools/internal/compat/arguments/JvmCompilerArgumentsImpl.kt

# Fix kotlin-build-tools-impl JvmCompilerArgumentsImpl.kt
sed -i 's/get(X_KLIB)?\.joinToString(File.pathSeparator)/get(X_KLIB)?.map { it.absolutePathStringOrThrow() }?.joinToString(File.pathSeparator)/g' \
    compiler/build-tools/kotlin-build-tools-impl/gen/org/jetbrains/kotlin/buildtools/internal/arguments/JvmCompilerArgumentsImpl.kt

sed -i 's/get(X_MODULE_PATH)?\.joinToString(File.pathSeparator)/get(X_MODULE_PATH)?.map { it.absolutePathStringOrThrow() }?.joinToString(File.pathSeparator)/g' \
    compiler/build-tools/kotlin-build-tools-impl/gen/org/jetbrains/kotlin/buildtools/internal/arguments/JvmCompilerArgumentsImpl.kt

sed -i 's/get(CLASSPATH)?\.joinToString(File.pathSeparator)/get(CLASSPATH)?.map { it.absolutePathStringOrThrow() }?.joinToString(File.pathSeparator)/g' \
    compiler/build-tools/kotlin-build-tools-impl/gen/org/jetbrains/kotlin/buildtools/internal/arguments/JvmCompilerArgumentsImpl.kt

echo "Patch applied successfully"
