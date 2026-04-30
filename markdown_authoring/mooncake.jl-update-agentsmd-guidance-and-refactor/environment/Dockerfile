FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/mooncake.jl && \
    cd /workspace/mooncake.jl && \
    git remote add origin https://github.com/chalk-lab/Mooncake.jl.git && \
    git fetch --depth=1 origin d78eb8936b00ea0821ece33b6c5427eaa3b1b5f4 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/mooncake.jl
