#!/usr/bin/env python3
"""Reverse proxy: receives Anthropic-format API calls, forwards to Fireworks.

E2B sandboxes connect to this proxy (your home IP) instead of Fireworks directly,
bypassing Fireworks' IP restrictions on E2B sandbox IPs.

Usage:
    set -a && source .env && set +a
    python scripts/fireworks_proxy.py --port 8080

Then set in backends.py:
    base_url="http://<YOUR_HOME_IP>:8080/inference"
"""

import argparse
import asyncio
import os
import sys
from aiohttp import web, ClientSession, ClientTimeout

FIREWORKS_BASE = "https://api.fireworks.ai"
FIREWORKS_API_KEY = os.environ.get("FIREWORKS_API_KEY", "")

async def proxy_handler(request: web.Request) -> web.StreamResponse:
    """Forward any request to Fireworks, preserving path and headers."""
    path = request.path
    target_url = f"{FIREWORKS_BASE}{path}"

    # Read request body
    body = await request.read()

    # Forward headers, replace auth with our Fireworks key
    headers = {}
    for key, value in request.headers.items():
        key_lower = key.lower()
        if key_lower in ('host', 'content-length', 'transfer-encoding'):
            continue
        headers[key] = value

    # Always use our Fireworks API key
    headers['Authorization'] = f'Bearer {FIREWORKS_API_KEY}'
    # Also set x-api-key for Anthropic-format compatibility
    if 'x-api-key' in headers:
        headers['x-api-key'] = FIREWORKS_API_KEY

    timeout = ClientTimeout(total=600)  # 10 min for long claude -p calls
    async with ClientSession(timeout=timeout) as session:
        async with session.request(
            method=request.method,
            url=target_url,
            headers=headers,
            data=body,
            params=request.query,
        ) as resp:
            # Stream response back
            response = web.StreamResponse(
                status=resp.status,
                headers={k: v for k, v in resp.headers.items()
                         if k.lower() not in ('transfer-encoding', 'content-encoding')},
            )
            await response.prepare(request)
            async for chunk in resp.content.iter_any():
                await response.write(chunk)
            await response.write_eof()
            return response


async def health(request: web.Request) -> web.Response:
    return web.Response(text="ok")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--host", default="0.0.0.0")
    args = parser.parse_args()

    if not FIREWORKS_API_KEY:
        print("FIREWORKS_API_KEY not set")
        sys.exit(1)

    app = web.Application()
    app.router.add_route("*", "/health", health)
    app.router.add_route("*", "/{path:.*}", proxy_handler)

    print(f"Fireworks proxy listening on {args.host}:{args.port}")
    print(f"Forward: http://{args.host}:{args.port}/inference -> {FIREWORKS_BASE}/inference")
    print(f"Set base_url='http://<YOUR_IP>:{args.port}/inference' in backends.py")
    web.run_app(app, host=args.host, port=args.port, print=None)


if __name__ == "__main__":
    main()
