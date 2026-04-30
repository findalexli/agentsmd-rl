#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bluefin

# Idempotency guard
if grep -qF "**Bluefin** is a cloud-native desktop operating system that reimagines the Linux" ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -4,37 +4,42 @@ This document provides essential information for coding agents working with the
 
 ## Repository Overview
 
-**Bluefin** is a cloud-native desktop operating system that reimagines the Linux desktop experience. It's an immutable OS built on Fedora Linux using container technologies with atomic updates.
+**Bluefin** is a cloud-native desktop operating system that reimagines the Linux desktop experience. It's an OS built on Fedora Linux using container technologies with atomic updates.
 
 - **Type**: Container-based Linux distribution build system (75MB total, 74MB system files)
 - **Base**: Fedora Linux with GNOME Desktop + Universal Blue infrastructure
 - **Languages**: Bash scripts, JSON configuration, Python utilities
 - **Build System**: Just (command runner), Podman/Docker containers, GitHub Actions
-- **Target**: Immutable desktop OS with two variants (base + developer experience)
+- **Target**: desktop OS with two variants (base + developer experience)
 
 ## Repository Structure
 
 ### Root Directory Files
 - `Containerfile` - Main container build definition (multi-stage: base → dx)
 - `Justfile` - Build automation recipes (33KB - like Makefile but more readable)
-- `packages.json` - Package inclusion/exclusion lists per Fedora version and variant
 - `.pre-commit-config.yaml` - Pre-commit hooks for basic validation
 - `image-versions.yml` - Image version configurations
 - `cosign.pub` - Container signing public key
 
 ### Key Directories
 - `system_files/` (74MB) - User-space files, configurations, fonts, themes
 - `build_files/` - Build scripts organized as base/, dx/, shared/
+  - `base/` - Base image build scripts (00-image-info.sh through 19-initramfs.sh)
+  - `dx/` - Developer experience build scripts
+  - `shared/` - Common build utilities and helper scripts
 - `.github/workflows/` - Comprehensive CI/CD pipelines
 - `just/` - Additional Just recipes for apps and system management
-- `flatpaks/` - Flatpak application lists
+- `brew/` - Homebrew Brewfile definitions for various tool collections
+- `flatpaks/` - Flatpak application lists (system-flatpaks.list, system-flatpaks-dx.list)
 - `iso_files/` - ISO installation configurations
 
 ### Architecture
 - **Two Build Targets**: `base` (regular users) and `dx` (developer experience)
 - **Image Flavors**: main, nvidia-open
 - **Fedora Versions**: 42, 43 supported
+- **Stream Tags**: `latest` (F42/43), `beta` (F42/43), `stable` (F42), `gts` (F42 Grand Touring Support)
 - **Build Process**: Sequential shell scripts in build_files/ directory
+- **Base Images**: Uses `ghcr.io/ublue-os/silverblue-main` as foundation from Universal Blue
 
 ## Build Instructions
 
@@ -64,13 +69,10 @@ pip install pre-commit
 # Note: .devcontainer.json will fail JSON check due to comments - this is expected
 pre-commit run --all-files
 
-# 2. Check specific JSON files manually:
-python3 -c "import json; json.load(open('packages.json'))"
-
-# 3. Check Just syntax (requires Just installation)
+# 2. Check Just syntax (requires Just installation)
 just check  # Only if Just command runner is available
 
-# 4. Fix formatting issues automatically
+# 3. Fix formatting issues automatically
 just fix    # Only if Just command runner is available
 ```
 
@@ -128,9 +130,6 @@ grep -n "^[a-zA-Z].*:" Justfile | head -20
 
 # Fix end-of-file and trailing whitespace automatically
 pre-commit run --all-files
-
-# Validate specific JSON files (excluding .devcontainer.json):
-python3 -c "import json; json.load(open('packages.json'))"  # Should pass
 ```
 
 **Just syntax errors (if Just is available):**
@@ -163,43 +162,61 @@ The repository uses mandatory pre-commit validation:
 ### GitHub Actions Workflows
 - `build-image-latest-main.yml` - Builds latest images on main branch changes
 - `build-image-stable.yml` - Builds stable release images
