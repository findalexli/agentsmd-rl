FROM oven/bun:1.3.10-debian

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        python3 \
        python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir --break-system-packages \
        pytest==8.3.4 \
        pytest-json-ctrf==0.3.5

ARG REPO_URL=https://github.com/anomalyco/opencode.git
ARG BASE_COMMIT=dcb17c6a678918ce0786640729fcc8cd8adb1746

WORKDIR /workspace

RUN git clone --filter=blob:none "$REPO_URL" opencode \
    && cd opencode \
    && git checkout "$BASE_COMMIT" \
    && git config user.email "task@local" \
    && git config user.name "task"

WORKDIR /workspace/opencode

RUN mkdir -p /logs/verifier
