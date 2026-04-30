"""Behavioral checks for unity-cli-loop-chore-update-uloop-skills (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/unity-cli-loop")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/uloop-clear-console/SKILL.md')
    assert '- `Message` (string): Description of the result; carries the failure summary when the operation fails (e.g. `"Failed to clear console: ..."`)' in text, "expected to find: " + '- `Message` (string): Description of the result; carries the failure summary when the operation fails (e.g. `"Failed to clear console: ..."`)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/uloop-clear-console/SKILL.md')
    assert '- `ErrorMessage` (string): Currently always empty for this tool — read `Message` for failure details' in text, "expected to find: " + '- `ErrorMessage` (string): Currently always empty for this tool — read `Message` for failure details'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/uloop-clear-console/SKILL.md')
    assert '- `ClearedLogCount` (number): Total number of log entries that were cleared' in text, "expected to find: " + '- `ClearedLogCount` (number): Total number of log entries that were cleared'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/uloop-compile/SKILL.md')
    assert '`uloop launch` auto-detects the project at the current working directory and opens it in the matching Unity Editor version. After Unity finishes launching, retry `uloop compile`.' in text, "expected to find: " + '`uloop launch` auto-detects the project at the current working directory and opens it in the matching Unity Editor version. After Unity finishes launching, retry `uloop compile`.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/uloop-compile/SKILL.md')
    assert "This removes any leftover lock files (`compiling.lock`, `domainreload.lock`, `serverstarting.lock`) from the Unity project's Temp directory. Then retry `uloop compile`." in text, "expected to find: " + "This removes any leftover lock files (`compiling.lock`, `domainreload.lock`, `serverstarting.lock`) from the Unity project's Temp directory. Then retry `uloop compile`."[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/uloop-compile/SKILL.md')
    assert '**Unity Editor not running** (CLI returns a connection failure and no Unity process is alive):' in text, "expected to find: " + '**Unity Editor not running** (CLI returns a connection failure and no Unity process is alive):'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/uloop-control-play-mode/SKILL.md')
    assert '- PlayMode entry may complete on the next editor frame. If a PlayMode-dependent command reports "PlayMode is not active" immediately after `--action Play`, wait briefly and retry.' in text, "expected to find: " + '- PlayMode entry may complete on the next editor frame. If a PlayMode-dependent command reports "PlayMode is not active" immediately after `--action Play`, wait briefly and retry.'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/uloop-execute-dynamic-code/SKILL.md')
    assert 'On `Success: false`, inspect `CompilationErrors` first. If empty, read `ErrorMessage` (and `Logs` for extra context) — the failure may be a runtime exception, security violation, cancellation, or an "' in text, "expected to find: " + 'On `Success: false`, inspect `CompilationErrors` first. If empty, read `ErrorMessage` (and `Logs` for extra context) — the failure may be a runtime exception, security violation, cancellation, or an "'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/uloop-execute-dynamic-code/SKILL.md')
    assert '- `CompilationErrors`: object[] — Roslyn diagnostics with `Message`, `Line`, `Column`, `ErrorCode`, optional `Hint` and `Suggestions`' in text, "expected to find: " + '- `CompilationErrors`: object[] — Roslyn diagnostics with `Message`, `Line`, `Column`, `ErrorCode`, optional `Hint` and `Suggestions`'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/uloop-execute-dynamic-code/SKILL.md')
    assert '- `Diagnostics`: object[] — structured diagnostics; same shape as `CompilationErrors`, usually populated together with it' in text, "expected to find: " + '- `Diagnostics`: object[] — structured diagnostics; same shape as `CompilationErrors`, usually populated together with it'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/uloop-find-game-objects/SKILL.md')
    assert 'description: "Find GameObjects in the active scene by various criteria. Use when you need to: (1) Search for objects by name, regex, or path, (2) Find objects with specific components, tags, or layers' in text, "expected to find: " + 'description: "Find GameObjects in the active scene by various criteria. Use when you need to: (1) Search for objects by name, regex, or path, (2) Find objects with specific components, tags, or layers'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/uloop-find-game-objects/SKILL.md')
    assert '- `components` (array): Each entry has `type` (short name, e.g., `Rigidbody`), `fullTypeName` (e.g., `UnityEngine.Rigidbody`), and `properties` (array of Inspector-visible `{name, type, value}` pairs)' in text, "expected to find: " + '- `components` (array): Each entry has `type` (short name, e.g., `Rigidbody`), `fullTypeName` (e.g., `UnityEngine.Rigidbody`), and `properties` (array of Inspector-visible `{name, type, value}` pairs)'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/uloop-find-game-objects/SKILL.md')
    assert 'Single-selection and search-mode calls (`Exact`, `Path`, `Regex`, `Contains`) always return inline. No selection (`Selected` mode with empty selection) returns empty `results` plus a `message`.' in text, "expected to find: " + 'Single-selection and search-mode calls (`Exact`, `Path`, `Regex`, `Contains`) always return inline. No selection (`Selected` mode with empty selection) returns empty `results` plus a `message`.'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/uloop-focus-window/SKILL.md')
    assert '- `Message`: Status message (e.g. `Unity Editor window focused (PID: 12345)`, or the failure reason such as `Unity project not found` / `No running Unity process found for this project` / `Failed to f' in text, "expected to find: " + '- `Message`: Status message (e.g. `Unity Editor window focused (PID: 12345)`, or the failure reason such as `Unity project not found` / `No running Unity process found for this project` / `Failed to f'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/uloop-focus-window/SKILL.md')
    assert 'These are the only two fields. There is no PID, window-handle, or platform field returned to the caller.' in text, "expected to find: " + 'These are the only two fields. There is no PID, window-handle, or platform field returned to the caller.'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/uloop-focus-window/SKILL.md')
    assert '- `Success`: Whether the focus operation succeeded' in text, "expected to find: " + '- `Success`: Whether the focus operation succeeded'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/uloop-get-hierarchy/SKILL.md')
    assert 'description: "Get Unity scene hierarchy as a structured tree. Use when you need to: (1) Inspect scene structure and parent-child relationships, (2) Explore GameObjects and their components, (3) Get hi' in text, "expected to find: " + 'description: "Get Unity scene hierarchy as a structured tree. Use when you need to: (1) Inspect scene structure and parent-child relationships, (2) Explore GameObjects and their components, (3) Get hi'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/uloop-get-hierarchy/SKILL.md')
    assert 'The hierarchy itself is **not** in the response — it is written to the file at `hierarchyFilePath`. Open that file to read the `Context` and `Hierarchy` payload (GameObject tree, components, etc.).' in text, "expected to find: " + 'The hierarchy itself is **not** in the response — it is written to the file at `hierarchyFilePath`. Open that file to read the `Context` and `Hierarchy` payload (GameObject tree, components, etc.).'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/uloop-get-hierarchy/SKILL.md')
    assert '- `hierarchyFilePath` (string): Filesystem path to the JSON file that contains the actual hierarchy data' in text, "expected to find: " + '- `hierarchyFilePath` (string): Filesystem path to the JSON file that contains the actual hierarchy data'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/uloop-get-logs/SKILL.md')
    assert 'description: "Retrieve current Unity Console entries via uloop CLI. Use when you need to: (1) inspect errors, warnings, or logs after compile, tests, PlayMode, or dynamic code execution, (2) search cu' in text, "expected to find: " + 'description: "Retrieve current Unity Console entries via uloop CLI. Use when you need to: (1) inspect errors, warnings, or logs after compile, tests, PlayMode, or dynamic code execution, (2) search cu'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/uloop-get-logs/SKILL.md')
    assert '- `SearchText` (string): The `--search-text` filter that was applied (empty when omitted)' in text, "expected to find: " + '- `SearchText` (string): The `--search-text` filter that was applied (empty when omitted)'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/uloop-get-logs/SKILL.md')
    assert '- `StackTrace` (string): Stack trace text. Empty when `--include-stack-trace` is `false`.' in text, "expected to find: " + '- `StackTrace` (string): Stack trace text. Empty when `--include-stack-trace` is `false`.'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/uloop-launch/SKILL.md')
    assert '`uloop launch` is not fire-and-forget. When Unity needs to start or restart, the command waits' in text, "expected to find: " + '`uloop launch` is not fire-and-forget. When Unity needs to start or restart, the command waits'[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/uloop-launch/SKILL.md')
    assert '- If launching, waits until Unity finishes startup and the CLI can connect to the project' in text, "expected to find: " + '- If launching, waits until Unity finishes startup and the CLI can connect to the project'[:80]


def test_signal_24():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/uloop-launch/SKILL.md')
    assert 'until Unity is actually ready for CLI operations before it exits.' in text, "expected to find: " + 'until Unity is actually ready for CLI operations before it exits.'[:80]


def test_signal_25():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/uloop-record-input/SKILL.md')
    assert 'description: "Record keyboard and mouse input during PlayMode into a JSON file. Use when you need to: (1) Capture human gameplay input for later replay, (2) Record input sequences for E2E testing, (3)' in text, "expected to find: " + 'description: "Record keyboard and mouse input during PlayMode into a JSON file. Use when you need to: (1) Capture human gameplay input for later replay, (2) Record input sequences for E2E testing, (3)'[:80]


def test_signal_26():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/uloop-record-input/SKILL.md')
    assert 'Replay injects input frame-by-frame, so the game must also be deterministic to produce identical results. If the recording will be used for E2E tests, bug reproduction, or replay verification, read [r' in text, "expected to find: " + 'Replay injects input frame-by-frame, so the game must also be deterministic to produce identical results. If the recording will be used for E2E tests, bug reproduction, or replay verification, read [r'[:80]


def test_signal_27():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/uloop-record-input/SKILL.md')
    assert 'The CLI output contains only these six payload fields. Internal metadata such as `Ver` is removed before printing. There is no `RecordingId`, `StartTimestamp`, `KeysCaptured`, or per-frame data in the' in text, "expected to find: " + 'The CLI output contains only these six payload fields. Internal metadata such as `Ver` is removed before printing. There is no `RecordingId`, `StartTimestamp`, `KeysCaptured`, or per-frame data in the'[:80]


def test_signal_28():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/uloop-record-input/references/deterministic-replay.md')
    assert 'Replay injects input frame-by-frame, so the game must produce identical results given identical input on each run. The following patterns break determinism and should be avoided in replay-targeted cod' in text, "expected to find: " + 'Replay injects input frame-by-frame, so the game must produce identical results given identical input on each run. The following patterns break determinism and should be avoided in replay-targeted cod'[:80]


def test_signal_29():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/uloop-record-input/references/deterministic-replay.md')
    assert 'Set `Application.targetFrameRate = 60` or another fixed target to reduce frame timing variance. See `InputReplayVerificationController` for a complete example of deterministic game logic.' in text, "expected to find: " + 'Set `Application.targetFrameRate = 60` or another fixed target to reduce frame timing variance. See `InputReplayVerificationController` for a complete example of deterministic game logic.'[:80]


def test_signal_30():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/uloop-record-input/references/deterministic-replay.md')
    assert '| `Time.deltaTime` for movement | Fixed per-frame constant (e.g. `MOVE_SPEED = 0.1f`) | Delta time varies between runs even at the same target frame rate |' in text, "expected to find: " + '| `Time.deltaTime` for movement | Fixed per-frame constant (e.g. `MOVE_SPEED = 0.1f`) | Delta time varies between runs even at the same target frame rate |'[:80]


def test_signal_31():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/uloop-replay-input/SKILL.md')
    assert 'description: "Replay recorded input during PlayMode with frame-precise injection. Use when you need to: (1) Reproduce recorded gameplay exactly, (2) Run E2E tests from recorded input, (3) Generate dem' in text, "expected to find: " + 'description: "Replay recorded input during PlayMode with frame-precise injection. Use when you need to: (1) Reproduce recorded gameplay exactly, (2) Run E2E tests from recorded input, (3) Generate dem'[:80]


def test_signal_32():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/uloop-replay-input/SKILL.md')
    assert 'Replay injects the exact same input frame-by-frame, but the game must also be deterministic to produce identical results. If replay output must be compared across runs, read [references/deterministic-' in text, "expected to find: " + 'Replay injects the exact same input frame-by-frame, but the game must also be deterministic to produce identical results. If replay output must be compared across runs, read [references/deterministic-'[:80]


def test_signal_33():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/uloop-replay-input/SKILL.md')
    assert 'These are the only eight fields. There is no `LoopCount`, `ElapsedSeconds`, `OverlayVisible`, or per-frame inspection data in the response.' in text, "expected to find: " + 'These are the only eight fields. There is no `LoopCount`, `ElapsedSeconds`, `OverlayVisible`, or per-frame inspection data in the response.'[:80]


def test_signal_34():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/uloop-replay-input/references/deterministic-replay.md')
    assert 'Replay injects input frame-by-frame, so the game must produce identical results given identical input on each run. The following patterns break determinism and should be avoided in replay-targeted cod' in text, "expected to find: " + 'Replay injects input frame-by-frame, so the game must produce identical results given identical input on each run. The following patterns break determinism and should be avoided in replay-targeted cod'[:80]


def test_signal_35():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/uloop-replay-input/references/deterministic-replay.md')
    assert 'Set `Application.targetFrameRate = 60` or another fixed target to reduce frame timing variance. See `InputReplayVerificationController` for a complete example of deterministic game logic.' in text, "expected to find: " + 'Set `Application.targetFrameRate = 60` or another fixed target to reduce frame timing variance. See `InputReplayVerificationController` for a complete example of deterministic game logic.'[:80]


def test_signal_36():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/uloop-replay-input/references/deterministic-replay.md')
    assert '| `Time.deltaTime` for movement | Fixed per-frame constant (e.g. `MOVE_SPEED = 0.1f`) | Delta time varies between runs even at the same target frame rate |' in text, "expected to find: " + '| `Time.deltaTime` for movement | Fixed per-frame constant (e.g. `MOVE_SPEED = 0.1f`) | Delta time varies between runs even at the same target frame rate |'[:80]


def test_signal_37():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/uloop-run-tests/SKILL.md')
    assert 'Before executing tests, `uloop run-tests` checks for unsaved loaded Scene changes and unsaved current Prefab Stage changes. If any are found, it returns `Success: false`, keeps `TestCount` at `0`, lis' in text, "expected to find: " + 'Before executing tests, `uloop run-tests` checks for unsaved loaded Scene changes and unsaved current Prefab Stage changes. If any are found, it returns `Success: false`, keeps `TestCount` at `0`, lis'[:80]


def test_signal_38():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/uloop-run-tests/SKILL.md')
    assert 'description: "Execute Unity Test Runner and get detailed results. Use when you need to: (1) Run EditMode or PlayMode unit tests, (2) Verify code changes pass all tests, (3) Diagnose test failures with' in text, "expected to find: " + 'description: "Execute Unity Test Runner and get detailed results. Use when you need to: (1) Run EditMode or PlayMode unit tests, (2) Verify code changes pass all tests, (3) Diagnose test failures with'[:80]


def test_signal_39():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/uloop-run-tests/SKILL.md')
    assert '- `XmlPath` (string): Path to NUnit XML result file. Empty string when no XML was saved (typically on `Success: true`); populated only when tests failed and the XML file exists on disk.' in text, "expected to find: " + '- `XmlPath` (string): Path to NUnit XML result file. Empty string when no XML was saved (typically on `Success: true`); populated only when tests failed and the XML file exists on disk.'[:80]


def test_signal_40():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/uloop-screenshot/SKILL.md')
    assert 'description: "Capture screenshots of Unity Editor windows as PNG files. Use when you need to: (1) Screenshot Game View, Scene View, Console, Inspector, or other windows, (2) Capture current visual sta' in text, "expected to find: " + 'description: "Capture screenshots of Unity Editor windows as PNG files. Use when you need to: (1) Screenshot Game View, Scene View, Console, Inspector, or other windows, (2) Capture current visual sta'[:80]


def test_signal_41():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/uloop-screenshot/SKILL.md')
    assert 'For `AnnotatedElements` fields and gameView coordinate conversion, read [references/annotated-elements.md](references/annotated-elements.md) before using screenshot coordinates with mouse simulation t' in text, "expected to find: " + 'For `AnnotatedElements` fields and gameView coordinate conversion, read [references/annotated-elements.md](references/annotated-elements.md) before using screenshot coordinates with mouse simulation t'[:80]


def test_signal_42():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/uloop-screenshot/SKILL.md')
    assert '| `--annotate-elements` | boolean | `false` | Annotate interactive UI elements with index labels and interaction hints (A / CLICK, B / DRAG, ...). Only works with `--capture-mode rendering` in PlayMod' in text, "expected to find: " + '| `--annotate-elements` | boolean | `false` | Annotate interactive UI elements with index labels and interaction hints (A / CLICK, B / DRAG, ...). Only works with `--capture-mode rendering` in PlayMod'[:80]


def test_signal_43():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/uloop-screenshot/references/annotated-elements.md')
    assert 'Annotated screenshots compensate border thickness for `ResolutionScale`, so the saved PNG keeps the intended outline width after downscaling. The neutral contrast borders are 2 output pixels each, and' in text, "expected to find: " + 'Annotated screenshots compensate border thickness for `ResolutionScale`, so the saved PNG keeps the intended outline width after downscaling. The neutral contrast borders are 2 output pixels each, and'[:80]


def test_signal_44():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/uloop-screenshot/references/annotated-elements.md')
    assert '- `Interaction`: Derived interaction category (`Click`, `Drag`, `Drop`, `Text`). Use this to choose between `simulate-mouse-ui --action Click` and drag actions.' in text, "expected to find: " + '- `Interaction`: Derived interaction category (`Click`, `Drag`, `Drop`, `Text`). Use this to choose between `simulate-mouse-ui --action Click` and drag actions.'[:80]


def test_signal_45():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/uloop-screenshot/references/annotated-elements.md')
    assert '- `Path`: Hierarchy path from the scene root, for example `Canvas/Panel/Button`. Use this as `simulate-mouse-ui --target-path` when bypassing raycast blockers.' in text, "expected to find: " + '- `Path`: Hierarchy path from the scene root, for example `Canvas/Panel/Button`. Use this as `simulate-mouse-ui --target-path` when bypassing raycast blockers.'[:80]


def test_signal_46():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/uloop-simulate-keyboard/SKILL.md')
    assert 'description: "Simulate keyboard key input in PlayMode via Input System. Use when you need to: (1) Press game control keys like WASD, Space, or Shift during PlayMode, (2) Hold keys down for continuous ' in text, "expected to find: " + 'description: "Simulate keyboard key input in PlayMode via Input System. Use when you need to: (1) Press game control keys like WASD, Space, or Shift during PlayMode, (2) Hold keys down for continuous '[:80]


def test_signal_47():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/uloop-simulate-keyboard/SKILL.md')
    assert '- To hold a key for a fixed duration, prefer `--action Press --duration <seconds>` (one-shot, blocks until release). For multi-key holds (e.g. Shift+W), issue separate `KeyDown` calls, then `sleep <se' in text, "expected to find: " + '- To hold a key for a fixed duration, prefer `--action Press --duration <seconds>` (one-shot, blocks until release). For multi-key holds (e.g. Shift+W), issue separate `KeyDown` calls, then `sleep <se'[:80]


def test_signal_48():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/uloop-simulate-keyboard/SKILL.md')
    assert '- `Success` (boolean): Whether the action succeeded (e.g. `KeyDown` on a not-yet-held key, `KeyUp` on a currently-held key, or `Press` round-trip)' in text, "expected to find: " + '- `Success` (boolean): Whether the action succeeded (e.g. `KeyDown` on a not-yet-held key, `KeyUp` on a currently-held key, or `Press` round-trip)'[:80]


def test_signal_49():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/uloop-simulate-mouse-input/SKILL.md')
    assert 'description: "Simulate mouse input in PlayMode for gameplay code that reads Unity Input System Mouse.current. Use when you need to: (1) Click or right-click in games that read Mouse.current button sta' in text, "expected to find: " + 'description: "Simulate mouse input in PlayMode for gameplay code that reads Unity Input System Mouse.current. Use when you need to: (1) Click or right-click in games that read Mouse.current button sta'[:80]


def test_signal_50():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/uloop-simulate-mouse-input/SKILL.md')
    assert 'These are the only six fields. There is no `DeltaX`, `DeltaY`, `ScrollX`, `ScrollY`, `Duration`, or hit-element field in the response — only the issued action, button, and target position are echoed b' in text, "expected to find: " + 'These are the only six fields. There is no `DeltaX`, `DeltaY`, `ScrollX`, `ScrollY`, `Duration`, or hit-element field in the response — only the issued action, button, and target position are echoed b'[:80]


def test_signal_51():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/uloop-simulate-mouse-input/SKILL.md')
    assert '- `Action`: Echoes which action was executed (`Click`, `LongPress`, `MoveDelta`, `SmoothDelta`, or `Scroll`)' in text, "expected to find: " + '- `Action`: Echoes which action was executed (`Click`, `LongPress`, `MoveDelta`, `SmoothDelta`, or `Scroll`)'[:80]


def test_signal_52():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/uloop-simulate-mouse-ui/SKILL.md')
    assert 'description: "Simulate mouse click, long-press, and drag on PlayMode UI elements via EventSystem screen coordinates from annotated screenshots. Use when you need to: (1) Click buttons or interactive U' in text, "expected to find: " + 'description: "Simulate mouse click, long-press, and drag on PlayMode UI elements via EventSystem screen coordinates from annotated screenshots. Use when you need to: (1) Click buttons or interactive U'[:80]


def test_signal_53():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/uloop-simulate-mouse-ui/SKILL.md')
    assert '| `--target-path` | string | `""` | Hierarchy path of the target GameObject, for example `Canvas/Panel/Button`. Required when `--bypass-raycast true` is used with `Click`, `LongPress`, `Drag`, or `Dra' in text, "expected to find: " + '| `--target-path` | string | `""` | Hierarchy path of the target GameObject, for example `Canvas/Panel/Button`. Required when `--bypass-raycast true` is used with `Click`, `LongPress`, `Drag`, or `Dra'[:80]


def test_signal_54():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/uloop-simulate-mouse-ui/SKILL.md')
    assert '3. Use the `AnnotatedElements` array to find the target element by `Label`, `Name`, or `Path` (A=frontmost, B=next, ...). Use `Interaction` to distinguish click targets from drag/drop/text targets, th' in text, "expected to find: " + '3. Use the `AnnotatedElements` array to find the target element by `Label`, `Name`, or `Path` (A=frontmost, B=next, ...). Use `Interaction` to distinguish click targets from drag/drop/text targets, th'[:80]


def test_signal_55():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/uloop-clear-console/SKILL.md')
    assert '- `Message` (string): Description of the result; carries the failure summary when the operation fails (e.g. `"Failed to clear console: ..."`)' in text, "expected to find: " + '- `Message` (string): Description of the result; carries the failure summary when the operation fails (e.g. `"Failed to clear console: ..."`)'[:80]


def test_signal_56():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/uloop-clear-console/SKILL.md')
    assert '- `ErrorMessage` (string): Currently always empty for this tool — read `Message` for failure details' in text, "expected to find: " + '- `ErrorMessage` (string): Currently always empty for this tool — read `Message` for failure details'[:80]


def test_signal_57():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/uloop-clear-console/SKILL.md')
    assert '- `ClearedLogCount` (number): Total number of log entries that were cleared' in text, "expected to find: " + '- `ClearedLogCount` (number): Total number of log entries that were cleared'[:80]


def test_signal_58():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/uloop-compile/SKILL.md')
    assert '`uloop launch` auto-detects the project at the current working directory and opens it in the matching Unity Editor version. After Unity finishes launching, retry `uloop compile`.' in text, "expected to find: " + '`uloop launch` auto-detects the project at the current working directory and opens it in the matching Unity Editor version. After Unity finishes launching, retry `uloop compile`.'[:80]


def test_signal_59():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/uloop-compile/SKILL.md')
    assert "This removes any leftover lock files (`compiling.lock`, `domainreload.lock`, `serverstarting.lock`) from the Unity project's Temp directory. Then retry `uloop compile`." in text, "expected to find: " + "This removes any leftover lock files (`compiling.lock`, `domainreload.lock`, `serverstarting.lock`) from the Unity project's Temp directory. Then retry `uloop compile`."[:80]


def test_signal_60():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/uloop-compile/SKILL.md')
    assert '**Unity Editor not running** (CLI returns a connection failure and no Unity process is alive):' in text, "expected to find: " + '**Unity Editor not running** (CLI returns a connection failure and no Unity process is alive):'[:80]


def test_signal_61():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/uloop-control-play-mode/SKILL.md')
    assert '- PlayMode entry may complete on the next editor frame. If a PlayMode-dependent command reports "PlayMode is not active" immediately after `--action Play`, wait briefly and retry.' in text, "expected to find: " + '- PlayMode entry may complete on the next editor frame. If a PlayMode-dependent command reports "PlayMode is not active" immediately after `--action Play`, wait briefly and retry.'[:80]


def test_signal_62():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/uloop-execute-dynamic-code/SKILL.md')
    assert 'description: "Execute C# code dynamically in Unity Editor. Use when you need to: (1) Wire prefab/material references and AddComponent operations, (2) Edit SerializedObject properties and reference wir' in text, "expected to find: " + 'description: "Execute C# code dynamically in Unity Editor. Use when you need to: (1) Wire prefab/material references and AddComponent operations, (2) Edit SerializedObject properties and reference wir'[:80]


def test_signal_63():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/uloop-execute-dynamic-code/SKILL.md')
    assert 'On `Success: false`, inspect `CompilationErrors` first. If empty, read `ErrorMessage` (and `Logs` for extra context) — the failure may be a runtime exception, security violation, cancellation, or an "' in text, "expected to find: " + 'On `Success: false`, inspect `CompilationErrors` first. If empty, read `ErrorMessage` (and `Logs` for extra context) — the failure may be a runtime exception, security violation, cancellation, or an "'[:80]


def test_signal_64():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/uloop-execute-dynamic-code/SKILL.md')
    assert '- `CompilationErrors`: object[] — Roslyn diagnostics with `Message`, `Line`, `Column`, `ErrorCode`, optional `Hint` and `Suggestions`' in text, "expected to find: " + '- `CompilationErrors`: object[] — Roslyn diagnostics with `Message`, `Line`, `Column`, `ErrorCode`, optional `Hint` and `Suggestions`'[:80]


def test_signal_65():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/uloop-execute-menu-item/SKILL.md')
    assert '.claude/skills/uloop-execute-menu-item/SKILL.md' in text, "expected to find: " + '.claude/skills/uloop-execute-menu-item/SKILL.md'[:80]


def test_signal_66():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/uloop-find-game-objects/SKILL.md')
    assert 'description: "Find GameObjects in the active scene by various criteria. Use when you need to: (1) Search for objects by name, regex, or path, (2) Find objects with specific components, tags, or layers' in text, "expected to find: " + 'description: "Find GameObjects in the active scene by various criteria. Use when you need to: (1) Search for objects by name, regex, or path, (2) Find objects with specific components, tags, or layers'[:80]


def test_signal_67():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/uloop-find-game-objects/SKILL.md')
    assert '- `components` (array): Each entry has `type` (short name, e.g., `Rigidbody`), `fullTypeName` (e.g., `UnityEngine.Rigidbody`), and `properties` (array of Inspector-visible `{name, type, value}` pairs)' in text, "expected to find: " + '- `components` (array): Each entry has `type` (short name, e.g., `Rigidbody`), `fullTypeName` (e.g., `UnityEngine.Rigidbody`), and `properties` (array of Inspector-visible `{name, type, value}` pairs)'[:80]


def test_signal_68():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/uloop-find-game-objects/SKILL.md')
    assert 'Single-selection and search-mode calls (`Exact`, `Path`, `Regex`, `Contains`) always return inline. No selection (`Selected` mode with empty selection) returns empty `results` plus a `message`.' in text, "expected to find: " + 'Single-selection and search-mode calls (`Exact`, `Path`, `Regex`, `Contains`) always return inline. No selection (`Selected` mode with empty selection) returns empty `results` plus a `message`.'[:80]


def test_signal_69():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/uloop-focus-window/SKILL.md')
    assert '- `Message`: Status message (e.g. `Unity Editor window focused (PID: 12345)`, or the failure reason such as `Unity project not found` / `No running Unity process found for this project` / `Failed to f' in text, "expected to find: " + '- `Message`: Status message (e.g. `Unity Editor window focused (PID: 12345)`, or the failure reason such as `Unity project not found` / `No running Unity process found for this project` / `Failed to f'[:80]


def test_signal_70():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/uloop-focus-window/SKILL.md')
    assert 'These are the only two fields. There is no PID, window-handle, or platform field returned to the caller.' in text, "expected to find: " + 'These are the only two fields. There is no PID, window-handle, or platform field returned to the caller.'[:80]


def test_signal_71():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/uloop-focus-window/SKILL.md')
    assert '- `Success`: Whether the focus operation succeeded' in text, "expected to find: " + '- `Success`: Whether the focus operation succeeded'[:80]


def test_signal_72():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/uloop-get-hierarchy/SKILL.md')
    assert 'description: "Get Unity scene hierarchy as a structured tree. Use when you need to: (1) Inspect scene structure and parent-child relationships, (2) Explore GameObjects and their components, (3) Get hi' in text, "expected to find: " + 'description: "Get Unity scene hierarchy as a structured tree. Use when you need to: (1) Inspect scene structure and parent-child relationships, (2) Explore GameObjects and their components, (3) Get hi'[:80]


def test_signal_73():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/uloop-get-hierarchy/SKILL.md')
    assert 'The hierarchy itself is **not** in the response — it is written to the file at `hierarchyFilePath`. Open that file to read the `Context` and `Hierarchy` payload (GameObject tree, components, etc.).' in text, "expected to find: " + 'The hierarchy itself is **not** in the response — it is written to the file at `hierarchyFilePath`. Open that file to read the `Context` and `Hierarchy` payload (GameObject tree, components, etc.).'[:80]


def test_signal_74():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/uloop-get-hierarchy/SKILL.md')
    assert '- `hierarchyFilePath` (string): Filesystem path to the JSON file that contains the actual hierarchy data' in text, "expected to find: " + '- `hierarchyFilePath` (string): Filesystem path to the JSON file that contains the actual hierarchy data'[:80]


def test_signal_75():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/uloop-get-logs/SKILL.md')
    assert 'description: "Retrieve current Unity Console entries via uloop CLI. Use when you need to: (1) inspect errors, warnings, or logs after compile, tests, PlayMode, or dynamic code execution, (2) search cu' in text, "expected to find: " + 'description: "Retrieve current Unity Console entries via uloop CLI. Use when you need to: (1) inspect errors, warnings, or logs after compile, tests, PlayMode, or dynamic code execution, (2) search cu'[:80]


def test_signal_76():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/uloop-get-logs/SKILL.md')
    assert '- `SearchText` (string): The `--search-text` filter that was applied (empty when omitted)' in text, "expected to find: " + '- `SearchText` (string): The `--search-text` filter that was applied (empty when omitted)'[:80]


def test_signal_77():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/uloop-get-logs/SKILL.md')
    assert '- `StackTrace` (string): Stack trace text. Empty when `--include-stack-trace` is `false`.' in text, "expected to find: " + '- `StackTrace` (string): Stack trace text. Empty when `--include-stack-trace` is `false`.'[:80]


def test_signal_78():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/uloop-launch/SKILL.md')
    assert '`uloop launch` is not fire-and-forget. When Unity needs to start or restart, the command waits' in text, "expected to find: " + '`uloop launch` is not fire-and-forget. When Unity needs to start or restart, the command waits'[:80]


def test_signal_79():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/uloop-launch/SKILL.md')
    assert '- If launching, waits until Unity finishes startup and the CLI can connect to the project' in text, "expected to find: " + '- If launching, waits until Unity finishes startup and the CLI can connect to the project'[:80]


def test_signal_80():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/uloop-launch/SKILL.md')
    assert 'until Unity is actually ready for CLI operations before it exits.' in text, "expected to find: " + 'until Unity is actually ready for CLI operations before it exits.'[:80]


def test_signal_81():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/uloop-record-input/SKILL.md')
    assert 'description: "Record keyboard and mouse input during PlayMode into a JSON file. Use when you need to: (1) Capture human gameplay input for later replay, (2) Record input sequences for E2E testing, (3)' in text, "expected to find: " + 'description: "Record keyboard and mouse input during PlayMode into a JSON file. Use when you need to: (1) Capture human gameplay input for later replay, (2) Record input sequences for E2E testing, (3)'[:80]


def test_signal_82():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/uloop-record-input/SKILL.md')
    assert 'Replay injects input frame-by-frame, so the game must also be deterministic to produce identical results. If the recording will be used for E2E tests, bug reproduction, or replay verification, read [r' in text, "expected to find: " + 'Replay injects input frame-by-frame, so the game must also be deterministic to produce identical results. If the recording will be used for E2E tests, bug reproduction, or replay verification, read [r'[:80]


def test_signal_83():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/uloop-record-input/SKILL.md')
    assert 'The CLI output contains only these six payload fields. Internal metadata such as `Ver` is removed before printing. There is no `RecordingId`, `StartTimestamp`, `KeysCaptured`, or per-frame data in the' in text, "expected to find: " + 'The CLI output contains only these six payload fields. Internal metadata such as `Ver` is removed before printing. There is no `RecordingId`, `StartTimestamp`, `KeysCaptured`, or per-frame data in the'[:80]


def test_signal_84():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/uloop-record-input/references/deterministic-replay.md')
    assert 'Replay injects input frame-by-frame, so the game must produce identical results given identical input on each run. The following patterns break determinism and should be avoided in replay-targeted cod' in text, "expected to find: " + 'Replay injects input frame-by-frame, so the game must produce identical results given identical input on each run. The following patterns break determinism and should be avoided in replay-targeted cod'[:80]


def test_signal_85():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/uloop-record-input/references/deterministic-replay.md')
    assert 'Set `Application.targetFrameRate = 60` or another fixed target to reduce frame timing variance. See `InputReplayVerificationController` for a complete example of deterministic game logic.' in text, "expected to find: " + 'Set `Application.targetFrameRate = 60` or another fixed target to reduce frame timing variance. See `InputReplayVerificationController` for a complete example of deterministic game logic.'[:80]


def test_signal_86():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/uloop-record-input/references/deterministic-replay.md')
    assert '| `Time.deltaTime` for movement | Fixed per-frame constant (e.g. `MOVE_SPEED = 0.1f`) | Delta time varies between runs even at the same target frame rate |' in text, "expected to find: " + '| `Time.deltaTime` for movement | Fixed per-frame constant (e.g. `MOVE_SPEED = 0.1f`) | Delta time varies between runs even at the same target frame rate |'[:80]


def test_signal_87():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/uloop-replay-input/SKILL.md')
    assert 'description: "Replay recorded input during PlayMode with frame-precise injection. Use when you need to: (1) Reproduce recorded gameplay exactly, (2) Run E2E tests from recorded input, (3) Generate dem' in text, "expected to find: " + 'description: "Replay recorded input during PlayMode with frame-precise injection. Use when you need to: (1) Reproduce recorded gameplay exactly, (2) Run E2E tests from recorded input, (3) Generate dem'[:80]


def test_signal_88():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/uloop-replay-input/SKILL.md')
    assert 'Replay injects the exact same input frame-by-frame, but the game must also be deterministic to produce identical results. If replay output must be compared across runs, read [references/deterministic-' in text, "expected to find: " + 'Replay injects the exact same input frame-by-frame, but the game must also be deterministic to produce identical results. If replay output must be compared across runs, read [references/deterministic-'[:80]


def test_signal_89():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/uloop-replay-input/SKILL.md')
    assert 'These are the only eight fields. There is no `LoopCount`, `ElapsedSeconds`, `OverlayVisible`, or per-frame inspection data in the response.' in text, "expected to find: " + 'These are the only eight fields. There is no `LoopCount`, `ElapsedSeconds`, `OverlayVisible`, or per-frame inspection data in the response.'[:80]


def test_signal_90():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/uloop-replay-input/references/deterministic-replay.md')
    assert 'Replay injects input frame-by-frame, so the game must produce identical results given identical input on each run. The following patterns break determinism and should be avoided in replay-targeted cod' in text, "expected to find: " + 'Replay injects input frame-by-frame, so the game must produce identical results given identical input on each run. The following patterns break determinism and should be avoided in replay-targeted cod'[:80]


def test_signal_91():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/uloop-replay-input/references/deterministic-replay.md')
    assert 'Set `Application.targetFrameRate = 60` or another fixed target to reduce frame timing variance. See `InputReplayVerificationController` for a complete example of deterministic game logic.' in text, "expected to find: " + 'Set `Application.targetFrameRate = 60` or another fixed target to reduce frame timing variance. See `InputReplayVerificationController` for a complete example of deterministic game logic.'[:80]


def test_signal_92():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/uloop-replay-input/references/deterministic-replay.md')
    assert '| `Time.deltaTime` for movement | Fixed per-frame constant (e.g. `MOVE_SPEED = 0.1f`) | Delta time varies between runs even at the same target frame rate |' in text, "expected to find: " + '| `Time.deltaTime` for movement | Fixed per-frame constant (e.g. `MOVE_SPEED = 0.1f`) | Delta time varies between runs even at the same target frame rate |'[:80]


def test_signal_93():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/uloop-run-tests/SKILL.md')
    assert 'Before executing tests, `uloop run-tests` checks for unsaved loaded Scene changes and unsaved current Prefab Stage changes. If any are found, it returns `Success: false`, keeps `TestCount` at `0`, lis' in text, "expected to find: " + 'Before executing tests, `uloop run-tests` checks for unsaved loaded Scene changes and unsaved current Prefab Stage changes. If any are found, it returns `Success: false`, keeps `TestCount` at `0`, lis'[:80]


def test_signal_94():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/uloop-run-tests/SKILL.md')
    assert 'description: "Execute Unity Test Runner and get detailed results. Use when you need to: (1) Run EditMode or PlayMode unit tests, (2) Verify code changes pass all tests, (3) Diagnose test failures with' in text, "expected to find: " + 'description: "Execute Unity Test Runner and get detailed results. Use when you need to: (1) Run EditMode or PlayMode unit tests, (2) Verify code changes pass all tests, (3) Diagnose test failures with'[:80]


def test_signal_95():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/uloop-run-tests/SKILL.md')
    assert '- `XmlPath` (string): Path to NUnit XML result file. Empty string when no XML was saved (typically on `Success: true`); populated only when tests failed and the XML file exists on disk.' in text, "expected to find: " + '- `XmlPath` (string): Path to NUnit XML result file. Empty string when no XML was saved (typically on `Success: true`); populated only when tests failed and the XML file exists on disk.'[:80]


def test_signal_96():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/uloop-screenshot/SKILL.md')
    assert 'description: "Capture screenshots of Unity Editor windows as PNG files. Use when you need to: (1) Screenshot Game View, Scene View, Console, Inspector, or other windows, (2) Capture current visual sta' in text, "expected to find: " + 'description: "Capture screenshots of Unity Editor windows as PNG files. Use when you need to: (1) Screenshot Game View, Scene View, Console, Inspector, or other windows, (2) Capture current visual sta'[:80]


def test_signal_97():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/uloop-screenshot/SKILL.md')
    assert 'For `AnnotatedElements` fields and gameView coordinate conversion, read [references/annotated-elements.md](references/annotated-elements.md) before using screenshot coordinates with mouse simulation t' in text, "expected to find: " + 'For `AnnotatedElements` fields and gameView coordinate conversion, read [references/annotated-elements.md](references/annotated-elements.md) before using screenshot coordinates with mouse simulation t'[:80]


def test_signal_98():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/uloop-screenshot/SKILL.md')
    assert '| `--annotate-elements` | boolean | `false` | Annotate interactive UI elements with index labels and interaction hints (A / CLICK, B / DRAG, ...). Only works with `--capture-mode rendering` in PlayMod' in text, "expected to find: " + '| `--annotate-elements` | boolean | `false` | Annotate interactive UI elements with index labels and interaction hints (A / CLICK, B / DRAG, ...). Only works with `--capture-mode rendering` in PlayMod'[:80]


def test_signal_99():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/uloop-screenshot/references/annotated-elements.md')
    assert 'Annotated screenshots compensate border thickness for `ResolutionScale`, so the saved PNG keeps the intended outline width after downscaling. The neutral contrast borders are 2 output pixels each, and' in text, "expected to find: " + 'Annotated screenshots compensate border thickness for `ResolutionScale`, so the saved PNG keeps the intended outline width after downscaling. The neutral contrast borders are 2 output pixels each, and'[:80]


def test_signal_100():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/uloop-screenshot/references/annotated-elements.md')
    assert '- `Interaction`: Derived interaction category (`Click`, `Drag`, `Drop`, `Text`). Use this to choose between `simulate-mouse-ui --action Click` and drag actions.' in text, "expected to find: " + '- `Interaction`: Derived interaction category (`Click`, `Drag`, `Drop`, `Text`). Use this to choose between `simulate-mouse-ui --action Click` and drag actions.'[:80]


def test_signal_101():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/uloop-screenshot/references/annotated-elements.md')
    assert '- `Path`: Hierarchy path from the scene root, for example `Canvas/Panel/Button`. Use this as `simulate-mouse-ui --target-path` when bypassing raycast blockers.' in text, "expected to find: " + '- `Path`: Hierarchy path from the scene root, for example `Canvas/Panel/Button`. Use this as `simulate-mouse-ui --target-path` when bypassing raycast blockers.'[:80]


def test_signal_102():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/uloop-simulate-keyboard/SKILL.md')
    assert 'description: "Simulate keyboard key input in PlayMode via Input System. Use when you need to: (1) Press game control keys like WASD, Space, or Shift during PlayMode, (2) Hold keys down for continuous ' in text, "expected to find: " + 'description: "Simulate keyboard key input in PlayMode via Input System. Use when you need to: (1) Press game control keys like WASD, Space, or Shift during PlayMode, (2) Hold keys down for continuous '[:80]


def test_signal_103():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/uloop-simulate-keyboard/SKILL.md')
    assert '- To hold a key for a fixed duration, prefer `--action Press --duration <seconds>` (one-shot, blocks until release). For multi-key holds (e.g. Shift+W), issue separate `KeyDown` calls, then `sleep <se' in text, "expected to find: " + '- To hold a key for a fixed duration, prefer `--action Press --duration <seconds>` (one-shot, blocks until release). For multi-key holds (e.g. Shift+W), issue separate `KeyDown` calls, then `sleep <se'[:80]


def test_signal_104():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/uloop-simulate-keyboard/SKILL.md')
    assert '- `Success` (boolean): Whether the action succeeded (e.g. `KeyDown` on a not-yet-held key, `KeyUp` on a currently-held key, or `Press` round-trip)' in text, "expected to find: " + '- `Success` (boolean): Whether the action succeeded (e.g. `KeyDown` on a not-yet-held key, `KeyUp` on a currently-held key, or `Press` round-trip)'[:80]


def test_signal_105():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/uloop-simulate-mouse-input/SKILL.md')
    assert 'description: "Simulate mouse input in PlayMode for gameplay code that reads Unity Input System Mouse.current. Use when you need to: (1) Click or right-click in games that read Mouse.current button sta' in text, "expected to find: " + 'description: "Simulate mouse input in PlayMode for gameplay code that reads Unity Input System Mouse.current. Use when you need to: (1) Click or right-click in games that read Mouse.current button sta'[:80]


def test_signal_106():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/uloop-simulate-mouse-input/SKILL.md')
    assert 'These are the only six fields. There is no `DeltaX`, `DeltaY`, `ScrollX`, `ScrollY`, `Duration`, or hit-element field in the response — only the issued action, button, and target position are echoed b' in text, "expected to find: " + 'These are the only six fields. There is no `DeltaX`, `DeltaY`, `ScrollX`, `ScrollY`, `Duration`, or hit-element field in the response — only the issued action, button, and target position are echoed b'[:80]


def test_signal_107():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/uloop-simulate-mouse-input/SKILL.md')
    assert '- `Action`: Echoes which action was executed (`Click`, `LongPress`, `MoveDelta`, `SmoothDelta`, or `Scroll`)' in text, "expected to find: " + '- `Action`: Echoes which action was executed (`Click`, `LongPress`, `MoveDelta`, `SmoothDelta`, or `Scroll`)'[:80]


def test_signal_108():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/uloop-simulate-mouse-ui/SKILL.md')
    assert 'description: "Simulate mouse click, long-press, and drag on PlayMode UI elements via EventSystem screen coordinates from annotated screenshots. Use when you need to: (1) Click buttons or interactive U' in text, "expected to find: " + 'description: "Simulate mouse click, long-press, and drag on PlayMode UI elements via EventSystem screen coordinates from annotated screenshots. Use when you need to: (1) Click buttons or interactive U'[:80]


def test_signal_109():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/uloop-simulate-mouse-ui/SKILL.md')
    assert '| `--target-path` | string | `""` | Hierarchy path of the target GameObject, for example `Canvas/Panel/Button`. Required when `--bypass-raycast true` is used with `Click`, `LongPress`, `Drag`, or `Dra' in text, "expected to find: " + '| `--target-path` | string | `""` | Hierarchy path of the target GameObject, for example `Canvas/Panel/Button`. Required when `--bypass-raycast true` is used with `Click`, `LongPress`, `Drag`, or `Dra'[:80]


def test_signal_110():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/uloop-simulate-mouse-ui/SKILL.md')
    assert '3. Use the `AnnotatedElements` array to find the target element by `Label`, `Name`, or `Path` (A=frontmost, B=next, ...). Use `Interaction` to distinguish click targets from drag/drop/text targets, th' in text, "expected to find: " + '3. Use the `AnnotatedElements` array to find the target element by `Label`, `Name`, or `Path` (A=frontmost, B=next, ...). Use `Interaction` to distinguish click targets from drag/drop/text targets, th'[:80]

