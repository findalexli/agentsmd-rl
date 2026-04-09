FROM python:3.12-slim

WORKDIR /workspace

# Install git, patch and dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    patch \
    && rm -rf /var/lib/apt/lists/*

# Clone sglang at base commit (pre-fix)
ARG BASE_COMMIT=cd2d45e22085045a5e9cd14666be7b0e96af601d
RUN git clone --filter=blob:none https://github.com/sgl-project/sglang.git && \
    cd sglang && \
    git checkout ${BASE_COMMIT}

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/sglang