-- `build-image-gts.yml` - Builds GTS (Go-To-Stable) images
+- `build-image-gts.yml` - Builds GTS (Grand Touring Support) images
+- `build-image-beta.yml` - Builds beta images for testing F42/F43
 - `reusable-build.yml` - Core build logic for all image variants
+- `build-iso-lts.yml` - Builds LTS ISO images
+- `generate-release.yml` - Generates release artifacts and changelogs
+- `validate-brewfiles.yml` - Validates Homebrew Brewfile syntax
+- `validate-flatpaks.yml` - Validates Flatpak list files
+- `clean.yml` - Cleanup old images and artifacts
+- `moderator.yml` - Repository moderation tasks
+
+**Workflow Architecture:**
+- Stream-specific workflows (gts, stable, latest, beta) call `reusable-build.yml`
+- `reusable-build.yml` builds both base and dx variants for all flavors (main, nvidia-open)
+- Fedora version is dynamically detected based on stream tag
+- Images are signed with cosign and pushed to GHCR
 
 ### Manual Validation Steps
 1. `pre-commit run --all-files` - Runs validation hooks (2-3 minutes, .devcontainer.json failure is expected)
-2. `python3 -c "import json; json.load(open('packages.json'))"` - Validate critical JSON files
-3. `just check` - Validates Just syntax (if Just is available, 30 seconds)
-4. `just fix` - Auto-fixes formatting issues (if Just is available, 30 seconds)
-5. Test builds only if making container-related changes (30+ minutes)
+2. `just check` - Validates Just syntax (if Just is available, 30 seconds)
+3. `just fix` - Auto-fixes formatting issues (if Just is available, 30 seconds)
+4. Test builds only if making container-related changes (30+ minutes)
 
 ## Package Management
 
