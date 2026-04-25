#!/usr/bin/env python3
"""LLM judge for task triviality.

Asks GLM-5.1 (z.ai) — falling back to Fireworks Kimi K2.5 turbo on failure —
"is this task trivial? would any model pass it without reasoning?"

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
import sys
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Backend config
# ---------------------------------------------------------------------------

GLM_KEY    = os.environ.get("GLM_API_KEY", "")
FW_KEY     = os.environ.get("FIREWORKS_API_KEY", "")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")

GLM_URL    = "https://api.z.ai/api/anthropic/v1/messages"
FW_URL     = "https://api.fireworks.ai/inference/v1/chat/completions"
GEMINI_URL = ("https://generativelanguage.googleapis.com/v1beta/models/"
              "gemini-2.5-flash:generateContent")
KIMI_MODEL = "accounts/fireworks/routers/kimi-k2p5-turbo"

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
  "reason": "≤25 words",
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


async def call_glm(prompt: str, client: httpx.AsyncClient) -> str:
    r = await client.post(
        GLM_URL,
        headers={
            "x-api-key": GLM_KEY,
            "content-type": "application/json",
            "anthropic-version": "2023-06-01",
        },
        json={
            "model": "claude-sonnet-4-5",
            "max_tokens": 200,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=45,
    )
    r.raise_for_status()
    data = r.json()
    return data["content"][0]["text"]


async def call_kimi(prompt: str, client: httpx.AsyncClient) -> str:
    r = await client.post(
        FW_URL,
        headers={"Authorization": f"Bearer {FW_KEY}", "Content-Type": "application/json"},
        json={
            "model": KIMI_MODEL,
            "max_tokens": 300,
            "messages": [
                {"role": "system", "content": "Output only valid JSON. No preamble."},
                {"role": "user", "content": prompt},
            ],
        },
        timeout=60,
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


async def call_gemini(prompt: str, client: httpx.AsyncClient) -> str:
    r = await client.post(
        f"{GEMINI_URL}?key={GEMINI_KEY}",
        headers={"Content-Type": "application/json"},
        json={
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.0,
                "maxOutputTokens": 1000,
                "responseMimeType": "application/json",
                "responseSchema": {
                    "type": "OBJECT",
                    "properties": {
                        "verdict": {"type": "STRING", "enum": ["trivial", "substantial"]},
                        "reason": {"type": "STRING"},
                        "confidence": {"type": "NUMBER"},
                    },
                    "required": ["verdict", "reason"],
                },
            },
        },
        timeout=60,
    )
    r.raise_for_status()
    data = r.json()
    cand = (data.get("candidates") or [{}])[0]
    parts = (cand.get("content") or {}).get("parts") or [{}]
    return parts[0].get("text", "")


def parse_verdict(text: str) -> dict | None:
    """Parse JSON verdict from LLM output, tolerating markdown fences and prose."""
    # Strip markdown fences
    t = text.strip()
    if t.startswith("```"):
        # Drop opening fence (and optional 'json' tag) and closing fence
        t = re.sub(r"^```(?:json)?\s*\n", "", t)
        t = re.sub(r"\n```\s*$", "", t)
    # Try direct parse
    try:
        return json.loads(t)
    except Exception:
        pass
    # Try greedy brace extraction
    s = t.find("{")
    e = t.rfind("}")
    if s == -1 or e == -1 or s >= e:
        return None
    try:
        return json.loads(t[s:e+1])
    except Exception:
        return None


async def judge_one(task_name: str, prompt: str, client: httpx.AsyncClient,
                    glm_sem: asyncio.Semaphore, kimi_sem: asyncio.Semaphore,
                    gemini_sem: asyncio.Semaphore, primary: str = "gemini") -> dict:
    """Call primary backend, fall back through other available backends.

    Default primary = gemini (most reliable + structured output).
    """
    out: dict[str, Any] = {"name": task_name, "verdict": None, "reason": "",
                           "backend": None, "confidence": None}

    backends: list[tuple[str, asyncio.Semaphore, str, callable]] = []
    if GEMINI_KEY:
        backends.append(("gemini", gemini_sem, "gemini_error", call_gemini))
    if GLM_KEY:
        backends.append(("glm",    glm_sem,    "glm_error",    call_glm))
    if FW_KEY:
        backends.append(("kimi",   kimi_sem,   "kimi_error",   call_kimi))
    # Reorder: primary first, others after
    backends.sort(key=lambda b: 0 if b[0] == primary else 1)

    for name, sem, err_key, fn in backends:
        async with sem:
            try:
                txt = await fn(prompt, client)
                v = parse_verdict(txt)
                if v and v.get("verdict") in ("trivial", "substantial"):
                    out.update(v)
                    out["backend"] = name
                    return out
                out[err_key] = f"unparseable: {txt[:200]}"
            except Exception as e:
                out[err_key] = str(e)[:200]
    return out


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


async def main_async(args: argparse.Namespace) -> None:
    # Load candidates
    if args.candidates:
        cands = json.loads(args.candidates.read_text())
        names = [r["name"] for r in cands["trivial"]]
    else:
        names = [p.name for p in args.task_dir.parent.glob(args.task_dir.name)]

    print(f"judging {len(names)} tasks…")

    glm_sem    = asyncio.Semaphore(args.glm_concurrency)
    kimi_sem   = asyncio.Semaphore(args.kimi_concurrency)
    gemini_sem = asyncio.Semaphore(args.gemini_concurrency)

    results: list[dict] = []
    async with httpx.AsyncClient() as client:
        async def runner(n: str) -> None:
            tdir = args.corpus / n
            prompt = build_prompt(tdir)
            if prompt is None:
                results.append({"name": n, "verdict": "skip",
                                "reason": "missing instruction or solve.sh"})
                return
            r = await judge_one(n, prompt, client, glm_sem, kimi_sem, gemini_sem,
                                primary=args.primary)
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
    ap.add_argument("--glm-concurrency", type=int, default=4)
    ap.add_argument("--kimi-concurrency", type=int, default=2)
    ap.add_argument("--gemini-concurrency", type=int, default=8)
    ap.add_argument("--primary", choices=["gemini", "glm", "kimi"], default="gemini",
                    help="Primary judge backend (default: gemini)")
    ap.add_argument("--out", type=Path, default=Path("/tmp/triviality_verdicts.json"))
    args = ap.parse_args()
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
