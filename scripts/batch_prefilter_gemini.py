#!/usr/bin/env python3
"""
Two-phase PR prefilter using Gemini Batch API.

Phase 1 (fetch):  Concurrent `gh` fetches for PR metadata + diffs → cache JSONL
Phase 2 (batch):  Build InlinedRequest list → submit one Gemini batch job
Phase 3 (poll):   Wait for batch completion, download results
Phase 4 (split):  Split results into accepted/rejected/error JSONL

Why batch: avoids per-request genai SDK connection-pool bottleneck. One submit,
one poll, then thousands of results back. Cost = same as Flex tier.

Usage:
  .venv/bin/python scripts/batch_prefilter_gemini.py \\
      --input scouted_new_prs.jsonl \\
      --cache prefilter_pr_cache.jsonl \\
      --output-accept prefiltered_accepted.jsonl \\
      --output-reject prefiltered_rejected.jsonl \\
      --fetch-concurrency 40 \\
      --poll-every 60

Resumable — re-reads existing caches and output files on startup.
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


def fetch_pr_data(repo: str, pr: int) -> dict:
    """Fetch PR title/body/files/diff via gh CLI. Returns dict with _error key on failure."""
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
        return {"pr_ref": f"{repo}#{pr}", "_error": (e.stderr or "")[:200]}
    except Exception as e:
        return {"pr_ref": f"{repo}#{pr}", "_error": str(e)[:200]}


# ---------------------------------------------------------------------------
# Phase 1: fetch PR metadata to cache
# ---------------------------------------------------------------------------

async def phase1_fetch(
    prs: list[tuple[str, int]],
    cache_path: Path,
    concurrency: int,
) -> dict[str, dict]:
    """Concurrently fetch PR data for refs not already in cache. Returns ref->data."""
    # Load existing cache
    cache: dict[str, dict] = {}
    if cache_path.exists():
        with cache_path.open() as f:
            for line in f:
                try:
                    obj = json.loads(line)
                    cache[obj["pr_ref"]] = obj
                except Exception:
                    continue

    todo = [(r, p) for (r, p) in prs if f"{r}#{p}" not in cache]
    print(f"Phase 1: cache has {len(cache)} PRs; fetching {len(todo)} new "
          f"(concurrency={concurrency})")

    if not todo:
        return cache

    sem = asyncio.Semaphore(concurrency)

    import concurrent.futures
    loop = asyncio.get_event_loop()
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=concurrency * 2)
    loop.set_default_executor(executor)

    cache_f = cache_path.open("a")
    cache_lock = asyncio.Lock()
    done = 0
    t0 = time.monotonic()

    async def worker(repo: str, pr: int):
        nonlocal done
        async with sem:
            data = await loop.run_in_executor(None, fetch_pr_data, repo, pr)

        async with cache_lock:
            cache_f.write(json.dumps(data) + "\n")
            cache_f.flush()
            cache[data["pr_ref"]] = data
            done += 1
            if done % 50 == 0:
                elapsed = time.monotonic() - t0
                print(f"  fetch: {done}/{len(todo)}  ({done/max(1,elapsed)*60:.0f}/min)")

    try:
        await asyncio.gather(*(worker(r, p) for r, p in todo))
    finally:
        cache_f.close()

    elapsed = time.monotonic() - t0
    print(f"Phase 1 done: {len(todo)} fetched in {elapsed:.0f}s "
          f"({len(todo)/max(1,elapsed)*60:.0f}/min)")
    return cache


# ---------------------------------------------------------------------------
# Phase 2: submit Gemini batch job
# ---------------------------------------------------------------------------

def build_batch_requests(prs_data: list[dict], prompt: str, model: str) -> list:
    """Build list of InlinedRequest for the batch API."""
    from google.genai import types

    requests = []
    for data in prs_data:
        if "_error" in data:
            continue  # Skip unfetchable PRs
        full_prompt = (
            prompt
            + "\n\n---\n\n## INPUT PR\n\n```json\n"
            + json.dumps(data, indent=2)
            + "\n```\n\nNow output the JSON object:"
        )
        cfg = types.GenerateContentConfig(
            temperature=0.1,
            max_output_tokens=2048,
            response_mime_type="application/json",
            response_schema=_PREFILTER_SCHEMA,
        )
        requests.append(types.InlinedRequest(
            model=model,
            contents=[types.Content(
                role="user",
                parts=[types.Part(text=full_prompt)],
            )],
            config=cfg,
            metadata={"pr_ref": data["pr_ref"]},
        ))
    return requests


def submit_batch_and_poll(
    requests: list,
    model: str,
    poll_every: int,
    api_key: str,
) -> list[dict]:
    """Submit batch, poll until done, return list of {pr_ref, response|error} dicts."""
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)
    print(f"\nPhase 2: submitting batch with {len(requests)} requests...")

    job = client.batches.create(
        model=model,
        src=requests,
        config=types.CreateBatchJobConfig(display_name=f"pr_prefilter_{int(time.time())}"),
    )
    print(f"  batch name: {job.name}")
    print(f"  initial state: {job.state}")

    # Poll
    print(f"\nPhase 3: polling every {poll_every}s...")
    last_state = ""
    t0 = time.monotonic()
    while True:
        job = client.batches.get(name=job.name)
        state = str(job.state)
        if state != last_state:
            elapsed = time.monotonic() - t0
            print(f"  [{elapsed:.0f}s] state: {state}")
            last_state = state
        if "SUCCEEDED" in state or "FAILED" in state or "CANCELLED" in state or "EXPIRED" in state:
            break
        time.sleep(poll_every)

    if "SUCCEEDED" not in state:
        print(f"  batch did not succeed: {state}", file=sys.stderr)
        return []

    # Extract results from inlined_responses
    print("\nPhase 4: extracting results...")
    results = []
    dest = job.dest
    if dest is None or dest.inlined_responses is None:
        print("  no inlined_responses in destination!", file=sys.stderr)
        return []

    inlined = dest.inlined_responses.inlined_responses or []
    # Map requests → responses by order (batch preserves order)
    for req, resp in zip(requests, inlined):
        pr_ref = (req.metadata or {}).get("pr_ref", "?")
        if resp.error:
            results.append({
                "pr_ref": pr_ref,
                "status": "api_error",
                "error": str(resp.error)[:200],
            })
            continue
        if resp.response is None:
            results.append({"pr_ref": pr_ref, "status": "empty_response"})
            continue

        # Extract text → JSON
        try:
            text = resp.response.text or ""
            parsed = json.loads(text.strip())
            results.append({
                "pr_ref": pr_ref,
                "status": "ok",
                **parsed,
            })
        except Exception as e:
            results.append({
                "pr_ref": pr_ref,
                "status": "parse_error",
                "error": str(e)[:200],
            })

    return results


# ---------------------------------------------------------------------------
# Phase 5: split results into accept/reject/error files
# ---------------------------------------------------------------------------

def write_results(
    results: list[dict],
    cache: dict[str, dict],
    accept_path: Path,
    reject_path: Path,
    error_path: Path,
    existing: set[str],
) -> dict:
    counts = {"ACCEPT": 0, "REJECT": 0, "ERROR": 0}
    with accept_path.open("a") as af, reject_path.open("a") as rf, error_path.open("a") as ef:
        for r in results:
            pr_ref = r.get("pr_ref", "?")
            if pr_ref in existing:
                continue
            # Enrich with PR metadata from cache
            pr_cache = cache.get(pr_ref, {})
            out = {
                "pr_ref": pr_ref,
                "title": pr_cache.get("title", ""),
                "files_count": len(pr_cache.get("files_changed", [])),
                **r,
            }
            line = json.dumps(out) + "\n"
            if r.get("status") != "ok":
                ef.write(line)
                counts["ERROR"] += 1
            elif r.get("decision") == "ACCEPT":
                af.write(line)
                counts["ACCEPT"] += 1
            elif r.get("decision") == "REJECT":
                rf.write(line)
                counts["REJECT"] += 1
            else:
                ef.write(line)
                counts["ERROR"] += 1
    return counts


def load_processed(paths: list[Path]) -> set[str]:
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


async def main_async(args):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    prompt = PROMPT_PATH.read_text()
    input_path = Path(args.input)
    cache_path = Path(args.cache)
    accept_path = Path(args.output_accept)
    reject_path = Path(args.output_reject)
    error_path = Path(args.output_error)

    for p in (cache_path, accept_path, reject_path, error_path):
        p.parent.mkdir(parents=True, exist_ok=True)

    # Collect PR refs from input
    processed = load_processed([accept_path, reject_path, error_path])
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

    print(f"PRs to classify: {len(prs)}\n")
    if not prs:
        print("Nothing to do.")
        return

    # ─── Phase 1: Fetch ────────────────────────────────────────────────
    cache = await phase1_fetch(prs, cache_path, args.fetch_concurrency)

    # Collect fetched data for the PRs we care about, filter out errors
    prs_data = []
    fetch_errors = 0
    for r, p in prs:
        ref = f"{r}#{p}"
        d = cache.get(ref)
        if d and "_error" not in d:
            prs_data.append(d)
        elif d and "_error" in d:
            fetch_errors += 1

    print(f"\n  fetched OK: {len(prs_data)}  fetch errors: {fetch_errors}")
    if not prs_data:
        print("No PRs to classify (all fetches failed).")
        return

    # ─── Phase 2: Build batch ──────────────────────────────────────────
    requests = build_batch_requests(prs_data, prompt, args.model)
    print(f"  built {len(requests)} batch requests")

    # Chunk if too many per batch. Gemini inline limit ≈ 20MB; our requests
    # are ~15KB so ~1300 fit in one batch. Split to be safe.
    chunk_size = args.chunk_size
    chunks = [requests[i:i+chunk_size] for i in range(0, len(requests), chunk_size)]
    print(f"  split into {len(chunks)} batch job(s) of ≤{chunk_size} each")

    all_results = []
    for i, chunk in enumerate(chunks):
        print(f"\n=== Batch {i+1}/{len(chunks)} ({len(chunk)} requests) ===")
        results = submit_batch_and_poll(chunk, args.model, args.poll_every, api_key)
        all_results.extend(results)

    # ─── Phase 5: Write output files ───────────────────────────────────
    counts = write_results(all_results, cache, accept_path, reject_path, error_path, processed)

    print("\n" + "=" * 60)
    total = sum(counts.values())
    print(f"Results: {total}")
    print(f"  ACCEPT: {counts['ACCEPT']}  ({counts['ACCEPT']/max(1,total)*100:.1f}%)")
    print(f"  REJECT: {counts['REJECT']}  ({counts['REJECT']/max(1,total)*100:.1f}%)")
    print(f"  ERROR:  {counts['ERROR']}")
    print(f"\nOutputs:")
    print(f"  ACCEPTS: {accept_path}")
    print(f"  REJECTS: {reject_path}")
    print(f"  ERRORS:  {error_path}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=str, default="scouted_new_prs.jsonl")
    p.add_argument("--cache", type=str, default="prefilter_pr_cache.jsonl",
                   help="Phase-1 gh fetch cache (resumable)")
    p.add_argument("--output-accept", type=str, default="prefiltered_accepted.jsonl")
    p.add_argument("--output-reject", type=str, default="prefiltered_rejected.jsonl")
    p.add_argument("--output-error", type=str, default="prefiltered_errors.jsonl")
    p.add_argument("--fetch-concurrency", type=int, default=30,
                   help="Parallel gh fetches in phase 1")
    p.add_argument("--chunk-size", type=int, default=500,
                   help="Max requests per Gemini batch job")
    p.add_argument("--poll-every", type=int, default=30,
                   help="Seconds between batch status polls")
    p.add_argument("--skip-first", type=int, default=0)
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--model", type=str, default="gemini-3.1-pro-preview")
    args = p.parse_args()
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
