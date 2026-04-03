#!/usr/bin/env bash
set -euo pipefail

cd /workspace/lotti

# Idempotent: skip if already applied
if grep -q 'widgetbook_macos_build' Makefile 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# --- 1. Create the build script ---
mkdir -p tool/widgetbook

cat > tool/widgetbook/build_macos_bundle.sh <<'BUILDSCRIPT'
#!/usr/bin/env bash
set -euo pipefail

upload_release=false
skip_build=false
release_tag="widgetbook-macos-latest"
release_title="Widgetbook macOS Latest"
release_notes="Latest local Widgetbook macOS bundle."

while (($# > 0)); do
  case "$1" in
    --upload-release)
      upload_release=true
      shift
      ;;
    --skip-build)
      skip_build=true
      shift
      ;;
    --release-tag)
      release_tag="${2:?Missing value for --release-tag}"
      shift 2
      ;;
    --release-title)
      release_title="${2:?Missing value for --release-title}"
      shift 2
      ;;
    --release-notes)
      release_notes="${2:?Missing value for --release-notes}"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "This script must be run on macOS." >&2
  exit 1
fi

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$repo_root"

if command -v fvm >/dev/null 2>&1; then
  flutter_cmd=(fvm flutter)
else
  flutter_cmd=(flutter)
fi

product_name="$(
  sed -n 's/^[[:space:]]*PRODUCT_NAME[[:space:]]*=[[:space:]]*//p' \
    macos/Runner/Configs/AppInfo.xcconfig | head -n 1
)"

if [[ -z "$product_name" ]]; then
  echo "Could not determine PRODUCT_NAME from macOS app config." >&2
  exit 1
fi

export_root="$repo_root/build/widgetbook_macos_export"
source_app="$repo_root/build/macos/Build/Products/Release/$product_name.app"
bundle_name="Lotti_Widgetbook.app"
bundle_path="$export_root/$bundle_name"
zip_path="$export_root/Lotti_Widgetbook.app.zip"

mkdir -p "$export_root"

if [[ "$skip_build" == false ]]; then
  rm -rf "$bundle_path"
  rm -f "$zip_path"

  "${flutter_cmd[@]}" pub get

  "${flutter_cmd[@]}" build macos \
    --target lib/widgetbook.dart \
    --release

  if [[ ! -d "$source_app" ]]; then
    echo "Expected macOS app bundle was not produced at: $source_app" >&2
    exit 1
  fi

  cp -R "$source_app" "$bundle_path"

  ditto -c -k --keepParent --sequesterRsrc "$bundle_path" "$zip_path"
elif [[ ! -f "$zip_path" ]]; then
  echo "Expected existing zip was not found at: $zip_path" >&2
  echo "Run the build first, or omit --skip-build." >&2
  exit 1
fi

if [[ -d "$bundle_path" ]]; then
  bundle_size="$(du -sh "$bundle_path" | awk '{print $1}')"
else
  bundle_size="not present"
fi
zip_size="$(du -sh "$zip_path" | awk '{print $1}')"

echo "Widgetbook macOS bundle ready."
echo "App: $bundle_path ($bundle_size)"
echo "Zip: $zip_path ($zip_size)"

if [[ "$upload_release" == true ]]; then
  if ! command -v gh >/dev/null 2>&1; then
    echo "gh CLI is required for --upload-release." >&2
    exit 1
  fi

  current_ref="$(git rev-parse HEAD)"

  git tag -f "$release_tag" "$current_ref"
  git push origin "refs/tags/$release_tag" --force

  if gh release view "$release_tag" >/dev/null 2>&1; then
    gh release edit "$release_tag" \
      --title "$release_title" \
      --notes "$release_notes" \
      --prerelease
  else
    gh release create "$release_tag" \
      --target "$current_ref" \
      --title "$release_title" \
      --notes "$release_notes" \
      --prerelease
  fi

  gh release upload "$release_tag" "$zip_path" --clobber

  echo "Uploaded $zip_path to GitHub release $release_tag."
fi
BUILDSCRIPT

chmod +x tool/widgetbook/build_macos_bundle.sh