-### packages.json Structure
-The `packages.json` file defines package inclusion/exclusion per Fedora version:
-```json
-{
-  "all": {
-    "include": {
-      "all": ["package1", "package2"],  // Base image packages
-      "dx": ["dev-package1", "dev-package2"]  // Developer additions
-    },
-    "exclude": {
-      "all": ["unwanted-package"],
-      "dx": []
-    }
-  },
-  "41": {  // Fedora 41 specific overrides
-    "include": {"all": ["fedora41-only-package"]},
-    "exclude": {"all": []}
-  }
-}
+### Package Configuration
+Packages are defined directly in build scripts rather than in a central configuration file:
+- `build_files/base/04-packages.sh` - Core package installations
+  - `FEDORA_PACKAGES` array - Packages from official Fedora repos (installed in bulk)
+  - `COPR_PACKAGES` array - Packages from COPR repos (installed individually with isolated enablement)
+  - Fedora version-specific package sections using case statements (e.g., `42)`, `43)`)
+- `build_files/dx/00-dx.sh` - Developer experience package additions
+
+### COPR Package Installation
+COPR packages use the `copr_install_isolated()` helper function from `build_files/shared/copr-helpers.sh`:
+```bash
+# Install packages from COPR with isolated repo enablement
+copr_install_isolated "ublue-os/staging" package1 package2
 ```
+This function:
+1. Enables the COPR repo
+2. Immediately disables it
+3. Installs packages with `--enablerepo` flag to prevent repo conflicts
 
 ### Making Package Changes
-1. Edit `packages.json` following the existing structure
-2. Validate JSON syntax: `pre-commit run check-json --all-files`
-3. Test with container build if critical changes
+1. Edit the appropriate shell script in `build_files/base/` or `build_files/dx/`
+2. Add packages to the appropriate array (`FEDORA_PACKAGES` or `COPR_PACKAGES`)
+3. For version-specific packages, add them in the Fedora version case statement
+4. Validate shell script syntax: `bash -n build_files/base/04-packages.sh`
+5. Run pre-commit hooks: `pre-commit run --all-files`
+6. Test with container build if making critical changes
+
+### Package Security Model
+**CRITICAL**: Packages are split into separate arrays to prevent COPR repos from injecting malicious versions of Fedora packages:
+- Fedora packages are installed first in bulk (safe)
+- COPR packages are installed individually with isolated repo enablement
 
 ## Configuration Files
 
@@ -216,6 +233,66 @@ The `packages.json` file defines package inclusion/exclusion per Fedora version:
 - `.github/renovate.json5` - Automated dependency updates
 - `Containerfile` - Container build instructions
 
+## Build System Deep Dive
+
+### Justfile Structure
+The `Justfile` is the central build orchestration tool with these key recipes:
+
+**Validation Recipes:**
+- `just check` - Validates Just syntax across all .just files
+- `just fix` - Auto-formats Just files
+- `just validate <image> <tag> <flavor>` - Validates image/tag/flavor combinations
+
+**Build Recipes:**
+- `just build <image> <tag> <flavor>` - Main build command (calls build.sh)
+- `just build-ghcr <image> <tag> <flavor>` - Build for GHCR (GitHub Container Registry)
+- `just rechunk <image> <tag> <flavor>` - Rechunk image for optimization
+
+**Image/Tag Definitions:**
+```bash
+images: bluefin, bluefin-dx
+flavors: main, nvidia-open
+tags: gts, stable, latest, beta
+```
+
+**Version Detection:**
+- `just fedora_version <image> <tag> <flavor>` - Dynamically detects Fedora version from upstream base images
+- For `gts` and `stable`: Checks `ghcr.io/ublue-os/base-main:<tag>`
+- For `latest`/`beta`: Checks corresponding upstream tags
+- Returns the Fedora major version (e.g., 42, 43)
+
+### Containerfile Multi-Stage Build
+The `Containerfile` uses a multi-stage build process:
+
+1. **Stage `ctx`** (FROM scratch): Copies all build context (system_files, build_files, etc.)
+2. **Stage `base`** (FROM silverblue-main): Base Bluefin image
+   - Mounts build context from `ctx` stage
+   - Runs `/ctx/build_files/shared/build.sh` which executes all scripts in order
+3. **Stage `dx`** (optional, in full Containerfile): Developer experience layer
+
+**Build Arguments:**
+- `BASE_IMAGE_NAME` - Upstream base (silverblue/kinoite)
+- `FEDORA_MAJOR_VERSION` - Dynamically set by Just (42/43)
+- `IMAGE_NAME` - Target image name (bluefin/bluefin-dx)
+- `KERNEL` - Pinned kernel version (optional)
+- `UBLUE_IMAGE_TAG` - Stream tag (gts/stable/latest/beta)
+
+### Build Script Execution Order
+Scripts in `build_files/base/` execute in numerical order:
+1. `00-image-info.sh` - Sets image metadata and os-release info
+2. `03-install-kernel-akmods.sh` - Installs kernel and akmod packages
+3. `04-packages.sh` - Installs Fedora and COPR packages
+4. `05-override-install.sh` - Overrides base image packages
+5. `08-firmware.sh` - Firmware configurations
+6. `17-cleanup.sh` - Cleanup operations
+7. `18-workarounds.sh` - Temporary fixes/workarounds
+8. `19-initramfs.sh` - Regenerates initramfs
+
+### Additional Recipe Collections
+- `just/bluefin-apps.just` - User-facing app management recipes
+- `just/bluefin-system.just` - System management recipes
+- `brew/*.Brewfile` - Homebrew package collections (ai, cli, fonts, k8s)
+
 ## Development Guidelines
 
 ### Making Changes
@@ -232,7 +309,7 @@ The `packages.json` file defines package inclusion/exclusion per Fedora version:
 - **Shell scripts**: Follow existing patterns in build_files/
 
 ### Common Modification Patterns
-- **Adding packages**: Edit `packages.json`, validate JSON syntax
+- **Adding packages**: Edit `build_files/base/04-packages.sh`, add to appropriate array
 - **System configuration**: Modify files in `system_files/shared/`
 - **Build logic**: Edit scripts in `build_files/base/` or `build_files/dx/`
 - **CI/CD**: Modify workflows in `.github/workflows/`
PATCH

echo "Gold patch applied."
