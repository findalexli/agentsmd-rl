FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/hermes-agent && \
    cd /workspace/hermes-agent && \
    git remote add origin https://github.com/NousResearch/hermes-agent.git && \
    git fetch --depth=1 origin f93d4624bf570239662989f79937b9a7a330c53b && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/hermes-agent
