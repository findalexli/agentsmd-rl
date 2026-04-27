FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    pytest==8.3.4 \
    pytest-json-ctrf==0.4.1

WORKDIR /workspace

RUN git clone --filter=blob:none https://github.com/anomalyco/opencode.git /workspace/opencode \
    && cd /workspace/opencode \
    && git checkout 58c65874ba6aff2f16f5310dacddc3a89eb7b2cd

RUN mkdir -p /logs/verifier

WORKDIR /workspace/opencode
