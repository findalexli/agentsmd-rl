FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/agent-governance-toolkit && \
    cd /workspace/agent-governance-toolkit && \
    git remote add origin https://github.com/microsoft/agent-governance-toolkit.git && \
    git fetch --depth=1 origin d0527a971b6783d0a8cb0d400f04163d1430aeec && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/agent-governance-toolkit
