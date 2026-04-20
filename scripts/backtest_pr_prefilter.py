#!/usr/bin/env python3
"""
Back-test the PR prefilter prompt against KNOWN-GOOD tasks.

Each task in harbor_tasks/ already passed nop=0/gold=1 — these are tasks the
production pipeline successfully built. If the prefilter REJECTS any of them,
that's a false negative: we'd lose this task in production.

Usage:
  .venv/bin/python scripts/backtest_pr_prefilter.py --sample 30 --concurrency 6
  .venv/bin/python scripts/backtest_pr_prefilter.py --tasks harbor_tasks/airflow-pr-64783,harbor_tasks/lancedb-update-lance-dep
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import random
import re
import subprocess
import sys
import time
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
PROMPT_PATH = REPO_ROOT / "taskforge" / "prompts" / "pr_prefilter.md"

# JSON schema for Gemini structured output
_PREFILTER_SCHEMA = {
    "type": "object",
    "properties": {
        "decision": {"type": "string", "enum": ["ACCEPT", "REJECT"]},
        "reject_reason_code": {"type": "string"},
        "reject_reason": {"type": "string"},
        "task_class": {"type": "string", "enum": ["code_only", "code_plus_config", "unknown"]},
        "bug_summary": {"type": "string"},
        "testability_note": {"type": "string"},
        "confidence": {"type": "number"},
        "priority_score": {"type": "number"},
        "priority_reason": {"type": "string"},
        "risk_flags": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["decision", "task_class", "confidence", "priority_score", "risk_flags"],
}

# Diff truncation (Gemini 1M context can take more, but cost is the constraint)
DIFF_MAX_CHARS = 30_000


def load_pr_ref(task_dir: Path) -> tuple[str, int] | None:
    """Read repo + pr from eval_manifest.yaml. Returns (owner/repo, pr_number).

    Handles five schema variants observed in the wild:
      A: source: {repo: "owner/repo", pr: 123}
      B: source: {repo: "owner/repo", pr_number: 123}
      C: source_pr: {repo: "owner/repo", number: 123}             (containerd-style)
      D: source_pr: {owner: "X", repo: "Y", number: 123}         (antd-style, also nested under task.)
      E: task.source_pr: "owner/repo#123"                         (lancedb-style string)
    """
    manifest = task_dir / "eval_manifest.yaml"
    if not manifest.exists():
        return None
    try:
        data = yaml.safe_load(manifest.read_text())
    except Exception:
        return None

    def _to_int(v):
        try:
            return int(v)
        except Exception:
            return None

    # Variant A/B: source: {repo, pr|pr_number}
    src = data.get("source") or {}
    if isinstance(src, dict):
        repo = src.get("repo")
        pr = src.get("pr") or src.get("pr_number") or src.get("number")
        if repo and pr:
            n = _to_int(pr)
            if n is not None:
                return (str(repo), n)

    # Variant C/D: source_pr at top level OR under task.
    for parent_key in ("source_pr", None):
        if parent_key:
            spr = data.get(parent_key)
        else:
            spr = (data.get("task") or {}).get("source_pr")
        if not spr:
            continue

        # Variant E: string "owner/repo#NUMBER"
        if isinstance(spr, str) and "#" in spr:
            try:
                r, n = spr.split("#", 1)
                return (r, int(n))
            except Exception:
                pass
            continue

        if isinstance(spr, dict):
            # Variant D: separate owner + repo
            owner = spr.get("owner")
            repo = spr.get("repo")
            number = spr.get("number") or spr.get("pr") or spr.get("pr_number")
            if owner and repo and number:
                n = _to_int(number)
                if n is not None:
                    return (f"{owner}/{repo}", n)
            # Variant C: combined repo + number
            if repo and number and "/" in str(repo):
                n = _to_int(number)
                if n is not None:
                    return (str(repo), n)

    return None


def fetch_pr_data(repo: str, pr: int) -> dict | None:
    """Fetch PR title, body, files, diff via gh CLI."""
    try:
        meta = subprocess.run(
            ["gh", "pr", "view", str(pr), "--repo", repo,
             "--json", "title,body,files"],
            capture_output=True, text=True, timeout=30, check=True,
        )
        meta_data = json.loads(meta.stdout)

        diff = subprocess.run(
            ["gh", "pr", "diff", str(pr), "--repo", repo],
            capture_output=True, text=True, timeout=60, check=True,
        )
        diff_text = diff.stdout
        if len(diff_text) > DIFF_MAX_CHARS:
            diff_text = diff_text[:DIFF_MAX_CHARS] + "\n... (truncated)"

        return {
            "pr_ref": f"{repo}#{pr}",
            "title": meta_data.get("title", ""),
            "body": (meta_data.get("body", "") or "")[:8000],
            "files_changed": [
                {
                    "path": f["path"],
                    "additions": f.get("additions", 0),
                    "deletions": f.get("deletions", 0),
                    "status": f.get("status", "modified"),
                }
                for f in meta_data.get("files", [])
            ],
            "diff": diff_text,
        }
    except subprocess.CalledProcessError as e:
        print(f"  gh fetch failed for {repo}#{pr}: {e.stderr[:200]}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"  fetch error for {repo}#{pr}: {e}", file=sys.stderr)
        return None


def call_gemini_prefilter(prompt: str, pr_payload: dict, api_key: str,
                          model: str = "gemini-3.1-pro-preview",
                          tier: str = "flex",
                          max_retries: int = 4) -> dict | None:
    """Call Gemini with the prefilter prompt + PR payload. Returns parsed JSON.

    Uses google-genai SDK with `service_tier='flex'` (50% cheaper, batch-suitable).
    Retries with exponential backoff on transient errors (429, 5xx, parse fail).
    """
    from google import genai
    from google.genai import types

    full_prompt = (
        prompt
        + "\n\n---\n\n## INPUT PR\n\n```json\n"
        + json.dumps(pr_payload, indent=2)
        + "\n```\n\nNow output the JSON object:"
    )

    client = genai.Client(api_key=api_key)
    config_kwargs = dict(
        temperature=0.1,
        max_output_tokens=2048,
        response_mime_type="application/json",
        response_schema=_PREFILTER_SCHEMA,
    )
    if tier:
        config_kwargs["service_tier"] = tier  # e.g. "flex" → 50% cheaper, batch
    config = types.GenerateContentConfig(**config_kwargs)

    last_err: str = ""
    for attempt in range(max_retries):
        try:
            resp = client.models.generate_content(
                model=model,
                contents=full_prompt,
                config=config,
            )
            text = (resp.text or "").strip()
            if not text:
                last_err = "empty response"
            else:
                try:
                    return json.loads(text)
                except json.JSONDecodeError as e:
                    last_err = f"parse: {e} | raw[:200]={text[:200]}"
        except Exception as e:
            msg = str(e)
            last_err = f"api: {msg[:200]}"
            # Don't retry on 4xx other than 429
            if any(code in msg for code in ("400", "401", "403", "404")):
                break

        # Backoff: 4s, 12s, 36s, 60s
        sleep = min(60, 4 * (3 ** attempt))
        time.sleep(sleep)

    return {"_error": last_err}


async def process_one(task_name: str, prompt: str, api_key: str, model: str,
                      tier: str, sem: asyncio.Semaphore) -> dict:
    async with sem:
        task_dir = REPO_ROOT / "harbor_tasks" / task_name
        ref = load_pr_ref(task_dir)
        if not ref:
            return {"task": task_name, "status": "skip", "reason": "no_pr_ref"}

        repo, pr = ref
        loop = asyncio.get_event_loop()

        pr_data = await loop.run_in_executor(None, fetch_pr_data, repo, pr)
        if not pr_data:
            return {"task": task_name, "status": "skip", "reason": "fetch_failed",
                    "pr_ref": f"{repo}#{pr}"}

        result = await loop.run_in_executor(None, call_gemini_prefilter,
                                            prompt, pr_data, api_key, model, tier)
        if result is None or "_error" in result:
            return {"task": task_name, "status": "skip", "reason": result,
                    "pr_ref": f"{repo}#{pr}"}

        return {
            "task": task_name,
            "status": "ok",
            "pr_ref": f"{repo}#{pr}",
            "title": pr_data["title"],
            "files_count": len(pr_data["files_changed"]),
            "decision": result.get("decision"),
            "reject_reason_code": result.get("reject_reason_code"),
            "reject_reason": result.get("reject_reason"),
            "task_class": result.get("task_class"),
            "confidence": result.get("confidence"),
            "risk_flags": result.get("risk_flags", []),
        }


async def main_async(args: argparse.Namespace) -> None:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    if not PROMPT_PATH.exists():
        print(f"ERROR: prompt not found at {PROMPT_PATH}", file=sys.stderr)
        sys.exit(1)
    prompt = PROMPT_PATH.read_text()

    if args.tasks:
        task_names = [t.strip().split("/")[-1] for t in args.tasks.split(",") if t.strip()]
    else:
        all_tasks = sorted(d.name for d in (REPO_ROOT / "harbor_tasks").iterdir()
                           if d.is_dir())
        random.seed(args.seed)
        task_names = random.sample(all_tasks, min(args.sample, len(all_tasks)))

    print(f"Backtesting {len(task_names)} known-good tasks against prefilter")
    print(f"Model: {args.model}, tier: {args.tier or 'default'}, concurrency: {args.concurrency}")
    print(f"Prompt: {PROMPT_PATH}")
    print()

    sem = asyncio.Semaphore(args.concurrency)
    t0 = time.monotonic()
    tasks = [process_one(name, prompt, api_key, args.model, args.tier, sem)
             for name in task_names]
    results = await asyncio.gather(*tasks)
    elapsed = time.monotonic() - t0

    # Aggregate
    accept = [r for r in results if r.get("decision") == "ACCEPT"]
    reject = [r for r in results if r.get("decision") == "REJECT"]
    skip = [r for r in results if r.get("status") == "skip"]

    print(f"\n=== RESULTS ({elapsed:.1f}s) ===")
    print(f"Total sampled: {len(task_names)}")
    print(f"  ACCEPT: {len(accept)} ({len(accept)/max(1,len(task_names))*100:.0f}%)")
    print(f"  REJECT: {len(reject)} ({len(reject)/max(1,len(task_names))*100:.0f}%)")
    print(f"  SKIP:   {len(skip)}  (gh fetch / api error)")

    if reject:
        # Auto-classify the existing test as mechanical vs behavioral
        # to distinguish "good rejection of low-quality task" from "true false negative"
        for r in reject:
            task_dir = REPO_ROOT / "harbor_tasks" / r["task"]
            test_path = task_dir / "tests" / "test_outputs.py"
            if not test_path.exists():
                test_path = task_dir / "tests" / "test.sh"
            if test_path.exists():
                test_content = test_path.read_text()[:8000]
                # Heuristic: count behavioral vs mechanical signals
                mechanical_signals = sum([
                    test_content.count(".exists()"),
                    test_content.count('in content'),
                    test_content.count('in src'),
                    test_content.count('in text'),
                    len(re.findall(r'assert "[^"]*" in', test_content)),
                ])
                behavioral_signals = sum([
                    test_content.count('subprocess.run'),
                    test_content.count('with pytest.raises'),
                    test_content.count('assert_called'),
                    test_content.count('==') - test_content.count('!='),  # rough call-result asserts
                    len(re.findall(r'def test_\w+\(.*?\):', test_content)),
                ])
                r["test_signal_mech"] = mechanical_signals
                r["test_signal_behav"] = behavioral_signals
                # Crude classification: if mechanical >> behavioral, this was probably a low-quality task
                if mechanical_signals >= 2 * max(1, behavioral_signals):
                    r["test_quality"] = "MECHANICAL (rejection likely correct)"
                elif behavioral_signals >= 2 * max(1, mechanical_signals):
                    r["test_quality"] = "BEHAVIORAL (likely true false-negative)"
                else:
                    r["test_quality"] = "MIXED (review)"
            else:
                r["test_quality"] = "?"

        print(f"\n=== REJECTED-BUT-PASSED-VALIDATION ({len(reject)}) ===")
        print("test_quality column estimates whether rejection was correct:")
        print("  MECHANICAL = our pipeline made a low-quality task; rejection saved us")
        print("  BEHAVIORAL = real benchmark task; rejection is true false-negative")
        print("  MIXED      = needs manual review")
        print()
        codes: dict[str, int] = {}
        quality_buckets: dict[str, int] = {}
        for r in reject:
            code = r.get("reject_reason_code", "?")
            codes[code] = codes.get(code, 0) + 1
            q = r.get("test_quality", "?")
            quality_buckets[q] = quality_buckets.get(q, 0) + 1
            print(f"  [{code}] {r['task']} ({r['pr_ref']}) conf={r.get('confidence',0):.2f}")
            print(f"    test_quality: {q}  (mech={r.get('test_signal_mech','?')}, behav={r.get('test_signal_behav','?')})")
            print(f"    title: {r.get('title','')[:80]}")
            print(f"    reason: {r.get('reject_reason','')[:120]}")
        print("\n  By reject code:")
        for code, n in sorted(codes.items(), key=lambda x: -x[1]):
            print(f"    {code}: {n}")
        print("\n  By test quality:")
        for q, n in sorted(quality_buckets.items(), key=lambda x: -x[1]):
            print(f"    {q}: {n}")

    if accept:
        # Show task_class distribution and sample of accepts
        classes: dict[str, int] = {}
        risks: dict[str, int] = {}
        for r in accept:
            classes[r.get("task_class", "?")] = classes.get(r.get("task_class", "?"), 0) + 1
            for flag in r.get("risk_flags", []) or []:
                risks[flag] = risks.get(flag, 0) + 1
        print(f"\n=== ACCEPT BREAKDOWN ===")
        print("  task_class:")
        for c, n in classes.items():
            print(f"    {c}: {n}")
        if risks:
            print("  risk_flags raised on accepts:")
            for f, n in sorted(risks.items(), key=lambda x: -x[1]):
                print(f"    {f}: {n}")

    if skip:
        print(f"\n=== SKIPPED ({len(skip)}) ===")
        for r in skip[:5]:
            print(f"  {r['task']}: {r.get('reason')}")

    # Write detailed JSONL output
    out_path = REPO_ROOT / "scripts" / f"backtest_results_{int(time.time())}.jsonl"
    with out_path.open("w") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")
    print(f"\nDetailed results: {out_path}")
    print(f"\nFalse-negative rate: {len(reject)/max(1,len(accept)+len(reject))*100:.1f}%")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--sample", type=int, default=30,
                   help="Number of random tasks to sample (default 30)")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--concurrency", type=int, default=6)
    p.add_argument("--tasks", type=str, default=None,
                   help="Comma-separated task names (overrides --sample)")
    p.add_argument("--model", type=str, default="gemini-3.1-pro-preview",
                   help="Gemini model (use gemini-3.1-flash-preview for cheap)")
    p.add_argument("--tier", type=str, default="flex",
                   help="Service tier: 'flex' (50%% cheaper, batch) or '' for default")
    args = p.parse_args()
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
