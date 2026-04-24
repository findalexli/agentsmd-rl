#!/usr/bin/env python3
"""Auto-fix tests/test.sh reward-purity bugs surfaced by the reward_is_pure_pytest
rubric (2026-04-24).

Applies 3 mechanically-safe fixes:

  wrong_path : /logs/verifier/reward      →  /logs/verifier/reward.txt
               /logs/verifier/reward.json →  /logs/verifier/reward.txt

  early_exit : `exit $?` / `exit $exit_code` / `exit <num>` BEFORE the
               "--- LLM Judge ---" marker → commented out (judge block
               was unreachable)

  json_reward: `echo '{reward: 1.0, status: success}' > ...reward.json`
               → `echo 1 > /logs/verifier/reward.txt`
               (and the corresponding 0.0/failure line → `echo 0 > …`)

NOT fixed (needs manual review — semantic context required):

  grep_gate      — `pytest | grep failed` deciding reward. The right fix
                   is to use `$?` but requires knowing the pytest
                   invocation, which varies. Flagged for human review.
  silent_install — `pip install pytest || true`. Safer long-term to fail
                   loud, but some tasks intentionally tolerate pip failures
                   when pytest is already baked in. Flagged for review.

Usage:
    .venv/bin/python scripts/fix_reward_purity.py --dry-run          # list affected, show diffs
    .venv/bin/python scripts/fix_reward_purity.py --apply            # write fixes
    .venv/bin/python scripts/fix_reward_purity.py --tasks a,b,c --apply   # subset
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
HARBOR_TASKS = ROOT / "harbor_tasks"

from taskforge.task_lint import lint_test_sh  # noqa: E402


# ─── Regexes for the 3 auto-fixable patterns ────────────────────────────────

# Match `/logs/verifier/reward` or `/logs/verifier/reward.json` on a write line
# (echo/cat/tee/> write). Don't touch reward.txt (already canonical), reward.log
# (intentional logging), or reward.json inside comments.
_WRONG_PATH_LINE_RE = re.compile(
    r"(echo\s+['\"]?[01](?:\.\d+)?['\"]?\s*>\s*)/logs/verifier/reward(\.json\b|\b(?!\.txt))",
)

# Match `echo '{reward: <n>, status: <s>}' > /logs/verifier/reward.<ext>` and
# replace with `echo <0|1> > /logs/verifier/reward.txt`.
# Capture group 1 = the 1.0/true/success side vs 0.0/false/failure side.
_JSON_REWARD_SUCCESS = re.compile(
    r"echo\s+['\"]?\{\s*reward\s*:\s*1(?:\.0+)?\s*,\s*status\s*:\s*\w+\s*\}['\"]?"
    r"\s*>\s*/logs/verifier/reward\.(?:json|yaml|yml)",
)
_JSON_REWARD_FAILURE = re.compile(
    r"echo\s+['\"]?\{\s*reward\s*:\s*0(?:\.0+)?\s*,\s*status\s*:\s*\w+\s*\}['\"]?"
    r"\s*>\s*/logs/verifier/reward\.(?:json|yaml|yml)",
)

# Early `exit <something>` at the top of a line. We'll only neutralize the
# first one appearing BEFORE the LLM Judge block marker.
_EXIT_STMT_LINE_RE = re.compile(
    r"^(\s*)(exit\s+(?:\$\?|\$exit_code|\$\{[^}]+\}|\d+|\$\w+)\s*)$",
    re.MULTILINE,
)

_JUDGE_MARKER_RE = re.compile(r"LLM Judge|standalone_judge\.py")


# ─── Fixers ────────────────────────────────────────────────────────────────

def fix_wrong_path(text: str) -> tuple[str, int]:
    """Normalize reward paths to .txt. Returns (new_text, count)."""
    count = 0

    def _sub(m: re.Match) -> str:
        nonlocal count
        count += 1
        return f"{m.group(1)}/logs/verifier/reward.txt"

    new_text = _WRONG_PATH_LINE_RE.sub(_sub, text)
    return new_text, count


def fix_json_reward(text: str) -> tuple[str, int]:
    """Replace JSON-valued reward with literal 0/1 to reward.txt."""
    count = 0
    new_text = _JSON_REWARD_SUCCESS.sub(
        "echo 1 > /logs/verifier/reward.txt", text,
    )
    if new_text != text:
        count += _JSON_REWARD_SUCCESS.subn(
            "echo 1 > /logs/verifier/reward.txt", text,
        )[1]
    text = new_text
    new_text = _JSON_REWARD_FAILURE.sub(
        "echo 0 > /logs/verifier/reward.txt", text,
    )
    if new_text != text:
        count += _JSON_REWARD_FAILURE.subn(
            "echo 0 > /logs/verifier/reward.txt", text,
        )[1]
    return new_text, count


def fix_early_exit(text: str) -> tuple[str, int]:
    """Comment out any `exit <x>` line that appears before the judge-block marker."""
    m = _JUDGE_MARKER_RE.search(text)
    if not m:
        return text, 0
    marker_pos = m.start()
    count = 0

    def _sub(m: re.Match) -> str:
        nonlocal count
        if m.start() >= marker_pos:
            return m.group(0)  # unchanged — after judge block
        count += 1
        return (
            f"{m.group(1)}# {m.group(2).rstrip()}"
            f"   # auto-disabled (prevented judge block from running)"
        )

    new_text = _EXIT_STMT_LINE_RE.sub(_sub, text)
    return new_text, count


# ─── Driver ────────────────────────────────────────────────────────────────

def get_flagged_tasks(explicit: list[str] | None) -> list[Path]:
    """Return task dirs that fail reward_is_pure_pytest."""
    if explicit:
        return [HARBOR_TASKS / t for t in explicit if (HARBOR_TASKS / t).is_dir()]
    out = []
    for td in sorted(HARBOR_TASKS.iterdir()):
        if not td.is_dir():
            continue
        fails = [f for f in lint_test_sh(td) if f.rubric == "reward_is_pure_pytest"]
        if fails:
            out.append(td)
    return out


def apply_fixes(text: str) -> tuple[str, dict]:
    """Apply all auto-fixes. Returns (new_text, counts_dict)."""
    counts = {}
    text, counts["wrong_path"] = fix_wrong_path(text)
    text, counts["json_reward"] = fix_json_reward(text)
    text, counts["early_exit"] = fix_early_exit(text)
    return text, counts


def task_needs_manual(findings) -> list[str]:
    """Return list of finding-detail reasons the task can't be auto-fixed."""
    reasons = []
    for f in findings:
        if "grep/awk/sed" in f.detail:
            reasons.append("grep_gate (needs manual rewrite)")
        elif "|| true`" in f.detail:
            reasons.append("silent_install (needs review)")
    return reasons


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true", help="Preview changes, don't write")
    p.add_argument("--apply", action="store_true", help="Write fixes to disk")
    p.add_argument("--tasks", default="", help="Comma-sep subset")
    p.add_argument("--verbose", action="store_true")
    args = p.parse_args()
    if not (args.dry_run or args.apply):
        p.error("Must pass --dry-run or --apply")

    explicit = [t for t in args.tasks.split(",") if t] if args.tasks else None
    tasks = get_flagged_tasks(explicit)
    print(f"Found {len(tasks)} tasks with reward_is_pure_pytest fails", file=sys.stderr)

    total_counts = {"wrong_path": 0, "json_reward": 0, "early_exit": 0}
    fully_fixed = []
    needs_manual = []
    partial = []
    unchanged = []

    for td in tasks:
        test_sh = td / "tests" / "test.sh"
        if not test_sh.exists():
            continue
        before = test_sh.read_text()
        after, counts = apply_fixes(before)

        findings = lint_test_sh(td)
        manual_reasons = task_needs_manual(findings)

        if after == before:
            unchanged.append(td.name)
            if args.verbose:
                print(f"  UNCHANGED  {td.name}  (manual: {manual_reasons})")
            continue

        for k, v in counts.items():
            total_counts[k] += v

        if args.apply:
            test_sh.write_text(after)

        # Re-lint with post-fix content (either on disk or synthetically)
        if args.apply:
            post = [f for f in lint_test_sh(td) if f.rubric == "reward_is_pure_pytest"]
        else:
            # Simulate by writing to a temp path check
            post = []  # can't easily recheck without writing
            for f in findings:
                # If this finding's pattern was in the "auto-fixable" set, assume fixed
                if any(p in f.detail for p in ("non-canonical", "JSON object", "terminates script")):
                    continue
                post.append(f)

        if post:
            partial.append((td.name, counts, [f.detail[:60] for f in post]))
        else:
            fully_fixed.append((td.name, counts))

        if manual_reasons and not post:
            needs_manual.append((td.name, manual_reasons))

    action = "APPLIED" if args.apply else "DRY-RUN"
    print(f"\n=== {action} summary ===")
    print(f"  Total changes: {sum(total_counts.values())}")
    for k, v in total_counts.items():
        print(f"    {k}: {v}")
    print(f"  Fully fixed:   {len(fully_fixed)}")
    print(f"  Partial fixed: {len(partial)}  (other fails remain — see --verbose)")
    print(f"  Unchanged:     {len(unchanged)}  (only grep_gate / silent_install remaining)")
    if args.verbose and partial:
        print("\n  Partial detail:")
        for name, counts, rem in partial[:10]:
            print(f"    {name}: fixed={counts}  remaining={rem}")


if __name__ == "__main__":
    main()
