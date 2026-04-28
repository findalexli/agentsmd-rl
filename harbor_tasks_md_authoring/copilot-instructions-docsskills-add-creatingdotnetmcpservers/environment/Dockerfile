FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/copilot-instructions && \
    cd /workspace/copilot-instructions && \
    git remote add origin https://github.com/SebastienDegodez/copilot-instructions.git && \
    git fetch --depth=1 origin 0cc79b9d98fb2467234a9980f27367f767eb5e8e && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/copilot-instructions
