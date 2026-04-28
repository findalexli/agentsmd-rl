#!/usr/bin/env bash
set -euo pipefail

cd /workspace/coil

# Idempotency guard
if grep -qF "- Multimodule Kotlin project with public modules like `coil`, `coil-core`, `coil" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -1,37 +1,31 @@
 # Repository Guidelines
 
 ## Project Structure & Module Organization
-- Multimodule Kotlin (KMP + Android) project managed by Gradle Kotlin DSL.
-- Public modules: `coil`, `coil-core`, `coil-compose`, `coil-compose-core`, `coil-network-*`, `coil-gif`, `coil-svg`, `coil-video`, `coil-bom`, `coil-test`.
-- Private/testing and samples live under `internal/*` and `samples/*`.
-- Source layout per module: `src/commonMain`, `src/jvmMain`, `src/androidMain`, `src/*Test` (e.g., `commonTest`, `jvmTest`, `androidUnitTest`), and `src/androidInstrumentedTest` where applicable.
+- Multimodule Kotlin project with public modules like `coil`, `coil-core`, `coil-compose`, network adapters, and artifacts under `internal/*` and `samples/*`.
+- Source sets follow `src/commonMain`, `src/jvmMain`, `src/androidMain`, plus matching `*Test` directories (for example `coil-core/src/commonTest`).
+- Shared test utilities live in `coil-test`, while platform demos reside in `samples/view` and `samples/compose`.
 
 ## Build, Test, and Development Commands
-- `./gradlew build`: Compile all modules and assemble artifacts.
-- `./gradlew check`: Run unit tests and verification tasks.
-- `./gradlew apiCheck`: Validate public API (binary compatibility).
-- `./gradlew spotlessApply` / `spotlessCheck`: Format or verify Kotlin/KTS style.
-- `./test.sh`: CI-equivalent suite (API, unit, connected, screenshot tests).
-- Screenshot tests: `./verify_screenshot_tests.sh` to verify; `./record_screenshot_tests.sh` to update snapshots.
-- Instrumentation: `./gradlew connectedDebugAndroidTest` (requires emulator/device).
-- Samples: `:samples:view:installDebug` (Android View); `:samples:compose:run` (Compose Desktop).
+- `./gradlew build` – compile every module and produce distributables.
+- `./gradlew check` – run unit tests and verification tasks across targets.
+- `./gradlew apiCheck` – verify binary compatibility for public APIs.
+- `./gradlew spotlessApply` / `spotlessCheck` – format Kotlin + KTS sources or validate formatting.
+- Samples: `./gradlew :samples:view:installDebug` (Android) or `./gradlew :samples:compose:run` (Desktop preview).
 
 ## Coding Style & Naming Conventions
-- Kotlin-first codebase. Indent 4 spaces, LF endings, ~100 char line length, trailing commas allowed.
-- Formatting via Spotless + ktlint. Run `./gradlew spotlessApply` before pushing.
-- Names: classes/objects `UpperCamelCase`; functions/properties `lowerCamelCase`; constants `UPPER_SNAKE_CASE`; packages lowercase.
+- Kotlin-first codebase, 4-space indent, LF endings, ~100 char guideline, trailing commas allowed where supported.
+- Run Spotless (ktlint) before committing; avoid manual formatting of generated code.
+- Naming: classes/objects UpperCamelCase, functions/props lowerCamelCase, constants UPPER_SNAKE_CASE, packages lowercase.
 
 ## Testing Guidelines
-- Place tests under `src/<target>Test` (e.g., `commonTest`, `jvmTest`, `androidUnitTest`).
-- Android instrumentation tests in `src/androidInstrumentedTest`; run `connectedDebugAndroidTest`.
-- Screenshot tests use Paparazzi/Roborazzi; verify/update with the provided scripts.
-- Prefer deterministic tests (no live network). Use helpers in `coil-test` and `internal:test-utils`.
+- Place tests inside the matching `src/<target>Test` tree; prefer deterministic mocks over live network.
+- Run `./gradlew check` for JVM/common tests and `./gradlew connectedDebugAndroidTest` for device tests (emulator required).
+- Screenshot tests use `./verify_screenshot_tests.sh`; update baselines with `./record_screenshot_tests.sh`.
 
 ## Commit & Pull Request Guidelines
-- Commits: imperative mood; prefer Conventional Commits (e.g., `feat:`, `fix:`, `chore(deps):`). Reference issues/PRs when relevant.
-- PRs: clear description, linked issues, and screenshots/GIFs for UI-visible changes.
-- Before opening a PR: run `./test.sh`, ensure `spotlessCheck` passes, and run `apiCheck` for public API changes.
+- Write commits in imperative mood, ideally Conventional Commits (e.g., `feat: add gif sample`).
+- Before pushing, run `./test.sh`, `spotlessCheck`, and `apiCheck` when APIs change.
+- PRs should describe intent, link related issues, and include screenshots or GIFs for visual updates.
 
 ## Security & Configuration Tips
-- Use JDK 17 (`JAVA_VERSION=17`) to match CI.
-- Avoid committing secrets. Keep builds/tests deterministic; no live network in tests.
+- Target JDK 17 locally (`JAVA_VERSION=17`), keep dependencies deterministic, and avoid embedding secrets in code or tests.
PATCH

echo "Gold patch applied."
