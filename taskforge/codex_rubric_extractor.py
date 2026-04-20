#!/usr/bin/env python3
"""Codex CLI-based rubric extractor — exact line numbers, no hallucination.

Uses `codex exec` (GPT-5.4) to navigate a cloned repo, read config files
with `cat -n`, cross-reference against the gold diff, and extract:
  - Rubric rules (conventions the gold diff follows)
  - Distractors (conventions that seem relevant but shouldn't apply)
  - Skipped rules (workflow, irrelevant, too generic)

Key advantage over Gemini: Codex reads files directly → exact line numbers.
No line drift, no hallucinated source text.

Usage:
    # Single task
    .venv/bin/python -m taskforge.codex_rubric_extractor \
        --task harbor_tasks_agentmd_edits/playwright-featmcp-add-cdp-option-to

    # Batch (parallel)
    .venv/bin/python -m taskforge.codex_rubric_extractor \
        --task-dir harbor_tasks_agentmd_edits --limit 10 --concurrency 3

    # Dry run (show what would be processed)
    .venv/bin/python -m taskforge.codex_rubric_extractor \
        --task-dir harbor_tasks_agentmd_edits --dry-run
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import yaml

ROOT = Path(__file__).resolve().parent.parent

# ── JSON Schema for Codex structured output ──────────────────────────────────

CODEX_OUTPUT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "config_files_found": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "path": {"type": "string"},
                    "type": {"type": "string"},
                    "total_lines": {"type": "integer"},
                },
                "required": ["path", "type", "total_lines"],
            },
        },
        "rubric_rules": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "rule": {"type": "string"},
                    "source_path": {"type": "string"},
                    "source_lines": {"type": "string"},
                    "source_text": {"type": "string"},
                    "evidence_in_gold": {"type": "string"},
                    "category": {"type": "string"},
                    "verification": {"type": "string"},
                },
                "required": [
                    "rule", "source_path", "source_lines", "source_text",
                    "evidence_in_gold", "category", "verification",
                ],
            },
        },
        "distractor_rules": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "rule": {"type": "string"},
                    "source_path": {"type": "string"},
                    "source_lines": {"type": "string"},
                    "source_text": {"type": "string"},
                    "collision_type": {"type": "string"},
                    "why_distracting": {"type": "string"},
                    "severity": {"type": "string"},
                },
                "required": [
                    "rule", "source_path", "source_lines", "source_text",
                    "collision_type", "why_distracting", "severity",
                ],
            },
        },
        "skipped_rules": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "rule_summary": {"type": "string"},
                    "source_path": {"type": "string"},
                    "source_lines": {"type": "string"},
                    "skip_reason": {"type": "string"},
                },
                "required": ["rule_summary", "source_path", "source_lines", "skip_reason"],
            },
        },
    },
    "required": ["config_files_found", "rubric_rules", "distractor_rules", "skipped_rules"],
}

# ── Prompt template ──────────────────────────────────────────────────────────

CODEX_PROMPT = """\
# Task: Extract Rubric Rules and Distractors from Agent Config Files

You are analyzing a repository to extract **coding convention rules** from agent \
configuration files (CLAUDE.md, AGENTS.md, SKILL.md, etc.) that are relevant to \
a specific code change (the "gold diff").

## Your Job

1. **Read each config file** listed below using `cat -n` to see exact line numbers.{config_files_hint}
2. **Read the gold diff** at {diff_path}
3. **Extract rules** from config files into three categories:

### Category A: Rubric Rules (gold diff FOLLOWS this convention)
Rules from config files that the gold diff demonstrably follows. These must be:
- Imperative coding conventions (naming, architecture, imports, testing patterns, \
config patterns, style, error handling)
- NOT workflow instructions ("run pre-commit", "use git add", "create PR", "push")
- Actually followed by the gold diff (provide specific evidence from the diff)

