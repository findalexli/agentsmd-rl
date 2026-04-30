#!/usr/bin/env bash
set -euo pipefail

cd /workspace/unity-cli-loop

# Idempotency guard
if grep -qF "- `Message` (string): Description of the result; carries the failure summary whe" ".agents/skills/uloop-clear-console/SKILL.md" && grep -qF "`uloop launch` auto-detects the project at the current working directory and ope" ".agents/skills/uloop-compile/SKILL.md" && grep -qF "- PlayMode entry may complete on the next editor frame. If a PlayMode-dependent " ".agents/skills/uloop-control-play-mode/SKILL.md" && grep -qF "On `Success: false`, inspect `CompilationErrors` first. If empty, read `ErrorMes" ".agents/skills/uloop-execute-dynamic-code/SKILL.md" && grep -qF "description: \"Find GameObjects in the active scene by various criteria. Use when" ".agents/skills/uloop-find-game-objects/SKILL.md" && grep -qF "- `Message`: Status message (e.g. `Unity Editor window focused (PID: 12345)`, or" ".agents/skills/uloop-focus-window/SKILL.md" && grep -qF "description: \"Get Unity scene hierarchy as a structured tree. Use when you need " ".agents/skills/uloop-get-hierarchy/SKILL.md" && grep -qF "description: \"Retrieve current Unity Console entries via uloop CLI. Use when you" ".agents/skills/uloop-get-logs/SKILL.md" && grep -qF "`uloop launch` is not fire-and-forget. When Unity needs to start or restart, the" ".agents/skills/uloop-launch/SKILL.md" && grep -qF "description: \"Record keyboard and mouse input during PlayMode into a JSON file. " ".agents/skills/uloop-record-input/SKILL.md" && grep -qF "Replay injects input frame-by-frame, so the game must produce identical results " ".agents/skills/uloop-record-input/references/deterministic-replay.md" && grep -qF "description: \"Replay recorded input during PlayMode with frame-precise injection" ".agents/skills/uloop-replay-input/SKILL.md" && grep -qF "Replay injects input frame-by-frame, so the game must produce identical results " ".agents/skills/uloop-replay-input/references/deterministic-replay.md" && grep -qF "Before executing tests, `uloop run-tests` checks for unsaved loaded Scene change" ".agents/skills/uloop-run-tests/SKILL.md" && grep -qF "description: \"Capture screenshots of Unity Editor windows as PNG files. Use when" ".agents/skills/uloop-screenshot/SKILL.md" && grep -qF "Annotated screenshots compensate border thickness for `ResolutionScale`, so the " ".agents/skills/uloop-screenshot/references/annotated-elements.md" && grep -qF "description: \"Simulate keyboard key input in PlayMode via Input System. Use when" ".agents/skills/uloop-simulate-keyboard/SKILL.md" && grep -qF "description: \"Simulate mouse input in PlayMode for gameplay code that reads Unit" ".agents/skills/uloop-simulate-mouse-input/SKILL.md" && grep -qF "description: \"Simulate mouse click, long-press, and drag on PlayMode UI elements" ".agents/skills/uloop-simulate-mouse-ui/SKILL.md" && grep -qF "- `Message` (string): Description of the result; carries the failure summary whe" ".claude/skills/uloop-clear-console/SKILL.md" && grep -qF "`uloop launch` auto-detects the project at the current working directory and ope" ".claude/skills/uloop-compile/SKILL.md" && grep -qF "- PlayMode entry may complete on the next editor frame. If a PlayMode-dependent " ".claude/skills/uloop-control-play-mode/SKILL.md" && grep -qF "description: \"Execute C# code dynamically in Unity Editor. Use when you need to:" ".claude/skills/uloop-execute-dynamic-code/SKILL.md" && grep -qF ".claude/skills/uloop-execute-menu-item/SKILL.md" ".claude/skills/uloop-execute-menu-item/SKILL.md" && grep -qF "description: \"Find GameObjects in the active scene by various criteria. Use when" ".claude/skills/uloop-find-game-objects/SKILL.md" && grep -qF "- `Message`: Status message (e.g. `Unity Editor window focused (PID: 12345)`, or" ".claude/skills/uloop-focus-window/SKILL.md" && grep -qF "description: \"Get Unity scene hierarchy as a structured tree. Use when you need " ".claude/skills/uloop-get-hierarchy/SKILL.md" && grep -qF "description: \"Retrieve current Unity Console entries via uloop CLI. Use when you" ".claude/skills/uloop-get-logs/SKILL.md" && grep -qF "`uloop launch` is not fire-and-forget. When Unity needs to start or restart, the" ".claude/skills/uloop-launch/SKILL.md" && grep -qF "description: \"Record keyboard and mouse input during PlayMode into a JSON file. " ".claude/skills/uloop-record-input/SKILL.md" && grep -qF "Replay injects input frame-by-frame, so the game must produce identical results " ".claude/skills/uloop-record-input/references/deterministic-replay.md" && grep -qF "description: \"Replay recorded input during PlayMode with frame-precise injection" ".claude/skills/uloop-replay-input/SKILL.md" && grep -qF "Replay injects input frame-by-frame, so the game must produce identical results " ".claude/skills/uloop-replay-input/references/deterministic-replay.md" && grep -qF "Before executing tests, `uloop run-tests` checks for unsaved loaded Scene change" ".claude/skills/uloop-run-tests/SKILL.md" && grep -qF "description: \"Capture screenshots of Unity Editor windows as PNG files. Use when" ".claude/skills/uloop-screenshot/SKILL.md" && grep -qF "Annotated screenshots compensate border thickness for `ResolutionScale`, so the " ".claude/skills/uloop-screenshot/references/annotated-elements.md" && grep -qF "description: \"Simulate keyboard key input in PlayMode via Input System. Use when" ".claude/skills/uloop-simulate-keyboard/SKILL.md" && grep -qF "description: \"Simulate mouse input in PlayMode for gameplay code that reads Unit" ".claude/skills/uloop-simulate-mouse-input/SKILL.md" && grep -qF "description: \"Simulate mouse click, long-press, and drag on PlayMode UI elements" ".claude/skills/uloop-simulate-mouse-ui/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/uloop-clear-console/SKILL.md b/.agents/skills/uloop-clear-console/SKILL.md
@@ -37,4 +37,12 @@ uloop clear-console --add-confirmation-message
 
 ## Output
 
-Returns JSON confirming the console was cleared.
+Returns JSON with:
+- `Success` (boolean): Whether the clear operation succeeded
+- `ClearedLogCount` (number): Total number of log entries that were cleared
+- `ClearedCounts` (object): Breakdown by log type
+  - `ErrorCount` (number): Errors cleared
+  - `WarningCount` (number): Warnings cleared
+  - `LogCount` (number): Info logs cleared
+- `Message` (string): Description of the result; carries the failure summary when the operation fails (e.g. `"Failed to clear console: ..."`)
+- `ErrorMessage` (string): Currently always empty for this tool — read `Message` for failure details
diff --git a/.agents/skills/uloop-compile/SKILL.md b/.agents/skills/uloop-compile/SKILL.md
@@ -51,10 +51,20 @@ Returns JSON:
 
 ## Troubleshooting
 
-If CLI hangs or shows "Unity is busy" errors after compilation, stale lock files may be preventing connection. Run the following to clean them up:
+Diagnose the failure mode before retrying.
+
+**Stale lock files** (CLI hangs or shows "Unity is busy" while Unity Editor *is* running):
 
 ```bash
 uloop fix
 ```
 
-This removes any leftover lock files (`compiling.lock`, `domainreload.lock`, `serverstarting.lock`) from the Unity project's Temp directory.
+This removes any leftover lock files (`compiling.lock`, `domainreload.lock`, `serverstarting.lock`) from the Unity project's Temp directory. Then retry `uloop compile`.
+
+**Unity Editor not running** (CLI returns a connection failure and no Unity process is alive):
+
+```bash
+uloop launch
+```
+
+`uloop launch` auto-detects the project at the current working directory and opens it in the matching Unity Editor version. After Unity finishes launching, retry `uloop compile`.
diff --git a/.agents/skills/uloop-control-play-mode/SKILL.md b/.agents/skills/uloop-control-play-mode/SKILL.md
@@ -51,3 +51,5 @@ Returns JSON with the current play mode state:
 - Stop action exits play mode and returns to edit mode
 - Pause action pauses the game while remaining in play mode
 - Useful for automated testing workflows
+
+- PlayMode entry may complete on the next editor frame. If a PlayMode-dependent command reports "PlayMode is not active" immediately after `--action Play`, wait briefly and retry.
diff --git a/.agents/skills/uloop-execute-dynamic-code/SKILL.md b/.agents/skills/uloop-execute-dynamic-code/SKILL.md
@@ -35,6 +35,22 @@ return x;
 
 **Forbidden** — these will be rejected at compile time: `System.IO.*`, `AssetDatabase.CreateFolder`, creating/editing `.cs`/`.asmdef` files. Use terminal commands for file operations instead.
 
+## Output
+
+Returns JSON:
+- `Success`: boolean — overall execution success
+- `Result`: string — value of the snippet's `return` statement (empty when omitted)
+- `Logs`: string[] — `Debug.Log` / `Debug.LogWarning` / `Debug.LogError` messages emitted during the run
+- `CompilationErrors`: object[] — Roslyn diagnostics with `Message`, `Line`, `Column`, `ErrorCode`, optional `Hint` and `Suggestions`
+- `ErrorMessage`: string — top-level failure summary (empty on success)
+- `Error`: string — alias of `ErrorMessage`
+- `SecurityLevel`: string — dynamic-code security level active for the request
+- `UpdatedCode`: string|null — the wrapped form actually compiled (handy when debugging using-statement reordering)
+- `DiagnosticsSummary`: string|null — compact summary when diagnostics are available
+- `Diagnostics`: object[] — structured diagnostics; same shape as `CompilationErrors`, usually populated together with it
+
+On `Success: false`, inspect `CompilationErrors` first. If empty, read `ErrorMessage` (and `Logs` for extra context) — the failure may be a runtime exception, security violation, cancellation, or an "execution in progress" rejection, all of which return empty `CompilationErrors`. Both EditMode and PlayMode are supported targets — the snippet runs in whichever mode the Editor is currently in.
+
 ## Code Examples by Category
 
 For detailed code examples, refer to these files:
diff --git a/.agents/skills/uloop-find-game-objects/SKILL.md b/.agents/skills/uloop-find-game-objects/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: uloop-find-game-objects
-description: "Find GameObjects in the active scene by various criteria. Use when you need to: (1) Search for objects by name, regex, or path, (2) Find objects with specific components, tags, or layers, (3) Get currently selected GameObjects in Unity Editor. Returns matching GameObjects with hierarchy paths and components."
+description: "Find GameObjects in the active scene by various criteria. Use when you need to: (1) Search for objects by name, regex, or path, (2) Find objects with specific components, tags, or layers, (3) Get currently selected GameObjects in Unity Editor. Returns matching GameObjects with hierarchy paths and components (or writes to a file when multiple GameObjects are selected)."
 ---
 
 # uloop find-game-objects
@@ -66,9 +66,22 @@ uloop find-game-objects --search-mode Selected --include-inactive
 
 ## Output
 
