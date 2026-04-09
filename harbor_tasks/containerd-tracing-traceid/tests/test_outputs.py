#!/usr/bin/env python3
"""Test outputs for containerd tracing trace ID injection feature."""

import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path("/workspace/containerd")
TRACING_PKG = REPO / "pkg" / "tracing"


def run_go_test(test_pattern=None, verbose=False):
    """Run Go tests in the tracing package."""
    cmd = ["go", "test", "-v"]
    if test_pattern:
        cmd.extend(["-run", test_pattern])
    cmd.append(".")

    result = subprocess.run(
        cmd,
        cwd=TRACING_PKG,
        capture_output=True,
        text=True,
        timeout=60
    )

    if verbose:
        print(f"STDOUT:\n{result.stdout}")
        print(f"STDERR:\n{result.stderr}")

    return result


def test_log_compiles():
    """F2P: Verify the tracing package compiles successfully."""
    result = subprocess.run(
        ["go", "build", "."],
        cwd=TRACING_PKG,
        capture_output=True,
        text=True,
        timeout=60
    )

    assert result.returncode == 0, f"Compilation failed:\n{result.stderr}"


def test_trace_id_injection_enabled():
    """F2P: Verify trace ID is injected when option is enabled."""
    result = run_go_test("TestLogrusHookTraceID/TraceIDInjected", verbose=True)

    assert result.returncode == 0, f"Test failed:\n{result.stdout}\n{result.stderr}"
    assert "PASS: TestLogrusHookTraceID/TraceIDInjected" in result.stdout or \
           "PASS\n" in result.stdout, "Test did not pass"


def test_trace_id_not_injected_when_disabled():
    """F2P: Verify trace ID is NOT injected when option is disabled."""
    result = run_go_test("TestLogrusHookTraceID/TraceIDNotInjected_OptionDisabled", verbose=True)

    assert result.returncode == 0, f"Test failed:\n{result.stdout}\n{result.stderr}"
    assert "PASS: TestLogrusHookTraceID/TraceIDNotInjected_OptionDisabled" in result.stdout or \
           "PASS\n" in result.stdout, "Test did not pass"


def test_trace_id_not_injected_without_span():
    """F2P: Verify trace ID is NOT injected when no span context exists."""
    result = run_go_test("TestLogrusHookTraceID/TraceIDNotInjected_NoSpan", verbose=True)

    assert result.returncode == 0, f"Test failed:\n{result.stdout}\n{result.stderr}"
    assert "PASS: TestLogrusHookTraceID/TraceIDNotInjected_NoSpan" in result.stdout or \
           "PASS\n" in result.stdout, "Test did not pass"


def test_config_has_log_trace_id_field():
    """F2P: Verify Debug config struct has LogTraceID field."""
    config_file = REPO / "cmd" / "containerd" / "server" / "config" / "config.go"

    assert config_file.exists(), f"Config file not found: {config_file}"

    content = config_file.read_text()

    # Check for LogTraceID field in Debug struct
    assert "LogTraceID" in content, "Debug config struct missing LogTraceID field"
    assert "log_trace_id" in content, "Debug config struct missing log_trace_id toml tag"


def test_main_registers_hook_with_config():
    """F2P: Verify main.go registers the tracing hook with config option."""
    main_file = REPO / "cmd" / "containerd" / "command" / "main.go"

    assert main_file.exists(), f"Main file not found: {main_file}"

    content = main_file.read_text()

    # Check that hook registration was moved from otlp.go to main.go
    assert "NewLogrusHook" in content, "main.go should call NewLogrusHook"
    assert "WithTraceIDField" in content, "main.go should use WithTraceIDField option"
    assert "config.Debug.LogTraceID" in content, "main.go should pass config.Debug.LogTraceID to WithTraceIDField"
    assert "logrus.StandardLogger().AddHook" in content, "main.go should register the hook"


def test_hook_has_enable_trace_id_field():
    """P2P: Verify LogrusHook struct has enableTraceIDField field."""
    log_file = TRACING_PKG / "log.go"

    assert log_file.exists(), f"log.go not found: {log_file}"

    content = log_file.read_text()

    # Check for the struct field
    assert "enableTraceIDField" in content, "LogrusHook struct missing enableTraceIDField"


def test_hook_opt_type_exists():
    """P2P: Verify HookOpt type is defined."""
    log_file = TRACING_PKG / "log.go"

    content = log_file.read_text()

    assert "type HookOpt" in content, "HookOpt type not found"
    assert "func(*LogrusHook)" in content, "HookOpt should be a function type taking *LogrusHook"


def test_with_trace_id_field_option_exists():
    """P2P: Verify WithTraceIDField function exists."""
    log_file = TRACING_PKG / "log.go"

    content = log_file.read_text()

    assert "func WithTraceIDField" in content, "WithTraceIDField function not found"


def test_new_logrus_hook_accepts_opts():
    """P2P: Verify NewLogrusHook accepts variadic HookOpt arguments."""
    log_file = TRACING_PKG / "log.go"

    content = log_file.read_text()

    assert "func NewLogrusHook(opts ...HookOpt)" in content or \
           "opts ...HookOpt" in content, "NewLogrusHook should accept variadic HookOpt arguments"


def test_fire_method_checks_span_context():
    """P2P: Verify Fire method properly checks span context validity."""
    log_file = TRACING_PKG / "log.go"

    content = log_file.read_text()

    # Should check for valid span context
    assert "span.SpanContext().IsValid()" in content, "Fire should check if span context is valid"
    assert "span.IsRecording()" in content, "Fire should check if span is recording"


def test_otlp_no_longer_registers_hook_in_init():
    """F2P: Verify otlp.go no longer registers hook in init()."""
    otlp_file = REPO / "pkg" / "tracing" / "plugin" / "otlp.go"

    assert otlp_file.exists(), f"otlp.go not found: {otlp_file}"

    content = otlp_file.read_text()

    # The init() function should NOT have the hook registration anymore
    lines = content.split("\n")
    in_init = False
    init_has_hook_registration = False
    brace_count = 0

    for line in lines:
        if "func init()" in line:
            in_init = True
            brace_count = 0

        if in_init:
            if "{" in line:
                brace_count += line.count("{")
            if "}" in line:
                brace_count -= line.count("}")

            if "logrus.StandardLogger().AddHook" in line or \
               ("AddHook" in line and "tracing.NewLogrusHook" in line):
                init_has_hook_registration = True

            if brace_count == 0 and "{" in line:
                in_init = False

    assert not init_has_hook_registration, "otlp.go init() should NOT register the logrus hook"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
