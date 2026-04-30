#!/usr/bin/env bash
set -euo pipefail

cd /workspace/lemonade

# Idempotency guard
if grep -qF "`Router` (`src/cpp/server/router.cpp`) manages a vector of `WrappedServer` insta" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -4,7 +4,7 @@ This file provides guidance to Claude Code and Claude-based code reviews when wo
 
 ## Project Overview
 
-Lemonade is a local LLM server (v9.4.x) providing GPU and NPU acceleration for running large language models on consumer hardware. It exposes OpenAI-compatible and Ollama-compatible REST APIs and supports multiple backends: llama.cpp, FastFlowLM, RyzenAI, whisper.cpp, stable-diffusion.cpp, and Kokoro TTS.
+Lemonade is a local LLM server (v10.0.0) providing GPU and NPU acceleration for running large language models on consumer hardware. It exposes OpenAI-compatible, Ollama-compatible, and Anthropic-compatible REST APIs, plus a WebSocket Realtime API. It supports multiple backends: llama.cpp, FastFlowLM, RyzenAI, whisper.cpp, stable-diffusion.cpp, and Kokoro TTS.
 
 ## Architecture
 
@@ -17,22 +17,22 @@ Lemonade is a local LLM server (v9.4.x) providing GPU and NPU acceleration for r
 
 ### Backend Abstraction
 
-`WrappedServer` (`src/cpp/include/lemon/wrapped_server.h`) is the abstract base class. Each backend inherits it and implements `install()`, `download_model()`, `load()`, `unload()`, and inference methods. Backends run as **subprocesses** — Lemonade forwards HTTP requests to them.
+`WrappedServer` (`src/cpp/include/lemon/wrapped_server.h`) is the abstract base class. Each backend inherits it and implements `load()`, `unload()`, `chat_completion()`, `completion()`, `responses()`, and optionally `install()` / `download_model()`. Backends run as **subprocesses** — Lemonade forwards HTTP requests to them.
 
-| Backend | Class | Purpose |
-|---------|-------|---------|
-| llama.cpp | `LlamaCppServer` | LLM inference — CPU/GPU (Vulkan, ROCm, Metal) |
-| FastFlowLM | `FastFlowLMServer` | NPU inference (multi-modal: LLM, ASR, embeddings, reranking) |
-| RyzenAI | `RyzenAIServer` | Hybrid NPU inference |
-| whisper.cpp | `WhisperServer` | Audio transcription |
-| stable-diffusion.cpp | `SdServer` | Image generation, editing, variations |
-| Kokoro | `KokoroServer` | Text-to-speech |
+| Backend | Class | Capabilities | Device | Purpose |
+|---------|-------|-------------|--------|---------|
+| llama.cpp | `LlamaCppServer` | Completion, Embeddings, Reranking | GPU | LLM inference — CPU/GPU (Vulkan, ROCm, Metal) |
+| FastFlowLM | `FastFlowLMServer` | Completion, Embeddings, Reranking, Audio | NPU | NPU inference (multi-modal: LLM, ASR, embeddings, reranking) |
+| RyzenAI | `RyzenAIServer` | Completion | NPU | Hybrid NPU inference |
+| whisper.cpp | `WhisperServer` | Audio | CPU | Audio transcription |
+| stable-diffusion.cpp | `SdServer` | Image | CPU | Image generation, editing, variations |
+| Kokoro | `KokoroServer` | TTS | CPU | Text-to-speech |
 
-Capability interfaces: `ICompletionServer`, `IEmbeddingsServer`, `IRerankingServer`, `IAudioServer`, `IImageServer`, `ITextToSpeechServer` (defined in `server_capabilities.h`).
+Capability interfaces: `ICompletionServer`, `IEmbeddingsServer`, `IRerankingServer`, `IAudioServer`, `IImageServer`, `ITextToSpeechServer` (defined in `server_capabilities.h`). Use `supports_capability<T>(server)` template for runtime checks.
 
 ### Router & Multi-Model Support
 
-`Router` (`src/cpp/server/router.cpp`) manages a vector of `WrappedServer` instances. Routes requests based on model recipe, maintains LRU caches per model type (LLM, embedding, reranking, audio), and enforces NPU exclusivity. Configurable via `--max-loaded-models`.
+`Router` (`src/cpp/server/router.cpp`) manages a vector of `WrappedServer` instances. Routes requests based on model recipe, maintains LRU caches per model type (LLM, embedding, reranking, audio, image, TTS — see `model_types.h`), and enforces NPU exclusivity. Configurable via `--max-loaded-models`. On non-file-not-found errors, the router uses a "nuclear option" — evicts all models and retries the load.
 
 ### Model Manager & Recipe System
 
@@ -50,6 +50,12 @@ All core endpoints are registered under **4 path prefixes**:
 
 **Ollama-compatible endpoints** (under `/api/` without version prefix): `chat`, `generate`, `tags`, `show`, `delete`, `pull`, `embed`, `embeddings`, `ps`, `version`
 
+**Anthropic-compatible endpoint:** `POST /api/messages` — supports message completion, tool use, and SSE streaming.
+
+**WebSocket Realtime API** (Windows/Linux only): OpenAI-compatible Realtime protocol for real-time audio transcription. Binds to an OS-assigned port (9000+), exposed via the `websocket_port` field in the `/health` endpoint response.
+
+**Internal endpoints:** `POST /internal/shutdown`
+
 Optional API key auth via `LEMONADE_API_KEY` env var. CORS enabled on all routes.
 
 ### Desktop & Web App
