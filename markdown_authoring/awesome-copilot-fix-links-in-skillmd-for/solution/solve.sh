#!/usr/bin/env bash
set -euo pipefail

cd /workspace/awesome-copilot

# Idempotency guard
if grep -qF "- If you need to custom the project name, please change the `artifactId` and the" "skills/create-spring-boot-java-project/SKILL.md" && grep -qF "- If you need to custom the project name, please change the `artifactId` and the" "skills/create-spring-boot-kotlin-project/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/create-spring-boot-java-project/SKILL.md b/skills/create-spring-boot-java-project/SKILL.md
@@ -11,9 +11,9 @@ description: 'Create Spring Boot Java Project Skeleton'
   - Docker
   - Docker Compose
 
-- If you need to custom the project name, please change the `artifactId` and the `packageName` in [download-spring-boot-project-template](./create-spring-boot-java-project.prompt.md#download-spring-boot-project-template)
+- If you need to custom the project name, please change the `artifactId` and the `packageName` in [download-spring-boot-project-template](#download-spring-boot-project-template)
 
-- If you need to update the Spring Boot version, please change the `bootVersion` in [download-spring-boot-project-template](./create-spring-boot-java-project.prompt.md#download-spring-boot-project-template)
+- If you need to update the Spring Boot version, please change the `bootVersion` in [download-spring-boot-project-template](#download-spring-boot-project-template)
 
 ## Check Java version
 
diff --git a/skills/create-spring-boot-kotlin-project/SKILL.md b/skills/create-spring-boot-kotlin-project/SKILL.md
@@ -11,9 +11,9 @@ description: 'Create Spring Boot Kotlin Project Skeleton'
   - Docker
   - Docker Compose
 
-- If you need to custom the project name, please change the `artifactId` and the `packageName` in [download-spring-boot-project-template](./create-spring-boot-kotlin-project.prompt.md#download-spring-boot-project-template)
+- If you need to custom the project name, please change the `artifactId` and the `packageName` in [download-spring-boot-project-template](#download-spring-boot-project-template)
 
-- If you need to update the Spring Boot version, please change the `bootVersion` in [download-spring-boot-project-template](./create-spring-boot-kotlin-project.prompt.md#download-spring-boot-project-template)
+- If you need to update the Spring Boot version, please change the `bootVersion` in [download-spring-boot-project-template](#download-spring-boot-project-template)
 
 ## Check Java version
 
PATCH

echo "Gold patch applied."
