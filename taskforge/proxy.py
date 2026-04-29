"""LiteLLM proxy for routing claude -p through DeepSeek via OpenRouter.

Starts a local litellm proxy that maps Anthropic model names to DeepSeek on
OpenRouter. Claude Code sees its normal API format; litellm translates under
the hood.

Usage:
    # As a context manager in Python
    with litellm_proxy(model="openrouter/deepseek/deepseek-v4-pro", port=4111) as url:
        os.environ["ANTHROPIC_BASE_URL"] = url
        # run claude -p ...

    # As CLI
    python -m taskforge.proxy --model openrouter/deepseek/deepseek-v4-pro
    python -m taskforge.proxy --model openrouter/deepseek/deepseek-v4-pro -- python -m taskforge.pipeline audit-tests --workers 4
"""

from __future__ import annotations

import argparse
import atexit
import os
import signal
import subprocess
import sys
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path

MASTER_KEY = "sk-litellm-local"


def _write_config(model: str, port: int) -> Path:
    """Write a temporary litellm config yaml."""
    # Use openai/ prefix + api_base so litellm routes via OpenAI-compatible
    # endpoint at OpenRouter, without doubling the provider prefix.
    clean_model = model.removeprefix("openrouter/")

    config = f"""model_list:
  - model_name: "deepseek-v4-pro"
    litellm_params:
      model: "openai/{clean_model}"
      api_key: "os.environ/OPENROUTER_API_KEY"
      api_base: "https://openrouter.ai/api/v1"
  - model_name: "deepseek-v4-flash"
    litellm_params:
      model: "openai/{clean_model}"
      api_key: "os.environ/OPENROUTER_API_KEY"
      api_base: "https://openrouter.ai/api/v1"

litellm_settings:
  drop_params: true
  use_chat_completions_url_for_anthropic_messages: true
"""
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, prefix="litellm_")
    f.write(config)
    f.close()
    return Path(f.name)


def _wait_for_proxy(port: int, timeout: int = 30) -> bool:
    """Wait for the proxy to be ready."""
    import urllib.request
    for _ in range(timeout):
        try:
            urllib.request.urlopen(f"http://localhost:{port}/health", timeout=2)
            return True
        except Exception:
            time.sleep(1)
    return False


@contextmanager
def litellm_proxy(
    model: str = "openrouter/deepseek/deepseek-v4-pro",
    port: int = 4111,
    openrouter_key: str | None = None,
):
    """Context manager that starts a litellm proxy and yields the base URL.

    Usage:
        with litellm_proxy(model="openrouter/deepseek/deepseek-v4-pro") as url:
            os.environ["ANTHROPIC_BASE_URL"] = url
            os.environ["ANTHROPIC_API_KEY"] = "sk-litellm-local"
            subprocess.run(["claude", "-p", ...])
    """
    # Resolve OpenRouter key
    key = openrouter_key or os.environ.get("OPENROUTER_API_KEY", "")
    if not key:
        # Try loading from .env
        env_file = Path.cwd() / ".env"
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                if line.startswith("OPENROUTER_API_KEY"):
                    key = line.split("=", 1)[1].strip().strip('"').strip("'")
                    break
    if not key:
        raise RuntimeError("OPENROUTER_API_KEY not found in env or .env")

    config_path = _write_config(model, port)

    # Find litellm in the same venv as this Python
    venv = Path(sys.executable).parent
    litellm_bin = venv / "litellm"
    if not litellm_bin.exists():
        litellm_bin = "litellm"  # fallback to PATH

    log_file = tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False, prefix="litellm_")
    log_path = Path(log_file.name)
    log_file.close()

    proc = subprocess.Popen(
        [str(litellm_bin), "--config", str(config_path), "--port", str(port)],
        env={**os.environ, "OPENROUTER_API_KEY": key},
        stdout=open(log_path, "w"),
        stderr=subprocess.STDOUT,
    )

    try:
        if not _wait_for_proxy(port):
            proc.kill()
            # Show log on failure for debugging
            if log_path.exists():
                print(log_path.read_text()[-1000:], file=sys.stderr)
            raise RuntimeError(f"litellm proxy failed to start on port {port}")

        yield f"http://localhost:{port}"
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        config_path.unlink(missing_ok=True)
        log_path.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description="Run commands through litellm proxy")
    parser.add_argument("--model", default="openrouter/deepseek/deepseek-v4-pro")
    parser.add_argument("--port", type=int, default=4111)
    parser.add_argument("command", nargs="*", help="Command to run (after --)")
    args = parser.parse_args()

    with litellm_proxy(model=args.model, port=args.port) as url:
        if args.command:
            env = {**os.environ, "ANTHROPIC_BASE_URL": url, "ANTHROPIC_API_KEY": MASTER_KEY}
            result = subprocess.run(args.command, env=env)
            sys.exit(result.returncode)
        else:
            print(f"Proxy running at {url}")
            print(f"Model: {args.model}")
            print(f"Set these env vars to use:")
            print(f"  export ANTHROPIC_BASE_URL={url}")
            print(f"  export ANTHROPIC_API_KEY={MASTER_KEY}")
            print(f"Press Ctrl+C to stop.")
            try:
                signal.pause()
            except KeyboardInterrupt:
                pass


if __name__ == "__main__":
    main()
