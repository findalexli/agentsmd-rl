FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /workspace /logs/verifier
WORKDIR /workspace

# Clone electron repo at base commit (shallow clone for efficiency)
ARG BASE_COMMIT=0d74dce4ee212c60fb2d16e8c757ae270306b234
RUN git clone --filter=blob:none --depth=50 https://github.com/electron/electron.git electron && \
    cd electron && \
    git checkout ${BASE_COMMIT}

# Pre-install pytest for the test harness
RUN pip install --no-cache-dir pytest

WORKDIR /workspace/electron
