FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/ios-simulator-skill && \
    cd /workspace/ios-simulator-skill && \
    git remote add origin https://github.com/conorluddy/ios-simulator-skill.git && \
    git fetch --depth=1 origin 44300e849b412d3049669828add41c72b24d3a1c && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/ios-simulator-skill
