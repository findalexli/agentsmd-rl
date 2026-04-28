FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/openwebui-extensions && \
    cd /workspace/openwebui-extensions && \
    git remote add origin https://github.com/Fu-Jie/openwebui-extensions.git && \
    git fetch --depth=1 origin 278a6ce12c8a16dfa42a62020cbcc6d7f789aa99 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/openwebui-extensions
