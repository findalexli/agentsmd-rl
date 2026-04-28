#!/usr/bin/env bash
set -euo pipefail

cd /workspace/lastchat

# Idempotency guard
if grep -qF "-   **Lists:** Never pass mutable collections (`SnapshotStateList`) directly to " "AGENTS.md" && grep -qF "CLAUDE.md" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -1,30 +1,98 @@
-# Repository Guidelines
-
-## Project Structure & Modules
-- `app/`: Android app (Jetpack Compose UI, DI, data, Room, navigation).
-- `ai/`: AI SDK and provider integrations (OpenAI, Google, Anthropic) with optional native/NN deps.
-- `highlight/`, `search/`, `tts/`, `common/`: Feature and utility modules.
-- Tests: `ai/src/test` (unit), `ai/src/androidTest` (instrumented); `app/src/test` scaffolded.
-- Assets: `app/src/main/assets`, resources under `app/src/main/res`.
-
-## Coding Style & Naming
-- Kotlin with 4‑space indent, 120 char line limit (`.editorconfig`).
-- Classes/objects: PascalCase; functions/properties: camelCase; resources: snake_case.
-- Compose: Composables start UpperCamelCase; pages typically end with `Page` (e.g., `SettingProviderPage`).
-- Keep modules isolated; share utilities via `common`.
-
-## Testing Guidelines
-- Frameworks: JUnit (unit), AndroidX test/espresso (instrumented).
-- Place unit tests alongside module under `src/test/...`; instrumented under `src/androidTest/...`.
-- Name tests `*Test.kt` and cover parsing, providers, and critical transforms.
-- Validate instrumented flows for streaming/SSE where feasible.
-
-## Commit & PR Guidelines
-- Use Conventional Commits: `feat:`, `fix:`, `chore:`, `refactor:` … with a clear, concise subject. Scope optional.
-- Keep PRs focused; include description, linked issue, and screenshots for UI changes.
-- Run `test` and `lint` before opening PRs; note any platform caveats (device/emulator).
-- Per README: do not submit new languages, unrelated large features, or broad refactors/AI‑generated mass edits.
-
-## Security & Configuration
-- Never commit secrets or signing files. Keep API keys in secure storage; avoid hardcoding.
-- `local.properties` holds signing values; `google-services.json` stays in `app/` and is ignored by Git.
+# AGENTS.md
+
+## 1. Core Principles & Design Philosophy
+
+**App Name:** LastChat (Repo: RikkaHub)
+
+**The "Fidget Toy" Philosophy:**
+LastChat is not just a tool; it is designed to be a "fidget toy".
+-   **Feel:** Interactions must be playful, physics-based, and deeply satisfying.
+-   **Tactile Feedback:** High-quality haptics are non-negotiable. Every tap, toggle, and drag must have appropriate feedback.
+-   **Motion:** **Strictly NO Linear (Tween) animations.** All motion must use physics-based interpolators (springs) to convey momentum and weight.
+
+**Persona & Communication:**
+-   **Tone:** Informal, enthusiastic, and transparent. We celebrate "glow-ups" (improvements) and own our mistakes.
+-   **Security (Sentinel Persona):** "Local First". Privacy is paramount. No hardcoded secrets. Least Privilege. Validate all inputs.
+
+**Workflow:**
+-   **Iterative Polish:** We prefer iterative "glow-ups" of specific components over massive, risky refactors.
+-   **Robustness:** The app must be crash-resistant. `NullPointerException` is the enemy.
+
+## 2. Architecture & Codebase Structure
+
+### Modules
+-   `app/`: Main application module. Contains UI (Compose), Core Logic, DI, Data Layers, and Room Database.
+-   `ai/`: Abstraction layer for AI providers (OpenAI, Google, Anthropic).
+-   `common/`: Shared utilities and extensions.
+-   `highlight/`: Syntax highlighting features.
+-   `search/`: Search functionality (Exa, Tavily, Zhipu).
+-   `tts/`: Text-to-Speech implementation.
+
+### Key Technologies
+-   **Language:** Kotlin (uses experimental `kotlin.uuid.Uuid`).
+-   **UI:** Jetpack Compose (Material You 3 Expressive / Android 16).
+-   **Dependency Injection:** Koin.
+-   **Database:** Room.
+-   **Network:** OkHttp (with SSE support).
+-   **Serialization:** Kotlinx Serialization.
+
+## 3. Coding Standards & Best Practices
+
+### Performance & Concurrency
+-   **I/O Operations:** MUST be explicitly executed on `Dispatchers.IO`.
+    -   *Crucial:* `AppScope` defaults to `Dispatchers.Default`. Do not block the main thread or the default dispatcher with I/O.
+-   **Compose Optimization:**
+    -   **Lists:** Never pass mutable collections (`SnapshotStateList`) directly to `LazyColumn` items. Use `derivedStateOf` to pass simple, immutable states (e.g., `Boolean`) to prevent unnecessary recompositions.
+-   **AI Context:** Prioritize token economy and vector memory efficiency. Use caching.
+
+### Robustness & Safety
+-   **JSON Handling:**
+    -   **STRICTLY PROHIBITED:** Non-null assertions (`!!`) on JSON elements.
+    -   **REQUIRED:** Use safe type checks (`is JsonArray`, `jsonPrimitiveOrNull`).
+-   **State Management:**
+    -   When updating `StateFlow` in services (e.g., `ChatService`), **snapshot** the current value into a local variable before applying complex transformations to avoid race conditions.
+
+### Serialization
+-   Use `me.rerere.rikkahub.utils.JsonInstant` (or `JsonInstantPretty`).
+    -   *Note:* It ignores unknown keys but **does not** apply snake_case strategies. Field mapping must be manual for external APIs.
+
+## 4. UI/UX Guidelines
+
+### Design Language
+-   **Standard:** Material You 3 Expressive / Android 16.
+-   **Shapes:** Adhere strictly to `me.rerere.rikkahub.ui.theme.AppShapes`:
+    -   **Cards:** `AppShapes.CardLarge` (28.dp), `AppShapes.CardMedium` (24.dp).
+    -   **Buttons:** `AppShapes.ButtonPill` (50%).
+
+### Haptics (Critical)
+-   **Library:** Use the custom `PremiumHaptics` wrapper.
+    -   `import me.rerere.rikkahub.ui.hooks.rememberPremiumHaptics`
+    -   `import me.rerere.rikkahub.ui.hooks.HapticPattern`
+-   **Usage:**
+    -   **Do not** use `LocalHapticFeedback`.
+    -   **Interactive Elements:** Buttons (like `BackButton`) must scale down to `0.85f` on press and trigger `HapticPattern.Pop`.
+    -   **Patterns:**
+        -   Click/Toggle: `HapticPattern.Pop`
+        -   Heavy Action/Drop: `HapticPattern.Thud`
+        -   Success: `HapticPattern.Success`
+
+### Animation
+-   **Standard Spec:** `spring(dampingRatio = 0.5f, stiffness = 400f)`
+-   **Bouncy/Clicky Spec:** `spring(dampingRatio = 0.6f, stiffness = 300f)`
+-   **Prohibited:** `tween` or linear animations.
+
+## 5. Specific Feature Guidelines
+
+### RAG & Embeddings
+-   **Persistence:** Embeddings are stored in source entities (`MemoryEntity`, `ChatEpisodeEntity`) **AND** `EmbeddingCacheDAO`.
+-   **Sync:** Operations (add/update/delete) must synchronize both stores.
+-   **Retrieval:** Always prefer existing entity embeddings over re-computation.
+
+### Documentation
+-   **Bolt's Journal:** Record significant performance learnings or critical insights in `.jules/bolt.md` following the existing format.
+
+## 6. Testing & Operations
+-   **Unit Tests:** Place in `src/test`. Cover parsing and logic.
+-   **Instrumented Tests:** Place in `src/androidTest`. Cover flows.
+-   **Commit Guidelines:** Use Conventional Commits (`feat:`, `fix:`, `chore:`).
+-   **Language Support:** Do not submit new languages unless explicitly requested.
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -1,7 +1,5 @@
 # CLAUDE.md
 
-This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
-
 ## Project Overview
 
 LastChat is a native Android LLM chat client that supports switching between different AI providers for conversations.
PATCH

echo "Gold patch applied."
