#!/usr/bin/env bash
set -euo pipefail

cd /workspace/quarkus

# Idempotency guard
if grep -qF "./mvnw verify -Dstart-containers -Dtest-containers -Dtest=fully.qualified.ClassN" ".agents/skills/building-and-testing/SKILL.md" && grep -qF "- The project enforces formatting via `formatter-maven-plugin` and `impsort-mave" ".agents/skills/coding-style/SKILL.md" && grep -qF "- **Prefer AssertJ** (`org.assertj.core.api.Assertions.assertThat`) over JUnit 5" ".agents/skills/writing-tests/SKILL.md" && grep -qF "./mvnw -Dquickly                                                                " "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/building-and-testing/SKILL.md b/.agents/skills/building-and-testing/SKILL.md
@@ -38,16 +38,16 @@ This skips tests, ITs, docs, native, and validation.
 
 ```bash
 # Run tests for an extension
-./mvnw verify -f extensions/<name>/
+./mvnw verify -f extensions/<name>/ -Dstart-containers -Dtest-containers
 
 # Run a single test class
-./mvnw test -f integration-tests/<name>/ -Dtest=MyTest
+./mvnw test -f integration-tests/<name>/ -Dstart-containers -Dtest-containers -Dtest=MyTest
 
 # Run a single test method
-./mvnw verify -Dtest=fully.qualified.ClassName#methodName
+./mvnw verify -Dstart-containers -Dtest-containers -Dtest=fully.qualified.ClassName#methodName
 
 # Native integration tests
-./mvnw verify -f integration-tests/<name>/ -Dnative
+./mvnw verify -f integration-tests/<name>/ -Dstart-containers -Dtest-containers -Dnative
 ```
 
 ## Incremental Build
diff --git a/.agents/skills/coding-style/SKILL.md b/.agents/skills/coding-style/SKILL.md
@@ -10,7 +10,8 @@ description: >
 ## Formatting
 
 - Quarkus uses 4-space indentation (no tabs)
-- The project enforces formatting via `formatter-maven-plugin` and `impsort-maven-plugin`
+- The project enforces formatting via `formatter-maven-plugin` and `impsort-maven-plugin`,
+  let the formatting plugins do their work, never use `-Dno-format`
 - Formatter config: `independent-projects/ide-config/src/main/resources/eclipse-format.xml`
 - Run `./mvnw process-sources` on your module to auto-format before committing
 - The build **will fail** on formatting violations
@@ -42,6 +43,8 @@ description: >
 - Avoid `static` imports except for well-known patterns (e.g., test assertions)
 - **Minimize lambdas and streams in runtime code** — reduces memory footprint for native
 - Prefer descriptive method and variable names over comments
+- Update existing code comments if your changes make them invalid
+- Never remove existing code comments that are still valid
 - Keep methods focused and short; extract when complexity warrants it
 - Use `Optional` for API return types that may be absent. In internal hot runtime
   code paths, direct null checks are acceptable for performance
diff --git a/.agents/skills/writing-tests/SKILL.md b/.agents/skills/writing-tests/SKILL.md
@@ -87,6 +87,13 @@ run the TCKs:
 ./mvnw verify -f tcks/<area>/ -Ptcks
 ```
 
+## Assertions
+
+- **Prefer AssertJ** (`org.assertj.core.api.Assertions.assertThat`) over JUnit 5
+  assertions (`org.junit.jupiter.api.Assertions`). AssertJ provides fluent,
+  readable assertions and better failure messages.
+- Use RestAssured for HTTP endpoint testing.
+
 ## Key Rules
 
 - Do NOT use `@QuarkusTest` in deployment module tests — use `QuarkusExtensionTest`
diff --git a/AGENTS.md b/AGENTS.md
@@ -9,7 +9,8 @@ when performing that type of work.
 - **Update documentation.** When changes affect user-facing behavior, config, or
   APIs, update the relevant `.adoc` files in `docs/src/main/asciidoc/`.
 - **Add or update tests.** Bug fixes need a reproducer test. New features need
-  tests. Test in both JVM and native mode for non-trivial changes.
+  tests. Test in both JVM and native mode for non-trivial changes. Prefer
+  AssertJ for assertions.
 - **You are responsible for what you submit.** Validate all changes. Do not
   submit AI-generated code without human oversight.
 
@@ -50,12 +51,12 @@ Quarkus has a split classloading model — the #1 source of mistakes:
 ## Build Commands
 
 ```bash
-./mvnw -Dquickly                           # Quick full build (skip tests/docs/native)
-./mvnw install -f extensions/<name>/       # Build one extension
-./mvnw install -f core/ -DskipTests        # Build core
-./mvnw verify -f extensions/<name>/        # Run extension tests
-./mvnw test -Dtest=MyTest                  # Run single test
-./mvnw verify -f integration-tests/<name>/ -Dnative  # Native tests
+./mvnw -Dquickly                                                                          # Quick full build (skip tests/docs/native)
+./mvnw install -f extensions/<name>/                                                      # Build one extension
+./mvnw install -f core/ -DskipTests                                                       # Build core
+./mvnw verify -f extensions/<name>/ -Dtest-containers -Dstart-containers                  # Run extension tests
+./mvnw test -Dtest=MyTest -Dtest-containers -Dstart-containers                            # Run single test
+./mvnw verify -f integration-tests/<name>/ -Dtest-containers -Dstart-containers -Dnative  # Native tests
 ```
 
 Set `MAVEN_OPTS="-Xmx4g"`. Always use `install` (not just `compile`).
@@ -65,14 +66,27 @@ If you change a runtime module, rebuild its deployment module too.
 |------|---------|
 | `-Dquickly` | Skip tests, ITs, docs, native, validation |
 | `-Dnative` | Build and test native image |
-| `-Dno-format` | Skip formatting check |
 | `-DskipTests` | Skip unit tests |
 | `-Dincremental` | Only build changed modules |
+| `-Dtest-containers -Dstart-containers` | Auto-start containers for tests (always use when running tests) |
+
+**Do NOT use `-Dno-format`** to skip formatting checks. Formatting and
+import sorting are applied automatically during compilation — there is no
+need for a separate step. Let the build fix formatting for you.
+
+## Editing Rules
+
+- **Preserve existing comments.** When editing a section of code, keep all
+  existing comments that are not directly invalidated by your change. Never
+  drop comments from code you are not modifying.
 
 ## Coding Style Essentials
 
 - 4-space indentation, enforced by `formatter-maven-plugin` — run
   `./mvnw process-sources` to auto-format
+- **Never manually sort or reorder imports** — `impsort-maven-plugin` handles
+  import ordering automatically. Just add imports where needed; do not make
+  edits whose sole purpose is reorganizing imports.
 - Use **JBoss Logging** (`org.jboss.logging.Logger`), not SLF4J/JUL/Log4j
 - No `@author` tags, no wildcard imports
 - Naming: `<Feature>Processor.java`, `<Feature>Recorder.java`,
PATCH

echo "Gold patch applied."
