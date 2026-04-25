#!/bin/bash
set -e

cd /workspace/electric/packages/elixir-client

# Fetch the full diff from the merged PR and apply it
curl -sL "https://github.com/electric-sql/electric/pull/4028.patch" | git apply -