#!/usr/bin/env bash
set -euo pipefail
cd /workspace/openclaw

TARGET="src/infra/clawhub.ts"

# Add import for safeDirName (alphabetically before runtime-guard.js)
sed -i '/^import.*from "\.\/install-safe-path\.js";$/d' "$TARGET" 2>/dev/null || true
sed -i '/^import path from "node:path";/a\import { safeDirName } from "./install-safe-path.js";' "$TARGET"

# Fix package archive path
sed -i 's/const archivePath = path\.join(tmpDir, `${params\.name}\.zip`);/const archivePath = path.join(tmpDir, `${safeDirName(params.name)}.zip`);/' "$TARGET"

# Fix skill archive path
sed -i 's/const archivePath = path\.join(tmpDir, `${params\.slug}\.zip`);/const archivePath = path.join(tmpDir, `${safeDirName(params.slug)}.zip`);/' "$TARGET"

# Run formatter to fix any formatting issues
npx oxfmt --write "$TARGET" 2>/dev/null || true
