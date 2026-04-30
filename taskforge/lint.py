"""Pre-audit linter for test.sh — catches 35% of issues programmatically.

Runs static checks on test.sh without needing Docker or LLM. Based on
analysis of 326 audit rewrites, the top programmatically-detectable issues:

  - Comment injection vulnerability (48% of tasks)
  - Ungated structural checks (9% of tasks)
  - set -euo pipefail instead of set +e (11% of tasks)
  - Weight sum errors
  - Import/AST fallback patterns (anti-patterns #2, #10)
  - Reward path wrong

These checks mirror the 10 Known Gaming Anti-Patterns from audit-tests.md.

Usage:
    python -m taskforge.lint                         # lint all tasks
    python -m taskforge.lint --tasks "sglang-*"      # glob pattern
    python -m taskforge.lint --severity critical      # only critical issues
    python -m taskforge.lint --json                   # machine-readable output
    python -m taskforge.lint --task-dir markdown_edits
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Sequence


class Severity(str, Enum):
    CRITICAL = "critical"   # Will cause test failures or gaming exploits
    WARNING = "warning"     # Likely quality issue
    INFO = "info"           # Suggestion


@dataclass
class LintIssue:
    severity: Severity
    line: int               # 0 if file-level
    rule: str               # Machine-readable rule ID
    message: str            # Human-readable explanation
    antipattern: int = 0    # Maps to anti-pattern # from audit-tests.md (0=none)


@dataclass
class LintResult:
    issues: list[LintIssue] = field(default_factory=list)
    weight_sum: float = 0.0
    behavioral_ratio: float = 0.0
    has_gate: bool = False
    has_f2p: bool = False
    reward_path: str = ""

    @property
    def critical_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == Severity.CRITICAL)

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == Severity.WARNING)

    @property
    def passed(self) -> bool:
        return self.critical_count == 0


def lint_test_sh(content: str) -> LintResult:
    """Run all lint checks on a test.sh file.

    Returns LintResult with issues found. Zero critical issues = passed.
    """
    result = LintResult()
    lines = content.splitlines()

    _check_set_flags(lines, result)
    _check_reward_path(lines, result)
    _check_weight_sum(content, result)
    _check_behavioral_ratio(content, result)
    _check_gate(content, result)
    _check_f2p(content, result)
    _check_comment_stripping(lines, result)
    _check_import_fallback(lines, result)
    _check_file_exists_fallback(lines, result)
    _check_ungated_structural(content, result)
    _check_annotations(content, result)
    _check_antistub_threshold(content, result)

    return result


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------

def _check_set_flags(lines: Sequence[str], result: LintResult) -> None:
    """set -euo pipefail causes test.sh to abort on first failure.
    Harbor tests must use set +e so all checks run and score is accumulated.
    """
    for i, line in enumerate(lines):
        stripped = line.strip()
        # set -e alone or set -euo pipefail
        if re.match(r'^set\s+-[a-z]*e', stripped) and 'set +e' not in stripped:
            result.issues.append(LintIssue(
                severity=Severity.CRITICAL,
                line=i + 1,
                rule="set-e-abort",
                message="'set -e' aborts on first failure — test.sh must use 'set +e' "
                        "so all checks run and partial scores accumulate",
            ))


def _check_reward_path(lines: Sequence[str], result: LintResult) -> None:
    """Reward must go to /logs/verifier/reward.txt (harbor convention)."""
    content = "\n".join(lines)

    # Find where reward is written
    reward_paths = re.findall(r'>\s*([^\s"]+reward[^\s"]*)', content)
    reward_paths += re.findall(r'>\s*"([^"]+reward[^"]*)"', content)
    reward_paths += re.findall(r"REWARD_FILE=[\"']?([^\"'\s]+)", content)

    canonical = "/logs/verifier/reward.txt"
    for path in reward_paths:
        result.reward_path = path
        if path and canonical not in path and "$REWARD_FILE" not in path:
            # Allow $REWARD_FILE variable that might be set to canonical
            if "reward.txt" in path and "/logs/verifier" not in path:
                result.issues.append(LintIssue(
                    severity=Severity.WARNING,
                    line=0,
                    rule="reward-path",
                    message=f"Reward written to '{path}', expected '{canonical}'. "
                            "Some tasks use /workspace/*/reward.txt but "
                            "/logs/verifier/reward.txt is the harbor standard.",
                ))
                break


def _check_weight_sum(content: str, result: LintResult) -> None:
    """Check that weight annotations sum to ~1.0."""
    # Pattern 1: WEIGHTS[key]=0.20 style (gradio/areal convention — most precise)
    weights_declared = re.findall(r'WEIGHTS\[\w+\]\s*=\s*(\d+\.\d+)', content)
    # Pattern 2: W_NAME=0.20 style
    weights_vars = re.findall(r'^W_\w+\s*=\s*(\d+\.\d+)', content, re.MULTILINE)
    # Pattern 3: (0.20): style annotations in comments
    weights_annotated = re.findall(r'\((\d+\.\d+)\)\s*:', content)

    # Prefer WEIGHTS[] > W_vars > annotations (most specific first)
    weights = weights_declared or weights_vars or weights_annotated
    if not weights:
        result.issues.append(LintIssue(
            severity=Severity.WARNING,
            line=0,
            rule="no-weights",
            message="No weight annotations found. "
                    "Each check should have a weight (e.g., '(0.20): description').",
        ))
        return

    total = sum(float(w) for w in weights)
    result.weight_sum = total

    if abs(total - 1.0) > 0.05:
        result.issues.append(LintIssue(
            severity=Severity.CRITICAL,
            line=0,
            rule="weight-sum",
            message=f"Weights sum to {total:.2f}, expected 1.00 (±0.05). "
                    f"Found {len(weights)} weights: {', '.join(weights)}",
        ))


def _check_behavioral_ratio(content: str, result: LintResult) -> None:
    """Behavioral tests should be >=60% of total weight."""
    # Look for check type markers
    behavioral_w = 0.0
    structural_w = 0.0
    total_w = 0.0

    for match in re.finditer(
        r'#\s*\[(\w+)\]\s*\((\d+\.\d+)\)', content
    ):
        origin = match.group(1)
        weight = float(match.group(2))
        total_w += weight
        if origin == "pr_diff":
            behavioral_w += weight
        elif origin in ("static", "structural"):
            structural_w += weight

    # Also count labeled checks
    for label in re.findall(r'(?:behavioral|fail.to.pass|f2p|regression|p2p)', content, re.IGNORECASE):
        pass  # Just presence detection

    if total_w > 0:
        result.behavioral_ratio = behavioral_w / total_w
        if result.behavioral_ratio < 0.55:
            result.issues.append(LintIssue(
                severity=Severity.WARNING,
                line=0,
                rule="low-behavioral",
                message=f"Behavioral ratio is {result.behavioral_ratio:.0%} "
                        f"(behavioral={behavioral_w:.2f}, total={total_w:.2f}). "
                        "Target is >=60%.",
            ))


def _check_gate(content: str, result: LintResult) -> None:
    """Should have a gate check (syntax/compilation) that aborts on failure."""
    gate_patterns = [
        r'GATE',
        r'gate.*fail',
        r'ast\.parse',
        r'python3\s+-c\s+.*compile',
        r'cargo\s+check',
        r'cargo\s+build',
        r'syntax.*check',
    ]
    result.has_gate = any(re.search(p, content, re.IGNORECASE) for p in gate_patterns)
    if not result.has_gate:
        result.issues.append(LintIssue(
            severity=Severity.WARNING,
            line=0,
            rule="no-gate",
            message="No gate/syntax check found. test.sh should have a gate that "
                    "aborts (score=0) if the code doesn't parse/compile.",
        ))


def _check_f2p(content: str, result: LintResult) -> None:
    """Should have at least one fail-to-pass behavioral test."""
    f2p_patterns = [
        r'fail.to.pass',
        r'f2p',
        r'FAIL.*on.*buggy',
        r'should.*fail.*before.*fix',
        r'behavioral.*fail',
    ]
    result.has_f2p = any(re.search(p, content, re.IGNORECASE) for p in f2p_patterns)
    if not result.has_f2p:
        result.issues.append(LintIssue(
            severity=Severity.WARNING,
            line=0,
            rule="no-f2p",
            message="No fail-to-pass test detected. At least one test should "
                    "FAIL on the buggy code and PASS after the fix.",
        ))


def _check_comment_stripping(lines: Sequence[str], result: LintResult) -> None:
    """Anti-pattern: grep/regex on source without stripping comments first.

    48% of v1 tasks had this — agent can inject keywords via comments.
    Maps to anti-pattern #9 (keyword stuffing).
    """
    for i, line in enumerate(lines):
        stripped = line.strip()
        # Looking for: grep "keyword" $FILE or grep -q "keyword" $FILE
        # WITHOUT a prior comment-stripping step
        if re.match(r'(grep|rg)\s+(-[a-z]+\s+)*["\']', stripped):
            # Check if there's comment stripping nearby (within 10 lines before)
            context = "\n".join(lines[max(0, i - 10):i])
            if not re.search(r'strip.*comment|remove.*comment|sed.*#|grep -v.*#', context, re.IGNORECASE):
                # Check if this is checking source code (not test output)
                if any(kw in stripped for kw in ['$TARGET', '$FILE', '/workspace', '.py', '.rs', '.ts', '.js']):
                    result.issues.append(LintIssue(
                        severity=Severity.WARNING,
                        line=i + 1,
                        rule="comment-injection",
                        message="grep on source without comment stripping — agent can "
                                "inject keywords via comments to pass this check",
                        antipattern=9,
                    ))
                    break  # Report once, not per-line


def _check_import_fallback(lines: Sequence[str], result: LintResult) -> None:
    """Anti-pattern #2: AST fallback on import failure.

    try: from X import fn; test(fn)
    except: check_ast()
    → stub file with keywords passes the fallback.
    """
    in_try = False
    has_import_in_try = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if 'try:' in stripped or 'try {' in stripped:
            in_try = True
            has_import_in_try = False
        elif in_try and ('import ' in stripped or 'require(' in stripped):
            has_import_in_try = True
        elif in_try and ('except' in stripped or 'catch' in stripped):
            if has_import_in_try:
                # Check if the except block does AST/structural checking
                next_lines = "\n".join(lines[i:i + 5])
                if re.search(r'ast\.|structural|grep|check_', next_lines, re.IGNORECASE):
                    result.issues.append(LintIssue(
                        severity=Severity.CRITICAL,
                        line=i + 1,
                        rule="import-fallback",
                        message="Import failure falls back to AST/structural check — "
                                "stub file with keywords passes the fallback. "
                                "Import failure should = 0 points.",
                        antipattern=2,
                    ))
            in_try = False


def _check_file_exists_fallback(lines: Sequence[str], result: LintResult) -> None:
    """Anti-pattern #10: Import fallback to file-exists check.

    try: import_module(X)
    except: if os.path.exists(file): REWARD += X
    → empty file scores points.
    """
    for i, line in enumerate(lines):
        if 'os.path.exists' in line or 'test -f' in line or '[ -f' in line:
            context = "\n".join(lines[max(0, i - 5):i + 3])
            if re.search(r'except|catch|\|\||!\s|else|fi', context):
                score_context = "\n".join(lines[i:i + 5])
                if re.search(r'REWARD|SCORE|PASS|score|reward', score_context, re.IGNORECASE):
                    result.issues.append(LintIssue(
                        severity=Severity.CRITICAL,
                        line=i + 1,
                        rule="exists-fallback",
                        message="File-exists check in error fallback awards points — "
                                "empty file scores. Remove existence fallbacks.",
                        antipattern=10,
                    ))
                    break


def _check_ungated_structural(content: str, result: LintResult) -> None:
    """Anti-patterns #7/#8: Structural checks that run without behavioral gate.

    Structural points should only be awarded if behavioral/compilation passed.
    """
    # Look for structural checks that have no gating
    has_gate_var = bool(re.search(r'GATE_PASS|gate_pass|BEHAVIORAL_PASS', content))
    has_structural = bool(re.search(r'structural|anti.stub|antistub', content, re.IGNORECASE))

    if has_structural and not has_gate_var:
        # Check if structural checks reference a gate condition
        structural_sections = re.findall(
            r'(?:structural|anti.stub|antistub).*?(?=(?:structural|anti.stub|Final|$))',
            content, re.IGNORECASE | re.DOTALL
        )
        for section in structural_sections:
            if not re.search(r'if.*(?:GATE|gate|BEHAVIORAL|behavioral|PASS)', section):
                result.issues.append(LintIssue(
                    severity=Severity.WARNING,
                    line=0,
                    rule="ungated-structural",
                    message="Structural/anti-stub checks may run even when gate fails. "
                            "Gate all structural points behind behavioral/compilation passing.",
                    antipattern=7,
                ))
                break


def _check_annotations(content: str, result: LintResult) -> None:
    """Checks should have source annotations: [pr_diff], [agent_config], etc."""
    has_annotations = bool(re.search(
        r'\[(pr_diff|agent_config|repo_tests|static)\]', content
    ))
    if not has_annotations:
        result.issues.append(LintIssue(
            severity=Severity.INFO,
            line=0,
            rule="no-annotations",
            message="No source annotations found ([pr_diff], [agent_config], etc.). "
                    "Each check should declare its origin for traceability.",
        ))


def _check_antistub_threshold(content: str, result: LintResult) -> None:
    """Anti-stub checks should require sufficient code depth."""
    # Look for line-count anti-stub checks with low thresholds
    for match in re.finditer(r'(?:wc -l|LINE_COUNT|line_count).*?(\d+)', content):
        threshold = int(match.group(1))
        if threshold < 10 and 'anti' in content[max(0, match.start() - 100):match.end()].lower():
            result.issues.append(LintIssue(
                severity=Severity.INFO,
                line=0,
                rule="low-antistub",
                message=f"Anti-stub line-count threshold is {threshold} — "
                        "consider raising to ≥20 for meaningful stub detection.",
            ))
            break


# ---------------------------------------------------------------------------
# solve.sh linter
# ---------------------------------------------------------------------------

def lint_solve_sh(content: str) -> LintResult:
    """Run lint checks on a solve.sh file."""
    result = LintResult()
    lines = content.splitlines()

    _check_patch_trailing_newline(content, lines, result)
    _check_solve_idempotent(content, lines, result)
    _check_solve_heredoc(content, lines, result)

    return result


def _check_patch_trailing_newline(content: str, lines: Sequence[str], result: LintResult) -> None:
    """Patch content must end with a blank line before the PATCH delimiter."""
    for i, line in enumerate(lines):
        if line.strip() == "PATCH" and i > 0:
            prev = lines[i - 1]
            if prev.strip():  # Non-blank line immediately before PATCH
                result.issues.append(LintIssue(
                    severity=Severity.CRITICAL,
                    line=i + 1,
                    rule="patch-no-trailing-newline",
                    message="Missing blank line before PATCH delimiter — git apply will fail.",
                ))
            break


def _check_solve_idempotent(content: str, lines: Sequence[str], result: LintResult) -> None:
    """solve.sh should have an idempotency check (grep + exit 0)."""
    has_idem = any("grep -q" in line or "already applied" in line.lower() for line in lines)
    if not has_idem:
        result.issues.append(LintIssue(
            severity=Severity.WARNING,
            line=0,
            rule="solve-no-idempotent",
            message="solve.sh has no idempotency check (grep for distinctive line + exit 0).",
        ))


def _check_solve_heredoc(content: str, lines: Sequence[str], result: LintResult) -> None:
    """solve.sh should use single-quoted HEREDOC (<<'PATCH' not <<PATCH)."""
    for i, line in enumerate(lines):
        if "<<PATCH" in line and "<<'PATCH'" not in line and '<<"PATCH"' not in line:
            result.issues.append(LintIssue(
                severity=Severity.WARNING,
                line=i + 1,
                rule="solve-unquoted-heredoc",
                message="HEREDOC should be single-quoted (<<'PATCH') to prevent variable expansion.",
            ))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _get_tasks(task_dir: str | None, pattern: str | None) -> list:
    """List task directories, optionally filtered by glob pattern."""
    import fnmatch
    from pathlib import Path

    root = Path(__file__).parent.parent
    base = root / (task_dir or "markdown_following")
    if not base.exists():
        return []
    tasks = sorted(t for t in base.iterdir() if t.is_dir() and (t / "tests" / "test.sh").exists())
    if pattern:
        tasks = [t for t in tasks if fnmatch.fnmatch(t.name, pattern)]
    return tasks


def main() -> None:
    import argparse
    import json
    import sys

    parser = argparse.ArgumentParser(description="Lint harbor task test.sh files")
    parser.add_argument("--tasks", help="Glob pattern for task names (e.g., 'sglang-*')")
    parser.add_argument("--task-dir", help="Task directory (default: markdown_following)")
    parser.add_argument("--severity", choices=["critical", "warning", "info"], default="warning")
    parser.add_argument("--json", action="store_true", dest="json_output")
    args = parser.parse_args()

    min_severity = {"critical": 0, "warning": 1, "info": 2}[args.severity]
    severity_order = {Severity.CRITICAL: 0, Severity.WARNING: 1, Severity.INFO: 2}

    tasks = _get_tasks(args.task_dir, args.tasks)
    if not tasks:
        print("No tasks found.")
        sys.exit(1)

    print(f"Linting {len(tasks)} tasks...\n")

    total_issues = 0
    total_critical = 0
    total_passed = 0
    all_results = []

    for task_dir in tasks:
        test_sh = (task_dir / "tests" / "test.sh").read_text()
        result = lint_test_sh(test_sh)

        filtered = [i for i in result.issues if severity_order[i.severity] <= min_severity]

        if args.json_output:
            all_results.append({
                "task": task_dir.name,
                "passed": result.passed,
                "weight_sum": result.weight_sum,
                "has_gate": result.has_gate,
                "issues": [
                    {"severity": i.severity.value, "rule": i.rule,
                     "line": i.line, "message": i.message, "antipattern": i.antipattern}
                    for i in filtered
                ],
            })
        elif filtered:
            print(f"{'FAIL' if result.critical_count else 'WARN'} {task_dir.name}")
            for issue in filtered:
                prefix = "  !!" if issue.severity == Severity.CRITICAL else "  ."
                loc = f":{issue.line}" if issue.line else ""
                print(f"{prefix} [{issue.rule}]{loc} {issue.message}")
            print()

        total_issues += len(filtered)
        total_critical += result.critical_count
        if result.passed:
            total_passed += 1

    if args.json_output:
        json.dump(all_results, sys.stdout, indent=2)
        print()
    else:
        print(f"{'='*60}")
        print(f"  {len(tasks)} tasks linted")
        print(f"  {total_passed} passed ({total_passed * 100 // len(tasks)}%)")
        print(f"  {total_critical} critical issues")
        print(f"  {total_issues} total issues (at {args.severity}+ severity)")
        print(f"{'='*60}")


if __name__ == "__main__":
    main()
