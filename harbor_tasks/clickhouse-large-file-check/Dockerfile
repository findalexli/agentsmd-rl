FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    bash \
    gawk \
    grep \
    coreutils \
    && rm -rf /var/lib/apt/lists/*

# Clone the ClickHouse repository at the base commit (parent of merge)
ARG BASE_COMMIT=cf5fb461472203d56bb0c169a61d194dd97fc2f2
RUN git clone --filter=blob:none --depth=50 https://github.com/ClickHouse/ClickHouse.git /workspace/ClickHouse \
    && cd /workspace/ClickHouse \
    && git checkout ${BASE_COMMIT}

WORKDIR /workspace/ClickHouse

# Ensure log directory exists for test harness
RUN mkdir -p /logs/verifier

# Copy the test file
COPY tests/test_outputs.py /workspace/task/tests/
