FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/mc-agent-toolkit && \
    cd /workspace/mc-agent-toolkit && \
    git remote add origin https://github.com/monte-carlo-data/mc-agent-toolkit.git && \
    git fetch --depth=1 origin 11b047bdf959097933f7753b75ded6554a8ac30d && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/mc-agent-toolkit
