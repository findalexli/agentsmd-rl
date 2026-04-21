"""Multi-backend pool with automatic fallback for LLM API calls.

Supports Anthropic-format (GLM, Anthropic API key) and OpenAI-format
(OpenRouter/Fireworks for Kimi K2.5) backends. Routes requests cheapest-first;
on 429 rate limits, transparently retries on the next available backend.

Two execution modes share the same pool:
  - Direct API (httpx)  — ~5 MB/request, for single-shot tasks
  - Subprocess (claude -p) — ~300 MB/process, for multi-turn agent tasks
    Note: OpenAI-format backends need a litellm proxy for subprocess mode.
"""

from __future__ import annotations

import asyncio
import json
import os
import random
import re
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import AsyncIterator, Literal

import httpx

# ---------------------------------------------------------------------------
# Backend
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Backend:
    """Immutable config for one LLM backend."""

    name: str
    base_url: str                          # "" → https://api.anthropic.com
    api_key: str
    auth_type: Literal["x-api-key", "bearer"] = "x-api-key"
    api_format: Literal["anthropic", "openai"] = "anthropic"
    model_map: dict[str, str] = field(default_factory=dict)
    max_concurrent: int = 4
    cost_tier: int = 0                     # 0 free → 1 sub → 2 paid → 3 cheap-paid
    supports_direct: bool = True           # False for OAuth
    supports_subprocess: bool = True       # False for OpenAI-format without proxy

    def resolve_model(self, logical: str) -> str:
        return self.model_map.get(logical, logical)

    def api_headers(self) -> dict[str, str]:
        h: dict[str, str] = {"content-type": "application/json"}
        if self.api_format == "anthropic":
            h["anthropic-version"] = "2023-06-01"
        if self.auth_type == "bearer":
            h["authorization"] = f"Bearer {self.api_key}"
        else:
            h["x-api-key"] = self.api_key
        return h

    def messages_url(self) -> str:
        base = self.base_url or "https://api.anthropic.com"
        if self.api_format == "openai":
            return f"{base}/chat/completions"
        return f"{base}/v1/messages"

    def subprocess_env(self) -> dict[str, str]:
        """Env vars for a claude -p subprocess.

        For Fire Pass setup: sets ALL model env vars (ANTHROPIC_MODEL,
        ANTHROPIC_SMALL_FAST_MODEL, and the DEFAULT_* variants) so Claude Code
        subagents also route through the Fireworks turbo router instead of
        falling back to Anthropic.
        """
        env: dict[str, str] = {}
        if self.base_url:
            env["ANTHROPIC_BASE_URL"] = self.base_url
        if self.auth_type == "bearer":
            env["CLAUDE_ACCESS_TOKEN"] = self.api_key
        else:
            env["ANTHROPIC_API_KEY"] = self.api_key
            env["ANTHROPIC_AUTH_TOKEN"] = self.api_key
        for logical, actual in self.model_map.items():
            env[f"ANTHROPIC_DEFAULT_{logical.upper()}_MODEL"] = actual
        # Fire Pass: force subagents to use the same model (not fallback to anthropic)
        primary = self.model_map.get("opus") or self.model_map.get("sonnet") or ""
        if primary:
            env["ANTHROPIC_MODEL"] = primary
            env["ANTHROPIC_SMALL_FAST_MODEL"] = primary
        return env


# ---------------------------------------------------------------------------
# Pool state
# ---------------------------------------------------------------------------

@dataclass
class _Slot:
    backend: Backend
    sem: asyncio.Semaphore = field(init=False)
    cooldown_until: float = 0.0
    consecutive_429s: int = 0
    total_ok: int = 0
    total_429: int = 0
    available: bool = True

    def __post_init__(self) -> None:
        self.sem = asyncio.Semaphore(self.backend.max_concurrent)

    @property
    def in_cooldown(self) -> bool:
        return time.monotonic() < self.cooldown_until


