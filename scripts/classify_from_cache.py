#!/usr/bin/env python3
"""
Classify PRs from the phase-1 cache using sync Gemini calls.

Cache-only input means no gh CLI fetches → Gemini is the only latency.
With concurrency 100 + Flex tier (~6-20s per call), 5000 PRs finish in 10-20 min.
"""
from __future__ import annotations
import argparse, asyncio, concurrent.futures, json, os, sys, time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PROMPT_PATH = REPO_ROOT / "taskforge" / "prompts" / "pr_prefilter.md"

_SCHEMA = {
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


def call_gemini(prompt: str, pr_data: dict, api_key: str, model: str, tier: str,
                max_retries: int = 3) -> dict:
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=api_key)
    cfg = dict(
        temperature=0.1, max_output_tokens=2048,
        response_mime_type="application/json",
        response_schema=_SCHEMA,
    )
    if tier:
        cfg["service_tier"] = tier
    config = types.GenerateContentConfig(**cfg)
    full_prompt = (
        prompt
        + "\n\n---\n\n## INPUT PR\n\n```json\n"
        + json.dumps(pr_data, indent=2)
        + "\n```\n\nNow output the JSON object:"
    )

    last = ""
    for attempt in range(max_retries):
        try:
            resp = client.models.generate_content(model=model, contents=full_prompt, config=config)
            text = (resp.text or "").strip()
            if text:
                try:
                    return json.loads(text)
                except Exception as e:
                    last = f"parse: {e}"
            else:
                last = "empty"
        except Exception as e:
            msg = str(e)[:150]
            last = msg
            if any(c in msg for c in ("400", "401", "403", "404")):
                break
        time.sleep(min(30, 3 * (3 ** attempt)))
    return {"_error": last}


def load_done(paths: list[Path]) -> set[str]:
    done = set()
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
    assert api_key, "GEMINI_API_KEY not set"

    prompt = PROMPT_PATH.read_text()
    cache_path = Path(args.cache)
    accept_p = Path(args.output_accept)
    reject_p = Path(args.output_reject)
    error_p = Path(args.output_error)

    # Load cache
    cache: dict[str, dict] = {}
    with cache_path.open() as f:
        for line in f:
            try:
                o = json.loads(line)
                if "_error" not in o:
                    cache[o["pr_ref"]] = o
            except Exception:
                continue

    done = load_done([accept_p, reject_p, error_p])
    todo = [ref for ref in cache if ref not in done]
    if args.limit:
        todo = todo[:args.limit]
    print(f"Cache has {len(cache)} PRs, {len(done)} already classified, "
          f"{len(todo)} to do")

    if not todo:
        return

    loop = asyncio.get_event_loop()
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=args.concurrency * 2)
    loop.set_default_executor(executor)

    sem = asyncio.Semaphore(args.concurrency)
    af = accept_p.open("a")
    rf = reject_p.open("a")
    ef = error_p.open("a")
    lock = asyncio.Lock()
    counts = {"A": 0, "R": 0, "E": 0}
    t0 = time.monotonic()
    done_n = 0

    async def worker(ref: str):
        nonlocal done_n
        async with sem:
            pr_data = cache[ref]
            result = await loop.run_in_executor(
                None, call_gemini, prompt, pr_data, api_key, args.model, args.tier)

        async with lock:
            out = {
                "pr_ref": ref,
                "title": pr_data.get("title", ""),
                "files_count": len(pr_data.get("files_changed", [])),
            }
            if "_error" in result:
                out["status"] = "api_error"
                out["error"] = result["_error"]
                ef.write(json.dumps(out) + "\n"); ef.flush()
                counts["E"] += 1
            else:
                out["status"] = "ok"
                out.update(result)
                if result.get("decision") == "ACCEPT":
                    af.write(json.dumps(out) + "\n"); af.flush()
                    counts["A"] += 1
                else:
                    rf.write(json.dumps(out) + "\n"); rf.flush()
                    counts["R"] += 1
            done_n += 1
            if done_n % 50 == 0:
                elapsed = time.monotonic() - t0
                rate = done_n / max(1, elapsed) * 60
                eta = (len(todo) - done_n) / max(1, rate) * 60
                print(f"  [{done_n}/{len(todo)}] A={counts['A']} R={counts['R']} E={counts['E']} "
                      f"({rate:.0f}/min, ETA {eta:.0f}s)")

    try:
        await asyncio.gather(*(worker(r) for r in todo))
    finally:
        af.close(); rf.close(); ef.close()

    elapsed = time.monotonic() - t0
    total = sum(counts.values())
    print("\n" + "=" * 60)
    print(f"Done in {elapsed:.0f}s ({elapsed/60:.1f}m)")
    print(f"  ACCEPT: {counts['A']}  ({counts['A']/max(1,total)*100:.1f}%)")
    print(f"  REJECT: {counts['R']}  ({counts['R']/max(1,total)*100:.1f}%)")
    print(f"  ERROR:  {counts['E']}")
    print(f"  Throughput: {total/max(1,elapsed)*60:.0f}/min")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--cache", default="prefilter_pr_cache.jsonl")
    p.add_argument("--output-accept", default="prefiltered_accepted.jsonl")
    p.add_argument("--output-reject", default="prefiltered_rejected.jsonl")
    p.add_argument("--output-error", default="prefiltered_errors.jsonl")
    p.add_argument("--concurrency", type=int, default=100)
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--model", default="gemini-3.1-pro-preview")
    p.add_argument("--tier", default="flex")
    asyncio.run(main_async(p.parse_args()))


if __name__ == "__main__":
    main()
