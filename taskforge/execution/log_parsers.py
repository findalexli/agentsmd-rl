"""Small normalized test-log parser registry.

This is a taskforge-facing wrapper, not a wholesale replacement for
SWE-rebench-V2's parser library. Add parsers here only when imported tasks need
them, and keep return values normalized.
"""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from enum import Enum
from typing import Any, Callable


class TestStatus(str, Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    __test__ = False


Parser = Callable[[str], dict[str, str]]


def parse_log_pytest(log: str) -> dict[str, str]:
    """Parse common pytest verbose output."""

    statuses: dict[str, str] = {}
    pattern = re.compile(
        r"^(?P<name>\S+::\S.*?)\s+(?P<status>PASSED|FAILED|SKIPPED|ERROR)\b"
    )
    for raw_line in log.splitlines():
        line = _strip_ansi(raw_line).strip()
        match = pattern.match(line)
        if not match:
            continue
        status = match.group("status")
        statuses[match.group("name")] = (
            TestStatus.FAILED.value if status == "ERROR" else status
        )
    return statuses


def parse_log_gotest(log: str) -> dict[str, str]:
    """Parse `go test -v` output."""

    statuses: dict[str, str] = {}
    pattern = re.compile(r"^--- (PASS|FAIL|SKIP): (.+?) \(")
    for raw_line in log.splitlines():
        line = _strip_ansi(raw_line).strip()
        match = pattern.match(line)
        if not match:
            continue
        status, name = match.groups()
        statuses[name] = {
            "PASS": TestStatus.PASSED.value,
            "FAIL": TestStatus.FAILED.value,
            "SKIP": TestStatus.SKIPPED.value,
        }[status]
    return statuses


def parse_log_jest(log: str) -> dict[str, str]:
    """Parse common Jest/Vitest textual output."""

    statuses: dict[str, str] = {}
    for raw_line in log.splitlines():
        line = _strip_ansi(raw_line).strip()
        if line.startswith(("✓ ", "√ ")):
            statuses[line[2:].strip()] = TestStatus.PASSED.value
        elif line.startswith(("✕ ", "× ", "✖ ")):
            statuses[line[2:].strip()] = TestStatus.FAILED.value
        elif line.startswith(("○ skipped ", "○ ")):
            statuses[line[2:].replace("skipped ", "", 1).strip()] = (
                TestStatus.SKIPPED.value
            )
        elif line.startswith(("PASS ", "FAIL ")):
            status, name = line.split(maxsplit=1)
            statuses[name.strip()] = (
                TestStatus.PASSED.value if status == "PASS" else TestStatus.FAILED.value
            )
    return statuses


def parse_log_cargo(log: str) -> dict[str, str]:
    """Parse Rust `cargo test` output."""

    statuses: dict[str, str] = {}
    pattern = re.compile(r"^test (?P<name>.+?) \.\.\. (?P<status>ok|FAILED|ignored)$")
    for raw_line in log.splitlines():
        line = _strip_ansi(raw_line).strip()
        match = pattern.match(line)
        if not match:
            continue
        status = match.group("status")
        statuses[match.group("name")] = {
            "ok": TestStatus.PASSED.value,
            "FAILED": TestStatus.FAILED.value,
            "ignored": TestStatus.SKIPPED.value,
        }[status]
    return statuses


def parse_log_jq(log: str) -> dict[str, str]:
    """Parse jq-style `PASS: name` / `FAIL: name` output."""

    statuses: dict[str, str] = {}
    pattern = re.compile(r"^\s*(PASS|FAIL):\s(.+)$")
    for raw_line in log.splitlines():
        line = _strip_ansi(raw_line).strip()
        match = pattern.match(line)
        if not match:
            continue
        status, name = match.groups()
        statuses[name] = (
            TestStatus.PASSED.value if status == "PASS" else TestStatus.FAILED.value
        )
    return statuses


def parse_log_julia(log: str) -> dict[str, str]:
    """Parse Julia `Test Summary:` tables."""

    statuses: dict[str, str] = {}
    test_line_re = re.compile(r"^(\s*)(.+?)\s+\|(.+)$")
    in_summary = False
    has_fail_column = False
    has_error_column = False

    for raw_line in log.splitlines():
        line = _strip_ansi(raw_line).rstrip()
        if "Test Summary:" in line:
            in_summary = True
            header = line.split("|", 1)[1] if "|" in line else line
            has_fail_column = "Fail" in header
            has_error_column = "Error" in header
            continue
        if not in_summary:
            continue

        match = test_line_re.match(line)
        if not match:
            continue
        test_name = match.group(2).strip()
        columns_text = match.group(3)
        numeric_parts = [part for part in columns_text.split() if part.isdigit()]
        if len(numeric_parts) < 2:
            continue

        total = int(numeric_parts[-1])
        status = TestStatus.PASSED.value
        if len(numeric_parts) == 2:
            first_count = int(numeric_parts[0])
            leading_spaces = len(columns_text) - len(columns_text.lstrip())
            if leading_spaces >= 10 or first_count != total:
                status = TestStatus.FAILED.value
        elif len(numeric_parts) == 3:
            middle_count = int(numeric_parts[1])
            if middle_count > 0 and (has_fail_column or has_error_column):
                status = TestStatus.FAILED.value
        else:
            fail_count = int(numeric_parts[1])
            error_count = int(numeric_parts[2])
            if fail_count or error_count:
                status = TestStatus.FAILED.value

        statuses[test_name] = status
    return statuses


def parse_log_php_v1(log: str) -> dict[str, str]:
    """Parse Pest/PHPUnit symbol lines used by SWE-rebench PHP v1 rows."""

    statuses: dict[str, str] = {}
    cross_mark = chr(0x2A2F)

    def clean(name: str) -> str:
        name = name.rstrip()
        name = re.sub(r"\s{2,}\d+(?:\.\d+)?s\s*$", "", name)
        name = re.sub(r"\s+\d+(?:\.\d+)?s\s*$", "", name)
        return name.strip()

    pass_line_re = re.compile(r"^\s*(?:✓|✔)\s+(?P<name>.+?)\s{2,}\d+\.?\d*s\b.*$")
    pass_line_no_timing_re = re.compile(r"^\s*(?:✓|✔)\s+(?P<name>.+?)\s*$")
    fail_line_re = re.compile(
        rf"^\s*(?:{cross_mark}|x)\s+(?P<name>.+?)\s{{2,}}\d+\.?\d*s\b.*$",
        re.IGNORECASE,
    )
    fail_line_no_timing_re = re.compile(
        rf"^\s*(?:{cross_mark}|x)\s+(?P<name>.+?)\s*$", re.IGNORECASE
    )
    skipped_line_re = re.compile(r"^\s*-\s+(?P<name>.+?)\s{2,}\d+\.?\d*s\b.*$")
    skipped_line_no_timing_re = re.compile(r"^\s*-\s+(?P<name>.+?)\s*$")
    suite_fail_re = re.compile(r"^\s*FAIL(?:ED)?\s+(?P<name>\S.+)$", re.IGNORECASE)
    inline_skipped_marker = re.compile(r"\(skipped\)|\bSKIPPED\b", re.IGNORECASE)

    for raw_line in log.splitlines():
        line = _strip_ansi(raw_line).rstrip()
        if not line:
            continue
        stripped = line.strip()
        if stripped.startswith(("___", "---", "Tests:", "Duration:")):
            continue

        if match := suite_fail_re.match(line):
            name = clean(match.group("name"))
            if name:
                statuses[name] = TestStatus.FAILED.value
            continue

        matched = False
        for pattern, status in (
            (fail_line_re, TestStatus.FAILED.value),
            (fail_line_no_timing_re, TestStatus.FAILED.value),
            (skipped_line_re, TestStatus.SKIPPED.value),
            (skipped_line_no_timing_re, TestStatus.SKIPPED.value),
            (pass_line_re, TestStatus.PASSED.value),
            (pass_line_no_timing_re, TestStatus.PASSED.value),
        ):
            match = pattern.match(line)
            if not match:
                continue
            name = clean(match.group("name"))
            if name:
                if status == TestStatus.PASSED.value:
                    statuses.setdefault(name, status)
                else:
                    statuses[name] = status
            matched = True
            break
        if matched:
            continue

        if inline_skipped_marker.search(line):
            token = re.sub(rf"^\s*(?:✓|✔|{cross_mark}|x|-)\s+", "", line)
            name = clean(token)
            if name and name not in statuses:
                statuses[name] = TestStatus.SKIPPED.value
    return statuses


def parse_log_swift(log: str) -> dict[str, str]:
    """Parse Swift XCTest completion lines."""

    statuses: dict[str, str] = {}
    pattern = re.compile(
        r"^Test Case '([^']+)'\s+(passed|failed)\s+\([0-9.]+\s+seconds\)$"
    )
    for raw_line in log.splitlines():
        line = _strip_ansi(raw_line).strip()
        if match := pattern.match(line):
            statuses[match.group(1)] = (
                TestStatus.PASSED.value
                if match.group(2) == "passed"
                else TestStatus.FAILED.value
            )
    return statuses


def parse_log_cpp_v3(log: str) -> dict[str, str]:
    """Parse C++ runner output used by SWE-rebench `parse_log_cpp_v3` rows."""

    statuses: dict[str, str] = {}
    botan_re = re.compile(
        r"^(.*?)\s+ran\s+(\d+)\s+tests\s+in\s+[\d.]+\s+(?:msec|sec)\s+(.+)$",
        re.IGNORECASE,
    )
    line_re = re.compile(r"^(?:\[[0-9]+/[0-9]+\]\s*)?(.*?)\s*\.\.\.\s*(\w+)$")
    failed_re = re.compile(r"\bFAILED\b|\bFAIL\b|\bFailure\b", re.IGNORECASE)
    skipped_re = re.compile(r"\bSKIPPED\b", re.IGNORECASE)
    passed_re = re.compile(r"\bOK\b|\bPASSED\b", re.IGNORECASE)

    for raw_line in log.splitlines():
        line = _strip_ansi(raw_line).strip()
        if not line:
            continue

        if match := botan_re.match(line):
            name, count, tail = match.group(1).strip(), match.group(2), match.group(3)
            key = f"{name} ran {count} tests {tail.strip()}"
            statuses[key] = (
                TestStatus.FAILED.value
                if failed_re.search(tail)
                else TestStatus.PASSED.value
            )
            continue

        if match := line_re.match(line):
            name = match.group(1).strip()
            status_token = match.group(2)
            if skipped_re.search(status_token) or skipped_re.search(line):
                statuses[name] = TestStatus.SKIPPED.value
            elif failed_re.search(status_token) or failed_re.search(line):
                statuses[name] = TestStatus.FAILED.value
            elif passed_re.search(status_token) or passed_re.search(line):
                statuses[name] = TestStatus.PASSED.value
            else:
                statuses[name] = TestStatus.FAILED.value
            continue

        if skipped_re.search(line):
            statuses[line] = TestStatus.SKIPPED.value
        elif failed_re.search(line):
            statuses[line] = TestStatus.FAILED.value
        elif passed_re.search(line):
            statuses[line] = TestStatus.PASSED.value

    return statuses


def parse_java_mvn(log: str) -> dict[str, str]:
    """Parse Maven Surefire text output."""

    statuses: dict[str, str] = {}
    current_test_name = "---NO TEST NAME FOUND YET---"
    any_failure = False
    any_success = False
    summary_re = re.compile(
        r"Tests run:\s*(?P<run>\d+),\s*Failures:\s*(?P<failures>\d+),\s*"
        r"Errors:\s*(?P<errors>\d+),\s*Skipped:\s*(?P<skipped>\d+)"
        r"(?:,[^-]*-\s+in\s+(?P<class>\S+))?"
    )
    failure_re = re.compile(
        r"^(?P<method>[^\s(]+)\((?P<class>[^)]+)\)\s+.*<<<\s+"
        r"(?:FAILURE|ERROR)!"
    )
    explicit_test_re = re.compile(r"^.*-Dtest=(\S+).*$")
    build_result_re = re.compile(r"^.*BUILD (SUCCESS|FAILURE)$")

    for raw_line in log.splitlines():
        line = _strip_ansi(raw_line).strip()
        if match := explicit_test_re.match(line):
            current_test_name = match.group(1)
            continue
        if match := build_result_re.match(line):
            if match.group(1) == "SUCCESS":
                statuses[current_test_name] = TestStatus.PASSED.value
                any_success = True
            else:
                statuses[current_test_name] = TestStatus.FAILED.value
                any_failure = True
            continue
        if match := summary_re.search(line):
            tests_run = int(match.group("run"))
            failures = int(match.group("failures"))
            errors = int(match.group("errors"))
            skipped = int(match.group("skipped"))
            class_name = match.group("class")
            status = TestStatus.PASSED.value
            if failures or errors:
                status = TestStatus.FAILED.value
                any_failure = True
            elif skipped == tests_run:
                status = TestStatus.SKIPPED.value
            else:
                any_success = True
            if class_name:
                statuses[class_name] = status
            continue
        if match := failure_re.match(line):
            class_name = match.group("class")
            method_name = match.group("method")
            statuses[class_name] = TestStatus.FAILED.value
            statuses[f"{class_name}.{method_name}"] = TestStatus.FAILED.value
            any_failure = True

    if any_failure:
        statuses["---NO TEST NAME FOUND YET---"] = TestStatus.FAILED.value
    elif any_success:
        statuses["---NO TEST NAME FOUND YET---"] = TestStatus.PASSED.value
    return statuses


def parse_java_mvn_v2(log: str) -> dict[str, str]:
    """Parse Maven module status lines such as `module ... SUCCESS`."""

    statuses: dict[str, str] = {}
    line_re = re.compile(
        r"^\[INFO\]\s+(?P<name>.+?)\s+\.\.+\s+"
        r"(?P<status>SUCCESS|FAILURE|SKIPPED)(?:\s|\[|$)"
    )
    summary_re = re.compile(
        r"Tests run:\s*(\d+),\s*Failures:\s*(\d+),\s*Errors:\s*(\d+),\s*Skipped:\s*(\d+)"
    )

    for raw_line in log.splitlines():
        line = _strip_ansi(raw_line).strip()
        match = line_re.match(line)
        if match:
            status_word = match.group("status")
            statuses[match.group("name")] = {
                "SUCCESS": TestStatus.PASSED.value,
                "FAILURE": TestStatus.FAILED.value,
                "SKIPPED": TestStatus.SKIPPED.value,
            }[status_word]
            continue

        summary_match = summary_re.search(line)
        if summary_match:
            tests_run, failures, errors, skipped = map(int, summary_match.groups())
            status = TestStatus.PASSED.value
            if failures or errors:
                status = TestStatus.FAILED.value
            elif skipped == tests_run:
                status = TestStatus.SKIPPED.value
            statuses.setdefault("__suite__", status)

    return statuses


def parse_log_gradle_custom(log: str) -> dict[str, str]:
    """Parse plain Gradle lines emitted as `<test name> PASSED|FAILED`."""

    statuses: dict[str, str] = {}
    pattern = re.compile(r"^([^>].+?)\s+(PASSED|FAILED)(?:\s+\(\d+(?:\.\d+)?s\))?$")
    for raw_line in log.splitlines():
        line = _strip_ansi(raw_line).strip()
        if match := pattern.match(line):
            test_name, status = match.groups()
            statuses[test_name] = (
                TestStatus.PASSED.value
                if status == "PASSED"
                else TestStatus.FAILED.value
            )
    return statuses


def parse_log_gradlew_v1(log: str) -> dict[str, str]:
    """Parse Gradle JUnit XML cat output."""

    statuses: dict[str, str] = {}
    for root in _iter_xml_roots(log):
        for case in root.iter("testcase"):
            name = case.attrib.get("name", "").strip()
            classname = case.attrib.get("classname", "").strip()
            if not name:
                continue
            full_name = f"{name} ({classname})" if classname else name
            if case.find("skipped") is not None:
                statuses[full_name] = TestStatus.SKIPPED.value
            elif case.find("failure") is not None or case.find("error") is not None:
                statuses[full_name] = TestStatus.FAILED.value
            else:
                statuses[full_name] = TestStatus.PASSED.value
    return statuses


def parse_log_junit(log: str) -> dict[str, str]:
    """Parse SBT/JUnit XML output as `classname name` keys."""

    return _parse_junit_testcases_from_text(log, joiner=" ")


def parse_log_csharp(log: str) -> dict[str, str]:
    """Parse common xUnit.net textual output."""

    statuses: dict[str, str] = {}
    passed_re = re.compile(r"^\s+Passed\s+(.+?)\s+\[.+?\]$")
    failed_re = re.compile(r"^\s+Failed\s+(.+?)\s+\[.+?\]$")
    skipped_re = re.compile(r"^\s+Skipped\s+(.+?)(?:\s+\[.+?\])?$")
    xunit_fail_re = re.compile(r"^\[xUnit\.net\s+[\d:.]+\]\s+(.+?)\s+\[FAIL\]$")

    for raw_line in log.splitlines():
        line = _strip_ansi(raw_line).rstrip()
        if match := xunit_fail_re.match(line):
            statuses[match.group(1)] = TestStatus.FAILED.value
        elif match := failed_re.match(line):
            statuses[match.group(1)] = TestStatus.FAILED.value
        elif match := skipped_re.match(line):
            statuses[match.group(1)] = TestStatus.SKIPPED.value
        elif match := passed_re.match(line):
            statuses.setdefault(match.group(1), TestStatus.PASSED.value)

    return statuses


def parse_log_dart(log: str) -> dict[str, str]:
    """Parse Dart JSON test protocol events."""

    statuses: dict[str, str] = {}
    test_id_to_name: dict[int, str] = {}

    for event in _iter_dart_protocol_events(log):
        event_type = event.get("type")
        if event_type == "testStart":
            test_info = event.get("test")
            if not isinstance(test_info, dict):
                continue
            test_id = test_info.get("id")
            test_name = test_info.get("name")
            if isinstance(test_id, int) and isinstance(test_name, str):
                if not test_name.startswith("loading "):
                    test_id_to_name[test_id] = test_name
        elif event_type == "testDone":
            test_id = event.get("testID")
            if not isinstance(test_id, int) or event.get("hidden", False):
                continue
            test_name = test_id_to_name.get(test_id)
            status = _dart_done_status(event)
            if test_name and status:
                statuses[test_name] = status

    return statuses


def parse_log_elixir(log: str) -> dict[str, str]:
    """Parse ExUnit output."""

    statuses: dict[str, str] = {}
    skipped_re = re.compile(r"^\*\s+test\s+(.*?)\s+\(skipped\)\s+\[L#\d+\]$")
    passed_timed_re = re.compile(
        r"^\*\s+test\s+(.*?)\s+\([0-9]+(?:\.[0-9]+)?ms\)\s+\[L#\d+\]$"
    )
    passed_basic_re = re.compile(r"^\*\s+test\s+(.*?)\s+\[L#\d+\]$")
    failure_header_re = re.compile(r"^\d+\)\s+test\s+(.*?)\s+\([^)]+\)$")

    for raw_line in log.splitlines():
        line = _strip_ansi(raw_line).strip()
        if match := skipped_re.match(line):
            statuses[match.group(1)] = TestStatus.SKIPPED.value
        elif match := failure_header_re.match(line):
            statuses[match.group(1)] = TestStatus.FAILED.value
        elif match := passed_timed_re.match(line):
            statuses.setdefault(match.group(1), TestStatus.PASSED.value)
        elif match := passed_basic_re.match(line):
            statuses.setdefault(match.group(1), TestStatus.PASSED.value)

    return statuses


def parse_log_phpunit(log: str) -> dict[str, str]:
    """Parse PHPUnit `--testdox` output."""

    statuses: dict[str, str] = {}
    suite: str | None = None
    suite_re = re.compile(r"^(.+?)\s+\(.+\)$")
    test_re = re.compile(r"^\s*([✔✘↩])\s*(.*?)\s*$")

    for raw_line in log.splitlines():
        line = _strip_ansi(raw_line).rstrip()
        if match := suite_re.match(line.strip()):
            suite = match.group(1).strip() or None
            continue
        if match := test_re.match(line):
            symbol, raw_name = match.groups()
            name = _strip_timing_suffix(raw_name)
            if not name:
                continue
            full_name = f"{suite or 'None'} > {name}"
            statuses[full_name] = {
                "✔": TestStatus.PASSED.value,
                "✘": TestStatus.FAILED.value,
                "↩": TestStatus.SKIPPED.value,
            }[symbol]

    return statuses


def parse_log_js(log: str) -> dict[str, str]:
    """Parse Mocha/Ava symbol output used by SWE-rebench `parse_log_js` rows."""

    statuses: dict[str, str] = {}
    passed_re = re.compile(r"^\s*✔\s+(.*?)$")
    failed_symbol_re = re.compile(r"^\s*[✖✘]\s+(.*?)$")
    skipped_re = re.compile(r"^\s*-\s+(.*?)$")
    failed_re = re.compile(r"^\s*\[W\]\s*\d+\)\s+(.*?)$")
    failed_header_re = re.compile(r"^\s*\d+\)\s+(.*?):$")

    for raw_line in log.splitlines():
        line = _strip_ansi(raw_line).strip()
        if not line:
            continue
        if match := skipped_re.match(line):
            if name := _strip_js_duration_suffix(match.group(1)):
                statuses[name] = TestStatus.SKIPPED.value
            continue
        if match := failed_header_re.match(line):
            if name := _strip_js_duration_suffix(match.group(1)):
                statuses[name] = TestStatus.FAILED.value
            continue
        if match := failed_re.match(line):
            if name := _strip_js_duration_suffix(match.group(1).rstrip()):
                statuses[name] = TestStatus.FAILED.value
            continue
        if match := failed_symbol_re.match(line):
            if name := _strip_js_duration_suffix(match.group(1)):
                statuses[name] = TestStatus.FAILED.value
            continue
        if match := passed_re.match(line):
            if name := _strip_js_duration_suffix(match.group(1)):
                statuses.setdefault(name, TestStatus.PASSED.value)

    return statuses


def parse_log_js_2(log: str) -> dict[str, str]:
    """Parse Mocha spec output used by SWE-rebench `parse_log_js_2` rows."""

    statuses: dict[str, str] = {}
    passed_re = re.compile(r"^\s*✔\s+(.*?)$")
    failed_re = re.compile(r"^\s*\d+\)\s+(.*?)$")
    skipped_re = re.compile(r"^\s*-\s+(.*?)$")
    lines = [_strip_ansi(raw_line).rstrip() for raw_line in log.splitlines()]
    for index, raw_line in enumerate(lines):
        next_line = ""
        for candidate in lines[index + 1 :]:
            if candidate.strip():
                next_line = candidate
                break
        line = _strip_ansi(raw_line).strip()
        if not line:
            continue
        if match := skipped_re.match(line):
            if name := _strip_js_duration_suffix(match.group(1)):
                statuses[name] = TestStatus.SKIPPED.value
            continue
        if match := failed_re.match(line):
            summary_name = next_line.strip().removesuffix(":")
            raw_name = (
                summary_name
                if next_line.startswith("     ") and summary_name
                else match.group(1)
            )
            if name := _strip_js_duration_suffix(raw_name):
                statuses[name] = TestStatus.FAILED.value
            continue
        if match := passed_re.match(line):
            if name := _strip_js_duration_suffix(match.group(1)):
                statuses.setdefault(name, TestStatus.PASSED.value)

    return statuses


def parse_log_js_3(log: str) -> dict[str, str]:
    """Parse TAP output used by SWE-rebench `parse_log_js_3` rows."""

    statuses: dict[str, str] = {}
    stack: list[str] = []
    tap_line_re = re.compile(
        r"^(?P<status>not ok|ok)\s+\d+\s+-\s+(?P<name>.*?)(?:\s+#.*)?$"
    )

    for raw_line in log.splitlines():
        line = _strip_ansi(raw_line).strip()
        if not line:
            continue
        if line.replace("}", "") == "":
            for _ in range(line.count("}")):
                if stack:
                    stack.pop()
            continue

        opens_context = line.endswith("{")
        if opens_context:
            line = line[:-1].rstrip()

        match = tap_line_re.match(line)
        if not match:
            continue

        raw_name = match.group("name")
        name = _strip_js_duration_suffix(re.split(r"\s+#", raw_name, maxsplit=1)[0])
        if not name:
            continue
        full_name = " :: ".join((*stack, name)) if stack else name
        skip_marker = any(
            token in raw_name.lower() for token in ("# skip", "# skipped", "# todo")
        )
        if skip_marker:
            statuses[full_name] = TestStatus.SKIPPED.value
        else:
            status_value = (
                TestStatus.PASSED.value
                if match.group("status") == "ok"
                else TestStatus.FAILED.value
            )
            if status_value == TestStatus.FAILED.value or full_name not in statuses:
                statuses[full_name] = status_value

        if opens_context:
            stack.append(name)

    return statuses


def parse_log_js_4(log: str) -> dict[str, str]:
    """Parse simple symbol-prefixed JavaScript runner output."""

    statuses: dict[str, str] = {}
    pass_symbols = ("\u2714", "\u2713")
    fail_symbols = ("\u2718", "\u2716", "\u2715", "\u00d7")
    skip_symbols = ("\u25cb", "\u25cc", "\u25e6", "\u26aa")
    skip_markers = ("(skipped)", "[skip]", "[skipped]", "[pending]", "[todo]")

    for raw_line in log.splitlines():
        line = _strip_ansi(raw_line).strip()
        if not line:
            continue

        symbol = line[0]
        payload = line[1:].strip() if len(line) > 1 else ""
        if symbol in pass_symbols:
            if name := _normalize_js_test_name(payload):
                statuses.setdefault(name, TestStatus.PASSED.value)
        elif symbol in fail_symbols:
            if name := _normalize_js_test_name(payload):
                statuses[name] = TestStatus.FAILED.value
        elif symbol in skip_symbols:
            if name := _normalize_js_test_name(payload):
                statuses[name] = TestStatus.SKIPPED.value
        elif any(marker in line.lower() for marker in skip_markers):
            candidate = line
            for marker in skip_markers:
                candidate = candidate.replace(marker, "")
            if name := _normalize_js_test_name(candidate):
                statuses[name] = TestStatus.SKIPPED.value

    return statuses


def parse_log_lein(log: str) -> dict[str, str]:
    """Parse Leiningen test namespace output."""

    statuses: dict[str, str] = {}
    current_namespace: str | None = None
    lein_re = re.compile(r"^lein test (.+)$")

    for raw_line in log.splitlines():
        line = _strip_ansi(raw_line).strip()
        if not line:
            continue
        if match := lein_re.match(line):
            payload = match.group(1).strip()
            tokens = payload.split()
            if tokens and tokens[0] == ":only":
                target = " ".join(tokens[1:]).strip()
                current_namespace = target.split("/", 1)[0].strip() or None
                if current_namespace:
                    statuses.setdefault(current_namespace, TestStatus.PASSED.value)
            else:
                for token in tokens:
                    current_namespace = token.strip() or None
                    if current_namespace:
                        statuses.setdefault(current_namespace, TestStatus.PASSED.value)
            continue
        if line.startswith(("FAIL in", "ERROR in")) and current_namespace:
            statuses[current_namespace] = TestStatus.FAILED.value

    return statuses


def parse_log_junit_xml(log: str) -> dict[str, str]:
    """Parse JUnit XML text if a runner prints or cats XML reports."""

    statuses: dict[str, str] = {}
    xml_chunks = re.findall(r"(<testsuite[\s\S]*?</testsuite>)", log)
    for chunk in xml_chunks or [log]:
        try:
            root = ET.fromstring(chunk)
        except ET.ParseError:
            continue
        for case in root.iter("testcase"):
            name = case.attrib.get("name", "").strip()
            classname = case.attrib.get("classname", "").strip()
            full_name = f"{classname}.{name}".strip(".") if classname else name
            if not full_name:
                continue
            if case.find("skipped") is not None:
                statuses[full_name] = TestStatus.SKIPPED.value
            elif case.find("failure") is not None or case.find("error") is not None:
                statuses[full_name] = TestStatus.FAILED.value
            else:
                statuses[full_name] = TestStatus.PASSED.value
    return statuses


NAME_TO_PARSER: dict[str, Parser] = {
    "pytest": parse_log_pytest,
    "parse_log_pytest": parse_log_pytest,
    "go": parse_log_gotest,
    "gotest": parse_log_gotest,
    "parse_log_gotest": parse_log_gotest,
    "jest": parse_log_jest,
    "parse_log_jest": parse_log_jest,
    "vitest": parse_log_jest,
    "parse_log_vitest": parse_log_jest,
    "cargo": parse_log_cargo,
    "parse_log_cargo": parse_log_cargo,
    "jq": parse_log_jq,
    "parse_log_jq": parse_log_jq,
    "parse_log_julia": parse_log_julia,
    "junit": parse_log_junit_xml,
    "maven": parse_java_mvn,
    "gradle": parse_log_junit_xml,
    "parse_java_mvn": parse_java_mvn,
    "parse_java_mvn_v2": parse_java_mvn_v2,
    "parse_log_maven": parse_java_mvn,
    "parse_log_gradle_custom": parse_log_gradle_custom,
    "parse_log_gradlew_v1": parse_log_gradlew_v1,
    "parse_log_junit": parse_log_junit,
    "parse_log_csharp": parse_log_csharp,
    "parse_log_cpp_v3": parse_log_cpp_v3,
    "parse_log_dart": parse_log_dart,
    "parse_log_elixir": parse_log_elixir,
    "parse_log_php_v1": parse_log_php_v1,
    "parse_log_phpunit": parse_log_phpunit,
    "parse_log_swift": parse_log_swift,
    "parse_log_js": parse_log_js,
    "parse_log_js_2": parse_log_js_2,
    "parse_log_js_3": parse_log_js_3,
    "parse_log_js_4": parse_log_js_4,
    "parse_log_lein": parse_log_lein,
}


def get_parser(name: str) -> Parser:
    """Return a parser by upstream or taskforge parser name."""

    key = name.strip()
    parser = NAME_TO_PARSER.get(key)
    if parser is None:
        raise KeyError(f"unknown log parser: {name}")
    return parser


def parse_with_parser(name: str, log: str) -> dict[str, str]:
    return get_parser(name)(log)


def _strip_ansi(text: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


def _iter_xml_roots(log: str) -> list[ET.Element]:
    roots: list[ET.Element] = []
    xml_blocks = re.findall(
        r"(<\?xml[\s\S]*?</testsuite>|<testsuite[\s\S]*?</testsuite>|<testsuites[\s\S]*?</testsuites>)",
        log,
    )
    for chunk in xml_blocks or [log]:
        try:
            roots.append(ET.fromstring(chunk))
        except ET.ParseError:
            continue
    return roots


def _parse_junit_testcases_from_text(log: str, *, joiner: str) -> dict[str, str]:
    statuses: dict[str, str] = {}
    open_tag_re = re.compile(r"<testcase\b([^>]*)>", re.DOTALL)
    attr_re = re.compile(r'(\w+)="([^"]*)"')

    pos = 0
    while match := open_tag_re.search(log, pos):
        raw_attrs = match.group(1) or ""
        attrs = dict(attr_re.findall(raw_attrs))
        name = attrs.get("name", "").strip()
        classname = attrs.get("classname", "").strip()
        if not name:
            pos = match.end()
            continue

        is_self_closing = raw_attrs.strip().endswith("/")
        content = ""
        if is_self_closing:
            pos = match.end()
        else:
            close_pos = log.find("</testcase>", match.end())
            if close_pos == -1:
                content = log[match.end() : match.end() + 4096]
                pos = match.end()
            else:
                content = log[match.end() : close_pos]
                pos = close_pos + len("</testcase>")

        full_name = f"{classname}{joiner}{name}".strip() if classname else name
        if "<skipped" in content:
            statuses[full_name] = TestStatus.SKIPPED.value
        elif "<failure" in content or "<error" in content:
            statuses[full_name] = TestStatus.FAILED.value
        else:
            statuses[full_name] = TestStatus.PASSED.value
    return statuses


_JS_DURATION_SUFFIX_RE = re.compile(
    r"\s*(?:\(\s*)?\d+(?:\.\d+)?\s*(?:ms|s)\s*(?:\))?\s*$",
    re.IGNORECASE,
)


def _normalize_js_test_name(payload: str) -> str:
    payload = payload.strip()
    if payload.startswith("[") and "]:" in payload:
        payload = payload.split("]:", 1)[1].strip()
    if payload.startswith(":"):
        payload = payload[1:].strip()
    return _strip_js_duration_suffix(payload)


def _strip_js_duration_suffix(name: str) -> str:
    return _JS_DURATION_SUFFIX_RE.sub("", name.strip()).strip()


_TIMING_SUFFIX_RES = (
    re.compile(r"\s*\[\s*\d+(?:\.\d+)?\s*(?:ms|s)\s*\]\s*$", re.IGNORECASE),
    re.compile(r"\s*\(\s*\d+(?:\.\d+)?\s*(?:ms|s)\s*\)\s*$", re.IGNORECASE),
)


def _strip_timing_suffix(name: str) -> str:
    name = name.strip()
    for pattern in _TIMING_SUFFIX_RES:
        name = pattern.sub("", name)
    return name.strip()


def _iter_dart_protocol_events(log: str) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for raw_line in log.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        try:
            decoded = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(decoded, dict):
            events.append(decoded)
        elif isinstance(decoded, list):
            events.extend(item for item in decoded if isinstance(item, dict))
    return events


def _dart_done_status(event: dict[str, Any]) -> str | None:
    if event.get("skipped", False):
        return TestStatus.SKIPPED.value
    result = event.get("result")
    if result == "success":
        return TestStatus.PASSED.value
    if result in {"failure", "error"}:
        return TestStatus.FAILED.value
    return None
