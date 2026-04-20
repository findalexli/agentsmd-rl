#!/usr/bin/env python3
"""Fast parallel task quality audit. Direct Anthropic API, one call per task.
~10x faster than harbor check (single prompt covers all 8 criteria).

Usage:
  .venv/bin/python scripts/audit_tasks_fast.py \\
    --task-dir harbor_tasks --concurrency 40 --model haiku
"""
from __future__ import annotations
import argparse, asyncio, concurrent.futures, json, os, time
from pathlib import Path
from collections import Counter, defaultdict

RUBRIC = [
    ("behavior_in_task_description", "All behavior that tests verify is clearly described in instruction.md (incl. exact file paths, function names, schema, commands). FAIL if tests require details not specified."),
    ("behavior_in_tests", "All behavior described in instruction.md is actually tested. FAIL if instruction has required behavior that tests don't check."),
    ("informative_test_structure", "Tests are well-organized with comments or sections describing what they check. FAIL if tests are a flat blob with no grouping or naming."),
    ("anti_cheating_measures", "Task discourages shortcuts. Agent cannot see solution/ or tests/. FAIL if answer is embedded in env files, tests trivially grep-matchable, or image includes solution."),
    ("structured_data_schema", "If task produces structured data (JSON/CSV/API/DB schema), the EXACT schema is documented in instruction.md or a referenced spec. PASS if not applicable."),
    ("pinned_dependencies", "Python/pip dependencies are version-pinned for reproducibility (apt packages need not be). FAIL if unpinned Python deps."),
    ("typos", "No typos in filenames, paths, commands, variable names. FAIL if any."),
    ("tests_or_solution_in_image", "Dockerfile does NOT COPY tests/ or solution/ into the image (harness mounts tests/ externally). FAIL if image includes them."),
]

PROMPT_TEMPLATE = """You are auditing the quality of a benchmark task used to evaluate LLM coding agents.

The agent receives ONLY `instruction.md`. It does NOT see `tests/` or `solution/`. Your job is to flag quality issues.

== instruction.md ==
{instruction}

== tests/test_outputs.py (first 8000 chars) ==
{tests}

== environment/Dockerfile (first 4000 chars) ==
{dockerfile}

== solution/solve.sh (first 4000 chars) ==
{solve}

---

Evaluate this task against these 8 criteria. For each, return PASS, FAIL, or NOT_APPLICABLE with a 1-sentence explanation.

{criteria}

Return a single JSON object (no prose) with this shape:
{{
  "behavior_in_task_description": {{"outcome": "pass|fail|not_applicable", "explanation": "..."}},
  "behavior_in_tests": {{...}},
  ...
}}
"""


def build_prompt(task_dir: Path) -> str:
    def read_trunc(p: Path, limit: int) -> str:
        if not p.exists(): return "(missing)"
        try: return p.read_text(errors="ignore")[:limit]
        except: return "(unreadable)"
    instr = read_trunc(task_dir / "instruction.md", 8000)
    tests = read_trunc(task_dir / "tests" / "test_outputs.py", 8000)
    if tests == "(missing)":
        tests = read_trunc(task_dir / "tests" / "test.sh", 8000)
    dockerfile = read_trunc(task_dir / "environment" / "Dockerfile", 4000)
    solve = read_trunc(task_dir / "solution" / "solve.sh", 4000)
    criteria_text = "\n".join(f"- **{name}**: {desc}" for name, desc in RUBRIC)
    return PROMPT_TEMPLATE.format(
        instruction=instr, tests=tests, dockerfile=dockerfile,
        solve=solve, criteria=criteria_text,
    )


def call_anthropic(prompt: str, api_key: str, model: str, max_retries: int = 3) -> dict:
    import urllib.request, urllib.error
    model_id = {"haiku": "claude-haiku-4-5", "sonnet": "claude-sonnet-4-5", "opus": "claude-opus-4-6"}.get(model, model)
    body = json.dumps({
        "model": model_id,
        "max_tokens": 2500,
        "messages": [{"role": "user", "content": prompt}],
    }).encode()
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(
                "https://api.anthropic.com/v1/messages",
                data=body,
                headers={"content-type": "application/json", "x-api-key": api_key, "anthropic-version": "2023-06-01"},
            )
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read())
            text = data["content"][0]["text"].strip()
            # Extract JSON (may be wrapped in ```json ... ```)
            if text.startswith("```"):
                lines = text.split("\n")
                text = "\n".join(l for l in lines[1:] if not l.startswith("```"))
            return json.loads(text)
        except (json.JSONDecodeError, KeyError) as e:
            if attempt < max_retries - 1:
                time.sleep(2 * (2 ** attempt))
                continue
            return {"_error": f"parse: {e}"}
        except urllib.error.HTTPError as e:
            if e.code in (429, 529, 500, 502, 503) and attempt < max_retries - 1:
                time.sleep(5 * (2 ** attempt))
                continue
            return {"_error": f"http: {e.code}"}
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(3)
                continue
            return {"_error": str(e)[:150]}
    return {"_error": "retries_exhausted"}


