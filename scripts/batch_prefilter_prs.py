#!/usr/bin/env python3
"""
Batch-run the Gemini PR prefilter over a JSONL of PR refs.

Fetches PR data via gh CLI, calls Gemini 3.1 Pro (Flex tier) with the
pr_prefilter.md prompt, writes a filtered output JSONL containing ACCEPTs
sorted by priority_score. Also writes a rejection log for auditing.

Usage:
  .venv/bin/python scripts/batch_prefilter_prs.py \\
      --input scouted_new_prs.jsonl \\
      --output-accept prefiltered_accepted.jsonl \\
      --output-reject prefiltered_rejected.jsonl \\
      --concurrency 16 \\
      --skip-first 900      # skip PRs already attempted by ramp

Resumable: the script reads the accept/reject files on startup and skips
pr_refs already processed. Safe to Ctrl-C and re-run.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PROMPT_PATH = REPO_ROOT / "taskforge" / "prompts" / "pr_prefilter.md"

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

DIFF_MAX_CHARS = 30_000


def parse_pr_ref(line: str) -> tuple[str, int] | None:
    """Accept either a plain 'owner/repo#NUMBER' or a JSON obj with pr_ref."""
    line = line.strip()
    if not line:
        return None
    try:
        obj = json.loads(line)
        ref = obj.get("pr_ref") or obj.get("ref")
        if ref and "#" in ref:
            r, n = ref.split("#", 1)
            return (r, int(n))
    except json.JSONDecodeError:
        if "#" in line:
            try:
                r, n = line.split("#", 1)
                return (r, int(n))
            except ValueError:
                return None
    return None


def fetch_pr_data(repo: str, pr: int) -> dict | None:
    """Fetch PR title/body/files/diff via gh CLI."""
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
        return {"_fetch_error": (e.stderr or "")[:200]}
    except Exception as e:
        return {"_fetch_error": str(e)[:200]}


def call_gemini(prompt: str, pr_payload: dict, api_key: str,
                model: str, tier: str, max_retries: int = 4) -> dict:
    """Gemini call with Flex tier + retry loop."""
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
        config_kwargs["service_tier"] = tier
    config = types.GenerateContentConfig(**config_kwargs)

    last_err = ""
    for attempt in range(max_retries):
        try:
            resp = client.models.generate_content(
                model=model, contents=full_prompt, config=config)
            text = (resp.text or "").strip()
            if text:
                try:
                    return json.loads(text)
                except json.JSONDecodeError as e:
                    last_err = f"parse: {e}"
            else:
                last_err = "empty response"
        except Exception as e:
            msg = str(e)
            last_err = f"api: {msg[:150]}"
            if any(code in msg for code in ("400", "401", "403", "404")):
                break

        sleep = min(60, 4 * (3 ** attempt))
        time.sleep(sleep)

    return {"_error": last_err}


def load_processed_refs(paths: list[Path]) -> set[str]:
    """Collect pr_refs already classified (in accept or reject files)."""
    done: set[str] = set()
    for p in paths:
        if not p.exists():
            continue
        with p.open() as f:
            for line in f:
                try:
                    obj = json.loads(line)
                    ref = obj.get("pr_ref")
                    if ref:
                        done.add(ref)
                except Exception:
                    continue
    return done


async def process_one(repo: str, pr: int, prompt: str, api_key: str,
                      model: str, tier: str,
                      sem: asyncio.Semaphore) -> dict:
    async with sem:
        loop = asyncio.get_event_loop()
        pr_data = await loop.run_in_executor(None, fetch_pr_data, repo, pr)
        if pr_data is None or "_fetch_error" in (pr_data or {}):
            return {
                "pr_ref": f"{repo}#{pr}",
                "status": "fetch_error",
                "error": (pr_data or {}).get("_fetch_error", "unknown"),
            }

        result = await loop.run_in_executor(None, call_gemini,
                                            prompt, pr_data, api_key, model, tier)
        if "_error" in result:
            return {
                "pr_ref": f"{repo}#{pr}",
                "status": "api_error",
                "error": result["_error"],
            }

        # Enrich output with PR metadata for downstream consumption.
        return {
            "pr_ref": f"{repo}#{pr}",
            "status": "ok",
            "title": pr_data["title"],
            "files_count": len(pr_data["files_changed"]),
            "decision": result.get("decision"),
            "reject_reason_code": result.get("reject_reason_code"),
            "reject_reason": result.get("reject_reason"),
            "task_class": result.get("task_class"),
            "bug_summary": result.get("bug_summary"),
            "testability_note": result.get("testability_note"),
            "confidence": result.get("confidence"),
            "priority_score": result.get("priority_score"),
            "priority_reason": result.get("priority_reason"),
            "risk_flags": result.get("risk_flags", []),
        }


async def main_async(args):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    # Default ThreadPoolExecutor only has ~32 threads. Each concurrent task
    # needs 2 slots (gh fetch + gemini call) so expand the pool to 2×concurrency.
    import concurrent.futures
    loop = asyncio.get_event_loop()
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=max(64, args.concurrency * 3))
    loop.set_default_executor(executor)

    prompt = PROMPT_PATH.read_text()
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: input not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    accept_path = Path(args.output_accept)
    reject_path = Path(args.output_reject)
    error_path = Path(args.output_error)
    for p in (accept_path, reject_path, error_path):
        p.parent.mkdir(parents=True, exist_ok=True)

    # Collect PRs from input, filter against already-processed.
    processed = load_processed_refs([accept_path, reject_path, error_path])
    print(f"Already classified: {len(processed)} PRs")

    prs: list[tuple[str, int]] = []
    with input_path.open() as f:
        for i, line in enumerate(f):
            if i < args.skip_first:
                continue
            pr_ref = parse_pr_ref(line)
            if pr_ref is None:
                continue
            ref_str = f"{pr_ref[0]}#{pr_ref[1]}"
            if ref_str in processed:
                continue
            prs.append(pr_ref)
            if args.limit and len(prs) >= args.limit:
                break

    print(f"PRs to classify: {len(prs)}  (concurrency={args.concurrency}, "
          f"model={args.model}, tier={args.tier or 'default'})")
    if not prs:
        print("Nothing to do.")
        return

    sem = asyncio.Semaphore(args.concurrency)

    # Streaming output — write each result as soon as it completes.
    accept_f = accept_path.open("a")
    reject_f = reject_path.open("a")
    error_f = error_path.open("a")
    counts = {"ACCEPT": 0, "REJECT": 0, "ERROR": 0}
    t0 = time.monotonic()

    async def run_one(repo, pr):
        r = await process_one(repo, pr, prompt, api_key, args.model, args.tier, sem)
        line = json.dumps(r) + "\n"
        if r.get("status") != "ok":
            error_f.write(line)
            error_f.flush()
            counts["ERROR"] += 1
        elif r.get("decision") == "ACCEPT":
            accept_f.write(line)
            accept_f.flush()
            counts["ACCEPT"] += 1
        else:
            reject_f.write(line)
            reject_f.flush()
            counts["REJECT"] += 1

        total = sum(counts.values())
        if total % 25 == 0:
            elapsed = time.monotonic() - t0
            rate = total / max(1, elapsed) * 60
            print(f"  [{total}/{len(prs)}] A={counts['ACCEPT']} "
                  f"R={counts['REJECT']} E={counts['ERROR']}  ({rate:.1f}/min)")

    try:
        await asyncio.gather(*(run_one(r, p) for r, p in prs))
    finally:
        accept_f.close()
        reject_f.close()
        error_f.close()

    elapsed = time.monotonic() - t0
    print("\n" + "=" * 60)
    print(f"Done in {elapsed:.0f}s ({elapsed/60:.1f}m)")
    print(f"  ACCEPT: {counts['ACCEPT']}  ({counts['ACCEPT']/max(1,sum(counts.values()))*100:.1f}%)")
    print(f"  REJECT: {counts['REJECT']}  ({counts['REJECT']/max(1,sum(counts.values()))*100:.1f}%)")
    print(f"  ERROR:  {counts['ERROR']}")
    print(f"  Throughput: {sum(counts.values())/max(1,elapsed)*60:.1f}/min")
    print(f"\nOutputs:")
    print(f"  ACCEPTS: {accept_path}")
    print(f"  REJECTS: {reject_path}")
    print(f"  ERRORS:  {error_path}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=str, default="scouted_new_prs.jsonl")
    p.add_argument("--output-accept", type=str, default="prefiltered_accepted.jsonl")
    p.add_argument("--output-reject", type=str, default="prefiltered_rejected.jsonl")
    p.add_argument("--output-error", type=str, default="prefiltered_errors.jsonl")
    p.add_argument("--concurrency", type=int, default=16)
    p.add_argument("--skip-first", type=int, default=0,
                   help="Skip first N lines of input (already processed by ramp)")
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--model", type=str, default="gemini-3.1-pro-preview")
    p.add_argument("--tier", type=str, default="flex",
                   help="'flex' (50%% cheaper) or '' for default")
    args = p.parse_args()
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
