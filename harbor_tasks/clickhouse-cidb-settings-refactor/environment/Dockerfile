FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install black for formatting checks
RUN pip install black

# Clone the ClickHouse repository at the base commit
ARG BASE_COMMIT=bc855b917b3f456bfd6198c5bc29a1bc5672aabf
RUN git clone --filter=blob:none https://github.com/ClickHouse/ClickHouse.git /workspace/ClickHouse \
    && cd /workspace/ClickHouse \
    && git checkout ${BASE_COMMIT}

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace
