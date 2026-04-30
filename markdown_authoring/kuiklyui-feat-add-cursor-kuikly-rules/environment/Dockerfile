FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/kuiklyui && \
    cd /workspace/kuiklyui && \
    git remote add origin https://github.com/Tencent-TDS/KuiklyUI.git && \
    git fetch --depth=1 origin 4ffd08768ec68c9b2cac46bca781592dd6a7bbeb && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/kuiklyui
