FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/curator && \
    cd /workspace/curator && \
    git remote add origin https://github.com/NVIDIA-NeMo/Curator.git && \
    git fetch --depth=1 origin ac74c94d6c2d079d0fdb154708cb0c164815e3b0 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/curator