class BackendPool:
    """Routes requests across backends, cheapest-first, with 429 fallback."""

    def __init__(self, backends: list[Backend], acquire_timeout: float = 3600):
        self._slots = sorted(
            [_Slot(b) for b in backends],
            key=lambda s: s.backend.cost_tier,
        )
        self._timeout = acquire_timeout

    @property
    def names(self) -> list[str]:
        return [s.backend.name for s in self._slots]

    # -- acquire / release --------------------------------------------------

    @asynccontextmanager
    async def acquire(self, *, direct_only: bool = False) -> AsyncIterator[Backend]:
        """Acquire the cheapest available backend. Releases on context exit."""
        slot = await self._wait(direct_only)
        try:
            yield slot.backend
        finally:
            slot.sem.release()

    def _ordered_slots(self) -> list["_Slot"]:
        """Return slots sorted for acquisition:
          primary:   cost_tier asc (cheapest first)
          secondary: free-capacity ratio DESC (least-loaded first within tier)
        This load-balances same-tier backends (fixes retrofit-run-1 where
        fireworks was first in declaration order and got hammered while
        MiniMax stayed idle)."""
        return sorted(
            self._slots,
            key=lambda s: (
                s.backend.cost_tier,
                # Negate free ratio so higher free-ratio sorts first within tier.
                # Guard against max_concurrent=0 though that would be a bug.
                -(s.sem._value / max(1, s.backend.max_concurrent)),
            ),
        )

    async def _wait(self, direct_only: bool) -> _Slot:
        deadline = time.monotonic() + self._timeout
        while True:
            now = time.monotonic()

            # Auto-resurrect suspended/dead backends whose cooldown has expired.
            # Instead of permanent death, backends get a second chance after
            # their cooldown period (default 5 min). The next request will
            # either succeed (resetting consecutive_429s) or fail again
            # (triggering another suspension cycle).
            for s in self._slots:
                if not s.available and now >= s.cooldown_until > 0:
                    s.available = True
                    print(f"  [{_ts()}] {s.backend.name} RESURRECTED "
                          f"(was suspended after {s.consecutive_429s} 429s)")

            # Prefer waiting for a cheap backend in short cooldown over
            # immediately falling back to an expensive one.
            # Note: _value check + await acquire() is safe in asyncio because
            # acquire() returns immediately (no yield) when _value > 0.
            cheapest_wait: float | None = None
            for s in self._ordered_slots():
                if not s.available:
                    continue
                if direct_only and not s.backend.supports_direct:
                    continue
                remaining = s.cooldown_until - now
                if remaining <= 0 and s.sem._value > 0:
                    await s.sem.acquire()
                    return s
                if 0 < remaining <= 15 and s.sem._value > 0:
                    if cheapest_wait is None or remaining < cheapest_wait:
                        cheapest_wait = remaining

            # If a cheap backend is cooling down briefly, wait for it
            if cheapest_wait is not None:
                await asyncio.sleep(cheapest_wait + 0.1)
                continue

            # Otherwise try any available backend (expensive tiers)
            for s in self._ordered_slots():
                if not s.available:
                    continue
                if direct_only and not s.backend.supports_direct:
                    continue
                if now < s.cooldown_until:
                    continue
                if s.sem._value > 0:
                    await s.sem.acquire()
                    return s

            # All busy or cooling — sleep until earliest cooldown.
            waits = [
                s.cooldown_until - now
                for s in self._slots
                if s.available and now < s.cooldown_until
                and (not direct_only or s.backend.supports_direct)
            ]
            delay = max(0.1, min(min(waits, default=2.0), 5.0))
            if time.monotonic() + delay > deadline:
                raise TimeoutError(
                    f"No backend available within {self._timeout}s. "
                    f"Pool: {self.stats()}"
                )
            await asyncio.sleep(delay)

    # -- feedback -----------------------------------------------------------

    def report_success(self, backend: Backend) -> None:
        s = self._find(backend)
        s.consecutive_429s = 0
        s.total_ok += 1

    def report_429(self, backend: Backend) -> None:
        s = self._find(backend)
        s.consecutive_429s += 1
        s.total_429 += 1

        # Suspend instead of blacklist — after 20 consecutive 429s, stop sending
        # new work but schedule a resurrection probe in 5 minutes.
        if s.consecutive_429s >= 20 and s.available:
            s.available = False
            # Schedule resurrection probe — pool will re-check in 5 min
            s.cooldown_until = time.monotonic() + 300
            print(f"  [{_ts()}] {backend.name} SUSPENDED after "
                  f"{s.consecutive_429s} consecutive 429s, will probe in 300s")
            return

        # Short exponential backoff — start at 10s, cap at 120s.
        # Old: 30s * 2^n → 600s cap (pool stuck for 10 min per 429)
        # New: 10s * 2^n → 120s cap (recover in ~2 min even after many 429s)
        base = 10 * (2 ** min(s.consecutive_429s - 1, 4))  # 10, 20, 40, 80, 160→cap
        delay = min(base, 120) + random.uniform(0, 15)
        s.cooldown_until = time.monotonic() + delay
        print(f"  [{_ts()}] 429 on {backend.name}, cooldown {delay:.0f}s "
              f"(consecutive: {s.consecutive_429s})")

    def report_dead(self, backend: Backend) -> None:
        s = self._find(backend)
        s.available = False
        # Allow resurrection after 5 minutes instead of permanent death
        s.cooldown_until = time.monotonic() + 300
        print(f"  [{_ts()}] {backend.name} marked dead, will probe in 300s")

    def _find(self, backend: Backend) -> _Slot:
        for s in self._slots:
            if s.backend is backend:
                return s
        raise ValueError(f"Unknown backend: {backend.name}")

    # -- stats --------------------------------------------------------------

    def stats(self) -> str:
        parts = []
        for s in self._slots:
            state = "dead" if not s.available else "ok"
            parts.append(f"{s.backend.name}({s.total_ok}ok/{s.total_429}×429/{state})")
        return " | ".join(parts)