@@ -66,31 +72,43 @@ Optional API key auth via `LEMONADE_API_KEY` env var. CORS enabled on all routes
 ## Build Commands
 
 ```bash
-# C++ server
-cd src/cpp && mkdir build && cd build
+# C++ server (CMakeLists.txt is at repository root)
+mkdir build && cd build
 cmake ..
 cmake --build . --config Release -j
 
 # Electron app
 cd src/app && npm install
 npm run build:win    # or build:mac / build:linux
 
-# Windows MSI installer
-cd src/cpp/build && cmake --build . --config Release --target wix_installer_minimal
+# Web app (auto-enabled on non-Windows, or pass -DBUILD_WEB_APP=ON)
+cmake --build build --config Release --target web-app
+
+# Windows MSI installer (WiX 5.0+ required)
+cmake --build build --config Release --target wix_installer_minimal  # server + web-app
+cmake --build build --config Release --target wix_installer_full     # server + electron + web-app
 
-# Linux .deb
-cd src/cpp/build && cpack
+# macOS signed installer
+cmake --build build --config Release --target package-macos
+
+# Linux .deb / .rpm
+cd build && cpack
+
+# Linux AppImage
+cmake --build build --config Release --target appimage
 ```
 
 CMake presets: `default` (Ninja), `windows` (VS 2022), `debug` (Ninja Debug).
 
+CMake options: `BUILD_WEB_APP` (ON by default on non-Windows), `BUILD_ELECTRON_APP` (Linux only, include Electron in deb), `LEMONADE_SYSTEMD_UNIT_NAME` (default: `lemonade-server.service`).
+
 ## Testing
 
 Integration tests in Python against a live server:
 
 ```bash
 pip install -r test/requirements.txt
-./src/cpp/build/Release/lemonade-router.exe --port 8000 --log-level debug
+./build/Release/lemonade-router.exe --port 8000 --log-level debug
 
 # Separate terminal
 python test/server_endpoints.py
@@ -100,10 +118,14 @@ python test/server_whisper.py
 python test/server_tts.py
 python test/server_system_info.py
 python test/server_cli.py
+python test/server_cli2.py
+python test/server_streaming_errors.py
 python test/test_ollama.py
+python test/test_flm_status.py
+python test/test_llamacpp_system_backend.py
 ```
 
-Test utilities in `test/utils/` with `server_base.py` as the base class.
+Test utilities in `test/utils/` with `server_base.py` as the base class. Test dependencies include `requests`, `httpx`, `openai`, `huggingface_hub`, `psutil`, `numpy`, `websockets`, and `ollama`.
 
 ## Code Style
 
@@ -136,6 +158,9 @@ Test utilities in `test/utils/` with `server_base.py` as the base class.
 | `src/cpp/resources/backend_versions.json` | Backend version pins |
 | `src/cpp/server/anthropic_api.cpp` | Anthropic API compatibility |
 | `src/cpp/server/ollama_api.cpp` | Ollama API compatibility |
+| `src/cpp/include/lemon/websocket_server.h` | WebSocket Realtime API server |
+| `src/cpp/include/lemon/model_types.h` | Model type and device type enums |
+| `src/cpp/include/lemon/recipe_options.h` | Per-recipe JSON configuration |
 | `src/cpp/tray/tray_app.cpp` | Tray application UI and logic |
 | `src/app/src/renderer/ModelManager.tsx` | Model management UI |
 | `src/app/src/renderer/ChatWindow.tsx` | Chat interface |
@@ -145,9 +170,9 @@ Test utilities in `test/utils/` with `server_base.py` as the base class.
 These MUST be maintained in all changes:
 
 1. **Quad-prefix registration** — Every new endpoint MUST be registered under `/api/v0/`, `/api/v1/`, `/v0/`, AND `/v1/`.
-2. **NPU exclusivity** — Only one NPU backend can be loaded at a time. Router must unload existing NPU models before loading a new one.
-3. **WrappedServer contract** — New backends MUST implement all virtual methods: `install()`, `download_model()`, `load()`, `unload()`.
-4. **Subprocess model** — Backends run as subprocesses (llama-server, whisper-server, sd-server, koko). They must NOT run in-process.
+2. **NPU exclusivity** — Exclusive-NPU recipes (`ryzenai-llm`, `whispercpp` on NPU) evict ALL other NPU models before loading. FastFlowLM (`flm`) can coexist with other FLM types (max 1 per FLM type) but not with exclusive-NPU recipes.
+3. **WrappedServer contract** — New backends MUST implement all core virtual methods: `load()`, `unload()`, `chat_completion()`, `completion()`, `responses()`.
+4. **Subprocess model** — Backends run as subprocesses (llama-server, whisper-server, sd-server, koko, flm, ryzenai-server). They must NOT run in-process.
 5. **Recipe integrity** — Changes to `server_models.json` must have valid recipes referencing backends in `backend_versions.json`.
 6. **Cross-platform** — Code must compile on Windows (MSVC), Linux (GCC/Clang), macOS (AppleClang). Platform-specific code must use `#ifdef` guards.
 7. **No hardcoded paths** — Use path utilities. Windows/Linux/macOS paths differ.
PATCH

echo "Gold patch applied."
