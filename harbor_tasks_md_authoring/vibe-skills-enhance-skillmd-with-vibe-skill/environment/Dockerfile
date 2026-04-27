FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/vibe-skills && \
    cd /workspace/vibe-skills && \
    git remote add origin https://github.com/foryourhealth111-pixel/Vibe-Skills.git && \
    git fetch --depth=1 origin 75fd1db13a48db2c008fcf8fc0f897314650233f && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/vibe-skills
