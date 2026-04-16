FROM python:3.12-slim

# Install minimal dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Clone ClickHouse at base commit
ARG BASE_COMMIT=5316ae89ac9d925b36281526d98a8adff23d0d3e
RUN git clone --filter=blob:none --depth=100 https://github.com/ClickHouse/ClickHouse.git /workspace/ClickHouse \
    && cd /workspace/ClickHouse \
    && git fetch origin ${BASE_COMMIT} \
    && git checkout ${BASE_COMMIT}

WORKDIR /workspace/ClickHouse

# Install pytest
RUN pip install pytest -q

# Create logs directory for verifier
RUN mkdir -p /logs/verifier
