FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/background-agents && \
    cd /workspace/background-agents && \
    git remote add origin https://github.com/ColeMurray/background-agents.git && \
    git fetch --depth=1 origin 12eb8befbdf20b202a8bcf912e9dacca09753e6b && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/background-agents
