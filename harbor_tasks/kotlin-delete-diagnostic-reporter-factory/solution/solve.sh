#!/bin/bash
set -e

cd /workspace/kotlin

# Apply the gold patch: Delete DiagnosticReporterFactory and inline its usage
cat <<'PATCH' | git apply -
diff --git a/compiler/frontend.common/src/org/jetbrains/kotlin/diagnostics/DiagnosticReporterFactory.kt b/compiler/frontend.common/src/org/jetbrains/kotlin/diagnostics/DiagnosticReporterFactory.kt
deleted file mode 100644
index 28eeec9eded59..0000000000000
--- a/compiler/frontend.common/src/org/jetbrains/kotlin/diagnostics/DiagnosticReporterFactory.kt
+++ /dev/null
@@ -1,16 +0,0 @@
-/*
- * Copyright 2010-2021 JetBrains s.r.o. and Kotlin Programming Language contributors.
- * Use of this source code is governed by the Apache 2.0 license that can be found in the license/LICENSE.txt file.
- */
-
-package org.jetbrains.kotlin.diagnostics
-
-import org.jetbrains.kotlin.diagnostics.impl.BaseDiagnosticsCollector
-import org.jetbrains.kotlin.diagnostics.impl.DiagnosticsCollectorImpl
-
-// TODO: delete the function with its only usage in Compose tests
-object DiagnosticReporterFactory {
-    fun createReporter(): BaseDiagnosticsCollector {
-        return DiagnosticsCollectorImpl()
-    }
-}
diff --git a/plugins/compose/compiler-hosted/integration-tests/src/jvmTest/kotlin/androidx/compose/compiler/plugins/kotlin/facade/K2CompilerFacade.kt b/plugins/compose/compiler-hosted/integration-tests/src/jvmTest/kotlin/androidx/compose/compiler/plugins/kotlin/facade/K2CompilerFacade.kt
index 077b36902f019..f2fafc771a226 100644
--- a/plugins/compose/compiler-hosted/integration-tests/src/jvmTest/kotlin/androidx/compose/compiler/plugins/kotlin/facade/K2CompilerFacade.kt
+++ b/plugins/compose/compiler-hosted/integration-tests/src/jvmTest/kotlin/androidx/compose/compiler/plugins/kotlin/facade/K2CompilerFacade.kt
@@ -37,9 +37,9 @@ import org.jetbrains.kotlin.compiler.plugin.getCompilerExtensions
 import org.jetbrains.kotlin.config.CommonConfigurationKeys
 import org.jetbrains.kotlin.config.CompilerConfiguration
 import org.jetbrains.kotlin.config.languageVersionSettings
-import org.jetbrains.kotlin.diagnostics.DiagnosticReporterFactory
 import org.jetbrains.kotlin.diagnostics.KtPsiDiagnostic
 import org.jetbrains.kotlin.diagnostics.impl.BaseDiagnosticsCollector
+import org.jetbrains.kotlin.diagnostics.impl.DiagnosticsCollectorImpl
 import org.jetbrains.kotlin.fir.DependencyListForCliModule
 import org.jetbrains.kotlin.fir.FirModuleData
 import org.jetbrains.kotlin.fir.FirSession
@@ -165,7 +165,7 @@ class K2CompilerFacade(environment: KotlinCoreEnvironment) : KotlinCompilerFacad
         val commonKtFiles = commonFiles.map { it.toKtFile(project) }
         val platformKtFiles = platformFiles.map { it.toKtFile(project) }

-        val reporter = DiagnosticReporterFactory.createReporter()
+        val reporter = DiagnosticsCollectorImpl()
         val commonAnalysis =
             buildResolveAndCheckFirFromKtFiles(commonSession, commonKtFiles, reporter)
         val platformAnalysis =
PATCH

echo "Gold patch applied successfully"
