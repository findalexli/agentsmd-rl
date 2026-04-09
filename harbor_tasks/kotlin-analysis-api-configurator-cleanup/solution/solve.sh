#!/bin/bash
set -e

cd /workspace/kotlin

# Check if patch is already applied (idempotency check)
if grep -q "TestModuleKind.SourceLike," native/swift/swift-export-ide/tests-gen/org/jetbrains/kotlin/swiftexport/ide/SwiftExportInIdeTestGenerated.java 2>/dev/null; then
    echo "Patch already applied, skipping..."
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/analysis/analysis-api-fir/testFixtures/org/jetbrains/kotlin/analysis/api/fir/test/configurators/AnalysisApiFirTestConfiguratorFactory.kt b/analysis/analysis-api-fir/testFixtures/org/jetbrains/kotlin/analysis/api/fir/test/configurators/AnalysisApiFirTestConfiguratorFactory.kt
index 9ccae29a8aebd..235dc3c540161 100644
--- a/analysis/analysis-api-fir/testFixtures/org/jetbrains/kotlin/analysis/api/fir/test/configurators/AnalysisApiFirTestConfiguratorFactory.kt
+++ b/analysis/analysis-api-fir/testFixtures/org/jetbrains/kotlin/analysis/api/fir/test/configurators/AnalysisApiFirTestConfiguratorFactory.kt
@@ -10,12 +10,6 @@ import org.jetbrains.kotlin.analysis.test.framework.test.configurators.*

 object AnalysisApiFirTestConfiguratorFactory : AnalysisApiTestConfiguratorFactory() {
     override fun createConfigurator(data: AnalysisApiTestConfiguratorFactoryData): AnalysisApiTestConfigurator {
-        // This is a workaround for the transition time to not fix non-generated tests right away
-        val data = when (data.moduleKind) {
-            TestModuleKind.Source, TestModuleKind.ScriptSource -> data.copy(moduleKind = TestModuleKind.SourceLike)
-            else -> data
-        }
-
         requireSupported(data)

         val targetPlatform = data.targetPlatform.targetPlatform
@@ -57,7 +51,7 @@ object AnalysisApiFirTestConfiguratorFactory : AnalysisApiTestConfiguratorFactor
         data.analysisApiMode != AnalysisApiMode.Ide -> false
         else -> when (data.moduleKind) {
             TestModuleKind.SourceLike,
-                 -> true
+                -> true

             TestModuleKind.Source,
             TestModuleKind.ScriptSource,
diff --git a/generators/sir-tests-generator/main/org/jetbrains/kotlin/generators/tests/native/swift/sir/GenerateSirTests.kt b/generators/sir-tests-generator/main/org/jetbrains/kotlin/generators/tests/native/swift/sir/GenerateSirTests.kt
index e4e1fec14baf4..b498bf801b2f5 100644
--- a/generators/sir-tests-generator/main/org/jetbrains/kotlin/generators/tests/native/swift/sir/GenerateSirTests.kt
+++ b/generators/sir-tests-generator/main/org/jetbrains/kotlin/generators/tests/native/swift/sir/GenerateSirTests.kt
@@ -1,12 +1,12 @@
 /*
- * Copyright 2010-2023 JetBrains s.r.o. and Kotlin Programming Language contributors.
+ * Copyright 2010-2026 JetBrains s.r.o. and Kotlin Programming Language contributors.
  * Use of this source code is governed by the Apache 2.0 license that can be found in the license/LICENSE.txt file.
  */

 package org.jetbrains.kotlin.generators.tests.native.swift.sir

 import org.jetbrains.kotlin.analysis.api.fir.test.configurators.AnalysisApiFirTestConfiguratorFactory
-import org.jetbrains.kotlin.analysis.test.framework.test.configurators.*
+import org.jetbrains.kotlin.analysis.test.framework.test.configurators.AnalysisApiTestConfiguratorFactoryData
 import org.jetbrains.kotlin.generators.dsl.junit5.generateTestGroupSuiteWithJUnit5
 import org.jetbrains.kotlin.generators.model.annotation
 import org.jetbrains.kotlin.generators.tests.analysis.api.dsl.FrontendConfiguratorTestModel
@@ -113,12 +113,7 @@ fun main() {
                 suiteTestClassName = "SwiftExportInIdeTestGenerated",
             ) {
                 model(recursive = false)
-                val data = AnalysisApiTestConfiguratorFactoryData(
-                    FrontendKind.Fir,
-                    TestModuleKind.Source,
-                    AnalysisSessionMode.Normal,
-                    AnalysisApiMode.Ide
-                )
+                val data = AnalysisApiTestConfiguratorFactoryData()
                 method(FrontendConfiguratorTestModel(AnalysisApiFirTestConfiguratorFactory::class, data))
             }
         }
diff --git a/native/swift/swift-export-ide/tests-gen/org/jetbrains/kotlin/swiftexport/ide/SwiftExportInIdeTestGenerated.java b/native/swift/swift-export-ide/tests-gen/org/jetbrains/kotlin/swiftexport/ide/SwiftExportInIdeTestGenerated.java
index a858cd24cbfa5..9c5174b757f98 100644
--- a/native/swift/swift-export-ide/tests-gen/org/jetbrains/kotlin/swiftexport/ide/SwiftExportInIdeTestGenerated.java
+++ b/native/swift/swift-export-ide/tests-gen/org/jetbrains/kotlin/swiftexport/ide/SwiftExportInIdeTestGenerated.java
@@ -33,7 +33,7 @@ public AnalysisApiTestConfigurator getConfigurator() {
     return AnalysisApiFirTestConfiguratorFactory.INSTANCE.createConfigurator(
       new AnalysisApiTestConfiguratorFactoryData(
         FrontendKind.Fir,
-        TestModuleKind.Source,
+        TestModuleKind.SourceLike,
         AnalysisSessionMode.Normal,
         AnalysisApiMode.Ide,
         TargetPlatformEnum.JVM
diff --git a/plugins/compose/compiler-hosted/src/test/kotlin/androidx/compose/compiler/plugins/kotlin/ComposeCompilerBoxTests.kt b/plugins/compose/compiler-hosted/src/test/kotlin/androidx/compose/compiler/plugins/kotlin/ComposeCompilerBoxTests.kt
index 586f49227fc7c..af4b0f799fb50 100644
--- a/plugins/compose/compiler-hosted/src/test/kotlin/androidx/compose/compiler/plugins/kotlin/ComposeCompilerBoxTests.kt
+++ b/plugins/compose/compiler-hosted/src/test/kotlin/androidx/compose/compiler/plugins/kotlin/ComposeCompilerBoxTests.kt
@@ -1,5 +1,5 @@
 /*
- * Copyright 2010-2024 JetBrains s.r.o. and Kotlin Programming Language contributors.
+ * Copyright 2010-2026 JetBrains s.r.o. and Kotlin Programming Language contributors.
  * Use of this source code is governed by the Apache 2.0 license that can be found in the license/LICENSE.txt file.
  */

@@ -8,10 +8,11 @@ package androidx.compose.compiler.plugins.kotlin
 import androidx.compose.compiler.plugins.kotlin.services.ComposeExtensionRegistrarConfigurator
 import androidx.compose.compiler.plugins.kotlin.services.ComposeJsClasspathProvider
 import androidx.compose.compiler.plugins.kotlin.services.ComposeJvmClasspathConfigurator
-import org.jetbrains.kotlin.analysis.api.fir.test.configurators.AnalysisApiFirTestConfiguratorFactory.createConfigurator
+import org.jetbrains.kotlin.analysis.api.fir.test.configurators.AnalysisApiFirTestConfiguratorFactory
 import org.jetbrains.kotlin.analysis.api.impl.base.test.cases.components.compilerFacility.AbstractCompilerFacilityTest
 import org.jetbrains.kotlin.analysis.test.framework.services.libraries.TestModuleCompiler.Directives.COMPILER_ARGUMENTS
-import org.jetbrains.kotlin.analysis.test.framework.test.configurators.*
+import org.jetbrains.kotlin.analysis.test.framework.test.configurators.AnalysisApiTestConfigurator
+import org.jetbrains.kotlin.analysis.test.framework.test.configurators.AnalysisApiTestConfiguratorFactoryData
 import org.jetbrains.kotlin.js.test.runners.AbstractJsTest
 import org.jetbrains.kotlin.test.TargetBackend
 import org.jetbrains.kotlin.test.builders.TestConfigurationBuilder
@@ -27,15 +28,9 @@ import org.jetbrains.kotlin.test.runners.AbstractPhasedJvmDiagnosticLightTreeTes
 import java.io.File

 abstract class AbstractCompilerFacilityTestForComposeCompilerPlugin : AbstractCompilerFacilityTest() {
-    override val configurator: AnalysisApiTestConfigurator
-        get() = createConfigurator(
-            AnalysisApiTestConfiguratorFactoryData(
-                FrontendKind.Fir,
-                TestModuleKind.Source,
-                AnalysisSessionMode.Normal,
-                AnalysisApiMode.Ide
-            )
-        )
+    override val configurator: AnalysisApiTestConfigurator = AnalysisApiFirTestConfiguratorFactory.createConfigurator(
+        AnalysisApiTestConfiguratorFactoryData()
+    )

     override fun configureTest(builder: TestConfigurationBuilder) {
         super.configureTest(builder)
diff --git a/plugins/kotlin-dataframe/testFixtures/org/jetbrains/kotlin/fir/dataframe/AbstractCompilerFacilityTestForDataFrame.kt b/plugins/kotlin-dataframe/testFixtures/org/jetbrains/kotlin/fir/dataframe/AbstractCompilerFacilityTestForDataFrame.kt
index 5610a4cae3c6d..79bd41f7cfb2a 100644
--- a/plugins/kotlin-dataframe/testFixtures/org/jetbrains/kotlin/fir/dataframe/AbstractCompilerFacilityTestForDataFrame.kt
+++ b/plugins/kotlin-dataframe/testFixtures/org/jetbrains/kotlin/fir/dataframe/AbstractCompilerFacilityTestForDataFrame.kt
@@ -1,26 +1,21 @@
 /*
- * Copyright 2010-2025 JetBrains s.r.o. and Kotlin Programming Language contributors.
+ * Copyright 2010-2026 JetBrains s.r.o. and Kotlin Programming Language contributors.
  * Use of this source code is governed by the Apache 2.0 license that can be found in the license/LICENSE.txt file.
  */

 package org.jetbrains.kotlin.fir.dataframe

-import org.jetbrains.kotlin.analysis.api.fir.test.configurators.AnalysisApiFirTestConfiguratorFactory.createConfigurator
+import org.jetbrains.kotlin.analysis.api.fir.test.configurators.AnalysisApiFirTestConfiguratorFactory
 import org.jetbrains.kotlin.analysis.api.impl.base.test.cases.components.compilerFacility.AbstractCompilerFacilityTest
-import org.jetbrains.kotlin.analysis.test.framework.test.configurators.*
-import org.jetbrains.kotlin.fir.dataframe.services.DataFrameRuntimeClasspathProvider
+import org.jetbrains.kotlin.analysis.test.framework.test.configurators.AnalysisApiTestConfigurator
+import org.jetbrains.kotlin.analysis.test.framework.test.configurators.AnalysisApiTestConfiguratorFactoryData
 import org.jetbrains.kotlin.fir.dataframe.services.DataFrameEnvironmentConfigurator
+import org.jetbrains.kotlin.fir.dataframe.services.DataFrameRuntimeClasspathProvider
 import org.jetbrains.kotlin.test.builders.TestConfigurationBuilder

 abstract class AbstractCompilerFacilityTestForDataFrame : AbstractCompilerFacilityTest() {
-
-    override val configurator: AnalysisApiTestConfigurator = createConfigurator(
-        AnalysisApiTestConfiguratorFactoryData(
-            FrontendKind.Fir,
-            TestModuleKind.Source,
-            AnalysisSessionMode.Normal,
-            AnalysisApiMode.Ide
-        )
+    override val configurator: AnalysisApiTestConfigurator = AnalysisApiFirTestConfiguratorFactory.createConfigurator(
+        AnalysisApiTestConfiguratorFactoryData()
     )

     override fun configureTest(builder: TestConfigurationBuilder) {
@@ -28,4 +23,4 @@ abstract class AbstractCompilerFacilityTestForDataFrame : AbstractCompilerFacili
         builder.useConfigurators(::DataFrameEnvironmentConfigurator)
         builder.useCustomRuntimeClasspathProviders(::DataFrameRuntimeClasspathProvider)
     }
-}
\ No newline at end of file
+}
diff --git a/plugins/kotlinx-serialization/testFixtures/org/jetbrains/kotlinx/serialization/runners/AbstractCompilerFacilityTestForSerialization.kt b/plugins/kotlinx-serialization/testFixtures/org/jetbrains/kotlinx/serialization/runners/AbstractCompilerFacilityTestForSerialization.kt
index 815a3b8928abe..f67bdce10906c 100644
--- a/plugins/kotlinx-serialization/testFixtures/org/jetbrains/kotlinx/serialization/runners/AbstractCompilerFacilityTestForSerialization.kt
+++ b/plugins/kotlinx-serialization/testFixtures/org/jetbrains/kotlinx/serialization/runners/AbstractCompilerFacilityTestForSerialization.kt
@@ -1,29 +1,24 @@
 /*
- * Copyright 2010-2024 JetBrains s.r.o. and Kotlin Programming Language contributors.
+ * Copyright 2010-2026 JetBrains s.r.o. and Kotlin Programming Language contributors.
  * Use of this source code is governed by the Apache 2.0 license that can be found in the license/LICENSE.txt file.
  */

 package org.jetbrains.kotlinx.serialization.runners

-import org.jetbrains.kotlin.analysis.api.fir.test.configurators.AnalysisApiFirTestConfiguratorFactory.createConfigurator
+import org.jetbrains.kotlin.analysis.api.fir.test.configurators.AnalysisApiFirTestConfiguratorFactory
 import org.jetbrains.kotlin.analysis.api.impl.base.test.cases.components.compilerFacility.AbstractCompilerFacilityTest
-import org.jetbrains.kotlin.analysis.test.framework.test.configurators.*
+import org.jetbrains.kotlin.analysis.test.framework.test.configurators.AnalysisApiTestConfigurator
+import org.jetbrains.kotlin.analysis.test.framework.test.configurators.AnalysisApiTestConfiguratorFactoryData
 import org.jetbrains.kotlin.test.builders.TestConfigurationBuilder
 import org.jetbrains.kotlinx.serialization.configureForKotlinxSerialization

 abstract class AbstractCompilerFacilityTestForSerialization : AbstractCompilerFacilityTest() {
-    override val configurator: AnalysisApiTestConfigurator
-        get() = createConfigurator(
-            AnalysisApiTestConfiguratorFactoryData(
-                FrontendKind.Fir,
-                TestModuleKind.Source,
-                AnalysisSessionMode.Normal,
-                AnalysisApiMode.Ide
-            )
-        )
+    override val configurator: AnalysisApiTestConfigurator = AnalysisApiFirTestConfiguratorFactory.createConfigurator(
+        AnalysisApiTestConfiguratorFactoryData()
+    )

     override fun configureTest(builder: TestConfigurationBuilder) {
         super.configureTest(builder)
         builder.configureForKotlinxSerialization()
     }
-}
\ No newline at end of file
+}
PATCH

echo "Patch applied successfully"
