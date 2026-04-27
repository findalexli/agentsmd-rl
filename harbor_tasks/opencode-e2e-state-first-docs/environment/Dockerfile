FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    pytest==8.3.4 \
    pyyaml==6.0.2

WORKDIR /workspace

RUN git clone --filter=blob:none --no-checkout \
    https://github.com/anomalyco/opencode.git opencode \
    && cd opencode \
    && git config advice.detachedHead false \
    && git checkout dcb17c6a678918ce0786640729fcc8cd8adb1746

RUN mkdir -p /logs/verifier
