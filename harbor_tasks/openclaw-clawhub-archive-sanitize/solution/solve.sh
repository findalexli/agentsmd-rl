#!/usr/bin/env bash
set -euo pipefail
cd /workspace/openclaw

TARGET="src/infra/clawhub.ts"

# Add import for safeDirName
sed -i '/^import.*from "\.\/runtime-guard\.js";/a\import { safeDirName } from "./install-safe-path.js";' "$TARGET"

# Fix package archive path
sed -i 's/const archivePath = path\.join(tmpDir, `${params\.name}\.zip`);/const archivePath = path.join(tmpDir, `${safeDirName(params.name)}.zip`);/' "$TARGET"

# Fix skill archive path
sed -i 's/const archivePath = path\.join(tmpDir, `${params\.slug}\.zip`);/const archivePath = path.join(tmpDir, `${safeDirName(params.slug)}.zip`);/' "$TARGET"