-Returns JSON with matching GameObjects.
-
-For `Selected` mode with multiple objects, results are exported to file:
-- Single selection: JSON response directly
-- Multiple selection: File at `.uloop/outputs/FindGameObjectsResults/`
-- No selection: Empty results with message
+Returns JSON with:
+- `results` (array): Matching GameObjects, each containing:
+  - `name` (string): GameObject name
+  - `path` (string): Hierarchy path (e.g., `Canvas/Panel/Button`)
+  - `isActive` (boolean): Active state in hierarchy
+  - `tag` (string): GameObject tag
+  - `layer` (number): Layer index
+  - `components` (array): Each entry has `type` (short name, e.g., `Rigidbody`), `fullTypeName` (e.g., `UnityEngine.Rigidbody`), and `properties` (array of Inspector-visible `{name, type, value}` pairs)
+- `totalFound` (number): Number of results returned inline, or number exported for multi-selection file output. For search modes, this is after `--max-results` clipping and serialization.
+- `errorMessage` (string): Top-level failure summary (empty on success)
+- `processingErrors` (array): Selected-mode per-GameObject serialization failures, each `{gameObjectName, gameObjectPath, error}`. Omitted/null or empty on clean runs.
+
+### Multi-selection file export
+
+For `Selected` mode with **multiple** successfully serialized GameObjects, inline `results` is not populated and the data is written to a file instead. Two extra fields appear:
+- `resultsFilePath` (string): Relative path under `.uloop/outputs/FindGameObjectsResults/`
+- `message` (string): Human-readable summary (e.g., "5 GameObjects exported")
+
+Single-selection and search-mode calls (`Exact`, `Path`, `Regex`, `Contains`) always return inline. No selection (`Selected` mode with empty selection) returns empty `results` plus a `message`.
diff --git a/.agents/skills/uloop-focus-window/SKILL.md b/.agents/skills/uloop-focus-window/SKILL.md
@@ -32,7 +32,11 @@ uloop focus-window
 
 ## Output
 
-Returns JSON confirming the window was focused.
+Returns JSON with:
+- `Success`: Whether the focus operation succeeded
+- `Message`: Status message (e.g. `Unity Editor window focused (PID: 12345)`, or the failure reason such as `Unity project not found` / `No running Unity process found for this project` / `Failed to focus Unity window: <reason>`)
+
+These are the only two fields. There is no PID, window-handle, or platform field returned to the caller.
 
 ## Notes
 
diff --git a/.agents/skills/uloop-get-hierarchy/SKILL.md b/.agents/skills/uloop-get-hierarchy/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: uloop-get-hierarchy
-description: "Get Unity scene hierarchy as a structured tree. Use when you need to: (1) Inspect scene structure and parent-child relationships, (2) Explore GameObjects and their components, (3) Get hierarchy from a specific root path or selected objects. Returns the scene's GameObject tree."
+description: "Get Unity scene hierarchy as a structured tree. Use when you need to: (1) Inspect scene structure and parent-child relationships, (2) Explore GameObjects and their components, (3) Get hierarchy from a specific root path or selected objects. Hierarchy data is written to a JSON file on disk and the response returns the file path (not the tree inline) — open the file to read the structure."
 ---
 
 # uloop get-hierarchy
@@ -52,4 +52,8 @@ uloop get-hierarchy --use-selection
 
 ## Output
 
-Returns JSON with hierarchical structure of GameObjects and their components.
+Returns JSON with:
+- `message` (string): Human-readable guidance pointing at the saved file
+- `hierarchyFilePath` (string): Filesystem path to the JSON file that contains the actual hierarchy data
+
+The hierarchy itself is **not** in the response — it is written to the file at `hierarchyFilePath`. Open that file to read the `Context` and `Hierarchy` payload (GameObject tree, components, etc.).
diff --git a/.agents/skills/uloop-get-logs/SKILL.md b/.agents/skills/uloop-get-logs/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: uloop-get-logs
-description: "Retrieve logs from Unity Console with filtering and search. Use when you need to: (1) Check for errors or warnings after compilation or play mode, (2) Debug issues by searching log messages, (3) Investigate failures with stack traces. Supports filtering by log type, text search, and regex."
+description: "Retrieve current Unity Console entries via uloop CLI. Use when you need to: (1) inspect errors, warnings, or logs after compile, tests, PlayMode, or dynamic code execution, (2) search current Console messages or stack traces, (3) confirm whether a recent Unity operation emitted logs. Prefer this over reading Editor.log or Unity log files for normal Console contents; use log files only for startup, crash, freeze, or uloop connection failures."
 ---
 
 # uloop get-logs
@@ -48,4 +48,14 @@ uloop get-logs --search-text "Missing.*Component" --use-regex
 
 ## Output
 
-Returns JSON array of log entries with message, type, and optional stack trace.
+Returns JSON with:
+- `TotalCount` (number): Total logs available before max-count clipping
+- `DisplayedCount` (number): Logs returned in this response (≤ `--max-count`)
+- `LogType` (string): The `--log-type` filter that was applied
+- `MaxCount` (number): The `--max-count` cap that was applied
+- `SearchText` (string): The `--search-text` filter that was applied (empty when omitted)
+- `IncludeStackTrace` (boolean): Whether stack traces are included in `Logs[]`
+- `Logs` (array): Each entry has:
+  - `Type` (string): `"Error"`, `"Warning"`, or `"Log"`
+  - `Message` (string): Log message body
+  - `StackTrace` (string): Stack trace text. Empty when `--include-stack-trace` is `false`.
diff --git a/.agents/skills/uloop-launch/SKILL.md b/.agents/skills/uloop-launch/SKILL.md
@@ -7,6 +7,9 @@ description: "Launch Unity project with matching Editor version via uloop CLI. U
 
 Launch Unity Editor with the correct version for a project.
 
+`uloop launch` is not fire-and-forget. When Unity needs to start or restart, the command waits
+until Unity is actually ready for CLI operations before it exits.
+
 ## Usage
 
 ```bash
@@ -48,4 +51,4 @@ uloop launch -a
 - Prints detected Unity version
 - Prints project path
 - If Unity is already running, focuses the existing window
-- If launching, opens Unity in background
+- If launching, waits until Unity finishes startup and the CLI can connect to the project
diff --git a/.agents/skills/uloop-record-input/SKILL.md b/.agents/skills/uloop-record-input/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: uloop-record-input
-description: "Record keyboard and mouse input during PlayMode into a JSON file. Use when you need to: (1) Capture human gameplay input for later replay, (2) Record input sequences for E2E testing, (3) Save input for bug reproduction."
+description: "Record keyboard and mouse input during PlayMode into a JSON file. Use when you need to: (1) Capture human gameplay input for later replay, (2) Record input sequences for E2E testing, (3) Save input for bug reproduction. Captures Input System device-state diffs frame-by-frame in PlayMode and serializes them to JSON when stopped. Requires PlayMode and the New Input System."
 ---
 
 # uloop record-input
@@ -31,21 +31,9 @@ uloop record-input --action Stop --output-path scripts/my-play.json
 | `--output-path` | string | auto | Save path. Auto-generates under `.uloop/outputs/InputRecordings/` |
 | `--keys` | string | `""` | Comma-separated key filter. Empty = all common game keys |
 
-## Design Guidelines for Deterministic Replay
+## Deterministic Replay
 
-Replay injects input frame-by-frame, so the game must produce identical results given identical input on each run. The following patterns break determinism and must be avoided in replay-targeted code:
-
-| Avoid | Use Instead | Why |
-|-------|-------------|-----|
-| `Time.deltaTime` for movement | Fixed per-frame constant (e.g. `MOVE_SPEED = 0.1f`) | deltaTime varies between runs even at the same target frame rate |
-| `Random.Range()` / `UnityEngine.Random` | Seeded random (`new System.Random(fixedSeed)`) or remove randomness | Different random sequence each run |
-| `Rigidbody` / Physics simulation | Kinematic movement via `Transform.Translate` | Physics is non-deterministic across runs |
-| `WaitForSeconds(n)` in coroutines | `WaitForEndOfFrame` or frame counting | Real-time waits depend on frame timing |
-| `Time.time` / `Time.realtimeSinceStartup` | Frame counter (`Time.frameCount - startFrame`) | Time values drift between runs |
-| `FindObjectsOfType` without sort | `FindObjectsByType(FindObjectsSortMode.InstanceID)` | Iteration order is non-deterministic |
-| `async/await` with `Task.Delay` | Frame-based waiting | Real-time delays are non-deterministic |
-
-Set `Application.targetFrameRate = 60` (or your target) to reduce frame timing variance. See `InputReplayVerificationController` for a complete example of deterministic game logic.
+Replay injects input frame-by-frame, so the game must also be deterministic to produce identical results. If the recording will be used for E2E tests, bug reproduction, or replay verification, read [references/deterministic-replay.md](references/deterministic-replay.md) before designing assertions or game logic.
 
 ## Prerequisites
 
@@ -55,9 +43,12 @@ Set `Application.targetFrameRate = 60` (or your target) to reduce frame timing v
 
 ## Output
 
-Returns JSON with:
+The CLI prints JSON with:
 - `Success`: Whether the operation succeeded
 - `Message`: Status message
-- `OutputPath`: Path to saved recording (Stop only)
-- `TotalFrames`: Number of frames recorded (Stop only)
-- `DurationSeconds`: Recording duration in seconds (Stop only)
+- `Action`: Echoes which action was executed (`Start` or `Stop`)
+- `OutputPath`: Path to saved recording (nullable; populated on `Stop` only)
+- `TotalFrames`: Number of frames recorded (nullable int; populated on `Stop` only)
+- `DurationSeconds`: Recording duration in seconds (nullable float; populated on `Stop` only)
+
+The CLI output contains only these six payload fields. Internal metadata such as `Ver` is removed before printing. There is no `RecordingId`, `StartTimestamp`, `KeysCaptured`, or per-frame data in the response — frame data lives only in the JSON file at `OutputPath`.
diff --git a/.agents/skills/uloop-record-input/references/deterministic-replay.md b/.agents/skills/uloop-record-input/references/deterministic-replay.md
@@ -0,0 +1,15 @@
+# Deterministic Replay
+
+Replay injects input frame-by-frame, so the game must produce identical results given identical input on each run. The following patterns break determinism and should be avoided in replay-targeted code:
+
+| Avoid | Use Instead | Why |
+|-------|-------------|-----|
+| `Time.deltaTime` for movement | Fixed per-frame constant (e.g. `MOVE_SPEED = 0.1f`) | Delta time varies between runs even at the same target frame rate |
+| `Random.Range()` / `UnityEngine.Random` | Seeded random (`new System.Random(fixedSeed)`) or remove randomness | Random sequences differ between runs |
+| `Rigidbody` / Physics simulation | Kinematic movement via `Transform.Translate` | Physics is non-deterministic across runs |
+| `WaitForSeconds(n)` in coroutines | `WaitForEndOfFrame` or frame counting | Real-time waits depend on frame timing |
+| `Time.time` / `Time.realtimeSinceStartup` | Frame counter (`Time.frameCount - startFrame`) | Time values drift between runs |
+| `FindObjectsOfType` without sort | `FindObjectsByType(FindObjectsSortMode.InstanceID)` | Iteration order is non-deterministic |
+| `async/await` with `Task.Delay` | Frame-based waiting | Real-time delays are non-deterministic |
+
+Set `Application.targetFrameRate = 60` or another fixed target to reduce frame timing variance. See `InputReplayVerificationController` for a complete example of deterministic game logic.
diff --git a/.agents/skills/uloop-replay-input/SKILL.md b/.agents/skills/uloop-replay-input/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: uloop-replay-input
-description: "Replay recorded input during PlayMode with frame-precise injection. Use when you need to: (1) Reproduce recorded gameplay exactly, (2) Run E2E tests from recorded input, (3) Generate demo videos with consistent input."
+description: "Replay recorded input during PlayMode with frame-precise injection. Use when you need to: (1) Reproduce recorded gameplay exactly, (2) Run E2E tests from recorded input, (3) Generate demo videos with consistent input. Deserializes the JSON recording and pushes captured device states back into Mouse.current / Keyboard.current frame-by-frame in PlayMode. Requires PlayMode and the New Input System."
 ---
 
 # uloop replay-input
@@ -37,15 +37,18 @@ uloop replay-input --action Stop
 
 ## Deterministic Replay
 
-Replay injects the exact same input frame-by-frame, but the game must also be deterministic to produce identical results. See the **"Design Guidelines for Deterministic Replay"** section in the `record-input` skill for the full list of patterns to avoid (`Time.deltaTime`, `Random.Range`, physics, etc.) and their deterministic alternatives.
+Replay injects the exact same input frame-by-frame, but the game must also be deterministic to produce identical results. If replay output must be compared across runs, read [references/deterministic-replay.md](references/deterministic-replay.md) before interpreting failures.
 
 ## Output
 
 Returns JSON with:
 - `Success`: Whether the operation succeeded
 - `Message`: Status message
-- `InputPath`: Path to recording file (Start only)
-- `CurrentFrame`: Current replay frame
-- `TotalFrames`: Total frames in recording
-- `Progress`: Replay progress (0.0 - 1.0)
-- `IsReplaying`: Whether replay is active
+- `Action`: Echoes which action was executed (`Start`, `Stop`, or `Status`)
+- `InputPath`: Path to recording file (nullable string; populated on `Start` only)
+- `CurrentFrame`: Current replay frame index (nullable int)
+- `TotalFrames`: Total frames in the recording (nullable int)
+- `Progress`: Replay progress (nullable float in 0.0 – 1.0)
+- `IsReplaying`: Whether replay is currently active (nullable bool)
+
+These are the only eight fields. There is no `LoopCount`, `ElapsedSeconds`, `OverlayVisible`, or per-frame inspection data in the response.
diff --git a/.agents/skills/uloop-replay-input/references/deterministic-replay.md b/.agents/skills/uloop-replay-input/references/deterministic-replay.md
@@ -0,0 +1,15 @@
+# Deterministic Replay
+
+Replay injects input frame-by-frame, so the game must produce identical results given identical input on each run. The following patterns break determinism and should be avoided in replay-targeted code:
+
+| Avoid | Use Instead | Why |
+|-------|-------------|-----|
+| `Time.deltaTime` for movement | Fixed per-frame constant (e.g. `MOVE_SPEED = 0.1f`) | Delta time varies between runs even at the same target frame rate |
+| `Random.Range()` / `UnityEngine.Random` | Seeded random (`new System.Random(fixedSeed)`) or remove randomness | Random sequences differ between runs |
+| `Rigidbody` / Physics simulation | Kinematic movement via `Transform.Translate` | Physics is non-deterministic across runs |
+| `WaitForSeconds(n)` in coroutines | `WaitForEndOfFrame` or frame counting | Real-time waits depend on frame timing |
+| `Time.time` / `Time.realtimeSinceStartup` | Frame counter (`Time.frameCount - startFrame`) | Time values drift between runs |
+| `FindObjectsOfType` without sort | `FindObjectsByType(FindObjectsSortMode.InstanceID)` | Iteration order is non-deterministic |
+| `async/await` with `Task.Delay` | Frame-based waiting | Real-time delays are non-deterministic |
+
+Set `Application.targetFrameRate = 60` or another fixed target to reduce frame timing variance. See `InputReplayVerificationController` for a complete example of deterministic game logic.
diff --git a/.agents/skills/uloop-run-tests/SKILL.md b/.agents/skills/uloop-run-tests/SKILL.md
@@ -1,12 +1,14 @@
 ---
 name: uloop-run-tests
-description: "Execute Unity Test Runner and get detailed results. Use when you need to: (1) Run EditMode or PlayMode unit tests, (2) Verify code changes pass all tests, (3) Diagnose test failures with error messages and stack traces. Auto-saves NUnit XML results on failure."
+description: "Execute Unity Test Runner and get detailed results. Use when you need to: (1) Run EditMode or PlayMode unit tests, (2) Verify code changes pass all tests, (3) Diagnose test failures with error messages and stack traces. Single-flight only — never run multiple `uloop run-tests` in parallel."
 ---
 
 # uloop run-tests
 
 Execute Unity Test Runner. When tests fail, NUnit XML results with error messages and stack traces are automatically saved. Read the XML file at `XmlPath` for detailed failure diagnosis.
 
+Before executing tests, `uloop run-tests` checks for unsaved loaded Scene changes and unsaved current Prefab Stage changes. If any are found, it returns `Success: false`, keeps `TestCount` at `0`, lists the unsaved items in `Message`, and does not start the Unity Test Runner. Save or discard those editor changes, then rerun the command. Use `--save-before-run true` only when the user explicitly asks to save editor changes before continuing.
+
 ## Usage
 
 ```bash
