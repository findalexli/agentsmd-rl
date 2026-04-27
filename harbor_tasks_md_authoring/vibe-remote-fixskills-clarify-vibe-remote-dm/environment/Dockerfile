FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/vibe-remote && \
    cd /workspace/vibe-remote && \
    git remote add origin https://github.com/cyhhao/vibe-remote.git && \
    git fetch --depth=1 origin 8e72772ef59ba5646ff23bc3df3ccd08fc4811a5 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/vibe-remote
