#!/bin/bash
set -e
cd /workspace/vitess
patch -p1 < /solution/gold.patch
echo "Patch applied successfully"