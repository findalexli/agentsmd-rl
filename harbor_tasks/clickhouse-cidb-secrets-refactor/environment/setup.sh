#!/bin/bash
set -e

cd /workspace

# Clone the ClickHouse repository at base commit
echo "Cloning ClickHouse repository..."
git clone --filter=blob:none https://github.com/ClickHouse/ClickHouse.git

cd ClickHouse
git checkout bc855b917b3f456bfd6198c5bc29a1bc5672aabf

echo "Repository cloned and checked out to base commit"