@@ -20,6 +22,7 @@ uloop run-tests [options]
 | `--test-mode` | string | `EditMode` | Test mode: `EditMode`, `PlayMode` |
 | `--filter-type` | string | `all` | Filter type: `all`, `exact`, `regex`, `assembly` |
 | `--filter-value` | string | - | Filter value (test name, pattern, or assembly) |
+| `--save-before-run` | boolean | `false` | Save unsaved loaded Scene changes and current Prefab Stage changes before running tests |
 
 ## Global Options
 
@@ -36,6 +39,9 @@ uloop run-tests
 # Run PlayMode tests
 uloop run-tests --test-mode PlayMode
 
+# Save explicitly approved editor changes before running tests
+uloop run-tests --save-before-run true
+
 # Run specific test
 uloop run-tests --filter-type exact --filter-value "MyTest.TestMethod"
 
@@ -48,11 +54,12 @@ uloop run-tests --filter-type regex --filter-value ".*Integration.*"
 Returns JSON with:
 - `Success` (boolean): Whether all tests passed
 - `Message` (string): Summary message
+- `CompletedAt` (string): ISO timestamp when the run finished
 - `TestCount` (number): Total tests executed
 - `PassedCount` (number): Passed tests
 - `FailedCount` (number): Failed tests
 - `SkippedCount` (number): Skipped tests
-- `XmlPath` (string): Path to NUnit XML result file (auto-saved when tests fail)
+- `XmlPath` (string): Path to NUnit XML result file. Empty string when no XML was saved (typically on `Success: true`); populated only when tests failed and the XML file exists on disk.
 
 ### XML Result File
 
diff --git a/.agents/skills/uloop-screenshot/SKILL.md b/.agents/skills/uloop-screenshot/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: uloop-screenshot
-description: "Capture screenshots of Unity Editor windows as PNG files. Use when you need to: (1) Screenshot Game View, Scene View, Console, Inspector, or other windows, (2) Capture current visual state for debugging or documentation, (3) Save editor window appearance as image files."
+description: "Capture screenshots of Unity Editor windows as PNG files. Use when you need to: (1) Screenshot Game View, Scene View, Console, Inspector, or other windows, (2) Capture current visual state for debugging or documentation, (3) Save editor window appearance as PNG files with optional UI element annotations. Writes PNG files via uloop CLI."
 ---
 
 # uloop screenshot
