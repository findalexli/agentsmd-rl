FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/hyperlane-warp-ui-template && \
    cd /workspace/hyperlane-warp-ui-template && \
    git remote add origin https://github.com/hyperlane-xyz/hyperlane-warp-ui-template.git && \
    git fetch --depth=1 origin b9211242cda62e63b40ecd30de52d5bacddf9cae && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/hyperlane-warp-ui-template