def _ts() -> str:
    return time.strftime("%H:%M:%S")


# ---------------------------------------------------------------------------
# Direct API client
# ---------------------------------------------------------------------------

class RateLimitError(Exception):
    pass


class APIError(Exception):
    def __init__(self, status: int, body: str):
        self.status = status
        super().__init__(f"HTTP {status}: {body[:300]}")


async def call_api(
    pool: BackendPool,
    *,
    messages: list[dict],
    model: str = "opus",
    max_tokens: int = 16384,
    system: str | None = None,
    http: httpx.AsyncClient | None = None,
) -> tuple[str, dict | None, str]:
    """Single-shot LLM call with automatic backend fallback.

    Returns ``(response_text, usage_or_None, backend_name)``.
    Retries across backends on 429; raises on persistent failure.
    """
    own_client = http is None
    if own_client:
        http = httpx.AsyncClient(timeout=httpx.Timeout(300, connect=15))

    last_err: Exception | None = None
    max_attempts = len(pool._slots) * 3
    try:
        for _ in range(max_attempts):
            async with pool.acquire(direct_only=True) as backend:
                try:
                    resp = await http.post(
                        backend.messages_url(),
                        json=_build_request(backend, messages, model, max_tokens, system),
                        headers=backend.api_headers(),
                    )
                except (httpx.ConnectError, httpx.ReadTimeout) as e:
                    pool.report_429(backend)
                    last_err = e
                    continue

                if resp.status_code == 200:
                    text, usage = _parse_response(backend, resp.json())
                    pool.report_success(backend)
                    return text, usage, backend.name

                if resp.status_code == 429:
                    pool.report_429(backend)
                    last_err = RateLimitError(resp.text[:200])
                    continue

                if resp.status_code == 401:
                    pool.report_dead(backend)
                    last_err = APIError(401, resp.text)
                    continue

                if resp.status_code >= 500:
                    last_err = APIError(resp.status_code, resp.text)
                    continue

                raise APIError(resp.status_code, resp.text)

        raise last_err or RuntimeError("All backends exhausted")
    finally:
        if own_client:
            await http.aclose()


