#!/usr/bin/env python3
"""Gemini CLI-based rubric extractor — exact line numbers via cat -n.

Drop-in replacement for codex_rubric_extractor.py using `gemini` CLI
(Google's @google/gemini-cli) instead of `codex exec` (OpenAI).

Uses `gemini -p "..." -y -o json -m gemini-3.1-pro-preview` to navigate
a cloned repo, read config files with `cat -n`, cross-reference against
the gold diff, and extract rubric rules + distractors.

Key advantage over Gemini API: CLI reads files directly → exact line numbers.
No line drift, no hallucinated source text. Same approach as the Codex extractor.

Requires:
    - gemini CLI installed: npm install -g @google/gemini-cli
    - GEMINI_API_KEY env var set (or in .env)

Usage:
    # Single task
    .venv/bin/python -m taskforge.gemini_cli_rubric_extractor \
        --task harbor_tasks_agentmd_edits/playwright-featmcp-add-cdp-option-to

    # Batch (parallel)
    .venv/bin/python -m taskforge.gemini_cli_rubric_extractor \
        --task-dir harbor_tasks_agentmd_edits --limit 10 --concurrency 3

    # Dry run (show what would be processed)
    .venv/bin/python -m taskforge.gemini_cli_rubric_extractor \
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

# ── JSON output schema (embedded in prompt since CLI has no --output-schema) ──

OUTPUT_SCHEMA_TEXT = """\
{
  "config_files_found": [
    {"path": "string", "type": "string", "total_lines": integer}
  ],
  "rubric_rules": [
    {
      "rule": "string — imperative coding convention",
      "source_path": "string — repo-relative path to config file",
      "source_lines": "string — e.g. '28-32' or '15'",
      "source_text": "string — verbatim text from those lines",
      "evidence_in_gold": "string — how the gold diff follows this rule",
      "category": "string — naming|style|architecture|testing|imports|error_handling|config|documentation",
      "verification": "string — llm_judge or programmatic"
    }
  ],
  "distractor_rules": [
    {
      "rule": "string — convention that SEEMS relevant but shouldn't apply",
      "source_path": "string",
      "source_lines": "string",
      "source_text": "string",
      "collision_type": "string — rule_conflict|scope_ambiguity|meta_confusion|architecture_boundary|would_cause_bug",
      "why_distracting": "string — why an agent might mistakenly follow this",
      "severity": "string — high|medium|low"
    }
  ],
  "skipped_rules": [
    {
      "rule_summary": "string",
      "source_path": "string",
      "source_lines": "string",
      "skip_reason": "string"
    }
  ]
}
"""

# ── Prompt template ──────────────────────────────────────────────────────────

GEMINI_PROMPT = """\
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

Respond with ONLY a single JSON object (no markdown fences, no explanation, no text \
before or after). The JSON must match this schema:

