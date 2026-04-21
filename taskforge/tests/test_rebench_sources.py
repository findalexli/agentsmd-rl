"""Tests for external source adapters."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from taskforge.execution.docker_templates import select_runtime_template
from taskforge.execution.log_parsers import TestStatus, parse_with_parser
from taskforge.sources.cli import main as sources_cli_main
from taskforge.sources.preflight import preflight_candidate
from taskforge.sources.r2e_commits import inspect_commit
from taskforge.sources.rebench_v2 import (
    candidate_from_record,
    load_candidate_tasks,
    render_task,
)
from taskforge.validators.invariants import (
    check_expected_transition,
    check_gold_expectations,
)


def _record() -> dict:
    return {
        "instance_id": "owner__repo-123",
        "repo": "owner/repo",
        "base_commit": "abc123",
        "problem_statement": "Fix the parser edge case.",
        "patch": "diff --git a/src/p.py b/src/p.py\n--- a/src/p.py\n+++ b/src/p.py\n@@ -1 +1 @@\n-old\n+new\n",
        "test_patch": "diff --git a/tests/test_p.py b/tests/test_p.py\n--- a/tests/test_p.py\n+++ b/tests/test_p.py\n@@ -0,0 +1 @@\n+def test_new(): pass\n",
        "language": "python",
        "FAIL_TO_PASS": ["tests/test_p.py::test_new"],
        "PASS_TO_PASS": ["tests/test_p.py::test_existing"],
        "install_config": {
            "install": ["python -m pip install -e ."],
            "test_cmd": ["python -m pytest tests/test_p.py -vv"],
            "log_parser": "pytest",
            "base_image_name": "python_3.11",
        },
    }


def test_rebench_record_normalizes_to_candidate():
    candidate = candidate_from_record(_record())

    assert candidate.repo == "owner/repo"
    assert candidate.owner == "owner"
    assert candidate.repo_name == "repo"
    assert candidate.task_slug == "owner__repo-123"
    assert candidate.tests.fail_to_pass == ["tests/test_p.py::test_new"]
    assert candidate.tests.install_config.test_cmd == [
        "python -m pytest tests/test_p.py -vv"
    ]


def test_candidate_manifest_uses_taskforge_checks():
    manifest = candidate_from_record(_record()).to_manifest()

    assert manifest.source.repo == "owner/repo"
    assert [check.type.value for check in manifest.checks] == [
        "fail_to_pass",
        "pass_to_pass",
    ]
    assert [check.origin.value for check in manifest.checks] == [
        "pr_diff",
        "repo_tests",
    ]


def test_load_candidate_tasks_supports_jsonl(tmp_path: Path):
    path = tmp_path / "rows.jsonl"
    path.write_text(json.dumps(_record()) + "\n")

    candidates = load_candidate_tasks(path)

    assert len(candidates) == 1
    assert candidates[0].instance_id == "owner__repo-123"


def test_render_task_writes_native_artifacts(tmp_path: Path):
    candidate = candidate_from_record(_record())
    task_dir = render_task(candidate, tmp_path)

    assert (task_dir / "eval_manifest.yaml").exists()
    assert (task_dir / "instruction.md").read_text().startswith("# owner  repo 123")
    assert (
        "git clone --filter=blob:none https://github.com/owner/repo.git"
        in (task_dir / "environment" / "Dockerfile").read_text()
    )
    assert (
        "python -m pytest tests/test_p.py -vv"
        in (task_dir / "tests" / "test.sh").read_text()
    )
    assert "score_rebench_log.py" in (task_dir / "tests" / "test.sh").read_text()
    assert (task_dir / "tests" / "score_rebench_log.py").exists()
    assert 'patch_file="$(mktemp)"' in (task_dir / "tests" / "test.sh").read_text()
    assert json.loads((task_dir / "tests" / "rebench_metadata.json").read_text())[
        "FAIL_TO_PASS"
    ] == ["tests/test_p.py::test_new"]


def test_render_task_preserves_patch_trailing_whitespace(tmp_path: Path):
    record = _record()
    record["test_patch"] = (
        "diff --git a/file.txt b/file.txt\n"
        "--- a/file.txt\n"
        "+++ b/file.txt\n"
        "@@ -1,2 +1,2 @@\n"
        " context with trailing space \n"
        "-old\n"
        "+new\n"
    )
    task_dir = render_task(candidate_from_record(record), tmp_path)

    assert (
        _extract_rendered_patch((task_dir / "tests" / "test.sh").read_text())
        == record["test_patch"]
    )


def test_render_task_normalizes_go_tarball_install_for_container_arch(tmp_path: Path):
    record = _record()
    record["language"] = "go"
    record["install_config"]["install"] = [
        "wget https://go.dev/dl/go1.23.0.linux-amd64.tar.gz -O go.tar.gz",
        "tar -C /usr/local -xzf go.tar.gz",
        "go mod download",
    ]
    task_dir = render_task(candidate_from_record(record), tmp_path)
    dockerfile = (task_dir / "environment" / "Dockerfile").read_text()

    assert 'export GO_TARBALL_ARCH="arm64"' in dockerfile
    assert "go1.23.0.linux-${GO_TARBALL_ARCH}.tar.gz" in dockerfile
    assert "rm -rf /usr/local/go\ntar -C /usr/local -xzf go.tar.gz" in dockerfile


def test_render_task_uses_full_clone_for_csharp_msbuild_git_tasks(tmp_path: Path):
    record = _record()
    record["language"] = "csharp"
    task_dir = render_task(candidate_from_record(record), tmp_path)
    dockerfile = (task_dir / "environment" / "Dockerfile").read_text()

    assert "git clone https://github.com/owner/repo.git" in dockerfile
    assert "git clone --filter=blob:none" not in dockerfile


def test_rendered_scorer_scores_expected_tests(tmp_path: Path):
    subprocess = pytest.importorskip("subprocess")
    task_dir = render_task(candidate_from_record(_record()), tmp_path / "tasks")
    log_path = tmp_path / "pytest.log"
    reward_path = tmp_path / "reward.txt"
    report_path = tmp_path / "score.json"
    log_path.write_text(
        "tests/test_p.py::test_new PASSED [ 50%]\n"
        "tests/test_p.py::test_existing PASSED [ 75%]\n"
        "tests/test_p.py::test_unlisted FAILED [100%]\n"
    )

    subprocess.run(
        [
            sys.executable,
            str(task_dir / "tests" / "score_rebench_log.py"),
            str(log_path),
            str(task_dir / "tests" / "rebench_metadata.json"),
            str(reward_path),
            str(report_path),
            "1",
        ],
        check=True,
    )

    assert reward_path.read_text() == "1\n"
    report = json.loads(report_path.read_text())
    assert report["missing"] == []
    assert report["strict_reward"] == 0
    assert report["outside_expected_failures"] == {
        "tests/test_p.py::test_unlisted": TestStatus.FAILED.value
    }


def test_rendered_scorer_treats_dart_skips_as_not_passed(tmp_path: Path):
    subprocess = pytest.importorskip("subprocess")
    record = _record()
    record["language"] = "dart"
    record["FAIL_TO_PASS"] = ["needs token"]
    record["PASS_TO_PASS"] = []
    record["install_config"]["log_parser"] = "parse_log_dart"
    record["install_config"]["base_image_name"] = "dart_base:latest"
    task_dir = render_task(candidate_from_record(record), tmp_path / "tasks")
    log_path = tmp_path / "dart.log"
    reward_path = tmp_path / "reward.txt"
    report_path = tmp_path / "score.json"
    log_path.write_text(
        '{"type":"testStart","test":{"id":1,"name":"needs token"}}\n'
        '{"type":"testDone","testID":1,"result":"success","skipped":true}\n'
    )

    subprocess.run(
        [
            sys.executable,
            str(task_dir / "tests" / "score_rebench_log.py"),
            str(log_path),
            str(task_dir / "tests" / "rebench_metadata.json"),
            str(reward_path),
            str(report_path),
            "0",
        ],
        check=True,
    )

    assert reward_path.read_text() == "0\n"
    assert json.loads(report_path.read_text())["unexpected"] == {
        "needs token": TestStatus.SKIPPED.value
    }


def test_rendered_scorer_parses_maven_surefire_classes(tmp_path: Path):
    subprocess = pytest.importorskip("subprocess")
    record = _record()
    record["language"] = "java"
    record["FAIL_TO_PASS"] = ["pkg.FixedTest", "---NO TEST NAME FOUND YET---"]
    record["PASS_TO_PASS"] = ["pkg.ExistingTest"]
    record["install_config"]["log_parser"] = "parse_java_mvn"
    record["install_config"]["base_image_name"] = "java_21:latest"
    task_dir = render_task(candidate_from_record(record), tmp_path / "tasks")
    log_path = tmp_path / "maven.log"
    reward_path = tmp_path / "reward.txt"
    report_path = tmp_path / "score.json"
    log_path.write_text(
        "Running pkg.FixedTest\n"
        "Tests run: 3, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.01 sec - in pkg.FixedTest\n"
        "Running pkg.ExistingTest\n"
        "Tests run: 2, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.01 sec - in pkg.ExistingTest\n"
        "Tests run: 5, Failures: 0, Errors: 0, Skipped: 0\n"
    )

    subprocess.run(
        [
            sys.executable,
            str(task_dir / "tests" / "score_rebench_log.py"),
            str(log_path),
            str(task_dir / "tests" / "rebench_metadata.json"),
            str(reward_path),
            str(report_path),
            "0",
        ],
        check=True,
    )

    assert reward_path.read_text() == "1\n"
    assert json.loads(report_path.read_text())["unexpected"] == {}


def test_rendered_scorer_normalizes_jvm_lambda_identities(tmp_path: Path):
    subprocess = pytest.importorskip("subprocess")
    class_name = "com.example.PropertiesFileTransformerTest"
    expected_name = (
        "[1] foo.properties, "
        "com.example.PropertiesFileTransformerTest$Companion$$Lambda/0x00007f3ed0533748@14292d71, "
        "{foo=bar} "
        f"({class_name})"
    )
    actual_name = (
        "[1] foo.properties, "
        "com.example.PropertiesFileTransformerTest$Companion$$Lambda/0x0000002001533980@48e74764, "
        "{foo=bar}"
    )
    record = _record()
    record["language"] = "kotlin"
    record["FAIL_TO_PASS"] = [expected_name]
    record["PASS_TO_PASS"] = []
    record["install_config"]["log_parser"] = "parse_log_gradlew_v1"
    record["install_config"]["base_image_name"] = "kotlin-jdk-21"
    task_dir = render_task(candidate_from_record(record), tmp_path / "tasks")
    log_path = tmp_path / "gradle.xml"
    reward_path = tmp_path / "gradle.reward.txt"
    report_path = tmp_path / "gradle.score.json"
    log_path.write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<testsuite name="suite">\n'
        f'  <testcase classname="{class_name}" name="{actual_name}"/>\n'
        "</testsuite>\n"
    )

    subprocess.run(
        [
            sys.executable,
            str(task_dir / "tests" / "score_rebench_log.py"),
            str(log_path),
            str(task_dir / "tests" / "rebench_metadata.json"),
            str(reward_path),
            str(report_path),
            "0",
        ],
        check=True,
    )

    assert reward_path.read_text() == "1\n"
    assert json.loads(report_path.read_text())["missing"] == []


def test_rendered_scorer_reports_jest_cross_failures(tmp_path: Path):
    subprocess = pytest.importorskip("subprocess")
    record = _record()
    record["language"] = "typescript"
    record["FAIL_TO_PASS"] = ["typescript"]
    record["PASS_TO_PASS"] = ["no routes"]
    record["install_config"]["log_parser"] = "parse_log_js_4"
    task_dir = render_task(candidate_from_record(record), tmp_path / "tasks")
    log_path = tmp_path / "jest.log"
    reward_path = tmp_path / "reward.txt"
    report_path = tmp_path / "score.json"
    log_path.write_text(
        "PASS src/core.test.ts\n"
        "  route generation\n"
        "    \u2713 no routes (1 ms)\n"
        "    \u2713 typescript (1 ms)\n"
        "FAIL e2e/e2e.test.ts\n"
        "  e2e\n"
        "    \u2715 npx nextjs-routes (8588 ms)\n"
    )

    subprocess.run(
        [
            sys.executable,
            str(task_dir / "tests" / "score_rebench_log.py"),
            str(log_path),
            str(task_dir / "tests" / "rebench_metadata.json"),
            str(reward_path),
            str(report_path),
            "1",
        ],
        check=True,
    )

    report = json.loads(report_path.read_text())
    assert reward_path.read_text() == "1\n"
    assert report["strict_reward"] == 0
    assert report["strict_failure_reasons"] == [
        "test command exited non-zero",
        "outside expected failures",
    ]
    assert report["outside_expected_failures"] == {
        "npx nextjs-routes": TestStatus.FAILED.value
    }


def test_rendered_scorer_supports_js_parser_variants(tmp_path: Path):
    subprocess = pytest.importorskip("subprocess")
    cases = [
        (
            "parse_log_js",
            "  \u2714 should pass (12ms)\n  \u2716 should fail \n",
            "should fail",
        ),
        (
            "parse_log_js_2",
            "  \u2714 should pass (12ms)\n  1) should fail\n\n  1) suite\n       should fail:\n",
            "should fail",
        ),
        (
            "parse_log_js_3",
            "ok 1 - root suite {\nnot ok 2 - nested fail\n}\n",
            "root suite :: nested fail",
        ),
    ]

    for parser_name, log_text, expected_name in cases:
        record = _record()
        record["instance_id"] = f"owner__repo-{parser_name}"
        record["language"] = "js"
        record["FAIL_TO_PASS"] = [expected_name]
        record["PASS_TO_PASS"] = []
        record["install_config"]["log_parser"] = parser_name
        task_dir = render_task(candidate_from_record(record), tmp_path / "tasks")
        log_path = tmp_path / f"{parser_name}.log"
        reward_path = tmp_path / f"{parser_name}.reward.txt"
        report_path = tmp_path / f"{parser_name}.score.json"
        log_path.write_text(log_text)

        subprocess.run(
            [
                sys.executable,
                str(task_dir / "tests" / "score_rebench_log.py"),
                str(log_path),
                str(task_dir / "tests" / "rebench_metadata.json"),
                str(reward_path),
                str(report_path),
                "1",
            ],
            check=True,
        )

        report = json.loads(report_path.read_text())
        assert reward_path.read_text() == "0\n"
        assert report["unexpected"] == {expected_name: TestStatus.FAILED.value}


def test_rendered_scorer_normalizes_phpunit_timing(tmp_path: Path):
    subprocess = pytest.importorskip("subprocess")
    record = _record()
    record["language"] = "php"
    record["FAIL_TO_PASS"] = ["Annotation Parser > Parses content [1.38 ms]"]
    record["PASS_TO_PASS"] = ["Annotation Parser > Keeps old behavior [0.04 ms]"]
    record["install_config"]["log_parser"] = "parse_log_phpunit"
    record["install_config"]["base_image_name"] = "php_8.3.16"
    task_dir = render_task(candidate_from_record(record), tmp_path / "tasks")
    log_path = tmp_path / "phpunit.log"
    reward_path = tmp_path / "phpunit.reward.txt"
    report_path = tmp_path / "phpunit.score.json"
    log_path.write_text(
        "Annotation Parser (Tests\\AnnotationParserTest)\n"
        " ✔ Parses content [0.07 ms]\n"
        " ✔ Keeps old behavior [0.05 ms]\n"
    )

    subprocess.run(
        [
            sys.executable,
            str(task_dir / "tests" / "score_rebench_log.py"),
            str(log_path),
            str(task_dir / "tests" / "rebench_metadata.json"),
            str(reward_path),
            str(report_path),
            "0",
        ],
        check=True,
    )

    report = json.loads(report_path.read_text())
    assert reward_path.read_text() == "1\n"
    assert report["missing"] == []
    assert report["unexpected"] == {}


def test_rebench_cli_imports_json(tmp_path: Path):
    input_path = tmp_path / "rows.json"
    output_dir = tmp_path / "tasks"
    report_path = tmp_path / "report.json"
    input_path.write_text(json.dumps([_record()]))

    exit_code = sources_cli_main(
        [
            "import-rebench-v2",
            "--input",
            str(input_path),
            "--output-dir",
            str(output_dir),
            "--report-json",
            str(report_path),
        ]
    )

    assert exit_code == 0
    assert (output_dir / "owner__repo-123" / "eval_manifest.yaml").exists()
    assert json.loads(report_path.read_text())[0]["status"] == "rendered"


def test_rebench_cli_audits_json(tmp_path: Path):
    input_path = tmp_path / "rows.json"
    report_path = tmp_path / "audit.json"
    bad_parser = _record()
    bad_parser["instance_id"] = "owner__repo-456"
    bad_parser["install_config"]["log_parser"] = "unknown_parser"
    input_path.write_text(json.dumps([_record(), bad_parser]))

    exit_code = sources_cli_main(
        [
            "audit-rebench-v2",
            "--input",
            str(input_path),
            "--report-json",
            str(report_path),
        ]
    )

    report = json.loads(report_path.read_text())
    assert exit_code == 0
    assert report["total"] == 2
    assert report["accepted"] == 1
    assert report["rejected"] == 1
    assert report["log_parsers"] == {"pytest": 1, "unknown_parser": 1}
    assert report["preflight_reasons"] == {"unknown log parser: unknown_parser": 1}


def test_rebench_cli_audit_reports_advisory_risks(tmp_path: Path):
    input_path = tmp_path / "rows.json"
    report_path = tmp_path / "audit.json"
    risky = _record()
    risky["language"] = "typescript"
    risky["install_config"]["install"] = ["pnpm install --frozen-lockfile"]
    risky["install_config"]["test_cmd"] = ["xvfb-run -a pnpm test"]
    risky["install_config"]["docker_specs"] = {"memory": "8g"}
    input_path.write_text(json.dumps([risky]))

    exit_code = sources_cli_main(
        [
            "audit-rebench-v2",
            "--input",
            str(input_path),
            "--report-json",
            str(report_path),
        ]
    )

    report = json.loads(report_path.read_text())
    assert exit_code == 0
    assert report["risk_reasons"] == {
        "browser/display tooling may require explicit setup": 1,
        "docker_specs present but renderer does not apply them": 1,
        "js package manager/runtime may require explicit setup": 1,
    }
    assert report["rows"][0]["risk_reasons"] == [
        "docker_specs present but renderer does not apply them",
        "js package manager/runtime may require explicit setup",
        "browser/display tooling may require explicit setup",
    ]


def test_preflight_rejects_missing_parser():
    record = _record()
    record["install_config"]["log_parser"] = "does_not_exist"

    result = preflight_candidate(candidate_from_record(record))

    assert not result.accepted
    assert "unknown log parser: does_not_exist" in result.reasons


def test_preflight_rejects_empty_parser_when_expected_tests_exist():
    record = _record()
    record["install_config"]["log_parser"] = ""

    result = preflight_candidate(candidate_from_record(record))

    assert not result.accepted
    assert "missing log parser" in result.reasons


def test_runtime_selection_is_conservative():
    assert select_runtime_template("typescript").image.startswith("node:")
    assert select_runtime_template("js").image.startswith("node:")
    assert select_runtime_template("csharp").image.startswith(
        "mcr.microsoft.com/dotnet/sdk:"
    )
    assert "maven" in select_runtime_template("java").setup_packages
    assert select_runtime_template("java", "java_11:latest").image.startswith(
        "maven:3.9-eclipse-temurin-11"
    )
    assert select_runtime_template("", "java_21:latest").image.startswith(
        "maven:3.9-eclipse-temurin-21"
    )
    assert select_runtime_template("kotlin", "kotlin-jdk-11").image.startswith(
        "eclipse-temurin:11-jdk"
    )
    assert select_runtime_template("kotlin", "kotlin-jdk-21").image.startswith(
        "eclipse-temurin:21-jdk"
    )
    assert select_runtime_template("clojure").setup_commands
    assert select_runtime_template("php").image == "php:8.3.16"
    assert "libzip-dev" in select_runtime_template("", "php_8.3.16").setup_packages
    c_runtime = select_runtime_template("", "c:latest")
    assert c_runtime.image == "ubuntu:22.04"
    assert "autoconf" in c_runtime.setup_packages


def test_log_parser_registry_parses_common_rebench_logs():
    pytest_log = "tests/test_p.py::test_new PASSED [ 50%]\ntests/test_p.py::test_old FAILED [100%]\n"
    go_log = "--- PASS: TestThing (0.00s)\n--- FAIL: TestOther (0.00s)\n"
    jq_log = "PASS: nccopy tst_filter_order\nFAIL: tst_hdf5\n"
    csharp_log = "  Passed My.Tests.Pass [1 ms]\n  Failed My.Tests.Fail [2 ms]\n"
    dart_log = (
        '{"type":"testStart","test":{"id":1,"name":"adds values"}}\n'
        '{"type":"testDone","testID":1,"result":"success"}\n'
        '{"type":"testStart","test":{"id":2,"name":"needs token"}}\n'
        '{"type":"testDone","testID":2,"result":"success","skipped":true}\n'
    )
    elixir_log = "* test accepts input [L#42]\n1) test rejects invalid (AppTest)\n"
    js_log = "\u2714 should pass (12ms)\n\u2716 should fail\n\u2715 also fails\n"
    js_mocha_log = "  ✔ should pass (12ms)\n  - should skip\n  1) should fail:\n"
    js_tap_log = "ok 1 - root suite {\nok 2 - nested pass\nnot ok 3 - nested fail\n}\n"
    phpunit_log = (
        "Annotation Parser (Tests\\AnnotationParserTest)\n"
        " ✔ Parses content [1.38 ms]\n"
        " ✘ Rejects invalid [0.04 ms]\n"
        " ↩ Skips missing [0.01 ms]\n"
    )
    lein_log = "lein test app.core-test\nFAIL in (thing) (core_test.clj:1)\n"
    mvn_log = (
        "+ mvn -Dtest=pkg.TargetTest test\n"
        "[INFO] BUILD SUCCESS\n"
        "Running pkg.PassingTest\n"
        "Tests run: 2, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.01 sec - in pkg.PassingTest\n"
        "Running pkg.FailingTest\n"
        "Tests run: 1, Failures: 1, Errors: 0, Skipped: 0, Time elapsed: 0.01 sec <<< FAILURE! - in pkg.FailingTest\n"
        "testThing(pkg.FailingTest)  Time elapsed: 0.01 sec  <<< FAILURE!\n"
    )
    mvn_v2_log = "[INFO] Piranha - HTTP - Implementation ........ FAILURE [  1.241 s]\n"
    gradle_log = "com.example.ParserTest parses input PASSED (0.12s)\ncom.example.ParserTest rejects bad input FAILED\n"
    gradle_xml_log = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<testsuite name="suite">\n'
        '  <testcase classname="com.example.ParserTest" name="parses input"/>\n'
        '  <testcase classname="com.example.ParserTest" name="rejects bad input"><failure/></testcase>\n'
        "</testsuite>\n"
    )

    assert (
        parse_with_parser("pytest", pytest_log)["tests/test_p.py::test_new"]
        == TestStatus.PASSED.value
    )
    assert parse_with_parser("gotest", go_log)["TestOther"] == TestStatus.FAILED.value
    assert (
        parse_with_parser("parse_log_jq", jq_log)["tst_hdf5"] == TestStatus.FAILED.value
    )
    assert (
        parse_with_parser("parse_log_csharp", csharp_log)["My.Tests.Fail"]
        == TestStatus.FAILED.value
    )
    assert (
        parse_with_parser("parse_log_dart", dart_log)["adds values"]
        == TestStatus.PASSED.value
    )
    assert (
        parse_with_parser("parse_log_dart", dart_log)["needs token"]
        == TestStatus.SKIPPED.value
    )
    assert (
        parse_with_parser("parse_log_elixir", elixir_log)["rejects invalid"]
        == TestStatus.FAILED.value
    )
    assert (
        parse_with_parser("parse_log_js_4", js_log)["should fail"]
        == TestStatus.FAILED.value
    )
    assert (
        parse_with_parser("parse_log_js_4", js_log)["also fails"]
        == TestStatus.FAILED.value
    )
    assert (
        parse_with_parser("parse_log_js", js_mocha_log)["should fail"]
        == TestStatus.FAILED.value
    )
    assert (
        parse_with_parser("parse_log_js_2", js_mocha_log)["should skip"]
        == TestStatus.SKIPPED.value
    )
    assert (
        parse_with_parser("parse_log_js_3", js_tap_log)["root suite :: nested fail"]
        == TestStatus.FAILED.value
    )
    assert (
        parse_with_parser("parse_log_phpunit", phpunit_log)[
            "Annotation Parser > Rejects invalid"
        ]
        == TestStatus.FAILED.value
    )
    assert (
        parse_with_parser("parse_log_phpunit", phpunit_log)[
            "Annotation Parser > Skips missing"
        ]
        == TestStatus.SKIPPED.value
    )
    assert (
        parse_with_parser("parse_log_lein", lein_log)["app.core-test"]
        == TestStatus.FAILED.value
    )
    assert (
        parse_with_parser("parse_java_mvn", mvn_log)["pkg.PassingTest"]
        == TestStatus.PASSED.value
    )
    assert (
        parse_with_parser("parse_java_mvn", mvn_log)["pkg.FailingTest"]
        == TestStatus.FAILED.value
    )
    assert (
        parse_with_parser("parse_java_mvn", mvn_log)["---NO TEST NAME FOUND YET---"]
        == TestStatus.FAILED.value
    )
    assert (
        parse_with_parser("parse_java_mvn_v2", mvn_v2_log)[
            "Piranha - HTTP - Implementation"
        ]
        == TestStatus.FAILED.value
    )
    assert (
        parse_with_parser("parse_log_maven", mvn_log)["---NO TEST NAME FOUND YET---"]
        == TestStatus.FAILED.value
    )
    assert (
        parse_with_parser("parse_log_maven", mvn_log)["pkg.TargetTest"]
        == TestStatus.PASSED.value
    )
    assert (
        parse_with_parser("parse_log_gradle_custom", gradle_log)[
            "com.example.ParserTest rejects bad input"
        ]
        == TestStatus.FAILED.value
    )
    assert (
        parse_with_parser("parse_log_gradlew_v1", gradle_xml_log)[
            "rejects bad input (com.example.ParserTest)"
        ]
        == TestStatus.FAILED.value
    )
    assert (
        parse_with_parser("parse_log_junit", gradle_xml_log)[
            "com.example.ParserTest parses input"
        ]
        == TestStatus.PASSED.value
    )


def test_transition_invariants():
    base = {
        "new": TestStatus.FAILED.value,
        "old": TestStatus.PASSED.value,
    }
    gold = {
        "new": TestStatus.PASSED.value,
        "old": TestStatus.PASSED.value,
    }

    assert check_expected_transition(
        base, gold, fail_to_pass=["new"], pass_to_pass=["old"]
    ).ok
    assert check_gold_expectations(gold, fail_to_pass=["new"], pass_to_pass=["old"]).ok

    aborted_base = {
        "new": TestStatus.FAILED.value,
        "old": TestStatus.PASSED.value,
    }
    aborted_gold = {
        "new": TestStatus.PASSED.value,
        "later_new": TestStatus.PASSED.value,
        "old": TestStatus.PASSED.value,
    }
    assert check_expected_transition(
        aborted_base,
        aborted_gold,
        fail_to_pass=["new", "later_new"],
        pass_to_pass=["old"],
    ).ok

    assert not check_expected_transition(
        {"old": TestStatus.PASSED.value},
        aborted_gold,
        fail_to_pass=["new", "later_new"],
        pass_to_pass=["old"],
    ).ok


def test_r2e_commit_inspection_detects_code_tests_and_agent_config(tmp_path: Path):
    subprocess = pytest.importorskip("subprocess")
    subprocess.run(
        ["git", "init", "-b", "master"], cwd=tmp_path, check=True, capture_output=True
    )
    subprocess.run(["git", "config", "user.email", "a@b.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "tester"], cwd=tmp_path, check=True)
    (tmp_path / "AGENTS.md").write_text("rules\n")
    (tmp_path / "src").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / "src" / "thing.py").write_text("x = 1\n")
    (tmp_path / "tests" / "test_thing.py").write_text("def test_x(): assert True\n")
    subprocess.run(
        ["git", "add", "AGENTS.md", "src/thing.py", "tests/test_thing.py"],
        cwd=tmp_path,
        check=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "add candidate"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )

    candidate = inspect_commit(tmp_path, "HEAD")

    assert candidate.has_code_and_tests
    assert candidate.has_agent_instruction_context
    assert candidate.score >= 10


def _extract_rendered_patch(script: str) -> str:
    marker = "cat > \"$patch_file\" <<'PATCH'\n"
    start = script.index(marker) + len(marker)
    end = script.index("\nPATCH\n", start)
    return script[start : end + 1]
