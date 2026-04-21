"""CLI helpers for external task-source adapters."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re

from taskforge.execution.docker_templates import select_runtime_template
from taskforge.sources.models import CandidateTask
from taskforge.sources.preflight import preflight_candidate
from taskforge.sources.rebench_v2 import load_candidate_tasks, render_task


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Import external task candidates into taskforge artifacts."
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    rebench = sub.add_parser(
        "import-rebench-v2", help="Render SWE-rebench-V2 JSON/JSONL rows."
    )
    rebench.add_argument(
        "--input", required=True, help="Path to SWE-rebench-style JSON or JSONL rows."
    )
    rebench.add_argument(
        "--output-dir",
        required=True,
        help="Directory where task directories will be written.",
    )
    rebench.add_argument(
        "--overwrite", action="store_true", help="Overwrite existing task directories."
    )
    rebench.add_argument(
        "--allow-preflight-fail",
        action="store_true",
        help="Render rows even when deterministic preflight reports missing evidence.",
    )
    rebench.add_argument(
        "--report-json", help="Optional path to write import report JSON."
    )

    audit = sub.add_parser(
        "audit-rebench-v2", help="Summarize SWE-rebench-V2 rows before import."
    )
    audit.add_argument(
        "--input", required=True, help="Path to SWE-rebench-style JSON or JSONL rows."
    )
    audit.add_argument("--report-json", help="Optional path to write audit JSON.")

    args = parser.parse_args(argv)
    if args.cmd == "import-rebench-v2":
        return _import_rebench_v2(args)
    if args.cmd == "audit-rebench-v2":
        return _audit_rebench_v2(args)
    raise AssertionError(f"unhandled command: {args.cmd}")


def _import_rebench_v2(args: argparse.Namespace) -> int:
    candidates = load_candidate_tasks(args.input)
    output_dir = Path(args.output_dir)
    report: list[dict[str, object]] = []
    failures = 0

    for candidate in candidates:
        preflight = preflight_candidate(candidate)
        if not preflight.accepted and not args.allow_preflight_fail:
            failures += 1
            report.append(
                {
                    "instance_id": candidate.instance_id,
                    "status": "preflight_failed",
                    "reasons": preflight.reasons,
                }
            )
            continue
        try:
            task_dir = render_task(candidate, output_dir, overwrite=args.overwrite)
        except Exception as exc:
            failures += 1
            report.append(
                {
                    "instance_id": candidate.instance_id,
                    "status": "error",
                    "error": str(exc),
                }
            )
            continue
        report.append(
            {
                "instance_id": candidate.instance_id,
                "status": "rendered",
                "task_dir": str(task_dir),
                "preflight_reasons": preflight.reasons,
            }
        )

    if args.report_json:
        Path(args.report_json).write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8"
        )
    else:
        print(json.dumps(report, indent=2))

    return 1 if failures else 0


def _audit_rebench_v2(args: argparse.Namespace) -> int:
    candidates = load_candidate_tasks(args.input)
    rows: list[dict[str, object]] = []
    language_counts: Counter[str] = Counter()
    base_image_counts: Counter[str] = Counter()
    parser_counts: Counter[str] = Counter()
    runtime_counts: Counter[str] = Counter()
    reason_counts: Counter[str] = Counter()
    risk_counts: Counter[str] = Counter()
    accepted = 0

    for candidate in candidates:
        preflight = preflight_candidate(candidate)
        runtime = select_runtime_template(
            candidate.source.language,
            candidate.tests.install_config.base_image_name,
        )
        risk_reasons = _audit_risk_reasons(candidate, runtime.language)
        language = candidate.source.language or "unknown"
        base_image = candidate.tests.install_config.base_image_name or "unknown"
        parser = candidate.tests.install_config.log_parser or "unknown"
        runtime_key = f"{runtime.language}:{runtime.image}"

        language_counts[language] += 1
        base_image_counts[base_image] += 1
        parser_counts[parser] += 1
        runtime_counts[runtime_key] += 1
        reason_counts.update(preflight.reasons)
        risk_counts.update(risk_reasons)
        accepted += int(preflight.accepted)

        rows.append(
            {
                "instance_id": candidate.instance_id,
                "repo": candidate.repo,
                "language": language,
                "base_image_name": base_image,
                "log_parser": parser,
                "runtime_language": runtime.language,
                "runtime_image": runtime.image,
                "runtime_notes": runtime.notes,
                "fail_to_pass_count": len(candidate.tests.fail_to_pass),
                "pass_to_pass_count": len(candidate.tests.pass_to_pass),
                "accepted": preflight.accepted,
                "preflight_reasons": preflight.reasons,
                "risk_reasons": risk_reasons,
            }
        )

    report: dict[str, object] = {
        "total": len(candidates),
        "accepted": accepted,
        "rejected": len(candidates) - accepted,
        "languages": dict(sorted(language_counts.items())),
        "base_images": dict(sorted(base_image_counts.items())),
        "log_parsers": dict(sorted(parser_counts.items())),
        "runtime_templates": dict(sorted(runtime_counts.items())),
        "preflight_reasons": dict(sorted(reason_counts.items())),
        "risk_reasons": dict(sorted(risk_counts.items())),
        "rows": rows,
    }

    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.report_json:
        Path(args.report_json).write_text(text, encoding="utf-8")
    else:
        print(text)
    return 0


def _audit_risk_reasons(candidate: CandidateTask, runtime_language: str) -> list[str]:
    """Non-blocking import risks that deserve review before full validation."""

    reasons: list[str] = []
    install_config = candidate.tests.install_config
    commands = [*install_config.install, *install_config.test_cmd]
    command_text = "\n".join(commands).lower()
    runtime_key = runtime_language.strip().lower()

    if runtime_key == "unknown":
        reasons.append("unknown runtime template")
    if not install_config.test_cmd:
        reasons.append("missing test command")
    if install_config.docker_specs:
        reasons.append("docker_specs present but renderer does not apply them")
    if runtime_key in {"node", "javascript", "typescript"}:
        if re.search(r"(^|[\s;&|])(pnpm|yarn|bun|deno)([\s;&|]|$)", command_text):
            reasons.append("js package manager/runtime may require explicit setup")
        if re.search(r"(^|[\s;&|])(playwright|xvfb-run)([\s;&|]|$)", command_text):
            reasons.append("browser/display tooling may require explicit setup")
    if "docker.sock" in command_text or "/var/run/docker.sock" in command_text:
        reasons.append("test command references host docker socket")

    return reasons


if __name__ == "__main__":
    raise SystemExit(main())
