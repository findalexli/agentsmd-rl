#!/bin/bash
set -e

cd /workspace/kotlin

# Apply the gold patch for Maven Toolchain support
patch -p1 << 'PATCH'
diff --git a/libraries/tools/kotlin-maven-plugin/src/main/java/org/jetbrains/kotlin/maven/K2JVMCompileMojo.java b/libraries/tools/kotlin-maven-plugin/src/main/java/org/jetbrains/kotlin/maven/K2JVMCompileMojo.java
index 147d6dd8380b5..a7418e692133b 100644
--- a/libraries/tools/kotlin-maven-plugin/src/main/java/org/jetbrains/kotlin/maven/K2JVMCompileMojo.java
+++ b/libraries/tools/kotlin-maven-plugin/src/main/java/org/jetbrains/kotlin/maven/K2JVMCompileMojo.java
@@ -20,6 +20,8 @@
 import org.apache.maven.plugin.MojoExecutionException;
 import org.apache.maven.plugin.MojoFailureException;
 import org.apache.maven.plugins.annotations.*;
+import org.apache.maven.toolchain.Toolchain;
+import org.apache.maven.toolchain.ToolchainManager;
 import org.jetbrains.annotations.NotNull;
 import org.jetbrains.annotations.Nullable;
 import org.jetbrains.kotlin.build.SourcesUtilsKt;
@@ -88,6 +90,12 @@ public class K2JVMCompileMojo extends KotlinCompileMojoBase<K2JVMCompilerArgumen
     @Parameter(property = "kotlin.compiler.jdkHome")
     protected String jdkHome;

+    @Component
+    protected ToolchainManager toolchainManager;
+
+    @Parameter
+    protected Map<String, String> jdkToolchain;
+
     @Parameter(property = "kotlin.compiler.scriptTemplates")
     protected List<String> scriptTemplates;

@@ -226,9 +234,17 @@ protected void configureSpecificCompilerArguments(@NotNull K2JVMCompilerArgument
             arguments.setJvmTarget(JvmTarget.DEFAULT.getDescription());
         }

+        String toolchainJdkHome = getToolchainJdkHome();
         if (jdkHome != null) {
+            if (toolchainJdkHome != null) {
+                getLog().warn("Toolchains are ignored, overwritten by 'jdkHome' parameter");
+            }
+
             getLog().info("Overriding JDK home path with: " + jdkHome);
             arguments.setJdkHome(jdkHome);
+        } else if (toolchainJdkHome != null) {
+            getLog().info("Overriding JDK home path with toolchain JDK: " + toolchainJdkHome);
+            arguments.setJdkHome(toolchainJdkHome);
         }

         if (scriptTemplates != null && !scriptTemplates.isEmpty()) {
@@ -246,6 +262,34 @@ private boolean isJava9Module(@NotNull List<File> sourceRoots) {
         );
     }

+    private @Nullable String getToolchainJdkHome() {
+        Toolchain toolchain = getToolchain();
+        if (toolchain == null) {
+            return null;
+        }
+
+        // Toolchain doesn't offer a way to extract the JDK home
+        // directly except for casting to JavaToolchainImpl, which
+        // is an internal class.
+        String javacPath = toolchain.findTool("javac");
+        if (javacPath == null) {
+            return null;
+        }
+        File javac = new File(javacPath);
+        File bin = javac.getParentFile();
+        return bin != null ? bin.getParent() : null;
+    }
+
+    private @Nullable Toolchain getToolchain() {
+        if (jdkToolchain != null) {
+            List<Toolchain> toolchains = toolchainManager.getToolchains(session, "jdk", jdkToolchain);
+            if (toolchains != null && !toolchains.isEmpty()) {
+                return toolchains.get(0);
+            }
+        }
+        return toolchainManager.getToolchainFromBuildContext("jdk", session);
+    }
+
     @Inject
     private KotlinArtifactResolver kotlinArtifactResolver;
 PATCH

# Verify the patch was applied (idempotency check)
if ! grep -q "getToolchainJdkHome" /workspace/kotlin/libraries/tools/kotlin-maven-plugin/src/main/java/org/jetbrains/kotlin/maven/K2JVMCompileMojo.java; then
    echo "ERROR: Patch was not applied successfully"
    exit 1
fi

echo "Patch applied successfully"
