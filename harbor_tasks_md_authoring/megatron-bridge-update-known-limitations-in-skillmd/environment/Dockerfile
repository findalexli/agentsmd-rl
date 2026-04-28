FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/megatron-bridge && \
    cd /workspace/megatron-bridge && \
    git remote add origin https://github.com/NVIDIA-NeMo/Megatron-Bridge.git && \
    git fetch --depth=1 origin 6489424841df0b1e36cf69ac8927e5d2f857bb0e && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/megatron-bridge
