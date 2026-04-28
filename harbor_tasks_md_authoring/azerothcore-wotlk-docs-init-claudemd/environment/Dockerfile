FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/azerothcore-wotlk && \
    cd /workspace/azerothcore-wotlk && \
    git remote add origin https://github.com/azerothcore/azerothcore-wotlk.git && \
    git fetch --depth=1 origin 4f5a63f1d174fd868eacbe558f8d71cd440a5c3d && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/azerothcore-wotlk
