"""Behavioral checks for kscrash-refactor-claudemd-into-clauderules-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/kscrash")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/CLAUDE.md')
    assert 'Public modules (API surface): KSCrashRecording, KSCrashFilters, KSCrashSinks, KSCrashInstallations, KSCrashDiscSpaceMonitor, KSCrashBootTimeMonitor, KSCrashDemangleFilter. Public headers: `Sources/[Mo' in text, "expected to find: " + 'Public modules (API surface): KSCrashRecording, KSCrashFilters, KSCrashSinks, KSCrashInstallations, KSCrashDiscSpaceMonitor, KSCrashBootTimeMonitor, KSCrashDemangleFilter. Public headers: `Sources/[Mo'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/CLAUDE.md')
    assert "**Known Issue**: Do not use `--filter` with sanitizers due to a bug in Xcode's xctest helper. Run the full test suite instead. See: https://github.com/swiftlang/swift-package-manager/issues/9546" in text, "expected to find: " + "**Known Issue**: Do not use `--filter` with sanitizers due to a bug in Xcode's xctest helper. Run the full test suite instead. See: https://github.com/swiftlang/swift-package-manager/issues/9546"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/CLAUDE.md')
    assert "Fixed 250ms threshold for main thread hang detection. Not configurable — aligns with Apple's definition. See `KSCrashMonitor_Watchdog.h`." in text, "expected to find: " + "Fixed 250ms threshold for main thread hang detection. Not configurable — aligns with Apple's definition. See `KSCrashMonitor_Watchdog.h`."[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/api-stability.md')
    assert 'The public API surface consists of: **KSCrashRecording**, **KSCrashFilters**, **KSCrashSinks**, **KSCrashInstallations**, **KSCrashDiscSpaceMonitor**, **KSCrashBootTimeMonitor**, and **KSCrashDemangle' in text, "expected to find: " + 'The public API surface consists of: **KSCrashRecording**, **KSCrashFilters**, **KSCrashSinks**, **KSCrashInstallations**, **KSCrashDiscSpaceMonitor**, **KSCrashBootTimeMonitor**, and **KSCrashDemangle'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/api-stability.md')
    assert '- **Method parameter changes**: Any addition, removal, type change, or reordering. ObjC has no default parameters, so even adding a nullable parameter breaks all call sites.' in text, "expected to find: " + '- **Method parameter changes**: Any addition, removal, type change, or reordering. ObjC has no default parameters, so even adding a nullable parameter breaks all call sites.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/api-stability.md')
    assert 'KSCrash prioritizes API stability. The following changes to public headers are **breaking** and need strong justification plus migration guidance:' in text, "expected to find: " + 'KSCrash prioritizes API stability. The following changes to public headers are **breaking** and need strong justification plus migration guidance:'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/async-signal-safety.md')
    assert '**IMPORTANT**: Apple recommends apps launch in under 400ms. KSCrash initializes during `kscrash_install`, which is on the startup path. All code in `kscrash_install` and `kscrs_initialize` must be as ' in text, "expected to find: " + '**IMPORTANT**: Apple recommends apps launch in under 400ms. KSCrash initializes during `kscrash_install`, which is on the startup path. All code in `kscrash_install` and `kscrs_initialize` must be as '[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/async-signal-safety.md')
    assert "**IMPORTANT**: Much of KSCrash's core code runs inside crash handlers (signal handlers, Mach exception handlers). This code must be async-signal-safe, meaning it can only call functions that are safe " in text, "expected to find: " + "**IMPORTANT**: Much of KSCrash's core code runs inside crash handlers (signal handlers, Mach exception handlers). This code must be async-signal-safe, meaning it can only call functions that are safe "[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/async-signal-safety.md')
    assert '- **`getsectiondata()` is async-signal-safe on Apple platforms**: Its only non-trivial call is `strncmp`, which is async-signal-safe on Apple platforms. The open-source dyld code confirms this. Do not' in text, "expected to find: " + '- **`getsectiondata()` is async-signal-safe on Apple platforms**: Its only non-trivial call is `strncmp`, which is async-signal-safe on Apple platforms. The open-source dyld code confirms this. Do not'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/code-style.md')
    assert '- **Non-obvious "why"**: if the reason for a choice isn\'t clear from the code alone, say why. "Load enterTime once — a second load could see a newer value if the main thread briefly woke" is useful. "' in text, "expected to find: " + '- **Non-obvious "why"**: if the reason for a choice isn\'t clear from the code alone, say why. "Load enterTime once — a second load could see a newer value if the main thread briefly woke" is useful. "'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/code-style.md')
    assert '- **Swift SPM modules**: Do **not** use the `KSCrash` prefix. Use plain names (e.g., `SwiftCore`, `Monitors`, `Profiler`, `Report`). The `KSCrash` prefix is only for C/ObjC targets.' in text, "expected to find: " + '- **Swift SPM modules**: Do **not** use the `KSCrash` prefix. Use plain names (e.g., `SwiftCore`, `Monitors`, `Profiler`, `Report`). The `KSCrash` prefix is only for C/ObjC targets.'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/code-style.md')
    assert "- **Simulated or fake values**: when code produces synthetic data (e.g., faking a SIGKILL for watchdog reports), say what it's mimicking and who undoes it." in text, "expected to find: " + "- **Simulated or fake values**: when code produces synthetic data (e.g., faking a SIGKILL for watchdog reports), say what it's mimicking and who undoes it."[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/monitor-sidecars.md')
    assert 'The sidecars directories are configured via `KSCrashReportStoreCConfiguration.reportSidecarsPath` and `runSidecarsPath`. If left `NULL` (the default), they are automatically set to `<installPath>/Side' in text, "expected to find: " + 'The sidecars directories are configured via `KSCrashReportStoreCConfiguration.reportSidecarsPath` and `runSidecarsPath`. If left `NULL` (the default), they are automatically set to `<installPath>/Side'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/monitor-sidecars.md')
    assert 'Sidecars allow monitors to store auxiliary data alongside crash reports without modifying the main report. This is important for monitors (like the Watchdog) that need to update report data after init' in text, "expected to find: " + 'Sidecars allow monitors to store auxiliary data alongside crash reports without modifying the main report. This is important for monitors (like the Watchdog) that need to update report data after init'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/monitor-sidecars.md')
    assert "2. **At report delivery time** (next app launch): When the report store reads a report via `kscrs_readReport`, it scans the sidecar directories for matching files and calls each monitor's `stitchRepor" in text, "expected to find: " + "2. **At report delivery time** (next app launch): When the report store reads a report via `kscrs_readReport`, it scans the sidecar directories for matching files and calls each monitor's `stitchRepor"[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/monitors.md')
    assert "Each monitor declares flags via its `monitorFlags()` callback. If a monitor's `setEnabled()` implementation is async-signal-safe (no ObjC, no locks, no heap allocation), it should declare `KSCrashMoni" in text, "expected to find: " + "Each monitor declares flags via its `monitorFlags()` callback. If a monitor's `setEnabled()` implementation is async-signal-safe (no ObjC, no locks, no heap allocation), it should declare `KSCrashMoni"[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/monitors.md')
    assert 'Built-in monitors are registered via `KSCrashMonitorType` flags. External monitors can be added as plugins via `KSCrashConfiguration.plugins` (Swift: `MonitorPlugin`, ObjC: `KSCrashMonitorPlugin`), wh' in text, "expected to find: " + 'Built-in monitors are registered via `KSCrashMonitorType` flags. External monitors can be added as plugins via `KSCrashConfiguration.plugins` (Swift: `MonitorPlugin`, ObjC: `KSCrashMonitorPlugin`), wh'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/monitors.md')
    assert 'The watchdog monitor uses a fixed 250ms threshold to detect hangs on the main thread. This threshold is intentionally not configurable — it aligns with Apple\'s definition of a "hang" (250ms+) and shou' in text, "expected to find: " + 'The watchdog monitor uses a fixed 250ms threshold to detect hangs on the main thread. This threshold is intentionally not configurable — it aligns with Apple\'s definition of a "hang" (250ms+) and shou'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/packaging.md')
    assert 'The public API surface consists of these modules: **KSCrashRecording**, **KSCrashFilters**, **KSCrashSinks**, **KSCrashInstallations**, **KSCrashDiscSpaceMonitor**, **KSCrashBootTimeMonitor**, and **K' in text, "expected to find: " + 'The public API surface consists of these modules: **KSCrashRecording**, **KSCrashFilters**, **KSCrashSinks**, **KSCrashInstallations**, **KSCrashDiscSpaceMonitor**, **KSCrashBootTimeMonitor**, and **K'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/packaging.md')
    assert '`KSCrash.podspec` must stay in sync with `Package.swift`. When adding a new target or dependency in Package.swift, always add the corresponding subspec and dependency in the podspec. CI lint jobs will' in text, "expected to find: " + '`KSCrash.podspec` must stay in sync with `Package.swift`. When adding a new target or dependency in Package.swift, always add the corresponding subspec and dependency in the podspec. CI lint jobs will'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/packaging.md')
    assert 'Swift SPM modules should **not** use the `KSCrash` prefix. Use plain names (e.g., `SwiftCore`, `Monitors`, `Profiler`, `Report`). The `KSCrash` prefix is only for C/ObjC targets.' in text, "expected to find: " + 'Swift SPM modules should **not** use the `KSCrash` prefix. Use plain names (e.g., `SwiftCore`, `Monitors`, `Profiler`, `Report`). The `KSCrash` prefix is only for C/ObjC targets.'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/run-id.md')
    assert '**Purpose**: Reports from the current run may still be updated (e.g., watchdog hang reports that get resolved). `sendAllReportsWithCompletion:` automatically excludes reports whose `run_id` matches th' in text, "expected to find: " + '**Purpose**: Reports from the current run may still be updated (e.g., watchdog hang reports that get resolved). `sendAllReportsWithCompletion:` automatically excludes reports whose `run_id` matches th'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/run-id.md')
    assert 'Each process gets a unique run ID (UUID string), generated once during `kscrash_install()` in `KSCrashC.c`. It is written into the `"report"` section of every crash report under the `"run_id"` key. Th' in text, "expected to find: " + 'Each process gets a unique run ID (UUID string), generated once during `kscrash_install()` in `KSCrashC.c`. It is written into the `"report"` section of every crash report under the `"run_id"` key. Th'[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/run-id.md')
    assert '- `KSCrashReportStore.m` / `KSCrashReportStore.h`: Filtering logic and `sendReportWithID:` API' in text, "expected to find: " + '- `KSCrashReportStore.m` / `KSCrashReportStore.h`: Filtering logic and `sendReportWithID:` API'[:80]


def test_signal_24():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/threadcrumb.md')
    assert "Threadcrumb is a technique for encoding short messages into a thread's call stack so they can be recovered from crash reports via symbolication. Each allowed character (A-Z, a-z, 0-9, _) maps to a uni" in text, "expected to find: " + "Threadcrumb is a technique for encoding short messages into a thread's call stack so they can be recovered from crash reports via symbolication. Each allowed character (A-Z, a-z, 0-9, _) maps to a uni"[:80]


def test_signal_25():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/threadcrumb.md')
    assert "Threadcrumb should be used sparingly or not at all if not needed. Each instance consumes a thread — even though it's parked and idle, it's still a limited system resource. The best approach is to enco" in text, "expected to find: " + "Threadcrumb should be used sparingly or not at all if not needed. Each instance consumes a thread — even though it's parked and idle, it's still a limited system resource. The best approach is to enco"[:80]


def test_signal_26():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/threadcrumb.md')
    assert 'When a crash report is symbolicated server-side, the threadcrumb frames resolve to their character symbols. The backend can parse these symbol names to reconstruct the encoded message without any spec' in text, "expected to find: " + 'When a crash report is symbolicated server-side, the threadcrumb frames resolve to their character symbols. The backend can parse these symbol names to reconstruct the encoded message without any spec'[:80]


def test_signal_27():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