def _build_request(
    backend: Backend,
    messages: list[dict],
    model: str,
    max_tokens: int,
    system: str | None,
) -> dict:
    resolved = backend.resolve_model(model)
    if backend.api_format == "openai":
        msgs = []
        if system:
            msgs.append({"role": "system", "content": system})
        msgs.extend(messages)
        return {"model": resolved, "max_tokens": max_tokens, "messages": msgs}
    else:
        body: dict = {"model": resolved, "max_tokens": max_tokens, "messages": messages}
        if system:
            body["system"] = system
        return body


def _parse_response(backend: Backend, data: dict) -> tuple[str, dict | None]:
    """Extract (text, usage) from either Anthropic or OpenAI response format."""
    if backend.api_format == "openai":
        choices = data.get("choices", [])
        if choices:
            msg = choices[0].get("message", {})
            text = msg.get("content") or ""
        else:
            text = ""
        usage = data.get("usage")
        return text, usage
    else:
        blocks = data.get("content", [])
        text = "".join(b["text"] for b in blocks if b.get("type") == "text")
        return text, data.get("usage")


# ---------------------------------------------------------------------------
# Output parsing — extract file contents from LLM response
# ---------------------------------------------------------------------------

_FILE_BLOCK = re.compile(
    r"<file\s+path=[\"']([^\"']+)[\"']\s*>\n(.*?)</file>",
    re.DOTALL,
)
_NAMED_FENCE = re.compile(
    r"```(?:python|yaml|toml)?\s+([\w./]+)\n(.*?)```",
    re.DOTALL,
)
_PLAIN_FENCE = re.compile(
    r"```(python|yaml|toml)\n(.*?)```",
    re.DOTALL,
)