{schema}
"""


# ── Core functions (shared with codex extractor) ────────────────────────────

def extract_gold_diff(task_path: Path) -> str:
    """Extract the gold diff from solve.sh.

    Tries structured diff formats first (git apply, diff --git),
    falls back to entire solve.sh for python/cat/sed-based patches.
    """
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
        diff = match.group(1)
        diff = re.sub(r"\n(PATCH|EOF)\s*$", "", diff)
        return diff

    # Fallback: return entire solve.sh — Gemini can understand
    # python/cat/sed-based patches too
    return text


def get_repo_info(task_path: Path) -> tuple[str, str]:
    """Extract repo URL and commit from Dockerfile, eval_manifest.yaml, or task.toml."""
    repo = ""
    commit = ""

    # Try Dockerfile first
    df = task_path / "environment" / "Dockerfile"
    if df.exists():
        text = df.read_text()
        # Allow dots in repo names (e.g. vercel/next.js)
        match = re.search(r"github\.com/([^/\s]+/[^\s]+?)(?:\.git|[\s]|$)", text)
        if match:
            repo = match.group(1).rstrip("/")
        for pattern in [
            r"git checkout\s+([a-f0-9]{7,40})",
            r"ARG\s+BASE_COMMIT=([a-f0-9]{7,40})",
            r"git fetch[^\n]*origin\s+([a-f0-9]{7,40})",
        ]:
            m = re.search(pattern, text)
            if m:
                commit = m.group(1)
                break

    # Fallback: eval_manifest.yaml (source.repo / source.base_commit)
    if not repo or not commit:
        manifest = task_path / "eval_manifest.yaml"
        if manifest.exists():
            try:
                m = yaml.safe_load(manifest.read_text()) or {}
                src = m.get("source", {}) or {}
                if not repo and src.get("repo"):
                    repo = str(src["repo"]).strip().strip('"')
                if not commit and src.get("base_commit"):
                    commit = str(src["base_commit"]).strip().strip('"')
            except Exception:
                pass

    # Fallback: task.toml (source_repo)
    if not repo or not commit:
        toml_path = task_path / "task.toml"
        if toml_path.exists():
            try:
                toml_text = toml_path.read_text()
                if not repo:
                    m = re.search(r'source_repo\s*=\s*"([^"]+)"', toml_text)
                    if m:
                        repo = m.group(1)
                if not commit:
                    m = re.search(r'base_commit\s*=\s*"([a-f0-9]{7,40})"', toml_text)
                    if m:
                        commit = m.group(1)
            except Exception:
                pass

    return repo, commit


def clone_or_checkout(repo: str, commit: str, cache_dir: Path) -> Path | None:
    """Shallow-clone repo at specific commit."""
    repo_dir = cache_dir / repo.replace("/", "_")

    if repo_dir.exists() and (repo_dir / ".git").exists():
        try:
            result = subprocess.run(
                ["git", "checkout", commit],
                capture_output=True, text=True, cwd=repo_dir, timeout=30,
            )
            if result.returncode == 0:
                return repo_dir
        except Exception:
            pass
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
    globs = [
        "**/CLAUDE.md", "**/AGENTS.md", "**/SKILL.md", "**/CONVENTIONS.md",
        ".claude/rules/*.md", ".claude/skills/*/*.md",
        ".cursor/rules/*.md", ".cursorrules",
        "**/skill/SKILL.md", "**/.agents/**/*.md",
    ]
    found = set()
    for g in globs:
        for p in repo_dir.glob(g):
            rel = str(p.relative_to(repo_dir))
            if not rel.startswith(".git/") and "/node_modules/" not in rel:
                found.add(rel)
    return sorted(found)


# ── Gemini CLI execution ────────────────────────────────────────────────────

def _find_gemini_bin() -> str:
    """Find the gemini CLI binary, checking nvm paths."""
    # Check PATH first
    result = shutil.which("gemini")
    if result:
        return result

    # Check common nvm locations
    nvm_dir = os.environ.get("NVM_DIR", os.path.expanduser("~/.nvm"))
    versions_dir = Path(nvm_dir) / "versions" / "node"
    if versions_dir.exists():
        for ver in sorted(versions_dir.iterdir(), reverse=True):
            candidate = ver / "bin" / "gemini"
            if candidate.exists():
                return str(candidate)

    raise FileNotFoundError(
        "gemini CLI not found. Install with: npm install -g @google/gemini-cli"
    )


def _parse_json_from_response(text: str) -> dict | None:
    """Extract JSON from Gemini's response text.

    Handles: raw JSON, markdown-fenced JSON, JSON embedded in text.
    """
    text = text.strip()

    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try markdown fences
    match = re.search(r"```(?:json)?\s*\n(.*?)```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass

    # Try finding first { to last }
    first_brace = text.find("{")
    last_brace = text.rfind("}")
    if first_brace >= 0 and last_brace > first_brace:
        try:
            return json.loads(text[first_brace:last_brace + 1])
        except json.JSONDecodeError:
            pass

    return None


def run_gemini_extraction(
    repo_dir: Path,
    gold_diff: str,
    model: str = "gemini-3.1-pro-preview",
    timeout: int = 600,
    api_key: str | None = None,
) -> dict | None:
    """Run gemini CLI on the repo to extract rubric rules.

    Returns parsed JSON output or None on failure.
    """
    gemini_bin = _find_gemini_bin()

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Write diff to temp file accessible from repo_dir
        diff_path = tmpdir / "gold_diff.patch"
        diff_path.write_text(gold_diff)

        # Pre-discover config files
        config_files = _discover_config_files(repo_dir)
        if config_files:
            hint = "\n   Known config files in this repo:\n" + \
                   "\n".join(f"   - {f}" for f in config_files) + \
                   "\n   Also check for any you might find beyond this list."
        else:
            hint = "\n   Search the repo for config files (CLAUDE.md, AGENTS.md, SKILL.md, etc.)"

        # Build prompt and write to file (too long for CLI arg)
        prompt = GEMINI_PROMPT.format(
            diff_path=str(diff_path),
            config_files_hint=hint,
            schema=OUTPUT_SCHEMA_TEXT,
        )
        prompt_path = tmpdir / "prompt.txt"
        prompt_path.write_text(prompt)

        env = os.environ.copy()
        if api_key:
            env["GEMINI_API_KEY"] = api_key

        # Build shell command that sources nvm, pipes prompt via stdin
        nvm_dir = os.environ.get("NVM_DIR", os.path.expanduser("~/.nvm"))
        nvm_sh = Path(nvm_dir) / "nvm.sh"

        # Use stdin for the prompt to avoid shell escaping issues.
        # -p flag with a short trigger puts gemini in headless mode;
        # stdin content is prepended to it.
        if nvm_sh.exists():
            shell_cmd = (
                f'source "{nvm_sh}" && nvm use 22 --silent && '
                f'cat "{prompt_path}" | "{gemini_bin}" -m {model} '
                f'-p "Follow the instructions from stdin." -y -o json'
            )
        else:
            shell_cmd = (
                f'cat "{prompt_path}" | "{gemini_bin}" -m {model} '
                f'-p "Follow the instructions from stdin." -y -o json'
            )

        try:
            result = subprocess.run(
                ["bash", "-c", shell_cmd],
                capture_output=True,
                text=True,
                cwd=str(repo_dir),
                timeout=timeout,
                env=env,
            )
        except subprocess.TimeoutExpired:
            print(f"  Gemini CLI timed out after {timeout}s")
            return None

        # Parse the JSON envelope from stdout
        stdout = result.stdout.strip()
        if not stdout:
            stderr = result.stderr[:500] if result.stderr else ""
            print(f"  Gemini CLI produced no output. stderr: {stderr}")
            return None

        try:
            envelope = json.loads(stdout)
        except json.JSONDecodeError:
            # Sometimes stderr gets mixed in — try to find JSON
            match = re.search(r"\{.*\"session_id\".*\}", stdout, re.DOTALL)
            if match:
                try:
                    envelope = json.loads(match.group(0))
                except json.JSONDecodeError:
                    print(f"  Could not parse Gemini CLI output")
                    return None
            else:
                print(f"  Could not parse Gemini CLI output: {stdout[:200]}")
                return None

        if "error" in envelope and envelope["error"]:
            print(f"  Gemini CLI error: {envelope['error']}")
            return None

        response_text = envelope.get("response", "")
        if not response_text:
            print(f"  Gemini CLI returned empty response")
            return None

        # Parse the JSON from the response text
        parsed = _parse_json_from_response(response_text)
        if not parsed:
            print(f"  Could not parse JSON from response: {response_text[:300]}")
            return None

        # Validate expected keys
        if "rubric_rules" not in parsed and "distractor_rules" not in parsed:
            print(f"  Response JSON missing rubric_rules/distractor_rules keys")
            return None

        return parsed


# ── Manifest merging (same as codex extractor) ──────────────────────────────

def merge_result(
    manifest_path: Path,
    extraction_result: dict,
    replace: bool = False,
) -> tuple[int, int, int]:
    """Merge extraction results into eval_manifest.yaml.

    Returns (added_rubrics, added_distractors, skipped_count)
    """
    m = yaml.safe_load(manifest_path.read_text())
    if not m:
        return 0, 0, 0

    existing_rubric = m.get("rubric", []) or []
    existing_distractors = m.get("distractors", []) or []

    existing_rule_keys = {
        r.get("rule", "")[:50].lower().strip()
        for r in existing_rubric if isinstance(r, dict)
    }
    existing_distractor_keys = {
        d.get("rule", "")[:50].lower().strip()
        for d in existing_distractors if isinstance(d, dict)
    }

    new_rubrics = []
    for r in extraction_result.get("rubric_rules", []):
        rule_text = r.get("rule", "")
        if not rule_text or len(rule_text) < 15:
            continue
        if not replace and rule_text[:50].lower().strip() in existing_rule_keys:
            continue
        new_rubrics.append({
            "rule": rule_text,
            "source": {
                "path": r.get("source_path", ""),
                "lines": str(r.get("source_lines", "")),
            },
            "source_text": r.get("source_text", ""),
            "evidence": r.get("evidence_in_gold", ""),
            "category": r.get("category", ""),
            "verification": "llm_judge",
        })

    new_distractors = []
    for d in extraction_result.get("distractor_rules", []):
        rule_text = d.get("rule", "")
        if not rule_text or len(rule_text) < 15:
            continue
        if not replace and rule_text[:50].lower().strip() in existing_distractor_keys:
            continue
        new_distractors.append({
            "rule": rule_text,
            "source": {
                "path": d.get("source_path", ""),
                "lines": str(d.get("source_lines", "")),
            },
            "source_text": d.get("source_text", ""),
            "collision_type": d.get("collision_type", "scope_ambiguity"),
            "why_distracting": d.get("why_distracting", ""),
            "severity": d.get("severity", "medium"),
        })

    skipped = len(extraction_result.get("skipped_rules", []))

    if replace:
        m["rubric"] = new_rubrics
        m["distractors"] = new_distractors
    else:
        m["rubric"] = existing_rubric + new_rubrics
        m["distractors"] = existing_distractors + new_distractors

    if new_rubrics or new_distractors:
        manifest_path.write_text(
            yaml.dump(m, default_flow_style=False, sort_keys=False, allow_unicode=True)
        )

    return len(new_rubrics), len(new_distractors), skipped


# ── Task processing ─────────────────────────────────────────────────────────

def process_task(
    task_path: Path,
    repo_cache: dict[str, Path],
    cache_dir: Path,
    model: str = "gemini-3.1-pro-preview",
    replace: bool = False,
    timeout: int = 600,
    api_key: str | None = None,
) -> dict:
    """Process a single task: clone repo, extract diff, run Gemini CLI, merge results."""
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

    repo, commit = get_repo_info(task_path)
    if not repo or not commit:
        result["error"] = "no repo/commit in Dockerfile"
        return result
    result["repo"] = repo

    gold_diff = extract_gold_diff(task_path)
    if not gold_diff:
        result["error"] = "no gold diff in solve.sh"
        return result

    repo_dir = repo_cache.get(repo)
    if not repo_dir:
        repo_dir = clone_or_checkout(repo, commit, cache_dir)
        if not repo_dir:
            result["error"] = "clone failed"
            return result
        repo_cache[repo] = repo_dir
    else:
        try:
            subprocess.run(
                ["git", "checkout", commit],
                capture_output=True, text=True, cwd=repo_dir, timeout=30,
            )
        except Exception:
            pass

    gemini_result = run_gemini_extraction(
        repo_dir, gold_diff, model=model, timeout=timeout, api_key=api_key,
    )
    if not gemini_result:
        result["error"] = "gemini extraction failed"
        result["time"] = time.monotonic() - t_start
        return result

    result["config_files"] = len(gemini_result.get("config_files_found", []))

    manifest_path = task_path / "eval_manifest.yaml"
    if not manifest_path.exists():
        result["error"] = "no eval_manifest.yaml"
        result["time"] = time.monotonic() - t_start
        return result

    added_r, added_d, skipped = merge_result(
        manifest_path, gemini_result, replace=replace
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
                pass

            tasks.append(task)

    return tasks


# ── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Extract rubric rules using Gemini CLI (exact line numbers via cat -n)"
    )
    parser.add_argument("--task", type=str, help="Single task path (relative to repo root)")
    parser.add_argument("--task-dir", type=str, help="Task directory to scan")
    parser.add_argument("--category", choices=["all", "weak", "no_rubric", "no_distractors"],
                        default="all")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--concurrency", type=int, default=3,
                        help="Parallel Gemini CLI processes")
    parser.add_argument("--model", type=str, default="gemini-3.1-pro-preview")
    parser.add_argument("--replace", action="store_true",
                        help="Replace existing rubric/distractors (vs merge)")
    parser.add_argument("--timeout", type=int, default=600,
                        help="Per-task Gemini CLI timeout in seconds")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--cache-dir", type=str, default="/tmp/repo_cache")
    parser.add_argument("--api-key", type=str, default=None,
                        help="Gemini API key (or set GEMINI_API_KEY env var)")
    args = parser.parse_args()

    # Resolve API key
    api_key = args.api_key or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        # Try .env file
        env_file = ROOT / ".env"
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                if line.startswith("GEMINI_API_KEY="):
                    api_key = line.split("=", 1)[1].strip()
                    break
    if not api_key:
        print("ERROR: No Gemini API key. Set GEMINI_API_KEY or pass --api-key")
        sys.exit(1)

    # Check gemini CLI is available
    try:
        _find_gemini_bin()
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
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
    print(f"Model: {args.model}")

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
        for repo, task in tasks_with_repo:
            processed += 1
            print(f"[{processed}/{len(tasks)}] {task.name} ({repo})")
            result = process_task(
                task, repo_cache, cache_dir,
                model=args.model, replace=args.replace,
                timeout=args.timeout, api_key=api_key,
            )
            results.append(result)
            _print_result(result)
    else:
        repo_groups = [
            (k, [t for _, t in g])
            for k, g in groupby(tasks_with_repo, key=lambda x: x[0])
        ]

        def process_group(repo: str, group_tasks: list[Path]) -> list[dict]:
            group_results = []
            for task in group_tasks:
                r = process_task(
                    task, repo_cache, cache_dir,
                    model=args.model, replace=args.replace,
                    timeout=args.timeout, api_key=api_key,
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
    print(f"  GEMINI CLI RUBRIC EXTRACTION COMPLETE")
    print(f"  Model:         {args.model}")
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
    log_file = log_dir / f"gemini_cli_rubric_{ts}.json"
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
