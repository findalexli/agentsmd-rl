#!/usr/bin/env python3
"""Phase 1 only: fetch PR metadata to cache. Run ahead of classify step."""
from __future__ import annotations
import argparse, asyncio, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from batch_prefilter_gemini import parse_pr_ref, phase1_fetch  # noqa: E402


async def main_async(args):
    input_path = Path(args.input)
    cache_path = Path(args.cache)
    cache_path.parent.mkdir(parents=True, exist_ok=True)

    prs: list[tuple[str, int]] = []
    with input_path.open() as f:
        for i, line in enumerate(f):
            if i < args.skip_first:
                continue
            pr_ref = parse_pr_ref(line)
            if pr_ref:
                prs.append(pr_ref)
            if args.limit and len(prs) >= args.limit:
                break

    print(f"Input: {len(prs)} PRs")
    await phase1_fetch(prs, cache_path, args.concurrency)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", default="scouted_new_prs.jsonl")
    p.add_argument("--cache", default="prefilter_pr_cache.jsonl")
    p.add_argument("--concurrency", type=int, default=50)
    p.add_argument("--skip-first", type=int, default=0)
    p.add_argument("--limit", type=int, default=None)
    asyncio.run(main_async(p.parse_args()))


if __name__ == "__main__":
    main()
