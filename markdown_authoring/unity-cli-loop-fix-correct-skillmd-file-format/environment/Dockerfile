FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/unity-cli-loop && \
    cd /workspace/unity-cli-loop && \
    git remote add origin https://github.com/hatayama/unity-cli-loop.git && \
    git fetch --depth=1 origin 0c9c2d5a02793e9b4ee7b6f7e4043a6045fbd8c3 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/unity-cli-loop
