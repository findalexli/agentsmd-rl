#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cursor-rules-java

# Idempotency guard
if grep -qF "description: Effective Maven usage involves robust dependency management via `<d" ".agents/skills/110-java-maven-best-practices/SKILL.md" && grep -qF "description: Treats the user as a knowledgeable partner in solving problems rath" ".agents/skills/111-java-maven-dependencies/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/110-java-maven-best-practices/SKILL.md b/.agents/skills/110-java-maven-best-practices/SKILL.md
@@ -1,6 +1,8 @@
 ---
 author: Juan Antonio Breña Moral
 version: 0.12.0-SNAPSHOT
+name: Maven Best Practices
+description: Effective Maven usage involves robust dependency management via `<dependencyManagement>` and BOMs, adherence to the standard directory layout, and centralized plugin management. Build profiles should be used for environment-specific configurations. POMs must be kept readable and maintainable with logical structure and properties for versions. Custom repositories should be declared explicitly and their use minimized, preferably managed via a central repository manager.
 ---
 # Maven Best Practices
 
@@ -624,4 +626,4 @@ Description: Define all dependency and plugin versions in the `<properties>` sec
 - **ASK USER before overriding** any existing configuration element
 - Verify changes with the command: `./mvnw clean verify`
 - Preserve existing dependency versions unless explicitly requested to update
-- Maintain backward compatibility with existing build process
\ No newline at end of file
+- Maintain backward compatibility with existing build process
diff --git a/.agents/skills/111-java-maven-dependencies/SKILL.md b/.agents/skills/111-java-maven-dependencies/SKILL.md
@@ -1,6 +1,8 @@
 ---
 author: Juan Antonio Breña Moral
 version: 0.12.0-SNAPSHOT
+name: Add Maven dependencies for improved code quality
+description: Treats the user as a knowledgeable partner in solving problems rather than prescribing one-size-fits-all solutions. Presents multiple approaches with clear trade-offs, asking for user input to understand context and constraints. Uses consultative language like "I found several options" and "Which approach fits your situation better?" Acknowledges that the user knows their business domain and team dynamics best, while providing technical expertise to inform decisions.
 ---
 # Add Maven dependencies for improved code quality
 
@@ -232,7 +234,7 @@ Create `.mvn/jvm.config` file with:
 ```
 
 **Package Name Update**: Update the `AnnotatedPackages` configuration in the compiler plugin to match your actual project package structure.
-            
+
 #### Step Constraints
 
 - **MUST** add only dependencies that were selected by the user
@@ -328,7 +330,7 @@ public static void collectionsExample() {
 # Compile will fail with nullness violations
 ./mvnw clean compile -Dmaven.compiler.showWarnings=true
 ```
-            
+
 ## Output Format
 
 - Ask questions one by one following the template exactly
@@ -346,4 +348,4 @@ public static void collectionsExample() {
 - Never proceed without user confirmation for each step
 - Ensure JSpecify dependency uses `provided` scope
 - Ensure VAVR dependency uses default `compile` scope
-- Test enhanced compiler analysis with a simple build
\ No newline at end of file
+- Test enhanced compiler analysis with a simple build
PATCH

echo "Gold patch applied."
