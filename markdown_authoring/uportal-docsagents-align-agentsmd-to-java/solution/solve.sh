#!/usr/bin/env bash
set -euo pipefail

cd /workspace/uportal

# Idempotency guard
if grep -qF "Source compiles under Java 11, so Java 9\u201311 language features and APIs (`var`, `" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -70,26 +70,26 @@ Source code MUST compile under Java 11. The CI matrix runs builds on Java 11 JVM
 
 ### SDKMAN for Java version management
 
-This project uses [SDKMAN](https://sdkman.io/) to manage Java versions. Common commands:
+This project uses [SDKMAN](https://sdkman.io/) to manage Java versions. uPortal and uPortal-start both require **Java 11**. Common commands:
 
 ```bash
 # List installed Java versions
 sdk list java
 
-# Install Java 8 (required for uPortal-start)
-sdk install java 8.0.472-amzn
+# Install Java 11 (required for uPortal and uPortal-start)
+sdk install java 11.0.30-amzn
 
 # Switch Java version in the current shell
-sdk use java 8.0.472-amzn
+sdk use java 11.0.30-amzn
 
 # Set a default Java version across all shells
-sdk default java 8.0.472-amzn
+sdk default java 11.0.30-amzn
 
 # Verify active version
 java -version
 ```
 
-Use `sdk use java 8.0.472-amzn` before running uPortal-start commands (`portalInit`, `tomcatStart`, etc.).
+Each repo has a `.sdkmanrc` that pins the expected version — `sdk env` inside the repo auto-activates it.
 
 ## Running uPortal locally
 
@@ -182,7 +182,7 @@ ls ~/.m2/repository/org/jasig/portal/uPortal-core/6.0.0-SNAPSHOT/
 | Symptom | Cause | Fix |
 |---------|-------|-----|
 | JARs still show old version (e.g., `5.17.1`) | `uPortalVersion` not changed in uPortal-start `gradle.properties` | Set `uPortalVersion=6.0.0-SNAPSHOT` |
-| `./gradlew install` fails | Java version mismatch | Use `sdk use java 8.0.472-amzn` |
+| `./gradlew install` fails | Java version mismatch | Use `sdk use java 11.0.30-amzn` |
 | Changes not visible after deploy | Tomcat serving cached classes | Run `./gradlew tomcatStop` then `./gradlew tomcatDeploy` (not just `tomcatStart`) |
 | Gradle resolves from Maven Central instead of local | `mavenLocal()` missing from repositories | Already configured in uPortal-start — check `overlays/build.gradle` |
 
@@ -507,13 +507,16 @@ The rendering pipeline uses chained XSLT transformations to compose portal pages
 
 ### Banned patterns
 
+Source compiles under Java 11, so Java 9–11 language features and APIs (`var`, `List.of()`, `Map.of()`, `Optional.isEmpty()`, `String.isBlank()`, etc.) are all fair game. The ban line is **Java 12 and later**.
+
 | Pattern | Why | What to do instead |
 |---------|-----|--------------------|
-| `var` keyword | Java 9+ | Use explicit types |
-| `List.of()`, `Map.of()` | Java 9+ | Use `Collections.unmodifiableList(Arrays.asList(...))` or Guava `ImmutableList.of()` |
-| `Optional.isEmpty()` | Java 11+ | Use `!optional.isPresent()` |
-| `String.isBlank()` | Java 11+ | Use `StringUtils.isBlank()` (commons-lang3) |
-| Records, text blocks, sealed classes | Java 14+ | Use regular classes |
+| Switch expressions with `->` | Java 14+ | Use classic `switch` statements |
+| Text blocks (`"""..."""`) | Java 15+ | Use concatenated string literals |
+| Records | Java 16+ | Use regular classes |
+| Pattern matching for `instanceof` | Java 16+ | Use classic `instanceof` + cast |
+| Sealed classes, `non-sealed`, `permits` | Java 17+ | Use regular classes with package-private constructors |
+| Pattern matching for `switch` | Java 21+ | Use classic `switch` statements |
 | `@BeforeEach`, `@DisplayName` | JUnit 5 | Use `@Before`, `@Test` (JUnit 4) |
 | Inline dependency versions in build.gradle | Breaks version management | Add to `gradle.properties` |
 | `commons-logging` imports | Banned transitive | Use SLF4J (`org.slf4j.Logger`) |
@@ -525,7 +528,7 @@ The rendering pipeline uses chained XSLT transformations to compose portal pages
 [ ] Tests exist for the change (or I've explained why not)
 [ ] Tests pass: ./gradlew :module:test
 [ ] Java formatting passes: ./gradlew verGJF
-[ ] No Java 9+ language features or APIs used
+[ ] No Java 12+ language features or APIs used
 [ ] No new dependencies added without version in gradle.properties
 [ ] License header present on any new files
 [ ] No secrets, passwords, or hardcoded hostnames
@@ -542,4 +545,4 @@ The rendering pipeline uses chained XSLT transformations to compose portal pages
   - You are unsure how existing code works after reading it
   - A change would affect more than one module
   - You cannot write a test to verify your change
-- 🚫 **Never do:** Guess at requirements. Add features that weren't asked for. "Improve" code adjacent to your change. Use Java 9+ features or APIs. Commit secrets.
+- 🚫 **Never do:** Guess at requirements. Add features that weren't asked for. "Improve" code adjacent to your change. Use Java 12+ features or APIs. Commit secrets.
PATCH

echo "Gold patch applied."
