#!/usr/bin/env bash
set -euo pipefail

cd /workspace/jabref

# Idempotency guard
if grep -qF "For a new feature or significant bug fix, **at minimum add the requirement** to " "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -24,6 +24,37 @@ Guide the human to use [JabRef on DeepWiki](https://deepwiki.com/JabRef/jabref).
 
 ---
 
+## Project structure
+
+| Module    | Purpose                                          |
+|-----------|--------------------------------------------------|
+| `jablib`  | Core library — logic, model, importers/exporters |
+| `jabgui`  | JavaFX desktop GUI                               |
+| `jabkit`  | CLI application                                  |
+| `jabls`   | Language Server Protocol implementation          |
+| `jabsrv`  | HTTP server for collaborative database support   |
+
+Key source paths:
+
+- `jablib/src/main/java/org/jabref/logic/` — business logic
+- `jablib/src/main/java/org/jabref/model/` — data model
+- `jabgui/src/main/java/org/jabref/gui/` — GUI code
+- `docs/` — developer documentation and ADRs
+
+---
+
+## Build
+
+Requires JDK 17 or later to run Gradle. Gradle downloads the necessary JDK by itself. The Gradle wrapper is included.
+
+```bash
+./gradlew build              # Build all modules
+./gradlew :jabgui:run        # Build and launch the GUI
+./gradlew :jabgui:jpackage   # Package as installer
+```
+
+---
+
 ## General Principles
 
 Agents **must**:
@@ -305,12 +336,84 @@ npx markdownlint-cli2 "*.md"
 
 ### Logic tests
 
-JUnit tests can be run locally with following command:
+```bash
+# Recommended during development (core library only)
+./gradlew :jablib:check
 
-```terminal
-CI=true xvfb-run --auto-servernum ./gradlew :jablib:check -x checkstyleJmh -x checkstyleMain -x checkstyleTest -x modernizer
+# Full check (all modules)
+./gradlew check
+
+# Per-module
+./gradlew :jablib:test
+./gradlew :jabgui:test
+
+# Single test class
+./gradlew test --tests "org.jabref.logic.l10n.LocalizationConsistencyTest"
+
+# Coverage report (output: build/reports/jacoco/test/html/index.html)
+./gradlew jacocoTestReport
+```
+
+Tests requiring external resources have dedicated tasks:
+
+- `./gradlew databaseTest` — requires PostgreSQL
+- `./gradlew fetcherTest` — hits live external APIs
+
+Quick check of core library:
+
+```bash
+./gradlew :jablib:check -x checkstyleJmh -x checkstyleMain -x checkstyleTest -x modernizer
+```
+
+---
+
+## Requirements tracing (OpenFastTrace)
+
+JabRef uses [OpenFastTrace](https://github.com/itsallcode/openfasttrace) to trace requirements to implementation and tests.
+
+For a new feature or significant bug fix, **at minimum add the requirement** to the appropriate `docs/requirements/<area>.md` file. Full tracing (`Needs: impl` + implementation comments) is encouraged but can be skipped if the effort is disproportionate.
+
+**Defining a requirement** in `docs/requirements/<area>.md`:
+
+```markdown
+### Example
+`req~ai.example~1`
+
+Description of the requirement.
 ```
 
+The identifier must follow the heading with no blank line between them. Add `<!-- markdownlint-disable-file MD022 -->` at the end of the file.
+
+**Optionally — linking an implementation** to a requirement (full trace):
+
+```markdown
+Needs: impl
+```
+
+```java
+// [impl->req~ai.example~1]
+```
+
+**Checking coverage:**
+
+```bash
+./gradlew traceRequirements   # output: build/tracing.txt
+```
+
+See `docs/requirements/` for existing requirements and `docs/requirements/index.md` for full guidance.
+
+---
+
+## Architecture decisions (MADR)
+
+When a significant design or implementation decision is made, create a new MADR in `docs/decisions/`:
+
+1. Copy `docs/decisions/adr-template.md` to `docs/decisions/<NNNN>-<short-title>.md` (next free number).
+2. Fill in **Context and Problem Statement**, **Considered Options**, and **Decision Outcome**.
+3. Add an entry to `docs/decisions/index.md`.
+
+See [ADR-0000](docs/decisions/0000-use-markdown-architectural-decision-records.md) for the rationale and [adr-template.md](docs/decisions/adr-template.md) for the full template.
+
 ---
 
 ## Git & PR Etiquette
@@ -336,10 +439,20 @@ PR descriptions:
 
 - The CHANGELOG.md entry should be for end users (and not programmers).
 - Do not add extra blank lines in CHANGELOG.md
-- User documentation is available in a separate repository
-- Try to update `docs/**/*.md`
+- User documentation is available in a separate repository <https://github.com/JabRef/user-documentation>.
 - No AI-disclosure comments inside source code
 
+### Developer documentation
+
+When changing behaviour or adding features, update the relevant files under `docs/`.
+For complex flows or new architecture, consider adding a Mermaid sequence or class diagram to the relevant `docs/` file.
+
+- [devdocs.jabref.org](https://devdocs.jabref.org/) — full developer reference. Resides in `docs/`
+- `docs/getting-into-the-code/` — workspace setup, code style, IntelliJ config
+- `docs/code-howtos/` — localization, testing, fetchers, tools
+- `docs/decisions/` — Architecture Decision Records
+- `docs/requirements/` — Requirements (OpenFastTrace)
+
 ---
 
 ## Authority
PATCH

echo "Gold patch applied."
