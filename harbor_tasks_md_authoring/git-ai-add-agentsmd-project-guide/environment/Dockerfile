FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/git-ai && \
    cd /workspace/git-ai && \
    git remote add origin https://github.com/git-ai-project/git-ai.git && \
    git fetch --depth=1 origin 1b7740c28795c43c573e92c7b23f1f4c394de99b && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/git-ai
