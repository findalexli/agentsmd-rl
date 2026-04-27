#!/usr/bin/env bash
set -euo pipefail

cd /workspace/lemonade

# Idempotency guard
if grep -qF "Integration tests in Python against a live server. Tests auto-discover the serve" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -71,58 +71,67 @@ Optional API key auth via `LEMONADE_API_KEY` env var. CORS enabled on all routes
 
 ## Build Commands
 
+CMakeLists.txt is at the repository root. Build uses CMake presets — run the setup script first, then build with `--preset`.
+
 ```bash
-# C++ server (CMakeLists.txt is at repository root)
-mkdir build && cd build
-cmake ..
-cmake --build . --config Release -j
+# 1. Setup (configures build directory and installs deps)
+./setup.sh          # Linux / macOS
+./setup.ps1         # Windows (PowerShell)
+
+# 2. Build C++ server
+cmake --build --preset default          # Linux / macOS (Ninja)
+cmake --build --preset windows          # Windows (Visual Studio 2022)
+cmake --build --preset vs18             # Windows (Visual Studio 2026)
 
-# Electron app
-cd src/app && npm install
-npm run build:win    # or build:mac / build:linux
+# 3. Electron app (optional, requires Node.js 20+)
+cmake --build --preset default --target electron-app    # Linux / macOS
+cmake --build --preset windows --target electron-app    # Windows (VS 2022)
+cmake --build --preset vs18 --target electron-app       # Windows (VS 2026)
 
-# Web app (auto-enabled on non-Windows, or pass -DBUILD_WEB_APP=ON)
-cmake --build build --config Release --target web-app
+# 4. Web app (auto-built on non-Windows; manual on Windows)
+cmake --build --preset default --target web-app         # Linux / macOS
+cmake --build --preset windows --target web-app         # Windows
 
-# Windows MSI installer (WiX 5.0+ required)
-cmake --build build --config Release --target wix_installer_minimal  # server + web-app
-cmake --build build --config Release --target wix_installer_full     # server + electron + web-app
+# 5. Windows MSI installer (WiX 5.0+ required)
+cmake --build --preset windows --target wix_installer_minimal  # server + web-app
+cmake --build --preset windows --target wix_installer_full     # server + electron + web-app
 
-# macOS signed installer
-cmake --build build --config Release --target package-macos
+# 6. macOS signed installer
+cmake --build --preset default --target package-macos
 
-# Linux .deb / .rpm
-cd build && cpack
+# 7. Linux .deb / .rpm
+cd build && cpack            # .deb
+cd build && cpack -G RPM     # .rpm
 
-# Linux AppImage
-cmake --build build --config Release --target appimage
+# 8. Linux AppImage
+cmake --build --preset default --target appimage
 ```
 
-CMake presets: `default` (Ninja), `windows` (VS 2022), `debug` (Ninja Debug).
+CMake presets: `default` (Ninja, Release), `windows` (VS 2022), `vs18` (VS 2026), `debug` (Ninja, Debug).
 
 CMake options: `BUILD_WEB_APP` (ON by default on non-Windows), `BUILD_ELECTRON_APP` (Linux only, include Electron in deb), `LEMONADE_SYSTEMD_UNIT_NAME` (default: `lemonade-server.service`).
 
 ## Testing
 
-Integration tests in Python against a live server:
+Integration tests in Python against a live server. Tests auto-discover the server binary from the build directory; use `--server-binary` to override.
 
 ```bash
 pip install -r test/requirements.txt
-./build/Release/lemonade-router.exe --port 8000 --log-level debug
 
-# Separate terminal
+# CLI tests (no inference backend needed)
+python test/server_cli.py
+
+# Endpoint tests (no inference backend needed)
 python test/server_endpoints.py
-python test/server_llm.py
-python test/server_sd.py
+
+# LLM tests (specify wrapped server and backend)
+python test/server_llm.py --wrapped-server llamacpp --backend vulkan
+
+# Audio transcription tests
 python test/server_whisper.py
-python test/server_tts.py
-python test/server_system_info.py
-python test/server_cli.py
-python test/server_cli2.py
-python test/server_streaming_errors.py
-python test/test_ollama.py
-python test/test_flm_status.py
-python test/test_llamacpp_system_backend.py
+
+# Image generation tests (slow)
+python test/server_sd.py
 ```
 
 Test utilities in `test/utils/` with `server_base.py` as the base class. Test dependencies include `requests`, `httpx`, `openai`, `huggingface_hub`, `psutil`, `numpy`, `websockets`, and `ollama`.
PATCH

echo "Gold patch applied."