@@ -22,7 +22,7 @@ uloop screenshot [--window-name <name>] [--resolution-scale <scale>] [--match-mo
 | `--match-mode` | enum | `exact` | Window name matching mode: `exact`, `prefix`, or `contains`. Ignored when `--capture-mode rendering`. |
 | `--capture-mode` | enum | `window` | `window`=capture EditorWindow including toolbar, `rendering`=capture game rendering only (PlayMode required, coordinates match simulate-mouse) |
 | `--output-directory` | string | `""` | Output directory path for saving screenshots. When empty, uses default path (.uloop/outputs/Screenshots/). Accepts absolute paths. |
-| `--annotate-elements` | boolean | `false` | Annotate interactive UI elements with index labels (A, B, C...) on the screenshot. Only works with `--capture-mode rendering` in PlayMode. |
+| `--annotate-elements` | boolean | `false` | Annotate interactive UI elements with index labels and interaction hints (A / CLICK, B / DRAG, ...). Only works with `--capture-mode rendering` in PlayMode. |
 | `--elements-only` | boolean | `false` | Return only annotated element JSON without capturing a screenshot image. Requires `--annotate-elements` and `--capture-mode rendering` in PlayMode. |
 
 ## Match Modes
@@ -80,28 +80,12 @@ Returns JSON with:
   - `FileSizeBytes`: Size of the saved file in bytes
   - `Width`: Captured image width in pixels
   - `Height`: Captured image height in pixels
-  - `CoordinateSystem`: `"gameView"` (image pixel coords that must be converted with `ResolutionScale` and `YOffset` before using with `simulate-mouse`) or `"window"` (EditorWindow capture)
+  - `CoordinateSystem`: `"gameView"` or `"window"`
   - `ResolutionScale`: Resolution scale used for capture
-  - `YOffset`: Y offset used in `sim_y = image_y / ResolutionScale + YOffset` when `CoordinateSystem` is `"gameView"`
-  - `AnnotatedElements`: Array of annotated UI element metadata. Empty unless `--annotate-elements` is used. Sorted by z-order (frontmost first). Each item contains:
-    - `Label`: Index label shown on the screenshot (`A`=frontmost, `B`=next, ...)
-    - `Name`: Element name
-    - `Type`: Element type (`Button`, `Toggle`, `Slider`, `Dropdown`, `InputField`, `Scrollbar`, `Draggable`, `DropTarget`, `Selectable`)
-    - `SimX`, `SimY`: Center position in simulate-mouse coordinates (use directly with `--x` and `--y`)
-    - `BoundsMinX`, `BoundsMinY`, `BoundsMaxX`, `BoundsMaxY`: Bounding box in simulate-mouse coordinates
-    - `SortingOrder`: Canvas sorting order (higher = in front)
-    - `SiblingIndex`: Transform sibling index under the element's direct parent (not a reliable z-order signal across nested UI hierarchies)
-
-### Coordinate Conversion (gameView)
-
-When `CoordinateSystem` is `"gameView"`, convert image pixel coordinates to simulate-mouse coordinates:
-
-```text
-sim_x = image_x / ResolutionScale
-sim_y = image_y / ResolutionScale + YOffset
-```
+  - `YOffset`: Y offset used for gameView coordinate conversion
+  - `AnnotatedElements`: Array of annotated UI element metadata. Empty unless `--annotate-elements` is used.
 
-When `ResolutionScale` is 1.0, this simplifies to `sim_x = image_x`, `sim_y = image_y + YOffset`.
+For `AnnotatedElements` fields and gameView coordinate conversion, read [references/annotated-elements.md](references/annotated-elements.md) before using screenshot coordinates with mouse simulation tools.
 
 When multiple windows match (e.g., multiple Inspector windows or when using `contains` mode), all matching windows are captured with numbered filenames (e.g., `Inspector_1_*.png`, `Inspector_2_*.png`).
 
diff --git a/.agents/skills/uloop-screenshot/references/annotated-elements.md b/.agents/skills/uloop-screenshot/references/annotated-elements.md
@@ -0,0 +1,37 @@
+# Annotated Elements and Coordinates
+
+Read this when using `uloop screenshot --capture-mode rendering --annotate-elements` to find coordinates for `simulate-mouse-ui` or `simulate-mouse-input`.
+
+## AnnotatedElements Fields
+
+`AnnotatedElements` is empty unless `--annotate-elements` is used. Entries are sorted by z-order, frontmost first. Each item contains:
+
+- `Label`: Index label in JSON (`A` = frontmost, `B` = next, ...). Screenshot labels also include the interaction hint, such as `A / CLICK` or `B / DRAG`.
+- `Name`: Element name
+- `Path`: Hierarchy path from the scene root, for example `Canvas/Panel/Button`. Use this as `simulate-mouse-ui --target-path` when bypassing raycast blockers.
+- `Type`: Element type (`Button`, `Toggle`, `Slider`, `Dropdown`, `InputField`, `Scrollbar`, `Draggable`, `DropTarget`, `Selectable`)
+- `Interaction`: Derived interaction category (`Click`, `Drag`, `Drop`, `Text`). Use this to choose between `simulate-mouse-ui --action Click` and drag actions.
+- `SimX`, `SimY`: Center position in simulate-mouse coordinates. Use these directly with `--x` and `--y`.
+- `BoundsMinX`, `BoundsMinY`, `BoundsMaxX`, `BoundsMaxY`: Bounding box in simulate-mouse coordinates
+- `SortingOrder`: Canvas sorting order. Higher values are in front.
+- `SiblingIndex`: Transform sibling index under the element's direct parent. Do not use it as a reliable z-order signal across nested UI hierarchies.
+
+## Coordinate Conversion
+
+When `CoordinateSystem` is `"gameView"`, convert image pixel coordinates to simulate-mouse coordinates:
+
+```text
+sim_x = image_x / ResolutionScale
+sim_y = image_y / ResolutionScale + YOffset
+```
+
+When `ResolutionScale` is `1.0`, this simplifies to:
+
+```text
+sim_x = image_x
+sim_y = image_y + YOffset
+```
+
+## Annotation Readability
+
+Annotated screenshots compensate border thickness for `ResolutionScale`, so the saved PNG keeps the intended outline width after downscaling. The neutral contrast borders are 2 output pixels each, and the colored middle border is 4 output pixels. Label outlines are also compensated and are separated from element borders by a 4 output pixel gap.
diff --git a/.agents/skills/uloop-simulate-keyboard/SKILL.md b/.agents/skills/uloop-simulate-keyboard/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: uloop-simulate-keyboard
-description: "Simulate keyboard key input in PlayMode via Input System. Use when you need to: (1) Press game control keys like WASD, Space, or Shift during PlayMode, (2) Hold keys down for continuous movement or actions, (3) Combine multiple held keys for complex input like Shift+W for sprint."
+description: "Simulate keyboard key input in PlayMode via Input System. Use when you need to: (1) Press game control keys like WASD, Space, or Shift during PlayMode, (2) Hold keys down for continuous movement or actions, (3) Combine multiple held keys for complex input like Shift+W for sprint. Injects into Unity Input System (`Keyboard.current`); requires PlayMode and the New Input System."
 context: fork
 ---
 
@@ -43,6 +43,7 @@ uloop simulate-keyboard --action <action> --key <key> [options]
 - `KeyUp` fails if the key is not currently held
 - Multiple keys can be held simultaneously (e.g. W + LeftShift for sprint)
 - All held keys are automatically released when PlayMode exits
+- To hold a key for a fixed duration, prefer `--action Press --duration <seconds>` (one-shot, blocks until release). For multi-key holds (e.g. Shift+W), issue separate `KeyDown` calls, then `sleep <seconds>` between them and the `KeyUp` calls.
 
 ### Global Options
 
@@ -70,6 +71,14 @@ uloop simulate-keyboard --action KeyUp --key W
 uloop simulate-keyboard --action KeyUp --key LeftShift
 ```
 
+## Output
+
+Returns JSON with:
+- `Success` (boolean): Whether the action succeeded (e.g. `KeyDown` on a not-yet-held key, `KeyUp` on a currently-held key, or `Press` round-trip)
+- `Message` (string): Description of what happened or why it failed
+- `Action` (string): The `--action` value that was applied (`Press`, `KeyDown`, or `KeyUp`)
+- `KeyName` (string, nullable): The key that was acted on; may be `null` when the action could not resolve a key
+
 ## Prerequisites
 
 - Unity must be in **PlayMode**
diff --git a/.agents/skills/uloop-simulate-mouse-input/SKILL.md b/.agents/skills/uloop-simulate-mouse-input/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: uloop-simulate-mouse-input
-description: "Simulate mouse input in PlayMode via Input System. Injects button clicks, mouse delta, and scroll wheel directly into Mouse.current. Use when you need to: (1) Click in games that read Mouse.current.leftButton.wasPressedThisFrame, (2) Right-click for actions like block placement, (3) Inject mouse delta for FPS camera control, (4) Inject scroll wheel for hotbar switching or zoom. Assumes the project uses the New Input System. If the project cannot use it, prefer execute-dynamic-code for a project-specific workaround. For UI elements with IPointerClickHandler, use simulate-mouse-ui instead."
+description: "Simulate mouse input in PlayMode for gameplay code that reads Unity Input System Mouse.current. Use when you need to: (1) Click or right-click in games that read Mouse.current button state, (2) Inject mouse delta for FPS camera control, (3) Inject scroll wheel for hotbar switching or zoom. Requires PlayMode and the New Input System; for EventSystem UI elements, use simulate-mouse-ui instead."
 context: fork
 ---
 
@@ -95,3 +95,15 @@ uloop simulate-mouse-input --action SmoothDelta --delta-x 300 --delta-y 0 --dura
 - **Input System package** must be installed (`com.unity.inputsystem`)
 - Game code must read input via Input System API (e.g. `Mouse.current.leftButton.wasPressedThisFrame`)
 - If the target project cannot use the New Input System, prefer `execute-dynamic-code` for a project-specific workaround instead of changing project settings just to use this tool
+
+## Output
+
+Returns JSON with:
+- `Success`: Whether the operation succeeded
+- `Message`: Status message
+- `Action`: Echoes which action was executed (`Click`, `LongPress`, `MoveDelta`, `SmoothDelta`, or `Scroll`)
+- `Button`: Which button was used (nullable string; populated for `Click` / `LongPress`, null otherwise)
+- `PositionX`: Target X coordinate (nullable float; populated for `Click` / `LongPress`)
+- `PositionY`: Target Y coordinate (nullable float; populated for `Click` / `LongPress`)
+
+These are the only six fields. There is no `DeltaX`, `DeltaY`, `ScrollX`, `ScrollY`, `Duration`, or hit-element field in the response — only the issued action, button, and target position are echoed back. Verify visual outcome with a follow-up screenshot.
diff --git a/.agents/skills/uloop-simulate-mouse-ui/SKILL.md b/.agents/skills/uloop-simulate-mouse-ui/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: uloop-simulate-mouse-ui
-description: "Simulate mouse click, long-press, and drag on PlayMode UI elements via EventSystem screen coordinates. Use when you need to: (1) Click buttons or interactive UI elements during PlayMode testing, (2) Drag UI elements from one position to another, (3) Hold a drag at a position for inspection before releasing, (4) Long-press UI elements that respond to sustained pointer-down. For game logic that reads Input System (e.g. WasPressedThisFrame), use simulate-mouse-input when the project uses the New Input System; otherwise prefer execute-dynamic-code."
+description: "Simulate mouse click, long-press, and drag on PlayMode UI elements via EventSystem screen coordinates from annotated screenshots. Use when you need to: (1) Click buttons or interactive UI elements during PlayMode testing, (2) Drag UI elements between annotated screen positions, (3) Long-press or hold a drag for sustained pointer interactions. First get target coordinates with `uloop screenshot --capture-mode rendering --annotate-elements --elements-only` and use `AnnotatedElements[].SimX` / `SimY`; for gameplay code that reads Mouse.current, use simulate-mouse-input instead."
 context: fork
 ---
 
@@ -12,7 +12,7 @@ Simulate mouse interaction on Unity PlayMode UI: $ARGUMENTS
 
 1. Ensure Unity is in PlayMode (use `uloop control-play-mode --action Play` if not)
 2. Get UI element info: `uloop screenshot --capture-mode rendering --annotate-elements --elements-only`
-3. Use the `AnnotatedElements` array to find the target element by `Name` or `Label` (A=frontmost, B=next, ...). Use `SimX`/`SimY` directly as `--x`/`--y` coordinates.
+3. Use the `AnnotatedElements` array to find the target element by `Label`, `Name`, or `Path` (A=frontmost, B=next, ...). Use `Interaction` to distinguish click targets from drag/drop/text targets, then use `SimX`/`SimY` directly as `--x`/`--y` coordinates.
 4. Execute the appropriate `uloop simulate-mouse-ui` command
 5. Take a screenshot to verify the result: `uloop screenshot --capture-mode rendering --annotate-elements`
 6. Report what happened
@@ -35,6 +35,9 @@ uloop simulate-mouse-ui --action <action> --x <x> --y <y> [options]
 | `--drag-speed` | number | `2000` | Drag speed in pixels per second (0 for instant). 2000 is fast (default), 200 is slow enough to watch. Applies to Drag, DragMove, and DragEnd actions. |
 | `--duration` | number | `0.5` | Hold duration in seconds for LongPress action. |
 | `--button` | enum | `Left` | Mouse button. `Click` and `LongPress` support `Left`, `Right`, and `Middle`. Drag actions support `Left` only; other buttons return an error. |
+| `--bypass-raycast` | boolean | `false` | For `Click`, `LongPress`, `Drag`, and `DragStart`, bypass EventSystem raycast and dispatch pointer events directly to `--target-path`. Use when a raycast-blocking overlay visually covers the intended target. |
+| `--target-path` | string | `""` | Hierarchy path of the target GameObject, for example `Canvas/Panel/Button`. Required when `--bypass-raycast true` is used with `Click`, `LongPress`, `Drag`, or `DragStart`; prefer `AnnotatedElements[].Path` from screenshot JSON. |
+| `--drop-target-path` | string | `""` | Optional hierarchy path of a drop target for `Drag` or `DragEnd`, for example `Canvas/DropZone`. Use this when the drop zone is also behind a raycast blocker. |
 
 ### Actions
 
@@ -68,13 +71,27 @@ uloop simulate-mouse-ui --action <action> --x <x> --y <y> [options]
 - Get coordinates from `AnnotatedElements` JSON (`SimX`/`SimY`) — do NOT look up GameObject positions
 - Clicking or long-pressing on empty space (no UI element) still succeeds with a message indicating no element was hit
 - Dragging on empty space (no draggable UI element) returns `Success = false`
+- `--bypass-raycast true` still uses coordinates for pointer event positions, but chooses the clicked, long-pressed, or dragged GameObject by `--target-path`
+- If `--target-path` or `--drop-target-path` matches multiple active GameObjects, the command fails instead of choosing an arbitrary duplicate
 
 ## Examples
 
 ```bash
 # Click a button at screen position
 uloop simulate-mouse-ui --action Click --x 400 --y 300
 
+# Force-click a button behind a raycast blocker by path
+uloop simulate-mouse-ui --action Click --x 400 --y 300 --bypass-raycast true --target-path "Canvas/Panel/Button"
+
+# Force-long-press a button behind a raycast blocker by path
+uloop simulate-mouse-ui --action LongPress --x 400 --y 300 --duration 3.0 --bypass-raycast true --target-path "Canvas/Panel/Button"
+
+# Force-drag an item behind a raycast blocker by path
+uloop simulate-mouse-ui --action Drag --from-x 400 --from-y 300 --x 600 --y 300 --bypass-raycast true --target-path "Canvas/Item"
+
+# Force-drag and dispatch Drop to a blocked drop zone
+uloop simulate-mouse-ui --action Drag --from-x 400 --from-y 300 --x 600 --y 300 --bypass-raycast true --target-path "Canvas/Item" --drop-target-path "Canvas/DropZone"
+
 # Long-press a button for 3 seconds
 uloop simulate-mouse-ui --action LongPress --x 400 --y 300 --duration 3.0
 
@@ -97,3 +114,19 @@ uloop simulate-mouse-ui --action DragEnd --x 600 --y 300
 - Target scene must have an **EventSystem** GameObject
 - UI elements must have a **GraphicRaycaster** on their Canvas
 - If you need gameplay mouse input rather than UI pointer events, `simulate-mouse-input` assumes the project uses the New Input System; otherwise prefer `execute-dynamic-code`
+
+## Output
+
+Returns JSON with:
+- `Success`: Whether the operation succeeded
+- `Message`: Status message (e.g. "Hit element: ButtonStart" or "No UI element under (x, y)")
+- `Action`: Echoes which action was executed (`Click`, `Drag`, `DragStart`, `DragMove`, `DragEnd`, or `LongPress`)
+- `HitGameObjectName`: Name of the topmost UI element under the pointer (nullable string; null if nothing was hit)
+- `PositionX`: Target X coordinate that was used
+- `PositionY`: Target Y coordinate that was used
+- `EndPositionX`: Drag end X coordinate (nullable float; populated for drag actions only)
+- `EndPositionY`: Drag end Y coordinate (nullable float; populated for drag actions only)
+
+These are the only eight fields. There is no `Button`, `Duration`, `DragSpeed`, raycast list, or pointer-event log in the response — verify the visual outcome with a follow-up `uloop screenshot --capture-mode rendering --annotate-elements`.
+
+Note: Click and LongPress on empty space (no UI element) still return `Success = true` with `HitGameObjectName = null`. Drag actions on empty space return `Success = false`.
diff --git a/.claude/skills/uloop-clear-console/SKILL.md b/.claude/skills/uloop-clear-console/SKILL.md
@@ -37,4 +37,12 @@ uloop clear-console --add-confirmation-message
 
 ## Output
 
-Returns JSON confirming the console was cleared.
+Returns JSON with:
+- `Success` (boolean): Whether the clear operation succeeded
+- `ClearedLogCount` (number): Total number of log entries that were cleared
+- `ClearedCounts` (object): Breakdown by log type
+  - `ErrorCount` (number): Errors cleared
+  - `WarningCount` (number): Warnings cleared
+  - `LogCount` (number): Info logs cleared
+- `Message` (string): Description of the result; carries the failure summary when the operation fails (e.g. `"Failed to clear console: ..."`)
+- `ErrorMessage` (string): Currently always empty for this tool — read `Message` for failure details
diff --git a/.claude/skills/uloop-compile/SKILL.md b/.claude/skills/uloop-compile/SKILL.md
@@ -51,10 +51,20 @@ Returns JSON:
 
 ## Troubleshooting
 
-If CLI hangs or shows "Unity is busy" errors after compilation, stale lock files may be preventing connection. Run the following to clean them up:
+Diagnose the failure mode before retrying.
+
+**Stale lock files** (CLI hangs or shows "Unity is busy" while Unity Editor *is* running):
 
 ```bash
 uloop fix
 ```
 
-This removes any leftover lock files (`compiling.lock`, `domainreload.lock`, `serverstarting.lock`) from the Unity project's Temp directory.
+This removes any leftover lock files (`compiling.lock`, `domainreload.lock`, `serverstarting.lock`) from the Unity project's Temp directory. Then retry `uloop compile`.
+
+**Unity Editor not running** (CLI returns a connection failure and no Unity process is alive):
+
+```bash
+uloop launch
+```
+
+`uloop launch` auto-detects the project at the current working directory and opens it in the matching Unity Editor version. After Unity finishes launching, retry `uloop compile`.
diff --git a/.claude/skills/uloop-control-play-mode/SKILL.md b/.claude/skills/uloop-control-play-mode/SKILL.md
@@ -51,3 +51,5 @@ Returns JSON with the current play mode state:
 - Stop action exits play mode and returns to edit mode
 - Pause action pauses the game while remaining in play mode
 - Useful for automated testing workflows
+
+- PlayMode entry may complete on the next editor frame. If a PlayMode-dependent command reports "PlayMode is not active" immediately after `--action Play`, wait briefly and retry.
diff --git a/.claude/skills/uloop-execute-dynamic-code/SKILL.md b/.claude/skills/uloop-execute-dynamic-code/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: uloop-execute-dynamic-code
-description: "Execute C# code dynamically in Unity Editor. Use when you need to: (1) Wire prefab/material references and AddComponent operations, (2) Edit SerializedObject properties and reference wiring, (3) Perform scene/hierarchy edits and batch operations, (4) PlayMode automation (click buttons, invoke methods, tweak runtime state), (5) PlayMode UI controls (InputField, Slider, Toggle, Dropdown), (6) PlayMode inspection (scene info, reflection, physics state, raycast checks). NOT for file I/O or script authoring."
+description: "Execute C# code dynamically in Unity Editor. Use when you need to: (1) Wire prefab/material references and AddComponent operations, (2) Edit SerializedObject properties and reference wiring, (3) Perform scene/hierarchy edits and batch operations, (4) Execute Unity Editor menu commands through EditorApplication.ExecuteMenuItem, (5) PlayMode automation (click buttons, invoke methods, tweak runtime state), (6) PlayMode UI controls (InputField, Slider, Toggle, Dropdown), (7) PlayMode inspection (scene info, reflection, physics state, raycast checks). NOT for file I/O or script authoring."
 context: fork
 ---
 
@@ -35,6 +35,22 @@ return x;
 
 **Forbidden** — these will be rejected at compile time: `System.IO.*`, `AssetDatabase.CreateFolder`, creating/editing `.cs`/`.asmdef` files. Use terminal commands for file operations instead.
 
+## Output
+
+Returns JSON:
+- `Success`: boolean — overall execution success
+- `Result`: string — value of the snippet's `return` statement (empty when omitted)
+- `Logs`: string[] — `Debug.Log` / `Debug.LogWarning` / `Debug.LogError` messages emitted during the run
+- `CompilationErrors`: object[] — Roslyn diagnostics with `Message`, `Line`, `Column`, `ErrorCode`, optional `Hint` and `Suggestions`
+- `ErrorMessage`: string — top-level failure summary (empty on success)
+- `Error`: string — alias of `ErrorMessage`
+- `SecurityLevel`: string — dynamic-code security level active for the request
+- `UpdatedCode`: string|null — the wrapped form actually compiled (handy when debugging using-statement reordering)
+- `DiagnosticsSummary`: string|null — compact summary when diagnostics are available
+- `Diagnostics`: object[] — structured diagnostics; same shape as `CompilationErrors`, usually populated together with it
+
+On `Success: false`, inspect `CompilationErrors` first. If empty, read `ErrorMessage` (and `Logs` for extra context) — the failure may be a runtime exception, security violation, cancellation, or an "execution in progress" rejection, all of which return empty `CompilationErrors`. Both EditMode and PlayMode are supported targets — the snippet runs in whichever mode the Editor is currently in.
+
 ## Code Examples by Category
 
 For detailed code examples, refer to these files:
diff --git a/.claude/skills/uloop-execute-menu-item/SKILL.md b/.claude/skills/uloop-execute-menu-item/SKILL.md
@@ -1,49 +0,0 @@
----
-name: uloop-execute-menu-item
-description: "Execute Unity Editor menu commands programmatically. Use when you need to: (1) Trigger menu commands like save, build, or refresh, (2) Automate editor actions via menu paths, (3) Run custom menu items defined in project scripts."
----
-
-# uloop execute-menu-item
-
-Execute Unity MenuItem.
-
-## Usage
-
-```bash
-uloop execute-menu-item --menu-item-path "<path>"
-```
-
-## Parameters
-
-| Parameter | Type | Default | Description |
-|-----------|------|---------|-------------|
-| `--menu-item-path` | string | - | Menu item path (e.g., "GameObject/Create Empty") |
-| `--use-reflection-fallback` | boolean | `true` | Use reflection fallback |
-
-## Global Options
-
-| Option | Description |
-|--------|-------------|
-| `--project-path <path>` | Optional. Use only when the target Unity project is not the current directory. |
-
-## Examples
-
-```bash
-# Create empty GameObject
-uloop execute-menu-item --menu-item-path "GameObject/Create Empty"
-
-# Save scene
-uloop execute-menu-item --menu-item-path "File/Save"
-
-# Open project settings
-uloop execute-menu-item --menu-item-path "Edit/Project Settings..."
-```
-
-## Output
-
-Returns JSON with execution result.
-
-## Notes
-
-- Use `uloop execute-dynamic-code` to discover available menu paths if needed
-- Some menu items may require specific context or selection
diff --git a/.claude/skills/uloop-find-game-objects/SKILL.md b/.claude/skills/uloop-find-game-objects/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: uloop-find-game-objects
-description: "Find GameObjects in the active scene by various criteria. Use when you need to: (1) Search for objects by name, regex, or path, (2) Find objects with specific components, tags, or layers, (3) Get currently selected GameObjects in Unity Editor. Returns matching GameObjects with hierarchy paths and components."
+description: "Find GameObjects in the active scene by various criteria. Use when you need to: (1) Search for objects by name, regex, or path, (2) Find objects with specific components, tags, or layers, (3) Get currently selected GameObjects in Unity Editor. Returns matching GameObjects with hierarchy paths and components (or writes to a file when multiple GameObjects are selected)."
 ---
 
 # uloop find-game-objects
@@ -66,9 +66,22 @@ uloop find-game-objects --search-mode Selected --include-inactive
 
 ## Output
 
-Returns JSON with matching GameObjects.
-
-For `Selected` mode with multiple objects, results are exported to file:
-- Single selection: JSON response directly
-- Multiple selection: File at `.uloop/outputs/FindGameObjectsResults/`
-- No selection: Empty results with message
+Returns JSON with:
+- `results` (array): Matching GameObjects, each containing:
+  - `name` (string): GameObject name
+  - `path` (string): Hierarchy path (e.g., `Canvas/Panel/Button`)
+  - `isActive` (boolean): Active state in hierarchy
+  - `tag` (string): GameObject tag
+  - `layer` (number): Layer index
+  - `components` (array): Each entry has `type` (short name, e.g., `Rigidbody`), `fullTypeName` (e.g., `UnityEngine.Rigidbody`), and `properties` (array of Inspector-visible `{name, type, value}` pairs)
+- `totalFound` (number): Number of results returned inline, or number exported for multi-selection file output. For search modes, this is after `--max-results` clipping and serialization.
+- `errorMessage` (string): Top-level failure summary (empty on success)
+- `processingErrors` (array): Selected-mode per-GameObject serialization failures, each `{gameObjectName, gameObjectPath, error}`. Omitted/null or empty on clean runs.
+
+### Multi-selection file export
+
+For `Selected` mode with **multiple** successfully serialized GameObjects, inline `results` is not populated and the data is written to a file instead. Two extra fields appear:
+- `resultsFilePath` (string): Relative path under `.uloop/outputs/FindGameObjectsResults/`
+- `message` (string): Human-readable summary (e.g., "5 GameObjects exported")
+
+Single-selection and search-mode calls (`Exact`, `Path`, `Regex`, `Contains`) always return inline. No selection (`Selected` mode with empty selection) returns empty `results` plus a `message`.
diff --git a/.claude/skills/uloop-focus-window/SKILL.md b/.claude/skills/uloop-focus-window/SKILL.md
@@ -32,7 +32,11 @@ uloop focus-window
 
 ## Output
 
-Returns JSON confirming the window was focused.
+Returns JSON with:
+- `Success`: Whether the focus operation succeeded
+- `Message`: Status message (e.g. `Unity Editor window focused (PID: 12345)`, or the failure reason such as `Unity project not found` / `No running Unity process found for this project` / `Failed to focus Unity window: <reason>`)
+
+These are the only two fields. There is no PID, window-handle, or platform field returned to the caller.
 
 ## Notes
 
diff --git a/.claude/skills/uloop-get-hierarchy/SKILL.md b/.claude/skills/uloop-get-hierarchy/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: uloop-get-hierarchy
-description: "Get Unity scene hierarchy as a structured tree. Use when you need to: (1) Inspect scene structure and parent-child relationships, (2) Explore GameObjects and their components, (3) Get hierarchy from a specific root path or selected objects. Returns the scene's GameObject tree."
+description: "Get Unity scene hierarchy as a structured tree. Use when you need to: (1) Inspect scene structure and parent-child relationships, (2) Explore GameObjects and their components, (3) Get hierarchy from a specific root path or selected objects. Hierarchy data is written to a JSON file on disk and the response returns the file path (not the tree inline) — open the file to read the structure."
 ---
 
 # uloop get-hierarchy
@@ -52,4 +52,8 @@ uloop get-hierarchy --use-selection
 
 ## Output
 
-Returns JSON with hierarchical structure of GameObjects and their components.
+Returns JSON with:
+- `message` (string): Human-readable guidance pointing at the saved file
+- `hierarchyFilePath` (string): Filesystem path to the JSON file that contains the actual hierarchy data
+
+The hierarchy itself is **not** in the response — it is written to the file at `hierarchyFilePath`. Open that file to read the `Context` and `Hierarchy` payload (GameObject tree, components, etc.).
diff --git a/.claude/skills/uloop-get-logs/SKILL.md b/.claude/skills/uloop-get-logs/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: uloop-get-logs
-description: "Retrieve logs from Unity Console with filtering and search. Use when you need to: (1) Check for errors or warnings after compilation or play mode, (2) Debug issues by searching log messages, (3) Investigate failures with stack traces. Supports filtering by log type, text search, and regex."
+description: "Retrieve current Unity Console entries via uloop CLI. Use when you need to: (1) inspect errors, warnings, or logs after compile, tests, PlayMode, or dynamic code execution, (2) search current Console messages or stack traces, (3) confirm whether a recent Unity operation emitted logs. Prefer this over reading Editor.log or Unity log files for normal Console contents; use log files only for startup, crash, freeze, or uloop connection failures."
 ---
 
 # uloop get-logs
@@ -48,4 +48,14 @@ uloop get-logs --search-text "Missing.*Component" --use-regex
 
 ## Output
 
-Returns JSON array of log entries with message, type, and optional stack trace.
+Returns JSON with:
+- `TotalCount` (number): Total logs available before max-count clipping
+- `DisplayedCount` (number): Logs returned in this response (≤ `--max-count`)
+- `LogType` (string): The `--log-type` filter that was applied
+- `MaxCount` (number): The `--max-count` cap that was applied
+- `SearchText` (string): The `--search-text` filter that was applied (empty when omitted)
+- `IncludeStackTrace` (boolean): Whether stack traces are included in `Logs[]`
+- `Logs` (array): Each entry has:
+  - `Type` (string): `"Error"`, `"Warning"`, or `"Log"`
+  - `Message` (string): Log message body
+  - `StackTrace` (string): Stack trace text. Empty when `--include-stack-trace` is `false`.
diff --git a/.claude/skills/uloop-launch/SKILL.md b/.claude/skills/uloop-launch/SKILL.md
@@ -7,6 +7,9 @@ description: "Launch Unity project with matching Editor version via uloop CLI. U
 
 Launch Unity Editor with the correct version for a project.
 
+`uloop launch` is not fire-and-forget. When Unity needs to start or restart, the command waits
+until Unity is actually ready for CLI operations before it exits.
+
 ## Usage
 
 ```bash
@@ -48,4 +51,4 @@ uloop launch -a
 - Prints detected Unity version
 - Prints project path
 - If Unity is already running, focuses the existing window
-- If launching, opens Unity in background
+- If launching, waits until Unity finishes startup and the CLI can connect to the project
diff --git a/.claude/skills/uloop-record-input/SKILL.md b/.claude/skills/uloop-record-input/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: uloop-record-input
-description: "Record keyboard and mouse input during PlayMode into a JSON file. Use when you need to: (1) Capture human gameplay input for later replay, (2) Record input sequences for E2E testing, (3) Save input for bug reproduction."
+description: "Record keyboard and mouse input during PlayMode into a JSON file. Use when you need to: (1) Capture human gameplay input for later replay, (2) Record input sequences for E2E testing, (3) Save input for bug reproduction. Captures Input System device-state diffs frame-by-frame in PlayMode and serializes them to JSON when stopped. Requires PlayMode and the New Input System."
 ---
 
 # uloop record-input
@@ -31,21 +31,9 @@ uloop record-input --action Stop --output-path scripts/my-play.json
 | `--output-path` | string | auto | Save path. Auto-generates under `.uloop/outputs/InputRecordings/` |
 | `--keys` | string | `""` | Comma-separated key filter. Empty = all common game keys |
 
-## Design Guidelines for Deterministic Replay
+## Deterministic Replay
 
-Replay injects input frame-by-frame, so the game must produce identical results given identical input on each run. The following patterns break determinism and must be avoided in replay-targeted code:
-
-| Avoid | Use Instead | Why |
-|-------|-------------|-----|
-| `Time.deltaTime` for movement | Fixed per-frame constant (e.g. `MOVE_SPEED = 0.1f`) | deltaTime varies between runs even at the same target frame rate |
-| `Random.Range()` / `UnityEngine.Random` | Seeded random (`new System.Random(fixedSeed)`) or remove randomness | Different random sequence each run |
-| `Rigidbody` / Physics simulation | Kinematic movement via `Transform.Translate` | Physics is non-deterministic across runs |
-| `WaitForSeconds(n)` in coroutines | `WaitForEndOfFrame` or frame counting | Real-time waits depend on frame timing |
-| `Time.time` / `Time.realtimeSinceStartup` | Frame counter (`Time.frameCount - startFrame`) | Time values drift between runs |
-| `FindObjectsOfType` without sort | `FindObjectsByType(FindObjectsSortMode.InstanceID)` | Iteration order is non-deterministic |
-| `async/await` with `Task.Delay` | Frame-based waiting | Real-time delays are non-deterministic |
-
-Set `Application.targetFrameRate = 60` (or your target) to reduce frame timing variance. See `InputReplayVerificationController` for a complete example of deterministic game logic.
+Replay injects input frame-by-frame, so the game must also be deterministic to produce identical results. If the recording will be used for E2E tests, bug reproduction, or replay verification, read [references/deterministic-replay.md](references/deterministic-replay.md) before designing assertions or game logic.
 
 ## Prerequisites
 
@@ -55,9 +43,12 @@ Set `Application.targetFrameRate = 60` (or your target) to reduce frame timing v
 
 ## Output
 
-Returns JSON with:
+The CLI prints JSON with:
 - `Success`: Whether the operation succeeded
 - `Message`: Status message
-- `OutputPath`: Path to saved recording (Stop only)
-- `TotalFrames`: Number of frames recorded (Stop only)
-- `DurationSeconds`: Recording duration in seconds (Stop only)
+- `Action`: Echoes which action was executed (`Start` or `Stop`)
+- `OutputPath`: Path to saved recording (nullable; populated on `Stop` only)
+- `TotalFrames`: Number of frames recorded (nullable int; populated on `Stop` only)
+- `DurationSeconds`: Recording duration in seconds (nullable float; populated on `Stop` only)
+
+The CLI output contains only these six payload fields. Internal metadata such as `Ver` is removed before printing. There is no `RecordingId`, `StartTimestamp`, `KeysCaptured`, or per-frame data in the response — frame data lives only in the JSON file at `OutputPath`.
diff --git a/.claude/skills/uloop-record-input/references/deterministic-replay.md b/.claude/skills/uloop-record-input/references/deterministic-replay.md
@@ -0,0 +1,15 @@
+# Deterministic Replay
+
+Replay injects input frame-by-frame, so the game must produce identical results given identical input on each run. The following patterns break determinism and should be avoided in replay-targeted code:
+
+| Avoid | Use Instead | Why |
+|-------|-------------|-----|
+| `Time.deltaTime` for movement | Fixed per-frame constant (e.g. `MOVE_SPEED = 0.1f`) | Delta time varies between runs even at the same target frame rate |
+| `Random.Range()` / `UnityEngine.Random` | Seeded random (`new System.Random(fixedSeed)`) or remove randomness | Random sequences differ between runs |
+| `Rigidbody` / Physics simulation | Kinematic movement via `Transform.Translate` | Physics is non-deterministic across runs |
+| `WaitForSeconds(n)` in coroutines | `WaitForEndOfFrame` or frame counting | Real-time waits depend on frame timing |
+| `Time.time` / `Time.realtimeSinceStartup` | Frame counter (`Time.frameCount - startFrame`) | Time values drift between runs |
+| `FindObjectsOfType` without sort | `FindObjectsByType(FindObjectsSortMode.InstanceID)` | Iteration order is non-deterministic |
+| `async/await` with `Task.Delay` | Frame-based waiting | Real-time delays are non-deterministic |
+
+Set `Application.targetFrameRate = 60` or another fixed target to reduce frame timing variance. See `InputReplayVerificationController` for a complete example of deterministic game logic.
diff --git a/.claude/skills/uloop-replay-input/SKILL.md b/.claude/skills/uloop-replay-input/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: uloop-replay-input
-description: "Replay recorded input during PlayMode with frame-precise injection. Use when you need to: (1) Reproduce recorded gameplay exactly, (2) Run E2E tests from recorded input, (3) Generate demo videos with consistent input."
+description: "Replay recorded input during PlayMode with frame-precise injection. Use when you need to: (1) Reproduce recorded gameplay exactly, (2) Run E2E tests from recorded input, (3) Generate demo videos with consistent input. Deserializes the JSON recording and pushes captured device states back into Mouse.current / Keyboard.current frame-by-frame in PlayMode. Requires PlayMode and the New Input System."
 ---
 
 # uloop replay-input
@@ -37,15 +37,18 @@ uloop replay-input --action Stop
 
 ## Deterministic Replay
 
-Replay injects the exact same input frame-by-frame, but the game must also be deterministic to produce identical results. See the **"Design Guidelines for Deterministic Replay"** section in the `record-input` skill for the full list of patterns to avoid (`Time.deltaTime`, `Random.Range`, physics, etc.) and their deterministic alternatives.
+Replay injects the exact same input frame-by-frame, but the game must also be deterministic to produce identical results. If replay output must be compared across runs, read [references/deterministic-replay.md](references/deterministic-replay.md) before interpreting failures.
 
 ## Output
 
 Returns JSON with:
 - `Success`: Whether the operation succeeded
 - `Message`: Status message
-- `InputPath`: Path to recording file (Start only)
-- `CurrentFrame`: Current replay frame
-- `TotalFrames`: Total frames in recording
-- `Progress`: Replay progress (0.0 - 1.0)
-- `IsReplaying`: Whether replay is active
+- `Action`: Echoes which action was executed (`Start`, `Stop`, or `Status`)
+- `InputPath`: Path to recording file (nullable string; populated on `Start` only)
+- `CurrentFrame`: Current replay frame index (nullable int)
+- `TotalFrames`: Total frames in the recording (nullable int)
+- `Progress`: Replay progress (nullable float in 0.0 – 1.0)
+- `IsReplaying`: Whether replay is currently active (nullable bool)
+
+These are the only eight fields. There is no `LoopCount`, `ElapsedSeconds`, `OverlayVisible`, or per-frame inspection data in the response.
diff --git a/.claude/skills/uloop-replay-input/references/deterministic-replay.md b/.claude/skills/uloop-replay-input/references/deterministic-replay.md
@@ -0,0 +1,15 @@
+# Deterministic Replay
+
+Replay injects input frame-by-frame, so the game must produce identical results given identical input on each run. The following patterns break determinism and should be avoided in replay-targeted code:
+
+| Avoid | Use Instead | Why |
+|-------|-------------|-----|
+| `Time.deltaTime` for movement | Fixed per-frame constant (e.g. `MOVE_SPEED = 0.1f`) | Delta time varies between runs even at the same target frame rate |
+| `Random.Range()` / `UnityEngine.Random` | Seeded random (`new System.Random(fixedSeed)`) or remove randomness | Random sequences differ between runs |
+| `Rigidbody` / Physics simulation | Kinematic movement via `Transform.Translate` | Physics is non-deterministic across runs |
+| `WaitForSeconds(n)` in coroutines | `WaitForEndOfFrame` or frame counting | Real-time waits depend on frame timing |
+| `Time.time` / `Time.realtimeSinceStartup` | Frame counter (`Time.frameCount - startFrame`) | Time values drift between runs |
+| `FindObjectsOfType` without sort | `FindObjectsByType(FindObjectsSortMode.InstanceID)` | Iteration order is non-deterministic |
+| `async/await` with `Task.Delay` | Frame-based waiting | Real-time delays are non-deterministic |
+
+Set `Application.targetFrameRate = 60` or another fixed target to reduce frame timing variance. See `InputReplayVerificationController` for a complete example of deterministic game logic.
diff --git a/.claude/skills/uloop-run-tests/SKILL.md b/.claude/skills/uloop-run-tests/SKILL.md
@@ -1,12 +1,14 @@
 ---
 name: uloop-run-tests
-description: "Execute Unity Test Runner and get detailed results. Use when you need to: (1) Run EditMode or PlayMode unit tests, (2) Verify code changes pass all tests, (3) Diagnose test failures with error messages and stack traces. Auto-saves NUnit XML results on failure."
+description: "Execute Unity Test Runner and get detailed results. Use when you need to: (1) Run EditMode or PlayMode unit tests, (2) Verify code changes pass all tests, (3) Diagnose test failures with error messages and stack traces. Single-flight only — never run multiple `uloop run-tests` in parallel."
 ---
 
 # uloop run-tests
 
 Execute Unity Test Runner. When tests fail, NUnit XML results with error messages and stack traces are automatically saved. Read the XML file at `XmlPath` for detailed failure diagnosis.
 
+Before executing tests, `uloop run-tests` checks for unsaved loaded Scene changes and unsaved current Prefab Stage changes. If any are found, it returns `Success: false`, keeps `TestCount` at `0`, lists the unsaved items in `Message`, and does not start the Unity Test Runner. Save or discard those editor changes, then rerun the command. Use `--save-before-run true` only when the user explicitly asks to save editor changes before continuing.
+
 ## Usage
 
 ```bash
@@ -20,6 +22,7 @@ uloop run-tests [options]
 | `--test-mode` | string | `EditMode` | Test mode: `EditMode`, `PlayMode` |
 | `--filter-type` | string | `all` | Filter type: `all`, `exact`, `regex`, `assembly` |
 | `--filter-value` | string | - | Filter value (test name, pattern, or assembly) |
+| `--save-before-run` | boolean | `false` | Save unsaved loaded Scene changes and current Prefab Stage changes before running tests |
 
 ## Global Options
 
@@ -36,6 +39,9 @@ uloop run-tests
 # Run PlayMode tests
 uloop run-tests --test-mode PlayMode
 
+# Save explicitly approved editor changes before running tests
+uloop run-tests --save-before-run true
+
 # Run specific test
 uloop run-tests --filter-type exact --filter-value "MyTest.TestMethod"
 
@@ -48,11 +54,12 @@ uloop run-tests --filter-type regex --filter-value ".*Integration.*"
 Returns JSON with:
 - `Success` (boolean): Whether all tests passed
 - `Message` (string): Summary message
+- `CompletedAt` (string): ISO timestamp when the run finished
 - `TestCount` (number): Total tests executed
 - `PassedCount` (number): Passed tests
 - `FailedCount` (number): Failed tests
 - `SkippedCount` (number): Skipped tests
-- `XmlPath` (string): Path to NUnit XML result file (auto-saved when tests fail)
+- `XmlPath` (string): Path to NUnit XML result file. Empty string when no XML was saved (typically on `Success: true`); populated only when tests failed and the XML file exists on disk.
 
 ### XML Result File
 
diff --git a/.claude/skills/uloop-screenshot/SKILL.md b/.claude/skills/uloop-screenshot/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: uloop-screenshot
-description: "Capture screenshots of Unity Editor windows as PNG files. Use when you need to: (1) Screenshot Game View, Scene View, Console, Inspector, or other windows, (2) Capture current visual state for debugging or documentation, (3) Save editor window appearance as image files."
+description: "Capture screenshots of Unity Editor windows as PNG files. Use when you need to: (1) Screenshot Game View, Scene View, Console, Inspector, or other windows, (2) Capture current visual state for debugging or documentation, (3) Save editor window appearance as PNG files with optional UI element annotations. Writes PNG files via uloop CLI."
 ---
 
 # uloop screenshot
@@ -22,7 +22,7 @@ uloop screenshot [--window-name <name>] [--resolution-scale <scale>] [--match-mo
 | `--match-mode` | enum | `exact` | Window name matching mode: `exact`, `prefix`, or `contains`. Ignored when `--capture-mode rendering`. |
 | `--capture-mode` | enum | `window` | `window`=capture EditorWindow including toolbar, `rendering`=capture game rendering only (PlayMode required, coordinates match simulate-mouse) |
 | `--output-directory` | string | `""` | Output directory path for saving screenshots. When empty, uses default path (.uloop/outputs/Screenshots/). Accepts absolute paths. |
-| `--annotate-elements` | boolean | `false` | Annotate interactive UI elements with index labels (A, B, C...) on the screenshot. Only works with `--capture-mode rendering` in PlayMode. |
+| `--annotate-elements` | boolean | `false` | Annotate interactive UI elements with index labels and interaction hints (A / CLICK, B / DRAG, ...). Only works with `--capture-mode rendering` in PlayMode. |
 | `--elements-only` | boolean | `false` | Return only annotated element JSON without capturing a screenshot image. Requires `--annotate-elements` and `--capture-mode rendering` in PlayMode. |
 
 ## Match Modes
@@ -80,28 +80,12 @@ Returns JSON with:
   - `FileSizeBytes`: Size of the saved file in bytes
   - `Width`: Captured image width in pixels
   - `Height`: Captured image height in pixels
-  - `CoordinateSystem`: `"gameView"` (image pixel coords that must be converted with `ResolutionScale` and `YOffset` before using with `simulate-mouse`) or `"window"` (EditorWindow capture)
+  - `CoordinateSystem`: `"gameView"` or `"window"`
   - `ResolutionScale`: Resolution scale used for capture
-  - `YOffset`: Y offset used in `sim_y = image_y / ResolutionScale + YOffset` when `CoordinateSystem` is `"gameView"`
-  - `AnnotatedElements`: Array of annotated UI element metadata. Empty unless `--annotate-elements` is used. Sorted by z-order (frontmost first). Each item contains:
-    - `Label`: Index label shown on the screenshot (`A`=frontmost, `B`=next, ...)
-    - `Name`: Element name
-    - `Type`: Element type (`Button`, `Toggle`, `Slider`, `Dropdown`, `InputField`, `Scrollbar`, `Draggable`, `DropTarget`, `Selectable`)
-    - `SimX`, `SimY`: Center position in simulate-mouse coordinates (use directly with `--x` and `--y`)
-    - `BoundsMinX`, `BoundsMinY`, `BoundsMaxX`, `BoundsMaxY`: Bounding box in simulate-mouse coordinates
-    - `SortingOrder`: Canvas sorting order (higher = in front)
-    - `SiblingIndex`: Transform sibling index under the element's direct parent (not a reliable z-order signal across nested UI hierarchies)
-
-### Coordinate Conversion (gameView)
-
-When `CoordinateSystem` is `"gameView"`, convert image pixel coordinates to simulate-mouse coordinates:
-
-```text
-sim_x = image_x / ResolutionScale
-sim_y = image_y / ResolutionScale + YOffset
-```
+  - `YOffset`: Y offset used for gameView coordinate conversion
+  - `AnnotatedElements`: Array of annotated UI element metadata. Empty unless `--annotate-elements` is used.
 
-When `ResolutionScale` is 1.0, this simplifies to `sim_x = image_x`, `sim_y = image_y + YOffset`.
+For `AnnotatedElements` fields and gameView coordinate conversion, read [references/annotated-elements.md](references/annotated-elements.md) before using screenshot coordinates with mouse simulation tools.
 
 When multiple windows match (e.g., multiple Inspector windows or when using `contains` mode), all matching windows are captured with numbered filenames (e.g., `Inspector_1_*.png`, `Inspector_2_*.png`).
 
diff --git a/.claude/skills/uloop-screenshot/references/annotated-elements.md b/.claude/skills/uloop-screenshot/references/annotated-elements.md
@@ -0,0 +1,37 @@
+# Annotated Elements and Coordinates
+
+Read this when using `uloop screenshot --capture-mode rendering --annotate-elements` to find coordinates for `simulate-mouse-ui` or `simulate-mouse-input`.
+
+## AnnotatedElements Fields
+
+`AnnotatedElements` is empty unless `--annotate-elements` is used. Entries are sorted by z-order, frontmost first. Each item contains:
+
+- `Label`: Index label in JSON (`A` = frontmost, `B` = next, ...). Screenshot labels also include the interaction hint, such as `A / CLICK` or `B / DRAG`.
+- `Name`: Element name
+- `Path`: Hierarchy path from the scene root, for example `Canvas/Panel/Button`. Use this as `simulate-mouse-ui --target-path` when bypassing raycast blockers.
+- `Type`: Element type (`Button`, `Toggle`, `Slider`, `Dropdown`, `InputField`, `Scrollbar`, `Draggable`, `DropTarget`, `Selectable`)
+- `Interaction`: Derived interaction category (`Click`, `Drag`, `Drop`, `Text`). Use this to choose between `simulate-mouse-ui --action Click` and drag actions.
+- `SimX`, `SimY`: Center position in simulate-mouse coordinates. Use these directly with `--x` and `--y`.
+- `BoundsMinX`, `BoundsMinY`, `BoundsMaxX`, `BoundsMaxY`: Bounding box in simulate-mouse coordinates
+- `SortingOrder`: Canvas sorting order. Higher values are in front.
+- `SiblingIndex`: Transform sibling index under the element's direct parent. Do not use it as a reliable z-order signal across nested UI hierarchies.
+
+## Coordinate Conversion
+
+When `CoordinateSystem` is `"gameView"`, convert image pixel coordinates to simulate-mouse coordinates:
+
+```text
+sim_x = image_x / ResolutionScale
+sim_y = image_y / ResolutionScale + YOffset
+```
+
+When `ResolutionScale` is `1.0`, this simplifies to:
+
+```text
+sim_x = image_x
+sim_y = image_y + YOffset
+```
+
+## Annotation Readability
+
+Annotated screenshots compensate border thickness for `ResolutionScale`, so the saved PNG keeps the intended outline width after downscaling. The neutral contrast borders are 2 output pixels each, and the colored middle border is 4 output pixels. Label outlines are also compensated and are separated from element borders by a 4 output pixel gap.
diff --git a/.claude/skills/uloop-simulate-keyboard/SKILL.md b/.claude/skills/uloop-simulate-keyboard/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: uloop-simulate-keyboard
-description: "Simulate keyboard key input in PlayMode via Input System. Use when you need to: (1) Press game control keys like WASD, Space, or Shift during PlayMode, (2) Hold keys down for continuous movement or actions, (3) Combine multiple held keys for complex input like Shift+W for sprint."
+description: "Simulate keyboard key input in PlayMode via Input System. Use when you need to: (1) Press game control keys like WASD, Space, or Shift during PlayMode, (2) Hold keys down for continuous movement or actions, (3) Combine multiple held keys for complex input like Shift+W for sprint. Injects into Unity Input System (`Keyboard.current`); requires PlayMode and the New Input System."
 context: fork
 ---
 
@@ -43,6 +43,7 @@ uloop simulate-keyboard --action <action> --key <key> [options]
 - `KeyUp` fails if the key is not currently held
 - Multiple keys can be held simultaneously (e.g. W + LeftShift for sprint)
 - All held keys are automatically released when PlayMode exits
+- To hold a key for a fixed duration, prefer `--action Press --duration <seconds>` (one-shot, blocks until release). For multi-key holds (e.g. Shift+W), issue separate `KeyDown` calls, then `sleep <seconds>` between them and the `KeyUp` calls.
 
 ### Global Options
 
@@ -70,6 +71,14 @@ uloop simulate-keyboard --action KeyUp --key W
 uloop simulate-keyboard --action KeyUp --key LeftShift
 ```
 
+## Output
+
+Returns JSON with:
+- `Success` (boolean): Whether the action succeeded (e.g. `KeyDown` on a not-yet-held key, `KeyUp` on a currently-held key, or `Press` round-trip)
+- `Message` (string): Description of what happened or why it failed
+- `Action` (string): The `--action` value that was applied (`Press`, `KeyDown`, or `KeyUp`)
+- `KeyName` (string, nullable): The key that was acted on; may be `null` when the action could not resolve a key
+
 ## Prerequisites
 
 - Unity must be in **PlayMode**
diff --git a/.claude/skills/uloop-simulate-mouse-input/SKILL.md b/.claude/skills/uloop-simulate-mouse-input/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: uloop-simulate-mouse-input
-description: "Simulate mouse input in PlayMode via Input System. Injects button clicks, mouse delta, and scroll wheel directly into Mouse.current. Use when you need to: (1) Click in games that read Mouse.current.leftButton.wasPressedThisFrame, (2) Right-click for actions like block placement, (3) Inject mouse delta for FPS camera control, (4) Inject scroll wheel for hotbar switching or zoom. Assumes the project uses the New Input System. If the project cannot use it, prefer execute-dynamic-code for a project-specific workaround. For UI elements with IPointerClickHandler, use simulate-mouse-ui instead."
+description: "Simulate mouse input in PlayMode for gameplay code that reads Unity Input System Mouse.current. Use when you need to: (1) Click or right-click in games that read Mouse.current button state, (2) Inject mouse delta for FPS camera control, (3) Inject scroll wheel for hotbar switching or zoom. Requires PlayMode and the New Input System; for EventSystem UI elements, use simulate-mouse-ui instead."
 context: fork
 ---
 
@@ -95,3 +95,15 @@ uloop simulate-mouse-input --action SmoothDelta --delta-x 300 --delta-y 0 --dura
 - **Input System package** must be installed (`com.unity.inputsystem`)
 - Game code must read input via Input System API (e.g. `Mouse.current.leftButton.wasPressedThisFrame`)
 - If the target project cannot use the New Input System, prefer `execute-dynamic-code` for a project-specific workaround instead of changing project settings just to use this tool
+
+## Output
+
+Returns JSON with:
+- `Success`: Whether the operation succeeded
+- `Message`: Status message
+- `Action`: Echoes which action was executed (`Click`, `LongPress`, `MoveDelta`, `SmoothDelta`, or `Scroll`)
+- `Button`: Which button was used (nullable string; populated for `Click` / `LongPress`, null otherwise)
+- `PositionX`: Target X coordinate (nullable float; populated for `Click` / `LongPress`)
+- `PositionY`: Target Y coordinate (nullable float; populated for `Click` / `LongPress`)
+
+These are the only six fields. There is no `DeltaX`, `DeltaY`, `ScrollX`, `ScrollY`, `Duration`, or hit-element field in the response — only the issued action, button, and target position are echoed back. Verify visual outcome with a follow-up screenshot.
diff --git a/.claude/skills/uloop-simulate-mouse-ui/SKILL.md b/.claude/skills/uloop-simulate-mouse-ui/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: uloop-simulate-mouse-ui
-description: "Simulate mouse click, long-press, and drag on PlayMode UI elements via EventSystem screen coordinates. Use when you need to: (1) Click buttons or interactive UI elements during PlayMode testing, (2) Drag UI elements from one position to another, (3) Hold a drag at a position for inspection before releasing, (4) Long-press UI elements that respond to sustained pointer-down. For game logic that reads Input System (e.g. WasPressedThisFrame), use simulate-mouse-input when the project uses the New Input System; otherwise prefer execute-dynamic-code."
+description: "Simulate mouse click, long-press, and drag on PlayMode UI elements via EventSystem screen coordinates from annotated screenshots. Use when you need to: (1) Click buttons or interactive UI elements during PlayMode testing, (2) Drag UI elements between annotated screen positions, (3) Long-press or hold a drag for sustained pointer interactions. First get target coordinates with `uloop screenshot --capture-mode rendering --annotate-elements --elements-only` and use `AnnotatedElements[].SimX` / `SimY`; for gameplay code that reads Mouse.current, use simulate-mouse-input instead."
 context: fork
 ---
 
@@ -12,7 +12,7 @@ Simulate mouse interaction on Unity PlayMode UI: $ARGUMENTS
 
 1. Ensure Unity is in PlayMode (use `uloop control-play-mode --action Play` if not)
 2. Get UI element info: `uloop screenshot --capture-mode rendering --annotate-elements --elements-only`
-3. Use the `AnnotatedElements` array to find the target element by `Name` or `Label` (A=frontmost, B=next, ...). Use `SimX`/`SimY` directly as `--x`/`--y` coordinates.
+3. Use the `AnnotatedElements` array to find the target element by `Label`, `Name`, or `Path` (A=frontmost, B=next, ...). Use `Interaction` to distinguish click targets from drag/drop/text targets, then use `SimX`/`SimY` directly as `--x`/`--y` coordinates.
 4. Execute the appropriate `uloop simulate-mouse-ui` command
 5. Take a screenshot to verify the result: `uloop screenshot --capture-mode rendering --annotate-elements`
 6. Report what happened
@@ -35,6 +35,9 @@ uloop simulate-mouse-ui --action <action> --x <x> --y <y> [options]
 | `--drag-speed` | number | `2000` | Drag speed in pixels per second (0 for instant). 2000 is fast (default), 200 is slow enough to watch. Applies to Drag, DragMove, and DragEnd actions. |
 | `--duration` | number | `0.5` | Hold duration in seconds for LongPress action. |
 | `--button` | enum | `Left` | Mouse button. `Click` and `LongPress` support `Left`, `Right`, and `Middle`. Drag actions support `Left` only; other buttons return an error. |
+| `--bypass-raycast` | boolean | `false` | For `Click`, `LongPress`, `Drag`, and `DragStart`, bypass EventSystem raycast and dispatch pointer events directly to `--target-path`. Use when a raycast-blocking overlay visually covers the intended target. |
+| `--target-path` | string | `""` | Hierarchy path of the target GameObject, for example `Canvas/Panel/Button`. Required when `--bypass-raycast true` is used with `Click`, `LongPress`, `Drag`, or `DragStart`; prefer `AnnotatedElements[].Path` from screenshot JSON. |
+| `--drop-target-path` | string | `""` | Optional hierarchy path of a drop target for `Drag` or `DragEnd`, for example `Canvas/DropZone`. Use this when the drop zone is also behind a raycast blocker. |
 
 ### Actions
 
@@ -68,13 +71,27 @@ uloop simulate-mouse-ui --action <action> --x <x> --y <y> [options]
 - Get coordinates from `AnnotatedElements` JSON (`SimX`/`SimY`) — do NOT look up GameObject positions
 - Clicking or long-pressing on empty space (no UI element) still succeeds with a message indicating no element was hit
 - Dragging on empty space (no draggable UI element) returns `Success = false`
+- `--bypass-raycast true` still uses coordinates for pointer event positions, but chooses the clicked, long-pressed, or dragged GameObject by `--target-path`
+- If `--target-path` or `--drop-target-path` matches multiple active GameObjects, the command fails instead of choosing an arbitrary duplicate
 
 ## Examples
 
 ```bash
 # Click a button at screen position
 uloop simulate-mouse-ui --action Click --x 400 --y 300
 
+# Force-click a button behind a raycast blocker by path
+uloop simulate-mouse-ui --action Click --x 400 --y 300 --bypass-raycast true --target-path "Canvas/Panel/Button"
+
+# Force-long-press a button behind a raycast blocker by path
+uloop simulate-mouse-ui --action LongPress --x 400 --y 300 --duration 3.0 --bypass-raycast true --target-path "Canvas/Panel/Button"
+
+# Force-drag an item behind a raycast blocker by path
+uloop simulate-mouse-ui --action Drag --from-x 400 --from-y 300 --x 600 --y 300 --bypass-raycast true --target-path "Canvas/Item"
+
+# Force-drag and dispatch Drop to a blocked drop zone
+uloop simulate-mouse-ui --action Drag --from-x 400 --from-y 300 --x 600 --y 300 --bypass-raycast true --target-path "Canvas/Item" --drop-target-path "Canvas/DropZone"
+
 # Long-press a button for 3 seconds
 uloop simulate-mouse-ui --action LongPress --x 400 --y 300 --duration 3.0
 
@@ -97,3 +114,19 @@ uloop simulate-mouse-ui --action DragEnd --x 600 --y 300
 - Target scene must have an **EventSystem** GameObject
 - UI elements must have a **GraphicRaycaster** on their Canvas
 - If you need gameplay mouse input rather than UI pointer events, `simulate-mouse-input` assumes the project uses the New Input System; otherwise prefer `execute-dynamic-code`
+
+## Output
+
+Returns JSON with:
+- `Success`: Whether the operation succeeded
+- `Message`: Status message (e.g. "Hit element: ButtonStart" or "No UI element under (x, y)")
+- `Action`: Echoes which action was executed (`Click`, `Drag`, `DragStart`, `DragMove`, `DragEnd`, or `LongPress`)
+- `HitGameObjectName`: Name of the topmost UI element under the pointer (nullable string; null if nothing was hit)
+- `PositionX`: Target X coordinate that was used
+- `PositionY`: Target Y coordinate that was used
+- `EndPositionX`: Drag end X coordinate (nullable float; populated for drag actions only)
+- `EndPositionY`: Drag end Y coordinate (nullable float; populated for drag actions only)
+
+These are the only eight fields. There is no `Button`, `Duration`, `DragSpeed`, raycast list, or pointer-event log in the response — verify the visual outcome with a follow-up `uloop screenshot --capture-mode rendering --annotate-elements`.
+
+Note: Click and LongPress on empty space (no UI element) still return `Success = true` with `HitGameObjectName = null`. Drag actions on empty space return `Success = false`.
PATCH

echo "Gold patch applied."
