#!/bin/bash
set -e

cd /workspace/payload

# Fetch the PR diff and apply it
curl -sL "https://github.com/payloadcms/payload/pull/16092.diff" | git apply -
