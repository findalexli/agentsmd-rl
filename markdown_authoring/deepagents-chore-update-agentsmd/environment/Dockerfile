FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/deepagents && \
    cd /workspace/deepagents && \
    git remote add origin https://github.com/langchain-ai/deepagents.git && \
    git fetch --depth=1 origin 5633c825832a0e8bd645681db23e97af31879b65 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/deepagents