def parse_file_blocks(text: str) -> dict[str, str]:
    """Extract named file contents from LLM response.

    Tries, in order:
      1. ``<file path="...">`` XML tags (most explicit)
      2. Fenced blocks with filename: ````` ```python test_outputs.py``
      3. Heuristic: largest ``python`` block → test_outputs.py,
         ``yaml`` block containing ``checks:`` → eval_manifest.yaml
    """
    blocks: dict[str, str] = {}

    # 1. XML-style tags
    for m in _FILE_BLOCK.finditer(text):
        blocks[m.group(1)] = m.group(2).strip()
    if blocks:
        return blocks

    # 2. Named fenced blocks
    for m in _NAMED_FENCE.finditer(text):
        blocks[m.group(1)] = m.group(2).strip()
    if blocks:
        return blocks

    # 3. Heuristic: match by content
    py_blocks = []
    yaml_blocks = []
    for m in _PLAIN_FENCE.finditer(text):
        lang, content = m.group(1), m.group(2).strip()
        if lang == "python":
            py_blocks.append(content)
        elif lang == "yaml":
            yaml_blocks.append(content)

    # Largest python block with test functions → test_outputs.py
    test_blocks = [b for b in py_blocks if "def test_" in b]
    if test_blocks:
        blocks["tests/test_outputs.py"] = max(test_blocks, key=len)

    # YAML block with checks → eval_manifest.yaml
    manifest_blocks = [b for b in yaml_blocks if "checks:" in b or "version:" in b]
    if manifest_blocks:
        blocks["eval_manifest.yaml"] = max(manifest_blocks, key=len)

    return blocks


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def backends_from_env(env_file: Path | None = None) -> list[Backend]:
    """Discover available backends from .env and os.environ."""
    dotenv: dict[str, str] = {}
    ef = env_file or Path(__file__).parent.parent / ".env"
    if ef.exists():
        for line in ef.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            dotenv[k.strip()] = v.strip().strip('"').strip("'")

    def _get(key: str) -> str:
        return os.environ.get(key) or dotenv.get(key, "")

    def _enabled(key: str) -> bool:
        """A flag is enabled iff its value is exactly '1' (truthy in our convention).
        Note: returning the raw _get() string would treat '0' as truthy in Python."""
        return _get(key) == "1"

    backends: list[Backend] = []

    # GLM-5.1 — free via Z.AI Anthropic proxy (set GLM_ENABLED=1)
    if _get("GLM_API_KEY") and _enabled("GLM_ENABLED"):
        backends.append(Backend(
            name="glm",
            base_url="https://api.z.ai/api/anthropic",
            api_key=_get("GLM_API_KEY"),
            model_map={"opus": "glm-5.1", "sonnet": "glm-5.1", "haiku": "glm-4.5-air"},
            max_concurrent=int(_get("GLM_MAX_CONCURRENT") or 30),
            cost_tier=0,  # free
        ))

    # ─── Tier-1 backends — ORDER MATTERS ─────────────────────────
    # BackendPool sorts by cost_tier (stable), so within the same tier we pick
    # in declaration order. In retrofit run 1, listing Fireworks first caused
    # it to absorb ALL overflow from GLM (30→78 workers = 48 spillover) — it
    # was hammered with 127× 429 while MiniMax stayed at 0×. Rebalance by
    # listing MiniMax FIRST so the first 50 tier-1 spillover lands there.

    # MiniMax via Anthropic-compatible proxy (MiniMax-M2.7)
    # Tier 1: cheap, subscription-style. In run 1 with max_concurrent=20, it
    # completed 414 tasks with only 3 × 429 — room to scale. Bumped to 50.
    if _get("MINIMAX_API_KEY") and _enabled("MINIMAX_ENABLED"):
        backends.append(Backend(
            name="minimax",
            base_url="https://api.minimax.io/anthropic",
            api_key=_get("MINIMAX_API_KEY"),
            auth_type="x-api-key",
            model_map={
                "opus": "MiniMax-M2.7",
                "sonnet": "MiniMax-M2.7",
                "haiku": "MiniMax-M2.7",
            },
            max_concurrent=int(_get("MINIMAX_MAX_CONCURRENT") or 50),
            cost_tier=1,
        ))

    # Kimi K2.5 via Fireworks — Anthropic-compatible API, supports subprocess
    # DISABLED 2026-04-13: account suspended (412 PRECONDITION_FAILED)
    # Re-enable by setting FIREWORKS_ENABLED=1 after restoring billing
    if _get("FIREWORKS_API_KEY") and _enabled("FIREWORKS_ENABLED"):
        backends.append(Backend(
            name="fireworks",
            base_url=_get("FIREWORKS_BASE_URL") or "https://api.fireworks.ai/inference",
            api_key=_get("FIREWORKS_API_KEY"),
            model_map={
                "opus": "accounts/fireworks/routers/kimi-k2p5-turbo",
                "sonnet": "accounts/fireworks/routers/kimi-k2p5-turbo",
                "haiku": "accounts/fireworks/routers/kimi-k2p5-turbo",
            },
            # Retrofit run 1: 127× 429 at max_concurrent=100 → 26× 429 at 50 —
            # provider-side limit is tighter than our semaphore. MiniMax
            # (listed before) takes first pick of tier-1 spillover.
            # Override at launch time with FIREWORKS_MAX_CONCURRENT=N.
            max_concurrent=int(_get("FIREWORKS_MAX_CONCURRENT") or 50),
            cost_tier=1,
        ))

    # Chutes.ai — OpenAI-compatible serverless GPU provider
    # Has MiniMax-M2.5-TEE, Kimi-K2.5-TEE, DeepSeek, GLM-5.1, etc.
    # Uses litellm proxy inside E2B sandbox to translate OpenAI → Anthropic format.
    # Different rate limits from Fireworks — good for parallel workloads.
    if _get("CHUTES_API_KEY") and _enabled("CHUTES_ENABLED"):
        chutes_model = _get("CHUTES_MODEL") or "moonshotai/Kimi-K2.5-TEE"
        backends.append(Backend(
            name="chutes",
            base_url="http://localhost:4000",  # litellm proxy started inside sandbox
            api_key="dummy",  # litellm doesn't need auth from localhost
            model_map={"opus": "opus", "sonnet": "sonnet", "haiku": "haiku"},
            max_concurrent=int(_get("CHUTES_MAX_CONCURRENT") or 5),
            cost_tier=1,
        ))

    # Gemini 3.1 Pro via litellm proxy inside sandbox
    # DISABLED as main agent — thinking tokens too expensive ($0.47/task vs $0.05 for Kimi)
    # Gemini is used ONLY for rubric judge (1 API call/task via judge.py)
    # To re-enable: set GEMINI_AS_AGENT=1 in env
    if _get("GEMINI_API_KEY") and _get("GEMINI_AS_AGENT"):
        backends.append(Backend(
            name="gemini",
            base_url="http://localhost:4000",  # litellm proxy started inside sandbox
            api_key="dummy",  # litellm doesn't need auth from localhost
            model_map={"opus": "opus", "sonnet": "sonnet", "haiku": "haiku"},
            max_concurrent=50,
            cost_tier=0,
        ))

    # Anthropic API key — direct, full API access, pay-per-token
    # Tier 2: reliable but paid. Use as primary when Fireworks/GLM unavailable.
    # Set ANTHROPIC_ENABLED=1 to include in pool (off by default — prefer cheap Kimi)
    if _get("ANTHROPIC_API_KEY") and _enabled("ANTHROPIC_ENABLED"):
        backends.append(Backend(
            name="anthropic",
            base_url="https://api.anthropic.com",
            api_key=_get("ANTHROPIC_API_KEY"),
            model_map={
                "opus": "claude-opus-4-7",
                "sonnet": "claude-sonnet-4-6",
                "haiku": "claude-haiku-4-5",
            },
            max_concurrent=50,
            cost_tier=2,
        ))

    # OAuth — Claude Code Max subscription via subprocess-only (direct API returns 401)
    # Tier 1: share tier-1 load with MiniMax/Fireworks using Sonnet 4.6.
    # Set OAUTH_DISABLED=1 to exclude (e.g., for Anthropic-only scaffold runs).
    # Subscription has a daily limit — if we start hitting 429s from the provider
    # itself, `consecutive_429s > 100` will auto-blacklist this backend.
    oauth_token = os.environ.get("CLAUDE_ACCESS_TOKEN", "")
    if _get("OAUTH_DISABLED") == "1":
        oauth_token = ""
    elif not oauth_token:
        for candidate in (".credentials.json", ".credentials_backup.json"):
            creds = Path.home() / ".claude" / candidate
            if creds.exists():
                try:
                    oauth_token = json.loads(creds.read_text()).get(
                        "claudeAiOauth", {}
                    ).get("accessToken", "")
                    if oauth_token:
                        break
                except (json.JSONDecodeError, KeyError):
                    pass
    if oauth_token:
        # Default to Opus for OAuth — Claude Code Max includes Opus access.
        # OAUTH_MODEL env var overrides (e.g., "claude-sonnet-4-6" for cheaper).
        oauth_model = os.environ.get("OAUTH_MODEL", "claude-opus-4-7")
        backends.append(Backend(
            name="oauth",
            base_url="",
            api_key=oauth_token,
            auth_type="bearer",
            model_map={
                "opus": oauth_model,
                "sonnet": oauth_model,
                "haiku": "claude-haiku-4-5",
            },
            # Reverted 50→15: round-3 hit 150× 429 → blacklisted at max=50.
            # 15 keeps us inside subscription-safe range.
            max_concurrent=15,
            cost_tier=1,
            supports_direct=False,
        ))

    return backends
