"""DeepSeek backend pool for LLM API calls.

Speaks DeepSeek's Anthropic-compatible endpoint. On 429 rate limits, applies
exponential cooldown and auto-suspend / auto-resurrect.

Two execution modes share the same pool:
  - Direct API (httpx)  — ~5 MB/request, for single-shot tasks
  - Subprocess (claude -p) — ~300 MB/process, for multi-turn agent tasks
"""

from __future__ import annotations

import asyncio
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
    auth_type: Literal["x-api-key", "bearer", "openrouter"] = "x-api-key"
    api_format: Literal["anthropic", "openai"] = "anthropic"
    model_map: dict[str, str] = field(default_factory=dict)
    max_concurrent: int = 4
    cost_tier: int = 0                     # 0 free → 1 sub → 2 paid → 3 cheap-paid
    supports_direct: bool = True           # False for OAuth
    supports_subprocess: bool = True       # False for OpenAI-format without proxy
    extra_env: dict[str, str] = field(default_factory=dict)  # backend-specific env passthrough (e.g. CLAUDE_CODE_EFFORT_LEVEL)

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

        Sets ALL model env vars (ANTHROPIC_MODEL, ANTHROPIC_SMALL_FAST_MODEL,
        and the DEFAULT_* variants) so Claude Code subagents route through
        DeepSeek too.
        """
        env: dict[str, str] = {}
        if self.base_url:
            env["ANTHROPIC_BASE_URL"] = self.base_url
        if self.auth_type == "bearer":
            env["CLAUDE_ACCESS_TOKEN"] = self.api_key
        elif self.auth_type == "openrouter":
            # OpenRouter Anthropic-Skin: ANTHROPIC_API_KEY MUST be empty string
            # to prevent Claude Code from preferring real Anthropic creds.
            env["ANTHROPIC_AUTH_TOKEN"] = self.api_key
            env["ANTHROPIC_API_KEY"] = ""
        else:
            env["ANTHROPIC_API_KEY"] = self.api_key
            env["ANTHROPIC_AUTH_TOKEN"] = self.api_key
        for logical, actual in self.model_map.items():
            env[f"ANTHROPIC_DEFAULT_{logical.upper()}_MODEL"] = actual
        primary = self.model_map.get("opus") or self.model_map.get("sonnet") or ""
        if primary:
            env["ANTHROPIC_MODEL"] = primary
            # Default SMALL_FAST_MODEL to the haiku slot if mapped, else fall
            # back to primary. DeepSeek's flash variant goes here for subagents.
            env["ANTHROPIC_SMALL_FAST_MODEL"] = self.model_map.get("haiku") or primary
        # extra_env wins (e.g. CLAUDE_CODE_EFFORT_LEVEL=max for DeepSeek)
        env.update(self.extra_env)
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
        """
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

    # DeepSeek V4 Pro via DeepSeek's native Anthropic-compatible endpoint.
    # Handles thinking-block signature round-trip internally (OpenRouter does not).
    # Set DEEPSEEK_ENABLED=1. Models overridable via DEEPSEEK_MODEL / DEEPSEEK_HAIKU.
    #
    # Model name conventions on DeepSeek's Anthropic shim:
    #   - "deepseek-v4-pro[1m]" routes to the 1M-context variant (use this)
    #   - "deepseek-v4-pro"     standard context
    #   - "deepseek-v4-flash"   cheap fast model for subagents/haiku slot
    # CLAUDE_CODE_EFFORT_LEVEL=max maximizes thinking budget per turn.
    ds_key = _get("DEEPSEEK_API_KEY") or _get("deepseek_api_key")
    if ds_key and _enabled("DEEPSEEK_ENABLED"):
        ds_model = _get("DEEPSEEK_MODEL") or "deepseek-v4-pro[1m]"
        ds_haiku = _get("DEEPSEEK_HAIKU") or "deepseek-v4-flash"
        ds_effort = _get("DEEPSEEK_EFFORT_LEVEL") or "max"
        backends.append(Backend(
            name="deepseek",
            base_url="https://api.deepseek.com/anthropic",
            api_key=ds_key,
            auth_type="x-api-key",
            model_map={"opus": ds_model, "sonnet": ds_model, "haiku": ds_haiku},
            max_concurrent=int(_get("DEEPSEEK_MAX_CONCURRENT") or 10),
            cost_tier=1,
            extra_env={
                "CLAUDE_CODE_EFFORT_LEVEL": ds_effort,
                "CLAUDE_CODE_SUBAGENT_MODEL": ds_haiku,
            },
        ))

    # OpenRouter + DeepSeek V4 Pro via Anthropic-Skin (ANTHROPIC_API_KEY must be "")
    # Set OPENROUTER_DEEPSEEK_ENABLED=1. Model overridable via OPENROUTER_DEEPSEEK_MODEL.
    if _get("OPENROUTER_API_KEY") and _enabled("OPENROUTER_DEEPSEEK_ENABLED"):
        ds_model = _get("OPENROUTER_DEEPSEEK_MODEL") or "deepseek/deepseek-v4-pro"
        ds_haiku = _get("OPENROUTER_DEEPSEEK_HAIKU") or "deepseek/deepseek-v4-flash"
        backends.append(Backend(
            name="openrouter-deepseek",
            base_url="https://openrouter.ai/api",
            api_key=_get("OPENROUTER_API_KEY"),
            auth_type="openrouter",
            model_map={"opus": ds_model, "sonnet": ds_model, "haiku": ds_haiku},
            max_concurrent=int(_get("OPENROUTER_DEEPSEEK_MAX_CONCURRENT") or 10),
            cost_tier=1,
        ))

    return backends
