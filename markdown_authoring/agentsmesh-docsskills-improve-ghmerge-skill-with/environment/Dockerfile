FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/agentsmesh && \
    cd /workspace/agentsmesh && \
    git remote add origin https://github.com/AgentsMesh/AgentsMesh.git && \
    git fetch --depth=1 origin 892889c87a275bb0defe0ef9f9e40d46355b0cc9 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/agentsmesh
