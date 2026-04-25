#!/bin/bash
set -e
cd /workspace/prisma_repo

# Fetch the actual PR patch from GitHub
curl -sL "https://github.com/prisma/prisma/pull/29182.patch" -o /tmp/prisma.patch

# Apply the patch
git apply --verbose /tmp/prisma.patch

rm /tmp/prisma.patch