# --- 2. Add Makefile targets ---
# Insert after the 'bundle:' target line (line 112) using sed line addressing
sed -i '112a\
\
.PHONY: widgetbook_macos_build\
widgetbook_macos_build:\
\tbash tool/widgetbook/build_macos_bundle.sh\
\
.PHONY: widgetbook_macos_upload\
widgetbook_macos_upload:\
\tbash tool/widgetbook/build_macos_bundle.sh --skip-build --upload-release\
\
.PHONY: widgetbook_macos_publish\
widgetbook_macos_publish:\
\tbash tool/widgetbook/build_macos_bundle.sh --upload-release' Makefile

# --- 3. Create CI workflow ---
mkdir -p .github/workflows

cat > .github/workflows/widgetbook-macos-release.yml <<'WORKFLOW'
name: Widgetbook macOS Release

on:
  push:
    branches:
      - main

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  release:
    name: Build and Publish Widgetbook macOS Bundle
    permissions:
      contents: write
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v5

      - name: Cache Pub Packages
        uses: actions/cache@v4
        with:
          path: ~/.pub-cache
          key: ${{ runner.os }}-pub-${{ hashFiles('**/pubspec.lock') }}

      - uses: kuhnroyal/flutter-fvm-config-action@v2
        id: fvm-config-action

      - uses: subosito/flutter-action@v2
        with:
          flutter-version: ${{ steps.fvm-config-action.outputs.FLUTTER_VERSION }}
          channel: ${{ steps.fvm-config-action.outputs.FLUTTER_CHANNEL }}
          cache: true

      - name: Build Widgetbook macOS Bundle
        run: bash tool/widgetbook/build_macos_bundle.sh

      - name: Move Continuous Release Tag
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          git config user.name github-actions[bot]
          git config user.email 41898282+github-actions[bot]@users.noreply.github.com
          git tag -f widgetbook-macos-latest "$GITHUB_SHA"
          git push origin refs/tags/widgetbook-macos-latest --force

      - name: Ensure Release Exists
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          if gh release view widgetbook-macos-latest >/dev/null 2>&1; then
            gh release edit widgetbook-macos-latest \
              --title "Widgetbook macOS Latest" \
              --notes "Latest unsigned Widgetbook macOS app bundle from main at $GITHUB_SHA." \
              --prerelease
          else
            gh release create widgetbook-macos-latest \
              --target "$GITHUB_SHA" \
              --title "Widgetbook macOS Latest" \
              --notes "Latest unsigned Widgetbook macOS app bundle from main at $GITHUB_SHA." \
              --prerelease
          fi

      - name: Upload Widgetbook Zip to Release
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: gh release upload widgetbook-macos-latest "build/widgetbook_macos_export/Lotti_Widgetbook.app.zip" --clobber
WORKFLOW

# --- 4. Update design system README ---
cat >> lib/features/design_system/README.md <<'README'

## Widgetbook Export

Build the standalone Widgetbook macOS bundle and zip it for review:

```sh
make widgetbook_macos_build
```

Upload the existing zip to the rolling GitHub release without rebuilding:

```sh
make widgetbook_macos_upload
```

Build and then upload the latest zip to the rolling GitHub release:

```sh
make widgetbook_macos_publish
```

This writes:

- `build/widgetbook_macos_export/Lotti_Widgetbook.app`
- `build/widgetbook_macos_export/Lotti_Widgetbook.app.zip`

The app is built from `lib/widgetbook.dart` and then copied into a separate
macOS app bundle for sharing.

After unzipping, open the app bundle in Finder:

```sh
open "build/widgetbook_macos_export/Lotti_Widgetbook.app"
```

Because the app is unsigned, macOS may warn on first launch, especially if it
was downloaded from GitHub Releases. In that case, use Finder's right-click
`Open`, or remove quarantine locally:

```sh
xattr -dr com.apple.quarantine "Lotti_Widgetbook.app"
```

The publish command updates the `widgetbook-macos-latest` tag and uploads the
zip to the matching prerelease via the GitHub CLI. It expects `gh` to be
installed and authenticated locally.
README

echo "Patch applied successfully."
