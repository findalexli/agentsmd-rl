FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Clone repo at the base commit (before the fix)
RUN git init /repo && \
    cd /repo && \
    git remote add origin https://github.com/sgl-project/sglang.git && \
    git fetch --depth=1 origin 33cca495ae75e745be62b5b009f4c87fb40dd044 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /repo

# Install test-runner dependencies (lightweight).
# The behavioral fail_to_pass tests use AST extraction + mocked modules
# and do not need sglang/transformers/torch importable at runtime.
RUN pip install --no-cache-dir pytest pytest-json-ctrf pyyaml tomli

# Configure git user for any patch operations
RUN git config user.email "test@test.com" && git config user.name "Test"
