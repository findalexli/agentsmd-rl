#!/bin/bash
set -e

cd /workspace/kotlin

# Check if already applied (idempotency)
if grep -q "SirImport.Mode.Exported" native/swift/swift-export-standalone/src/org/jetbrains/kotlin/swiftexport/standalone/translation/ModuleTranslation.kt; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/native/swift/swift-export-standalone-integration-tests/coroutines/testData/generation/closures/golden_result/main/main.swift b/native/swift/swift-export-standalone-integration-tests/coroutines/testData/generation/closures/golden_result/main/main.swift
index 708914d91dc6c..9ab558a95d502 100644
--- a/native/swift/swift-export-standalone-integration-tests/coroutines/testData/generation/closures/golden_result/main/main.swift
+++ b/native/swift/swift-export-standalone-integration-tests/coroutines/testData/generation/closures/golden_result/main/main.swift
@@ -1,5 +1,5 @@
 @_implementationOnly import KotlinBridges_main
-import KotlinCoroutineSupport
+@_exported import KotlinCoroutineSupport
 import KotlinRuntime
 import KotlinRuntimeSupport

diff --git a/native/swift/swift-export-standalone-integration-tests/coroutines/testData/generation/coroutines/golden_result/KotlinxCoroutinesCore/KotlinxCoroutinesCore.swift b/native/swift/swift-export-standalone-integration-tests/coroutines/testData/generation/coroutines/golden_result/KotlinxCoroutinesCore/KotlinxCoroutinesCore.swift
index 6acce0711c0c9..c9b5b1222af84 100644
--- a/native/swift/swift-export-standalone-integration-tests/coroutines/testData/generation/coroutines/golden_result/KotlinxCoroutinesCore/KotlinxCoroutinesCore.swift
+++ b/native/swift/swift-export-standalone-integration-tests/coroutines/testData/generation/coroutines/golden_result/KotlinxCoroutinesCore/KotlinxCoroutinesCore.swift
@@ -1,6 +1,6 @@
 @_exported import ExportedKotlinPackages
 @_implementationOnly import KotlinBridges_KotlinxCoroutinesCore
-import KotlinCoroutineSupport
+@_exported import KotlinCoroutineSupport
 import KotlinRuntime
 import KotlinRuntimeSupport

diff --git a/native/swift/swift-export-standalone-integration-tests/coroutines/testData/generation/coroutines/golden_result/flow_overrides/flow_overrides.swift b/native/swift/swift-export-standalone-integration-tests/coroutines/testData/generation/coroutines/golden_result/flow_overrides/flow_overrides.swift
index bfd671a9fed55..aec5e1d7299f1 100644
--- a/native/swift/swift-export-standalone-integration-tests/coroutines/testData/generation/coroutines/golden_result/flow_overrides/flow_overrides.swift
+++ b/native/swift/swift-export-standalone-integration-tests/coroutines/testData/generation/coroutines/golden_result/flow_overrides/flow_overrides.swift
@@ -1,6 +1,6 @@
 @_exported import ExportedKotlinPackages
 @_implementationOnly import KotlinBridges_flow_overrides
-import KotlinCoroutineSupport
+@_exported import KotlinCoroutineSupport
 import KotlinRuntime
 import KotlinRuntimeSupport
 import KotlinxCoroutinesCore
diff --git a/native/swift/swift-export-standalone-integration-tests/coroutines/testData/generation/coroutines/golden_result/main/main.swift b/native/swift/swift-export-standalone-integration-tests/coroutines/testData/generation/coroutines/golden_result/main/main.swift
index 58a9e95768089..3eb6b0ea2437d 100644
--- a/native/swift/swift-export-standalone-integration-tests/coroutines/testData/generation/coroutines/golden_result/main/main.swift
+++ b/native/swift/swift-export-standalone-integration-tests/coroutines/testData/generation/coroutines/golden_result/main/main.swift
@@ -1,5 +1,5 @@
 @_implementationOnly import KotlinBridges_main
-import KotlinCoroutineSupport
+@_exported import KotlinCoroutineSupport
 import KotlinRuntime
 import KotlinRuntimeSupport
 import KotlinxCoroutinesCore
diff --git a/native/swift/swift-export-standalone-integration-tests/coroutines/testData/generation/coroutinesWithPackageFlattening/golden_result/main/main.swift b/native/swift/swift-export-standalone-integration-tests/coroutines/testData/generation/coroutinesWithPackageFlattening/golden_result/main/main.swift
index 4ccefcc82ff5c..c2774c6db92bc 100644
--- a/native/swift/swift-export-standalone-integration-tests/coroutines/testData/generation/coroutinesWithPackageFlattening/golden_result/main/main.swift
+++ b/native/swift/swift-export-standalone-integration-tests/coroutines/testData/generation/coroutinesWithPackageFlattening/golden_result/main/main.swift
@@ -1,6 +1,6 @@
 @_exported import ExportedKotlinPackages
 @_implementationOnly import KotlinBridges_main
-import KotlinCoroutineSupport
+@_exported import KotlinCoroutineSupport
 import KotlinRuntime
 import KotlinRuntimeSupport

diff --git a/native/swift/swift-export-standalone/src/org/jetbrains/kotlin/swiftexport/standalone/translation/ModuleTranslation.kt b/native/swift/swift-export-standalone/src/org/jetbrains/kotlin/swiftexport/standalone/translation/ModuleTranslation.kt
index 88657330994ea..81a2060d031f2 100644
--- a/native/swift/swift-export-standalone/src/org/jetbrains/kotlin/swiftexport/standalone/translation/ModuleTranslation.kt
+++ b/native/swift/swift-export-standalone/src/org/jetbrains/kotlin/swiftexport/standalone/translation/ModuleTranslation.kt
@@ -158,7 +158,7 @@ private fun createTranslationResult(
     // It might not be the case, but precise tracking seems like an overkill at the moment.
     sirModule.updateImport(SirImport(config.runtimeSupportModuleName))
     if (config.enableCoroutinesSupport) {
-        sirModule.updateImport(SirImport(config.coroutineSupportModuleName))
+        sirModule.updateImport(SirImport(config.coroutineSupportModuleName, SirImport.Mode.Exported))
     }
     sirModule.updateImport(SirImport(config.runtimeModuleName))
PATCH

echo "Patch applied successfully"
