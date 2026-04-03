# Preserve existing provider/auth flow in setup installer

## Problem

The interactive installer (`scripts/setup.sh`) prompts users to confirm keeping their existing provider/model config and API keys every time it runs. When Codex is already configured with a working `config.toml` and `auth.json`, the installer should silently preserve those settings instead of asking redundant questions.

Additionally, the installer only recognizes `OPENAI_API_KEY`. Users who use other providers (DeepSeek, Anthropic, Groq, etc.) have to manually manage credentials. The installer should be able to auto-detect common `*_API_KEY` environment variables and support custom API key env var names.

The installer also currently requires `python3` for its dependency check and config merge logic, but the project is a Node.js/Codex CLI tool — `node` should be the required dependency instead.

## Expected Behavior

1. When an existing `config.toml` is found, the installer should silently preserve the provider/model configuration without prompting.
2. When an existing `auth.json` is found, the installer should silently preserve the authentication without prompting.
3. When `auth.json` is absent but a known API key env var is already exported (e.g., `DEEPSEEK_API_KEY`, `ANTHROPIC_API_KEY`), the installer should detect and persist it automatically for Codex compatibility.
4. For fresh installs, the installer should let users specify a custom API key env var name (not just `OPENAI_API_KEY`).
5. When writing `auth.json` with a non-`OPENAI_API_KEY` env var, the file should include both the custom key and an `OPENAI_API_KEY` entry for Codex compatibility.
6. The dependency check should require `node` instead of `python3`.
7. After fixing the code, update the relevant documentation (both English and Chinese READMEs) to accurately describe the new installer behavior — especially the silent preservation and env var auto-detection features.

## Files to Look At

- `scripts/setup.sh` — the interactive installer script
- `README.md` — English documentation, "Quick Start" section describes installer behavior
- `README.zh-CN.md` — Chinese documentation, mirrors the English Quick Start section
