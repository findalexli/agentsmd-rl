FROM ubuntu:24.04

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ca-certificates \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN git clone --filter=blob:none \
    https://github.com/cloudflare/workers-sdk.git \
    /workspace/workers-sdk && \
    cd /workspace/workers-sdk && \
    git checkout ad6799bd48742f0a589ed5867b269055015e4293

RUN pip install --break-system-packages pytest==8.3.4

RUN mkdir -p /logs/verifier

WORKDIR /workspace