### Category B: Distractor Rules (gold diff correctly IGNORES this convention)
Rules from config files that SEEM relevant to the PR but should NOT be followed because:
- They apply to a different scope/domain than the changed files
- Following them would cause a bug or break architecture boundaries
- They conflict with the specific requirements of this change
- They mention technologies/patterns used in the diff but for a different purpose

### Category C: Skip (workflow, irrelevant, too generic)
Rules about git operations, PR creation, build commands, test execution — NOT about \
code patterns. Also skip rules completely unrelated to the changed files' domain.

## CRITICAL Requirements

- **Exact line numbers**: Use `cat -n <file>` to read config files. Report the EXACT \
line range where each rule appears. Do NOT guess or approximate.
- **Quote source text**: Copy the verbatim text from the config file at those lines.
- **Evidence for rubric rules**: Show specifically how the gold diff follows the rule \
(reference actual code, variable names, patterns from the diff).
- **Why distracting**: For distractors, explain why an agent working on THIS specific \
change might mistakenly follow this rule.
- **No workflow rules**: Skip anything about: running commands, git operations, PR \
creation, CI/CD, pre-commit hooks, build systems, deployment.
- **Collision types** for distractors: rule_conflict, scope_ambiguity, meta_confusion, \
architecture_boundary, would_cause_bug
- **Severity** for distractors: high (would cause bug), medium (wasted effort), \
low (minor confusion)

## Output