async def main_async(args):
    api_key = os.environ["ANTHROPIC_API_KEY"]
    task_dir = Path(args.task_dir)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Collect tasks
    tasks = [d.name for d in task_dir.iterdir()
             if d.is_dir() and (d / "instruction.md").exists()
             and (d / "tests").is_dir() and (d / "environment").is_dir()]
    # Skip already-done
    done = {f.stem for f in out_dir.glob("*.json") if f.stat().st_size > 50}
    todo = [t for t in tasks if t not in done]
    print(f"Tasks: {len(tasks)} total, {len(done)} done, {len(todo)} to audit")
    if args.sample:
        import random; random.seed(42); todo = random.sample(todo, min(args.sample, len(todo)))
        print(f"Sampled to {len(todo)}")

    loop = asyncio.get_event_loop()
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=args.concurrency * 2)
    loop.set_default_executor(executor)
    sem = asyncio.Semaphore(args.concurrency)
    t0 = time.monotonic()
    done_n = 0

    async def run_one(task_name: str):
        nonlocal done_n
        async with sem:
            prompt = build_prompt(task_dir / task_name)
            result = await loop.run_in_executor(None, call_anthropic, prompt, api_key, args.model)
        out_path = out_dir / f"{task_name}.json"
        out_path.write_text(json.dumps({"task": task_name, "checks": result}, indent=2))
        done_n += 1
        if done_n % 25 == 0:
            elapsed = time.monotonic() - t0
            rate = done_n / max(1, elapsed) * 60
            eta = (len(todo) - done_n) / max(1, rate) * 60
            print(f"  [{done_n}/{len(todo)}]  rate={rate:.0f}/min  eta={eta:.0f}s")

    await asyncio.gather(*(run_one(t) for t in todo))

    elapsed = time.monotonic() - t0
    print(f"\nDone in {elapsed:.0f}s ({elapsed/60:.1f}m). {len(todo)}/{args.concurrency} concurrency → {len(todo)/max(1,elapsed)*60:.0f}/min")

    # Aggregate
    print(f"\n=== Aggregate (scanning {out_dir}) ===")
    results = {}
    for f in out_dir.glob("*.json"):
        try:
            d = json.loads(f.read_text())
            if d.get("checks") and "_error" not in d["checks"]:
                results[f.stem] = d["checks"]
        except: pass
    print(f"Valid reports: {len(results)}")
    crit_totals = defaultdict(Counter)
    for task, checks in results.items():
        for name, info in checks.items():
            if isinstance(info, dict):
                crit_totals[name][info.get("outcome", "?")] += 1
    print("\nPer-criterion outcomes:")
    for name in [c[0] for c in RUBRIC]:
        c = crit_totals.get(name, Counter())
        total = sum(c.values())
        pass_n = c.get("pass", 0)
        print(f"  {name}: {pass_n}/{total} pass ({pass_n/max(1,total)*100:.0f}%)  | {dict(c)}")

    # Bad spec tasks
    bad_spec = [t for t, ch in results.items()
                if isinstance(ch.get("behavior_in_task_description"), dict)
                and ch["behavior_in_task_description"].get("outcome") == "fail"]
    print(f"\nTasks failing behavior_in_task_description (spec too vague): {len(bad_spec)}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--task-dir", default="harbor_tasks")
    p.add_argument("--output-dir", default=f"pipeline_logs/audit_fast_{int(time.time())}")
    p.add_argument("--concurrency", type=int, default=40)
    p.add_argument("--model", default="haiku", choices=["haiku", "sonnet", "opus"])
    p.add_argument("--sample", type=int, default=None, help="Random sample of N tasks")
    args = p.parse_args()
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
