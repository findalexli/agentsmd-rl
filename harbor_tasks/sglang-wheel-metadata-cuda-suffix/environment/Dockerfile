FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux zip unzip && \
    rm -rf /var/lib/apt/lists/*

# Install wheel package (needed by rename_wheels.sh)
RUN pip install --no-cache-dir wheel

# Clone repo at base commit (BEFORE the fix)
ARG BASE_COMMIT=80389fec004394db409e9d04aef263465a3b235c
RUN git clone --filter=blob:none https://github.com/sgl-project/sglang.git /repo && \
    cd /repo && \
    git checkout ${BASE_COMMIT}

# Configure git user for any patches
RUN cd /repo && \
    git config user.email "test@test.com" && \
    git config user.name "Test"

RUN mkdir -p /logs/verifier

WORKDIR /repo