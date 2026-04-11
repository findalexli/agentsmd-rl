#!/usr/bin/env bash
set -euo pipefail

cd /workspace/rabbitmq-server

# Idempotent: skip if already applied
if grep -q 'list_certificates' deps/rabbitmq_trust_store/src/rabbit_trust_store.erl 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix /solution/fix.patch

echo "Patch applied successfully."
