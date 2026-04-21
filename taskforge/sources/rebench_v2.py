"""SWE-rebench-V2 source adapter.

This module imports SWE-rebench-style task rows into taskforge's neutral
CandidateTask model and can render a native taskforge task directory. It is a
compatibility seam, not a replacement evaluation harness.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from taskforge.execution.docker_templates import select_runtime_template
from taskforge.sources.models import (
    CandidateTask,
    InstallConfig,
    SourceEvidence,
    SourceKind,
    TestEvidence,
)


def load_records(path: str | Path) -> list[dict[str, Any]]:
    """Load SWE-rebench-style rows from JSON or JSONL."""

    source_path = Path(path)
    text = source_path.read_text(encoding="utf-8")
    if source_path.suffix == ".jsonl":
        return [json.loads(line) for line in text.splitlines() if line.strip()]
    data = json.loads(text)
    if isinstance(data, dict):
        return [data]
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    raise ValueError(f"expected JSON object, list, or JSONL rows in {source_path}")


def load_candidate_tasks(path: str | Path) -> list[CandidateTask]:
    return [candidate_from_record(record) for record in load_records(path)]


def candidate_from_record(record: dict[str, Any]) -> CandidateTask:
    """Normalize one SWE-rebench-V2 row."""

    install_raw = record.get("install_config") or {}
    install_config = InstallConfig(
        install=install_raw.get("install", []),
        test_cmd=install_raw.get("test_cmd", []),
        log_parser=install_raw.get("log_parser", ""),
        base_image_name=install_raw.get("base_image_name", ""),
        docker_specs=install_raw.get("docker_specs"),
    )

    instance_id = str(record.get("instance_id") or "").strip()
    if not instance_id:
        raise ValueError("SWE-rebench row missing instance_id")

    return CandidateTask(
        instance_id=instance_id,
        repo=str(record["repo"]),
        base_commit=str(record.get("base_commit") or ""),
        problem_statement=str(
            record.get("problem_statement") or record.get("pr_description") or ""
        ),
        source=SourceEvidence(
            kind=SourceKind.REBENCH_V2,
            upstream_id=instance_id,
            pr_number=_extract_pr_number(record),
            merge_commit=str(record.get("merge_commit") or ""),
            language=str(record.get("language") or ""),
            image_name=str(record.get("image_name") or ""),
            metadata={
                "created_at": record.get("created_at", ""),
                "interface": record.get("interface", ""),
                "meta": record.get("meta", {}),
                "original_install_config": install_raw,
            },
        ),
        tests=TestEvidence(
            patch=str(record.get("patch") or ""),
            test_patch=str(record.get("test_patch") or ""),
            fail_to_pass=list(record.get("FAIL_TO_PASS") or []),
            pass_to_pass=list(record.get("PASS_TO_PASS") or []),
            install_config=install_config,
        ),
    )


def render_task(
    candidate: CandidateTask, output_root: str | Path, *, overwrite: bool = False
) -> Path:
    """Render a native taskforge task directory from a normalized candidate."""

    task_dir = Path(output_root) / candidate.task_slug
    if task_dir.exists() and not overwrite:
        raise FileExistsError(f"task already exists: {task_dir}")

    (task_dir / "environment").mkdir(parents=True, exist_ok=True)
    (task_dir / "tests").mkdir(parents=True, exist_ok=True)
    (task_dir / "solution").mkdir(parents=True, exist_ok=True)

    (task_dir / "eval_manifest.yaml").write_text(
        candidate.to_manifest().to_yaml(), encoding="utf-8"
    )
    (task_dir / "instruction.md").write_text(
        _render_instruction(candidate), encoding="utf-8"
    )
    (task_dir / "task.toml").write_text(_render_task_toml(candidate), encoding="utf-8")
    (task_dir / "environment" / "Dockerfile").write_text(
        _render_dockerfile(candidate), encoding="utf-8"
    )
    (task_dir / "solution" / "solve.sh").write_text(
        _render_solve_sh(candidate), encoding="utf-8"
    )
    (task_dir / "tests" / "test.sh").write_text(
        _render_test_sh(candidate), encoding="utf-8"
    )
    (task_dir / "tests" / "score_rebench_log.py").write_text(
        _render_score_py(), encoding="utf-8"
    )
    (task_dir / "tests" / "rebench_metadata.json").write_text(
        json.dumps(_metadata_for_tests(candidate), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    return task_dir


def _extract_pr_number(record: dict[str, Any]) -> int:
    for key in ("pr", "pr_number", "pull_number", "number"):
        value = record.get(key)
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.isdigit():
            return int(value)
    instance = str(record.get("instance_id", ""))
    match = re.search(r"(?:pr_|-)(\d+)(?:[_.-]|$)", instance)
    return int(match.group(1)) if match else 0


def _render_instruction(candidate: CandidateTask) -> str:
    title = candidate.instance_id.replace("_", " ").replace("-", " ").strip()
    return f"""# {title}

