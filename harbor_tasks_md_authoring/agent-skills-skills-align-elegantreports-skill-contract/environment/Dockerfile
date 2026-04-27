FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/agent-skills && \
    cd /workspace/agent-skills && \
    git remote add origin https://github.com/jdrhyne/agent-skills.git && \
    git fetch --depth=1 origin 2d7a3c9e2657399c9f60ecddb9c188730284cb7b && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/agent-skills
