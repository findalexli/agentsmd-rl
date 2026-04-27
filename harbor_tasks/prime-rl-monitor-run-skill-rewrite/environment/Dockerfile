FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && \
    apt-get install -y --no-install-recommends git ca-certificates && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace

RUN git clone --filter=blob:none https://github.com/PrimeIntellect-ai/prime-rl.git && \
    cd prime-rl && \
    git checkout 27645f39ab6f1550b2990ba4c5bb47be7f35402e

RUN mkdir -p /logs/verifier