Produce your response as structured JSON matching the --output-schema.
"""


# ── Core functions ───────────────────────────────────────────────────────────

def extract_gold_diff(task_path: Path) -> str:
    """Extract the gold diff from solve.sh."""
    solve_sh = task_path / "solution" / "solve.sh"
    if not solve_sh.exists():
        return ""
    text = solve_sh.read_text()

    # Try to extract patch content between PATCH markers
    match = re.search(r"git apply.*?<<\s*['\"]?PATCH['\"]?\n(.*?)^PATCH", text,
                      re.MULTILINE | re.DOTALL)
    if match:
        return match.group(1)

    # Try diff blocks
    match = re.search(r"(diff --git.*)", text, re.DOTALL)
    if match:
        # Remove trailing PATCH/EOF markers
        diff = match.group(1)
        diff = re.sub(r"\n(PATCH|EOF)\s*$", "", diff)
        return diff

    return ""


def get_repo_info(task_path: Path) -> tuple[str, str]:
    """Extract repo URL and commit from Dockerfile."""
    df = task_path / "environment" / "Dockerfile"
    if not df.exists():
        return "", ""
    text = df.read_text()

    repo = ""
    # Allow dots in repo names (e.g. vercel/next.js)
    match = re.search(r"github\.com/([^/\s]+/[^\s]+?)(?:\.git|[\s]|$)", text)
    if match:
        repo = match.group(1)

    commit = ""
    for pattern in [
        r"git checkout\s+([a-f0-9]{7,40})",
        r"ARG\s+BASE_COMMIT=([a-f0-9]{7,40})",
        r"git fetch.*origin\s+([a-f0-9]{7,40})",
    ]:
        m = re.search(pattern, text)
        if m:
            commit = m.group(1)
            break

    return repo, commit


def clone_or_checkout(repo: str, commit: str, cache_dir: Path) -> Path | None:
    """Shallow-clone repo at specific commit. Uses git init + fetch --depth=1."""
    repo_dir = cache_dir / repo.replace("/", "_")

    if repo_dir.exists() and (repo_dir / ".git").exists():
        # Already have a clone — try checkout, then shallow fetch if needed
        try:
            result = subprocess.run(
                ["git", "checkout", commit],
                capture_output=True, text=True, cwd=repo_dir, timeout=30,
            )
            if result.returncode == 0:
                return repo_dir
        except Exception:
            pass
        # Fetch this specific commit (shallow)
        try:
            subprocess.run(
                ["git", "fetch", "--depth=1", "origin", commit],
                capture_output=True, text=True, cwd=repo_dir, timeout=120,
            )
            subprocess.run(
                ["git", "checkout", commit],
                capture_output=True, text=True, cwd=repo_dir, timeout=30,
            )
            return repo_dir
        except Exception:
            pass

    # Fresh shallow clone at specific commit
    repo_dir.mkdir(parents=True, exist_ok=True)
    try:
        if not (repo_dir / ".git").exists():
            subprocess.run(
                ["git", "init", str(repo_dir)],
                capture_output=True, text=True, timeout=10, check=True,
            )
            subprocess.run(
                ["git", "remote", "add", "origin",
                 f"https://github.com/{repo}.git"],
                capture_output=True, text=True, cwd=repo_dir, timeout=10,
                check=True,
            )
        subprocess.run(
            ["git", "fetch", "--depth=1", "origin", commit],
            capture_output=True, text=True, cwd=repo_dir, timeout=300,
            check=True,
        )
        subprocess.run(
            ["git", "checkout", commit],
            capture_output=True, text=True, cwd=repo_dir, timeout=60,
            check=True,
        )
        return repo_dir
    except Exception as e:
        print(f"  Clone failed for {repo}@{commit[:10]}: {e}")
        return None


def _discover_config_files(repo_dir: Path) -> list[str]:
    """Pre-discover agent config files in the repo."""
    patterns = [
        "CLAUDE.md", "AGENTS.md", "CONVENTIONS.md", ".cursorrules",
    ]
    globs = [
        "**/CLAUDE.md", "**/AGENTS.md", "**/SKILL.md", "**/CONVENTIONS.md",
        ".claude/rules/*.md", ".claude/skills/*/*.md",
        ".cursor/rules/*.md",
        "**/skill/SKILL.md", "**/.agents/**/*.md",
    ]
    found = set()
    for g in globs:
        for p in repo_dir.glob(g):
            rel = str(p.relative_to(repo_dir))
            if not rel.startswith(".git/") and not "/node_modules/" in rel:
                found.add(rel)
    return sorted(found)


def run_codex_extraction(
    repo_dir: Path,
    gold_diff: str,
    model: str = "gpt-5.4",
    timeout: int = 600,
) -> dict | None:
    """Run codex exec on the repo to extract rubric rules.

    Returns parsed JSON output or None on failure.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Write diff to temp file
        diff_path = tmpdir / "gold_diff.patch"
        diff_path.write_text(gold_diff)

        # Write schema
        schema_path = tmpdir / "output_schema.json"
        schema_path.write_text(json.dumps(CODEX_OUTPUT_SCHEMA))

        # Write output path
        output_path = tmpdir / "result.json"

        # Pre-discover config files to save Codex search time
        config_files = _discover_config_files(repo_dir)
        if config_files:
            hint = "\n   Known config files in this repo:\n" + \
                   "\n".join(f"   - {f}" for f in config_files) + \
                   "\n   Also check for any you might find beyond this list."
        else:
            hint = "\n   Search the repo for config files (CLAUDE.md, AGENTS.md, SKILL.md, etc.)"

        # Build prompt
        prompt = CODEX_PROMPT.format(diff_path=str(diff_path), config_files_hint=hint)

        # Run codex exec
        # Use read-only sandbox so Codex doesn't try to load repo's SKILL.md as its own
        cmd = [
            "codex", "exec",
            "-a", "never",
            "-s", "read-only",
            "-m", model,
            "-c", "model_reasoning_effort=\"high\"",
            "--output-schema", str(schema_path),
            "-o", str(output_path),
            prompt,
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(repo_dir),
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            print(f"  Codex timed out after {timeout}s")
            return None

        if not output_path.exists() or output_path.stat().st_size == 0:
            stderr = result.stderr[:500] if result.stderr else ""
            stdout = result.stdout[:500] if result.stdout else ""
            print(f"  Codex produced no output. stderr: {stderr}")
            print(f"  stdout: {stdout}")
            return None

        try:
            return json.loads(output_path.read_text())
        except json.JSONDecodeError as e:
            print(f"  Invalid JSON from Codex: {e}")
            return None


def merge_codex_result(
    manifest_path: Path,
    codex_result: dict,
    replace: bool = False,
) -> tuple[int, int, int]:
    """Merge Codex extraction results into eval_manifest.yaml.

    Args:
        manifest_path: Path to eval_manifest.yaml
        codex_result: Parsed Codex output
        replace: If True, replace existing rubric/distractors entirely.
                 If False, only add new rules (dedup by rule text prefix).

    Returns:
        (added_rubrics, added_distractors, skipped_count)
    """
    m = yaml.safe_load(manifest_path.read_text())
    if not m:
        return 0, 0, 0

    existing_rubric = m.get("rubric", []) or []
    existing_distractors = m.get("distractors", []) or []

    # Build dedup sets from existing rules
    existing_rule_keys = {
        r.get("rule", "")[:50].lower().strip()
        for r in existing_rubric if isinstance(r, dict)
    }
    existing_distractor_keys = {
        d.get("rule", "")[:50].lower().strip()
        for d in existing_distractors if isinstance(d, dict)
    }

    # Convert Codex rubric rules
    new_rubrics = []
    for r in codex_result.get("rubric_rules", []):
        rule_text = r.get("rule", "")
        if not rule_text or len(rule_text) < 15:
            continue
        if not replace and rule_text[:50].lower().strip() in existing_rule_keys:
            continue
        new_rubrics.append({
            "rule": rule_text,
            "source": {
                "path": r.get("source_path", ""),
                "lines": r.get("source_lines", ""),
            },
            "source_text": r.get("source_text", ""),
            "evidence": r.get("evidence_in_gold", ""),
            "category": r.get("category", ""),
            "verification": "llm_judge",
        })

    # Convert Codex distractor rules
    new_distractors = []
    for d in codex_result.get("distractor_rules", []):
        rule_text = d.get("rule", "")
        if not rule_text or len(rule_text) < 15:
            continue
        if not replace and rule_text[:50].lower().strip() in existing_distractor_keys:
            continue
        new_distractors.append({
            "rule": rule_text,
            "source": {
                "path": d.get("source_path", ""),
                "lines": d.get("source_lines", ""),
            },
            "source_text": d.get("source_text", ""),
            "collision_type": d.get("collision_type", "scope_ambiguity"),
            "why_distracting": d.get("why_distracting", ""),
            "severity": d.get("severity", "medium"),
        })

    skipped = len(codex_result.get("skipped_rules", []))

    if replace:
        m["rubric"] = new_rubrics
        m["distractors"] = new_distractors
    else:
        m["rubric"] = existing_rubric + new_rubrics
        m["distractors"] = existing_distractors + new_distractors

    # Only write if we have changes
    if new_rubrics or new_distractors:
        manifest_path.write_text(
            yaml.dump(m, default_flow_style=False, sort_keys=False, allow_unicode=True)
        )

    return len(new_rubrics), len(new_distractors), skipped


def process_task(
    task_path: Path,
    repo_cache: dict[str, Path],
    cache_dir: Path,
    model: str = "gpt-5.4",
    replace: bool = False,
    timeout: int = 300,
) -> dict:
    """Process a single task: clone repo, extract diff, run Codex, merge results."""
    task_name = task_path.name
    result = {
        "task": task_name,
        "status": "error",
        "rubrics_added": 0,
        "distractors_added": 0,
        "skipped": 0,
        "config_files": 0,
        "error": "",
        "time": 0,
    }

    t_start = time.monotonic()

    # Get repo info
    repo, commit = get_repo_info(task_path)
    if not repo or not commit:
        result["error"] = "no repo/commit in Dockerfile"
        return result
    result["repo"] = repo

    # Extract gold diff
    gold_diff = extract_gold_diff(task_path)
    if not gold_diff:
        result["error"] = "no gold diff in solve.sh"
        return result

    # Clone/checkout repo
    repo_dir = repo_cache.get(repo)
    if not repo_dir:
        repo_dir = clone_or_checkout(repo, commit, cache_dir)
        if not repo_dir:
            result["error"] = "clone failed"
            return result
        repo_cache[repo] = repo_dir
    else:
        # Checkout right commit
        try:
            subprocess.run(
                ["git", "checkout", commit],
                capture_output=True, text=True, cwd=repo_dir, timeout=30,
            )
        except Exception:
            pass

    # Run Codex
    codex_result = run_codex_extraction(repo_dir, gold_diff, model=model, timeout=timeout)
    if not codex_result:
        result["error"] = "codex extraction failed"
        result["time"] = time.monotonic() - t_start
        return result

    result["config_files"] = len(codex_result.get("config_files_found", []))

    # Merge into manifest
    manifest_path = task_path / "eval_manifest.yaml"
    if not manifest_path.exists():
        result["error"] = "no eval_manifest.yaml"
        result["time"] = time.monotonic() - t_start
        return result

    added_r, added_d, skipped = merge_codex_result(
        manifest_path, codex_result, replace=replace
    )

    result["rubrics_added"] = added_r
    result["distractors_added"] = added_d
    result["skipped"] = skipped
    result["status"] = "ok" if (added_r + added_d) > 0 else "no_new_rules"
    result["time"] = time.monotonic() - t_start

    return result


# ── Scanning ─────────────────────────────────────────────────────────────────

def scan_tasks(
    task_dir: str | None = None,
    category: str = "all",
) -> list[Path]:
    """Find tasks that need rubric extraction."""
    tasks = []

    dirs = [task_dir] if task_dir else ["harbor_tasks", "harbor_tasks_agentmd_edits"]

    for base in dirs:
        base_path = ROOT / base
        if not base_path.exists():
            continue
        for task in sorted(base_path.iterdir()):
            if not task.is_dir():
                continue
            manifest = task / "eval_manifest.yaml"
            solve = task / "solution" / "solve.sh"
            dockerfile = task / "environment" / "Dockerfile"
            if not manifest.exists() or not solve.exists() or not dockerfile.exists():
                continue

            try:
                m = yaml.safe_load(manifest.read_text())
            except Exception:
                continue
            if not m:
                continue

            rubric = m.get("rubric", []) or []
            distractors = m.get("distractors", []) or []

            if category == "weak" and len(rubric) > 1:
                continue
            elif category == "no_distractors" and distractors:
                continue
            elif category == "no_rubric" and rubric:
                continue
            elif category == "all":
                pass  # Include everything

            tasks.append(task)

    return tasks


# ── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Extract rubric rules using Codex CLI (exact line numbers)"
    )
    parser.add_argument("--task", type=str, help="Single task path (relative to repo root)")
    parser.add_argument("--task-dir", type=str, help="Task directory to scan")
    parser.add_argument("--category", choices=["all", "weak", "no_rubric", "no_distractors"],
                        default="all")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--concurrency", type=int, default=3,
                        help="Parallel Codex processes")
    parser.add_argument("--model", type=str, default="gpt-5.4")
    parser.add_argument("--replace", action="store_true",
                        help="Replace existing rubric/distractors (vs merge)")
    parser.add_argument("--timeout", type=int, default=600,
                        help="Per-task Codex timeout in seconds")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--cache-dir", type=str, default="/tmp/repo_cache")
    args = parser.parse_args()

    # Check codex is available
    try:
        subprocess.run(["codex", "--version"], capture_output=True, timeout=5)
    except Exception:
        print("ERROR: codex CLI not found. Install with: npm install -g @openai/codex")
        sys.exit(1)

    if args.task:
        task_path = ROOT / args.task
        if not task_path.exists():
            print(f"Task not found: {task_path}")
            sys.exit(1)
        tasks = [task_path]
    else:
        tasks = scan_tasks(task_dir=args.task_dir, category=args.category)
        tasks = tasks[args.offset:]
        if args.limit:
            tasks = tasks[:args.limit]

    print(f"Tasks to process: {len(tasks)}")

    if args.dry_run:
        for t in tasks[:30]:
            repo, commit = get_repo_info(t)
            diff = extract_gold_diff(t)
            diff_lines = len(diff.splitlines()) if diff else 0
            print(f"  {t.parent.name}/{t.name} repo={repo} diff={diff_lines}L")
        if len(tasks) > 30:
            print(f"  ... and {len(tasks) - 30} more")
        return

    cache_dir = Path(args.cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    repo_cache: dict[str, Path] = {}

    # Group by repo for efficient cloning
    from itertools import groupby
    tasks_with_repo = []
    for t in tasks:
        repo, commit = get_repo_info(t)
        tasks_with_repo.append((repo, t))
    tasks_with_repo.sort(key=lambda x: x[0])

    results = []
    t_start = time.monotonic()
    processed = 0

    if args.concurrency <= 1:
        # Sequential
        for repo, task in tasks_with_repo:
            processed += 1
            print(f"[{processed}/{len(tasks)}] {task.name} ({repo})")
            result = process_task(
                task, repo_cache, cache_dir,
                model=args.model, replace=args.replace, timeout=args.timeout,
            )
            results.append(result)
            _print_result(result)
    else:
        # Parallel — group by repo, process each group sequentially
        # but run groups in parallel
        repo_groups = [
            (k, [t for _, t in g])
            for k, g in groupby(tasks_with_repo, key=lambda x: x[0])
        ]

        def process_group(repo: str, group_tasks: list[Path]) -> list[dict]:
            group_results = []
            for task in group_tasks:
                r = process_task(
                    task, repo_cache, cache_dir,
                    model=args.model, replace=args.replace, timeout=args.timeout,
                )
                group_results.append(r)
            return group_results

        with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
            futures = {
                pool.submit(process_group, repo, group): (repo, group)
                for repo, group in repo_groups
            }
            for future in as_completed(futures):
                repo, group = futures[future]
                try:
                    group_results = future.result()
                    for r in group_results:
                        processed += 1
                        print(f"[{processed}/{len(tasks)}] {r['task']} ({repo})")
                        _print_result(r)
                    results.extend(group_results)
                except Exception as e:
                    print(f"  GROUP ERROR ({repo}): {e}")

    elapsed = time.monotonic() - t_start

    # Summary
    ok = sum(1 for r in results if r["status"] == "ok")
    no_new = sum(1 for r in results if r["status"] == "no_new_rules")
    errors = sum(1 for r in results if r["status"] == "error")
    total_r = sum(r["rubrics_added"] for r in results)
    total_d = sum(r["distractors_added"] for r in results)

    print()
    print("=" * 70)
    print(f"  CODEX RUBRIC EXTRACTION COMPLETE")
    print(f"  Processed:     {len(results)}")
    print(f"  Updated:       {ok}")
    print(f"  No new rules:  {no_new}")
    print(f"  Errors:        {errors}")
    print(f"  +Rubrics:      {total_r}")
    print(f"  +Distractors:  {total_d}")
    print(f"  Time:          {elapsed:.1f}s ({elapsed / 60:.1f}m)")
    print(f"  Avg per task:  {elapsed / max(len(results), 1):.1f}s")
    print("=" * 70)

    # Save results log
    ts = time.strftime("%Y%m%d_%H%M%S")
    log_dir = ROOT / "pipeline_logs"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"codex_rubric_{ts}.json"
    log_file.write_text(json.dumps(results, indent=2))
    print(f"\nResults: {log_file}")


def _print_result(result: dict):
    """Print a single task result."""
    if result["status"] == "ok":
        print(f"  OK: +{result['rubrics_added']}R +{result['distractors_added']}D "
              f"(skip={result['skipped']}, files={result['config_files']}) "
              f"[{result['time']:.1f}s]")
    elif result["status"] == "no_new_rules":
        print(f"  SKIP: no new rules [{result['time']:.1f}s]")
    else:
        print(f"  ERROR: {result['error'][:80]}")


if __name__ == "__main__":
    main()
