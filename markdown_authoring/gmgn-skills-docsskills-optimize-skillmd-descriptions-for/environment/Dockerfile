FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/gmgn-skills && \
    cd /workspace/gmgn-skills && \
    git remote add origin https://github.com/GMGNAI/gmgn-skills.git && \
    git fetch --depth=1 origin eeb4a77cf76575431dcd6805de1ef2a02a515aab && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/gmgn-skills