## Problem

{candidate.problem_statement.strip()}

## Source

- Repo: `{candidate.repo}`
- Base commit: `{candidate.base_commit}`
- Upstream source: `{candidate.source.kind.value}`
- Upstream id: `{candidate.source.upstream_id}`

## Expected Outcome

Modify the repository so the imported fail-to-pass tests pass while preserving
the imported pass-to-pass tests.
"""


def _render_task_toml(candidate: CandidateTask) -> str:
    tags = [candidate.repo_name, candidate.source.kind.value]
    if candidate.source.language:
        tags.append(candidate.source.language)
    tags_toml = ", ".join(json.dumps(tag) for tag in tags)
    return f"""version = "1.0"

[metadata]
author_name = "Taskforge Importer"
author_email = "noreply@example.com"
difficulty = "medium"
category = "bugfix"
tags = [{tags_toml}]
expert_time_estimate_min = 15.0
junior_time_estimate_min = 45.0

[verifier]
env = {{ LLM_JUDGE = "${{LLM_JUDGE:-0}}" }}
timeout_sec = 300.0

[agent]
timeout_sec = 1800.0

[environment]
build_timeout_sec = 1200.0
cpus = 2
memory_mb = 4096
storage_mb = 10240
allow_internet = true
"""


def _render_dockerfile(candidate: CandidateTask) -> str:
    runtime = select_runtime_template(
        candidate.source.language,
        candidate.tests.install_config.base_image_name,
    )
    packages = [
        "git",
        "curl",
        "ca-certificates",
        "build-essential",
        *runtime.setup_packages,
    ]
    apt_install = " ".join(dict.fromkeys(packages))
    setup_lines = _render_runtime_setup(runtime.setup_commands)
    clone_command = _render_clone_command(candidate)
    install_lines = _render_install_block(candidate)

    return f"""FROM {runtime.image}

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \\
    apt-get install -y --no-install-recommends {apt_install} && \\
    rm -rf /var/lib/apt/lists/*

{setup_lines}

RUN {clone_command} && \\
    cd /workspace/{candidate.repo_name} && \\
    git checkout {candidate.base_commit} && \\
    git config user.email "agent@test" && \\
    git config user.name "Agent"

WORKDIR /workspace/{candidate.repo_name}

{install_lines}

RUN mkdir -p /logs/verifier
"""


def _render_clone_command(candidate: CandidateTask) -> str:
    language = candidate.source.language.strip().lower()
    filter_arg = "" if language in {"csharp", "c#"} else " --filter=blob:none"
    return (
        f"git clone{filter_arg} https://github.com/{candidate.repo}.git "
        f"/workspace/{candidate.repo_name}"
    )


def _render_solve_sh(candidate: CandidateTask) -> str:
    patch = _patch_payload(candidate.tests.patch)
    return f"""#!/usr/bin/env bash
set -euo pipefail

cd /workspace/{candidate.repo_name}

patch_file="$(mktemp)"
trap 'rm -f "$patch_file"' EXIT
cat > "$patch_file" <<'PATCH'
{patch}PATCH

if ! git apply --recount --ignore-space-change --whitespace=nowarn "$patch_file"; then
    git apply --3way --recount --ignore-space-change --whitespace=nowarn "$patch_file"
fi

echo "Patch applied successfully."
"""


def _render_test_sh(candidate: CandidateTask) -> str:
    test_cmd = " && ".join(candidate.tests.install_config.test_cmd)
    if not candidate.tests.install_config.test_cmd:
        test_cmd = "true"
    test_patch = _patch_payload(candidate.tests.test_patch)
    return f"""#!/usr/bin/env bash
set +e

cd /workspace/{candidate.repo_name}

patch_file="$(mktemp)"
cat > "$patch_file" <<'PATCH'
{test_patch}PATCH

if ! git apply --recount --ignore-space-change --whitespace=nowarn "$patch_file"; then
    if ! git apply --3way --recount --ignore-space-change --whitespace=nowarn "$patch_file"; then
        echo "Imported test patch failed to apply." > /logs/verifier/rebench_test.log
        echo 0 > /logs/verifier/reward.txt
        cat /logs/verifier/rebench_test.log
        rm -f "$patch_file"
        exit 0
    fi
fi
rm -f "$patch_file"

({test_cmd}) > /logs/verifier/rebench_test.log 2>&1
status=$?
cat /logs/verifier/rebench_test.log

python3 /tests/score_rebench_log.py \\
    /logs/verifier/rebench_test.log \\
    /tests/rebench_metadata.json \\
    /logs/verifier/reward.txt \\
    /logs/verifier/rebench_score.json \\
    "$status"
exit 0
"""


def _render_score_py() -> str:
    return r'''#!/usr/bin/env python3
"""Score an imported SWE-rebench task log without taskforge runtime deps."""

from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

PASSED = "PASSED"
FAILED = "FAILED"
SKIPPED = "SKIPPED"


def main(argv: list[str]) -> int:
    if len(argv) != 6:
        raise SystemExit(
            "usage: score_rebench_log.py LOG METADATA REWARD_OUT REPORT_OUT EXIT_STATUS"
        )

    log_path = Path(argv[1])
    metadata_path = Path(argv[2])
    reward_path = Path(argv[3])
    report_path = Path(argv[4])
    command_status = int(argv[5])

    log = log_path.read_text(encoding="utf-8", errors="replace")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    parser_name = metadata.get("install_config", {}).get("log_parser", "")
    parsed = normalize_status_map(parse_with_parser(parser_name, log))

    expected = [
        normalize_test_name(name)
        for name in list(metadata.get("FAIL_TO_PASS", []))
        + list(metadata.get("PASS_TO_PASS", []))
    ]
    expected_set = set(expected)
    missing: list[str] = []
    unexpected: dict[str, str] = {}
    if expected:
        for name in expected:
            status = parsed.get(name)
            if status is None:
                missing.append(name)
            elif status != PASSED:
                unexpected[name] = status
        reward = 0 if missing or unexpected else 1
    else:
        reward = 1 if command_status == 0 else 0
    outside_expected_failures = {
        name: status
        for name, status in parsed.items()
        if name not in expected_set and status == FAILED
    }
    strict_failure_reasons: list[str] = []
    if reward == 0:
        strict_failure_reasons.append("expected tests did not satisfy reward")
    if command_status != 0:
        strict_failure_reasons.append("test command exited non-zero")
    if outside_expected_failures:
        strict_failure_reasons.append("outside expected failures")
    strict_reward = 0 if strict_failure_reasons else 1

    report = {
        "reward": reward,
        "strict_reward": strict_reward,
        "strict_failure_reasons": strict_failure_reasons,
        "parser": parser_name,
        "command_status": command_status,
        "parsed_tests": len(parsed),
        "expected_tests": len(expected),
        "missing": missing,
        "unexpected": unexpected,
        "outside_expected_failures": outside_expected_failures,
    }
    reward_path.write_text(f"{reward}\n", encoding="utf-8")
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return 0


def parse_with_parser(name: str, log: str) -> dict[str, str]:
    parsers = {
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
        "parse_log_dart": parse_log_dart,
        "parse_log_elixir": parse_log_elixir,
        "parse_log_phpunit": parse_log_phpunit,
        "parse_log_js": parse_log_js,
        "parse_log_js_2": parse_log_js_2,
        "parse_log_js_3": parse_log_js_3,
        "parse_log_js_4": parse_log_js_4,
        "parse_log_lein": parse_log_lein,
    }
    parser = parsers.get(name.strip())
    if parser is None:
        return {}
    return parser(log)


def parse_log_pytest(log: str) -> dict[str, str]:
    statuses: dict[str, str] = {}
    pattern = re.compile(
        r"^(?P<name>\S+::\S.*?)\s+(?P<status>PASSED|FAILED|SKIPPED|ERROR)\b"
    )
    for raw_line in log.splitlines():
        line = strip_ansi(raw_line).strip()
        match = pattern.match(line)
        if match:
            status = match.group("status")
            statuses[match.group("name")] = FAILED if status == "ERROR" else status
    return statuses


def parse_log_gotest(log: str) -> dict[str, str]:
    statuses: dict[str, str] = {}
    pattern = re.compile(r"^--- (PASS|FAIL|SKIP): (.+?) \(")
    for raw_line in log.splitlines():
        line = strip_ansi(raw_line).strip()
        match = pattern.match(line)
        if match:
            status, name = match.groups()
            statuses[name] = {"PASS": PASSED, "FAIL": FAILED, "SKIP": SKIPPED}[status]
    return statuses


def parse_log_jest(log: str) -> dict[str, str]:
    statuses: dict[str, str] = {}
    for raw_line in log.splitlines():
        line = strip_ansi(raw_line).strip()
        if line.startswith(("\u2713 ", "\u221a ")):
            statuses[line[2:].strip()] = PASSED
        elif line.startswith(("\u2715 ", "\u00d7 ", "\u2716 ")):
            statuses[line[2:].strip()] = FAILED
        elif line.startswith(("\u25cb skipped ", "\u25cb ")):
            statuses[line[2:].replace("skipped ", "", 1).strip()] = SKIPPED
        elif line.startswith(("PASS ", "FAIL ")):
            status, name = line.split(maxsplit=1)
            statuses[name.strip()] = PASSED if status == "PASS" else FAILED
    return statuses


def parse_log_cargo(log: str) -> dict[str, str]:
    statuses: dict[str, str] = {}
    pattern = re.compile(r"^test (?P<name>.+?) \.\.\. (?P<status>ok|FAILED|ignored)$")
    for raw_line in log.splitlines():
        line = strip_ansi(raw_line).strip()
        match = pattern.match(line)
        if match:
            status = match.group("status")
            statuses[match.group("name")] = {
                "ok": PASSED,
                "FAILED": FAILED,
                "ignored": SKIPPED,
            }[status]
    return statuses


def parse_log_jq(log: str) -> dict[str, str]:
    statuses: dict[str, str] = {}
    pattern = re.compile(r"^\s*(PASS|FAIL):\s(.+)$")
    for raw_line in log.splitlines():
        line = strip_ansi(raw_line).strip()
        match = pattern.match(line)
        if match:
            status, name = match.groups()
            statuses[name] = PASSED if status == "PASS" else FAILED
    return statuses


def parse_java_mvn(log: str) -> dict[str, str]:
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
        line = strip_ansi(raw_line).strip()
        if match := explicit_test_re.match(line):
            current_test_name = match.group(1)
            continue
        if match := build_result_re.match(line):
            if match.group(1) == "SUCCESS":
                statuses[current_test_name] = PASSED
                any_success = True
            else:
                statuses[current_test_name] = FAILED
                any_failure = True
            continue
        if match := summary_re.search(line):
            tests_run = int(match.group("run"))
            failures = int(match.group("failures"))
            errors = int(match.group("errors"))
            skipped = int(match.group("skipped"))
            class_name = match.group("class")
            status = PASSED
            if failures or errors:
                status = FAILED
                any_failure = True
            elif skipped == tests_run:
                status = SKIPPED
            else:
                any_success = True
            if class_name:
                statuses[class_name] = status
            continue
        if match := failure_re.match(line):
            class_name = match.group("class")
            method_name = match.group("method")
            statuses[class_name] = FAILED
            statuses[f"{class_name}.{method_name}"] = FAILED
            any_failure = True
    if any_failure:
        statuses["---NO TEST NAME FOUND YET---"] = FAILED
    elif any_success:
        statuses["---NO TEST NAME FOUND YET---"] = PASSED
    return statuses


def parse_java_mvn_v2(log: str) -> dict[str, str]:
    statuses: dict[str, str] = {}
    line_re = re.compile(
        r"^\[INFO\]\s+(?P<name>.+?)\s+\.\.+\s+"
        r"(?P<status>SUCCESS|FAILURE|SKIPPED)(?:\s|\[|$)"
    )
    summary_re = re.compile(
        r"Tests run:\s*(\d+),\s*Failures:\s*(\d+),\s*Errors:\s*(\d+),\s*Skipped:\s*(\d+)"
    )
    for raw_line in log.splitlines():
        line = strip_ansi(raw_line).strip()
        match = line_re.match(line)
        if match:
            statuses[match.group("name")] = {
                "SUCCESS": PASSED,
                "FAILURE": FAILED,
                "SKIPPED": SKIPPED,
            }[match.group("status")]
            continue
        summary_match = summary_re.search(line)
        if summary_match:
            tests_run, failures, errors, skipped = map(int, summary_match.groups())
            status = PASSED
            if failures or errors:
                status = FAILED
            elif skipped == tests_run:
                status = SKIPPED
            statuses.setdefault("__suite__", status)
    return statuses


def parse_log_gradle_custom(log: str) -> dict[str, str]:
    statuses: dict[str, str] = {}
    pattern = re.compile(r"^([^>].+?)\s+(PASSED|FAILED)(?:\s+\(\d+(?:\.\d+)?s\))?$")
    for raw_line in log.splitlines():
        line = strip_ansi(raw_line).strip()
        if match := pattern.match(line):
            test_name, status = match.groups()
            statuses[test_name] = PASSED if status == "PASSED" else FAILED
    return statuses


def parse_log_gradlew_v1(log: str) -> dict[str, str]:
    statuses: dict[str, str] = {}
    for root in iter_xml_roots(log):
        for case in root.iter("testcase"):
            name = case.attrib.get("name", "").strip()
            classname = case.attrib.get("classname", "").strip()
            if not name:
                continue
            full_name = f"{name} ({classname})" if classname else name
            if case.find("skipped") is not None:
                statuses[full_name] = SKIPPED
            elif case.find("failure") is not None or case.find("error") is not None:
                statuses[full_name] = FAILED
            else:
                statuses[full_name] = PASSED
    return statuses


def parse_log_junit(log: str) -> dict[str, str]:
    return parse_junit_testcases_from_text(log, joiner=" ")


def parse_log_csharp(log: str) -> dict[str, str]:
    statuses: dict[str, str] = {}
    passed_re = re.compile(r"^\s+Passed\s+(.+?)\s+\[.+?\]$")
    failed_re = re.compile(r"^\s+Failed\s+(.+?)\s+\[.+?\]$")
    skipped_re = re.compile(r"^\s+Skipped\s+(.+?)(?:\s+\[.+?\])?$")
    xunit_fail_re = re.compile(r"^\[xUnit\.net\s+[\d:.]+\]\s+(.+?)\s+\[FAIL\]$")
    for raw_line in log.splitlines():
        line = strip_ansi(raw_line).rstrip()
        if match := xunit_fail_re.match(line):
            statuses[match.group(1)] = FAILED
        elif match := failed_re.match(line):
            statuses[match.group(1)] = FAILED
        elif match := skipped_re.match(line):
            statuses[match.group(1)] = SKIPPED
        elif match := passed_re.match(line):
            statuses.setdefault(match.group(1), PASSED)
    return statuses


def parse_log_dart(log: str) -> dict[str, str]:
    statuses: dict[str, str] = {}
    test_id_to_name: dict[int, str] = {}
    for event in iter_dart_protocol_events(log):
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
            status = dart_done_status(event)
            if test_name and status:
                statuses[test_name] = status
    return statuses


def parse_log_elixir(log: str) -> dict[str, str]:
    statuses: dict[str, str] = {}
    skipped_re = re.compile(r"^\*\s+test\s+(.*?)\s+\(skipped\)\s+\[L#\d+\]$")
    passed_timed_re = re.compile(
        r"^\*\s+test\s+(.*?)\s+\([0-9]+(?:\.[0-9]+)?ms\)\s+\[L#\d+\]$"
    )
    passed_basic_re = re.compile(r"^\*\s+test\s+(.*?)\s+\[L#\d+\]$")
    failure_header_re = re.compile(r"^\d+\)\s+test\s+(.*?)\s+\([^)]+\)$")
    for raw_line in log.splitlines():
        line = strip_ansi(raw_line).strip()
        if match := skipped_re.match(line):
            statuses[match.group(1)] = SKIPPED
        elif match := failure_header_re.match(line):
            statuses[match.group(1)] = FAILED
        elif match := passed_timed_re.match(line):
            statuses.setdefault(match.group(1), PASSED)
        elif match := passed_basic_re.match(line):
            statuses.setdefault(match.group(1), PASSED)
    return statuses


def parse_log_phpunit(log: str) -> dict[str, str]:
    statuses: dict[str, str] = {}
    suite: str | None = None
    suite_re = re.compile(r"^(.+?)\s+\(.+\)$")
    test_re = re.compile(r"^\s*([✔✘↩])\s*(.*?)\s*$")
    for raw_line in log.splitlines():
        line = strip_ansi(raw_line).rstrip()
        if match := suite_re.match(line.strip()):
            suite = match.group(1).strip() or None
            continue
        if match := test_re.match(line):
            symbol, raw_name = match.groups()
            name = strip_timing_suffix(raw_name)
            if not name:
                continue
            full_name = f"{suite or 'None'} > {name}"
            statuses[full_name] = {
                "✔": PASSED,
                "✘": FAILED,
                "↩": SKIPPED,
            }[symbol]
    return statuses


def parse_log_js(log: str) -> dict[str, str]:
    statuses: dict[str, str] = {}
    passed_re = re.compile(r"^\s*✔\s+(.*?)$")
    failed_symbol_re = re.compile(r"^\s*[✖✘]\s+(.*?)$")
    skipped_re = re.compile(r"^\s*-\s+(.*?)$")
    failed_re = re.compile(r"^\s*\[W\]\s*\d+\)\s+(.*?)$")
    failed_header_re = re.compile(r"^\s*\d+\)\s+(.*?):$")
    for raw_line in log.splitlines():
        line = strip_ansi(raw_line).strip()
        if not line:
            continue
        if match := skipped_re.match(line):
            if name := strip_js_duration_suffix(match.group(1)):
                statuses[name] = SKIPPED
            continue
        if match := failed_header_re.match(line):
            if name := strip_js_duration_suffix(match.group(1)):
                statuses[name] = FAILED
            continue
        if match := failed_re.match(line):
            if name := strip_js_duration_suffix(match.group(1).rstrip()):
                statuses[name] = FAILED
            continue
        if match := failed_symbol_re.match(line):
            if name := strip_js_duration_suffix(match.group(1)):
                statuses[name] = FAILED
            continue
        if match := passed_re.match(line):
            if name := strip_js_duration_suffix(match.group(1)):
                statuses.setdefault(name, PASSED)
    return statuses


def parse_log_js_2(log: str) -> dict[str, str]:
    statuses: dict[str, str] = {}
    passed_re = re.compile(r"^\s*✔\s+(.*?)$")
    failed_re = re.compile(r"^\s*\d+\)\s+(.*?)$")
    skipped_re = re.compile(r"^\s*-\s+(.*?)$")
    lines = [strip_ansi(raw_line).rstrip() for raw_line in log.splitlines()]
    for index, raw_line in enumerate(lines):
        next_line = ""
        for candidate in lines[index + 1 :]:
            if candidate.strip():
                next_line = candidate
                break
        line = strip_ansi(raw_line).strip()
        if not line:
            continue
        if match := skipped_re.match(line):
            if name := strip_js_duration_suffix(match.group(1)):
                statuses[name] = SKIPPED
            continue
        if match := failed_re.match(line):
            summary_name = next_line.strip().removesuffix(":")
            raw_name = (
                summary_name
                if next_line.startswith("     ") and summary_name
                else match.group(1)
            )
            if name := strip_js_duration_suffix(raw_name):
                statuses[name] = FAILED
            continue
        if match := passed_re.match(line):
            if name := strip_js_duration_suffix(match.group(1)):
                statuses.setdefault(name, PASSED)
    return statuses


def parse_log_js_3(log: str) -> dict[str, str]:
    statuses: dict[str, str] = {}
    stack: list[str] = []
    tap_line_re = re.compile(
        r"^(?P<status>not ok|ok)\s+\d+\s+-\s+(?P<name>.*?)(?:\s+#.*)?$"
    )
    for raw_line in log.splitlines():
        line = strip_ansi(raw_line).strip()
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
        name = strip_js_duration_suffix(re.split(r"\s+#", raw_name, maxsplit=1)[0])
        if not name:
            continue
        full_name = " :: ".join((*stack, name)) if stack else name
        skip_marker = any(
            token in raw_name.lower() for token in ("# skip", "# skipped", "# todo")
        )
        if skip_marker:
            statuses[full_name] = SKIPPED
        else:
            status_value = PASSED if match.group("status") == "ok" else FAILED
            if status_value == FAILED or full_name not in statuses:
                statuses[full_name] = status_value
        if opens_context:
            stack.append(name)
    return statuses


def parse_log_js_4(log: str) -> dict[str, str]:
    statuses: dict[str, str] = {}
    pass_symbols = ("\u2714", "\u2713")
    fail_symbols = ("\u2718", "\u2716", "\u2715", "\u00d7")
    skip_symbols = ("\u25cb", "\u25cc", "\u25e6", "\u26aa")
    skip_markers = ("(skipped)", "[skip]", "[skipped]", "[pending]", "[todo]")
    for raw_line in log.splitlines():
        line = strip_ansi(raw_line).strip()
        if not line:
            continue
        symbol = line[0]
        payload = line[1:].strip() if len(line) > 1 else ""
        if symbol in pass_symbols:
            if name := normalize_js_test_name(payload):
                statuses.setdefault(name, PASSED)
        elif symbol in fail_symbols:
            if name := normalize_js_test_name(payload):
                statuses[name] = FAILED
        elif symbol in skip_symbols:
            if name := normalize_js_test_name(payload):
                statuses[name] = SKIPPED
        elif any(marker in line.lower() for marker in skip_markers):
            candidate = line
            for marker in skip_markers:
                candidate = candidate.replace(marker, "")
            if name := normalize_js_test_name(candidate):
                statuses[name] = SKIPPED
    return statuses


def parse_log_lein(log: str) -> dict[str, str]:
    statuses: dict[str, str] = {}
    current_namespace: str | None = None
    lein_re = re.compile(r"^lein test (.+)$")
    for raw_line in log.splitlines():
        line = strip_ansi(raw_line).strip()
        if not line:
            continue
        if match := lein_re.match(line):
            payload = match.group(1).strip()
            tokens = payload.split()
            if tokens and tokens[0] == ":only":
                target = " ".join(tokens[1:]).strip()
                current_namespace = target.split("/", 1)[0].strip() or None
                if current_namespace:
                    statuses.setdefault(current_namespace, PASSED)
            else:
                for token in tokens:
                    current_namespace = token.strip() or None
                    if current_namespace:
                        statuses.setdefault(current_namespace, PASSED)
            continue
        if line.startswith(("FAIL in", "ERROR in")) and current_namespace:
            statuses[current_namespace] = FAILED
    return statuses


def parse_log_junit_xml(log: str) -> dict[str, str]:
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
                statuses[full_name] = SKIPPED
            elif case.find("failure") is not None or case.find("error") is not None:
                statuses[full_name] = FAILED
            else:
                statuses[full_name] = PASSED
    return statuses


def strip_ansi(text: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


def iter_xml_roots(log: str) -> list[ET.Element]:
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


def parse_junit_testcases_from_text(log: str, *, joiner: str) -> dict[str, str]:
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
            statuses[full_name] = SKIPPED
        elif "<failure" in content or "<error" in content:
            statuses[full_name] = FAILED
        else:
            statuses[full_name] = PASSED
    return statuses


JS_DURATION_SUFFIX_RE = re.compile(
    r"\s*(?:\(\s*)?\d+(?:\.\d+)?\s*(?:ms|s)\s*(?:\))?\s*$",
    re.IGNORECASE,
)


def normalize_js_test_name(payload: str) -> str:
    payload = payload.strip()
    if payload.startswith("[") and "]:" in payload:
        payload = payload.split("]:", 1)[1].strip()
    if payload.startswith(":"):
        payload = payload[1:].strip()
    return strip_js_duration_suffix(payload)


def strip_js_duration_suffix(name: str) -> str:
    return JS_DURATION_SUFFIX_RE.sub("", name.strip()).strip()


TIMING_NORMALIZE_RES = (
    re.compile(r"\s*\[\s*\d+(?:\.\d+)?\s*(?:ms|s)\s*\]\s*$", re.IGNORECASE),
    re.compile(r"\s+in\s+\d+(?:\.\d+)?\s+(?:msec|sec)\b", re.IGNORECASE),
    re.compile(r"\s*\(\s*\d+(?:\.\d+)?\s*(?:ms|s)\s*\)\s*$", re.IGNORECASE),
    re.compile(r"/0x[0-9a-fA-F]+@[0-9a-fA-F]+"),
)


def normalize_test_name(name: str) -> str:
    for pattern in TIMING_NORMALIZE_RES:
        name = pattern.sub("", name)
    return name.strip()


def normalize_status_map(statuses: dict[str, str]) -> dict[str, str]:
    normalized: dict[str, str] = {}
    for name, status in statuses.items():
        normalized_name = normalize_test_name(name)
        if not normalized_name:
            continue
        if status == FAILED or normalized_name not in normalized:
            normalized[normalized_name] = status
    return normalized


def strip_timing_suffix(name: str) -> str:
    return normalize_test_name(name)


def iter_dart_protocol_events(log: str) -> list[dict[str, object]]:
    events: list[dict[str, object]] = []
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


def dart_done_status(event: dict[str, object]) -> str | None:
    if event.get("skipped", False):
        return SKIPPED
    result = event.get("result")
    if result == "success":
        return PASSED
    if result in {"failure", "error"}:
        return FAILED
    return None


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
'''


def _metadata_for_tests(candidate: CandidateTask) -> dict[str, Any]:
    return {
        "instance_id": candidate.instance_id,
        "repo": candidate.repo,
        "base_commit": candidate.base_commit,
        "source_kind": candidate.source.kind.value,
        "language": candidate.source.language,
        "image_name": candidate.source.image_name,
        "install_config": candidate.tests.install_config.model_dump(mode="json"),
        "FAIL_TO_PASS": candidate.tests.fail_to_pass,
        "PASS_TO_PASS": candidate.tests.pass_to_pass,
    }


def _render_install_block(candidate: CandidateTask) -> str:
    if not candidate.tests.install_config.install:
        return "# No upstream install commands provided."

    commands = "\n".join(_normalize_install_commands(candidate))
    return f"""RUN cd /workspace/{candidate.repo_name} && bash <<'INSTALL'
set -eo pipefail
{commands}
INSTALL"""


def _normalize_install_commands(candidate: CandidateTask) -> list[str]:
    commands = list(candidate.tests.install_config.install)
    if not _needs_go_tarball_arch_normalization(candidate, commands):
        return commands

    normalized = [
        'case "$(dpkg --print-architecture)" in',
        '  amd64) export GO_TARBALL_ARCH="amd64" ;;',
        '  arm64) export GO_TARBALL_ARCH="arm64" ;;',
        '  *) echo "unsupported Go tarball architecture: $(dpkg --print-architecture)" >&2; exit 1 ;;',
        "esac",
    ]
    for command in commands:
        command = command.replace("linux-amd64", "linux-${GO_TARBALL_ARCH}")
        if _extracts_go_tarball(command) and "rm -rf /usr/local/go" not in command:
            normalized.append("rm -rf /usr/local/go")
        normalized.append(command)
    return normalized


def _needs_go_tarball_arch_normalization(
    candidate: CandidateTask, commands: list[str]
) -> bool:
    language = candidate.source.language.lower()
    return language in {"go", "golang"} and any(
        "go.dev/dl/go" in command and "linux-amd64" in command for command in commands
    )


def _extracts_go_tarball(command: str) -> bool:
    return "tar " in command and "-C /usr/local" in command and "go.tar.gz" in command


def _render_runtime_setup(commands: tuple[str, ...]) -> str:
    if not commands:
        return "# No runtime-specific setup commands."
    rendered = "\n".join(f"RUN {command}" for command in commands)
    return rendered


def _patch_payload(patch: str) -> str:
    """Preserve patch bytes except for ensuring a heredoc terminator newline."""

    if patch.endswith("\n"):
        return patch
    return f"{patch}\n"
