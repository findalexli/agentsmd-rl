#!/usr/bin/env python3
"""Fireworks Kimi K2.5 rate limit probe.

Sends streaming requests with realistic token sizes at increasing
concurrency. All requests use stream=true (required for max_tokens>4096).
Parses SSE usage from the message_delta stop event.

Usage:
    set -a && source .env && set +a
    .venv/bin/python scripts/fireworks_rate_limit_probe.py
"""

import asyncio
import json
import os
import sys
import time

import httpx

API_URL = "https://api.fireworks.ai/inference/v1/messages"
MODEL = "accounts/fireworks/routers/kimi-k2p5-turbo"
API_KEY = os.environ.get("FIREWORKS_API_KEY", "")

HEADERS = {
    "Content-Type": "application/json",
    "x-api-key": API_KEY,
    "anthropic-version": "2023-06-01",
}


def _pad(n_tokens: int) -> str:
    """Generate filler text targeting ~n_tokens input tokens."""
    # ~1.3 tokens per word for simple English
    return ("buffalo " * max(1, n_tokens // 2))[: n_tokens * 4]


async def send(
    i: int,
    client: httpx.AsyncClient,
    input_tok: int,
    max_output: int,
) -> tuple[int, float, int, int, int, str]:
    """Send one streaming request. Returns (status, latency_ms, in, cached, out, err)."""
    body = {
        "model": MODEL,
        "max_tokens": max_output,
        "stream": True,
        "messages": [
            {"role": "user", "content": f"Say OK. {_pad(input_tok)}"},
        ],
    }
    t0 = time.monotonic()
    try:
        async with client.stream(
            "POST", API_URL, json=body, headers=HEADERS, timeout=180
        ) as resp:
            status = resp.status_code
            chunks: list[str] = []
            async for chunk in resp.aiter_text():
                chunks.append(chunk)
            dt = (time.monotonic() - t0) * 1000
            text = "".join(chunks)

            if status != 200:
                return status, dt, 0, 0, 0, text[:150]

            # Parse usage from the message_delta event (last one with usage)
            inp = out = cached = 0
            for line in reversed(text.split("\n")):
                if not line.startswith("data: ") or line == "data: [DONE]":
                    continue
                try:
                    d = json.loads(line[6:])
                    u = d.get("usage", {})
                    if u.get("output_tokens"):
                        inp = u.get("input_tokens", 0)
                        out = u.get("output_tokens", 0)
                        cached = u.get("cache_read_input_tokens", 0)
                        break
                except json.JSONDecodeError:
                    pass
            return 200, dt, inp, cached, out, ""
    except Exception as e:
        dt = (time.monotonic() - t0) * 1000
        return -1, dt, 0, 0, 0, str(e)[:150]


async def run_test(label: str, n: int, in_tok: int, max_out: int = 4096):
    """Run n concurrent streaming requests and report."""
    print(f"\n{'=' * 65}")
    print(f"  {label}")
    print(f"  {n} concurrent, ~{in_tok:,} input tokens, max_out={max_out}")
    print(f"{'=' * 65}")

    async with httpx.AsyncClient() as client:
        t0 = time.monotonic()
        results = await asyncio.gather(
            *[send(i, client, in_tok, max_out) for i in range(n)]
        )
        wall = time.monotonic() - t0

    ok = err429 = errors = 0
    total_in = total_out = total_cached = 0
    latencies: list[float] = []

    for status, dt, inp, cached, out, err in sorted(results, key=lambda r: r[1]):
        tag = f"req: {status}"
        if status == 200:
            ok += 1
            total_in += inp
            total_out += out
            total_cached += cached
            latencies.append(dt)
            print(f"    {status}  {dt:7.0f}ms  in={inp:6d}  cache={cached:6d}  out={out:4d}")
        elif status == 429:
            err429 += 1
            print(f"    429  {dt:7.0f}ms  RATE LIMITED  {err[:80]}")
        else:
            errors += 1
            print(f"    {status}  {dt:7.0f}ms  {err[:80]}")

    print(f"\n  Summary: {ok} OK  {err429} 429  {errors} error  wall={wall:.1f}s")
    if ok:
        avg_lat = sum(latencies) / ok
        rpm = ok / wall * 60
        tpm = total_in / wall * 60 if total_in else 0
        print(f"  Avg latency: {avg_lat:.0f}ms  RPM={rpm:.1f}"
              f"  in_TPM={tpm:,.0f}  cached={total_cached:,}")
    return ok, err429


async def main():
    if not API_KEY:
        print("ERROR: FIREWORKS_API_KEY not set")
        sys.exit(1)

    print("Fireworks Kimi K2.5 Rate Limit Probe (streaming)")
    print(f"API Key: ...{API_KEY[-4:]}")

    # ── Escalating concurrency at scaffold Turn-1 size (3.5K tokens) ──
    for n in [1, 5, 10, 15, 20, 30]:
        await run_test(f"Turn-1 size ({n} concurrent)", n, 3500, 4096)

    # ── Escalating concurrency at mid-scaffold size (20K tokens) ──
    for n in [3, 5, 10, 15]:
        await run_test(f"Mid-scaffold ({n} concurrent)", n, 20000, 4096)

    # ── Large payloads ──
    await run_test("Late-scaffold (5 × 50K)", 5, 50000, 4096)
    await run_test("Very late (3 × 100K)", 3, 100000, 4096)

    # ── Sustained sequential throughput ──
    print(f"\n{'=' * 65}")
    print(f"  Sustained sequential: 15 × 20K tokens, streaming")
    print(f"{'=' * 65}")
    async with httpx.AsyncClient() as client:
        t0 = time.monotonic()
        ok_count = 0
        total_in_seq = 0
        for i in range(15):
            status, dt, inp, cached, out, err = await send(i, client, 20000, 4096)
            ok_count += status == 200
            total_in_seq += inp
            sym = "✓" if status == 200 else "✗"
            print(f"    {sym} req{i:2d}: {status}  {dt:7.0f}ms  in={inp:6d}  out={out:4d}")
        wall = time.monotonic() - t0
        print(f"  {ok_count}/15 OK in {wall:.0f}s"
              f"  = {ok_count / wall * 60:.1f} RPM"
              f"  = {total_in_seq / wall * 60:,.0f} in_TPM")

    print(f"\n{'=' * 65}")
    print("PROBE COMPLETE")
    print(f"{'=' * 65}")


if __name__ == "__main__":
    asyncio.run(main())
