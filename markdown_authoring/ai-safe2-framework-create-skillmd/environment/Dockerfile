FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/ai-safe2-framework && \
    cd /workspace/ai-safe2-framework && \
    git remote add origin https://github.com/CyberStrategyInstitute/ai-safe2-framework.git && \
    git fetch --depth=1 origin a3595cba45a9851cb8c604820a7eee6eccb5b27a && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/ai-safe2-framework
