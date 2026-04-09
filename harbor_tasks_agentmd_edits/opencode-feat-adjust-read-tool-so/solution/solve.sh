#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opencode

# Idempotent: skip if already applied
if grep -q 'logging.Warn.*Error accumulating message' internal/llm/provider/anthropic.go 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use sed to replace the error handling pattern
# Old: eventChan <- ProviderEvent{Type: EventError, Error: err}
# New: logging.Warn("Error accumulating message", "error", err)
sed -i 's/eventChan <- ProviderEvent{Type: EventError, Error: err}/logging.Warn("Error accumulating message", "error", err)/' internal/llm/provider/anthropic.go

echo "Patch applied successfully."
