FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/linea-attestation-registry && \
    cd /workspace/linea-attestation-registry && \
    git remote add origin https://github.com/Consensys/linea-attestation-registry.git && \
    git fetch --depth=1 origin 1ff4788165a4cbba7723b1c6169b0a9719556e74 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/linea-attestation-registry
