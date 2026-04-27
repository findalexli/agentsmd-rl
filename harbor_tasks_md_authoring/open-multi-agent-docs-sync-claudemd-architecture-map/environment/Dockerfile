FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/open-multi-agent && \
    cd /workspace/open-multi-agent && \
    git remote add origin https://github.com/JackChen-me/open-multi-agent.git && \
    git fetch --depth=1 origin ff987cfc37a77769cca15ca5ef773a9bc7d02e2f && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/open-multi-agent
