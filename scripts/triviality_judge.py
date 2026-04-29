#!/usr/bin/env python3
"""LLM judge for task triviality.

Asks DeepSeek (Anthropic-compatible endpoint) "is this task trivial? would
any model pass it without reasoning?".

A task is judged TRIVIAL if:
- The fix is < ~5 functional lines AND has no real conceptual content
- Or the gold patch only modifies docs without forcing real code changes
- Or the change is purely cosmetic (whitespace, comment, type annotation)

A task is judged SUBSTANTIAL if:
- The fix encodes a real behavior change (race condition, edge case, bug fix)
- The agent must understand context to apply the right change
- Even small, the patch matters

Usage:
    triviality_judge.py harbor_tasks/<task>           # single task
    triviality_judge.py --candidates /tmp/foo.json    # batch
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Backend config
# ---------------------------------------------------------------------------

DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com/anthropic")
DEEPSEEK_URL = f"{DEEPSEEK_BASE_URL}/v1/messages"
DEEPSEEK_MODEL = os.environ.get("DEEPSEEK_JUDGE_MODEL", "deepseek-v4-pro[1m]")

JUDGE_PROMPT = """\
You judge whether a software-engineering task is TRIVIAL or SUBSTANTIAL.

A task is TRIVIAL if a model with no understanding of the codebase could
plausibly pass it just by pattern-matching the instruction. Examples:
- Pure documentation/comment edits with no code behavior to verify
- Whitespace, formatting, or import-ordering only changes
- Type-annotation-only changes (e.g., adding `| None`)
- One-line constant tweaks with no logical reasoning required
- "Add a section to README" with literal copy-pasted text
- Changes that any code-completion would auto-suggest correctly

A task is SUBSTANTIAL if the agent must actually understand the bug:
- Race conditions, off-by-one errors, edge cases
- API mismatches, type errors with non-obvious correct types
- Logic bugs where the wrong fix is plausible
- Concurrency, memory, or correctness issues
- Cross-file refactors where the pattern matters

Read the gold patch and instruction below, then output JSON:

{
  "verdict": "trivial" | "substantial",
  "reason": "<=25 words",
  "confidence": 0.0-1.0
}

Output ONLY the JSON, no preamble. Keep `reason` under 25 words.

=== INSTRUCTION ===
{instruction}

=== GOLD PATCH (solve.sh) ===
{solve_sh}
"""


def build_prompt(task_dir: Path) -> str | None:
    instr = task_dir / "instruction.md"
    sv    = task_dir / "solution" / "solve.sh"
    if not instr.exists() or not sv.exists():
        return None
    instruction = instr.read_text(errors="ignore")[:4000]
    solve_sh    = sv.read_text(errors="ignore")[:8000]
    return (JUDGE_PROMPT
            .replace("{instruction}", instruction)
            .replace("{solve_sh}", solve_sh))


# ---------------------------------------------------------------------------
# Backend calls
# ---------------------------------------------------------------------------


async def call_deepseek(prompt: str, client: httpx.AsyncClient) -> str:
    r = await client.post(
        DEEPSEEK_URL,
        headers={
            "x-api-key": DEEPSEEK_KEY,
            "content-type": "application/json",
            "anthropic-version": "2023-06-01",
        },
        json={
            "model": DEEPSEEK_MODEL,
            "max_tokens": 300,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=60,
    )
    r.raise_for_status()
    data = r.json()
    return data["content"][0]["text"]


def parse_verdict(text: str) -> dict | None:
    """Parse JSON verdict from LLM output, tolerating markdown fences and prose."""
    t = text.strip()
    if t.startswith("```"):
        t = re.sub(r"^```(?:json)?\s*\n", "", t)
        t = re.sub(r"\n```\s*$", "", t)
    try:
        return json.loads(t)
    except Exception:
        pass
    s = t.find("{")
    e = t.rfind("}")
    if s == -1 or e == -1 or s >= e:
        return None
    try:
        return json.loads(t[s:e+1])
    except Exception:
        return None


async def judge_one(task_name: str, prompt: str, client: httpx.AsyncClient,
                    sem: asyncio.Semaphore) -> dict:
    out: dict[str, Any] = {"name": task_name, "verdict": None, "reason": "",
                           "backend": None, "confidence": None}
    if not DEEPSEEK_KEY:
        out["error"] = "no DEEPSEEK_API_KEY"
        return out
    async with sem:
        try:
            txt = await call_deepseek(prompt, client)
            v = parse_verdict(txt)
            if v and v.get("verdict") in ("trivial", "substantial"):
                out.update(v)
                out["backend"] = "deepseek"
                return out
            out["error"] = f"unparseable: {txt[:200]}"
        except Exception as e:
            out["error"] = str(e)[:200]
    return out


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


async def main_async(args: argparse.Namespace) -> None:
    if args.candidates:
        cands = json.loads(args.candidates.read_text())
        names = [r["name"] for r in cands["trivial"]]
    else:
        names = [p.name for p in args.task_dir.parent.glob(args.task_dir.name)]

    print(f"judging {len(names)} tasks…")

    sem = asyncio.Semaphore(args.concurrency)

    results: list[dict] = []
    async with httpx.AsyncClient() as client:
        async def runner(n: str) -> None:
            tdir = args.corpus / n
            prompt = build_prompt(tdir)
            if prompt is None:
                results.append({"name": n, "verdict": "skip",
                                "reason": "missing instruction or solve.sh"})
                return
            r = await judge_one(n, prompt, client, sem)
            results.append(r)
            verdict = r.get("verdict") or "ERROR"
            print(f"  [{len(results):>3}/{len(names)}] {verdict:>11s}  "
                  f"({r.get('backend','no-backend')})  {n}")

        await asyncio.gather(*[runner(n) for n in names])

    args.out.write_text(json.dumps(results, indent=2))
    counts: dict[str, int] = {}
    for r in results:
        counts[r["verdict"] or "error"] = counts.get(r["verdict"] or "error", 0) + 1
    print("\n=== Summary ===")
    for k, v in sorted(counts.items()):
        print(f"  {k:>11s}: {v}")
    print(f"\nResults → {args.out}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, default=Path("harbor_tasks"))
    ap.add_argument("--candidates", type=Path,
                    help="JSON from detect_trivial_tasks.py — uses .trivial[].name")
    ap.add_argument("--task-dir", type=Path, help="single task dir to judge")
    ap.add_argument("--concurrency", type=int, default=8)
    ap.add_argument("--out", type=Path, default=Path("/tmp/triviality_verdicts.json"))
    args = ap.parse_args()
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
