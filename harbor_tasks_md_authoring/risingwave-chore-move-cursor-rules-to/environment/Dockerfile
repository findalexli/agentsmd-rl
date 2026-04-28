FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/risingwave && \
    cd /workspace/risingwave && \
    git remote add origin https://github.com/risingwavelabs/risingwave.git && \
    git fetch --depth=1 origin fc8819f6bd3695ecf3d51bca7b2ab15f084cbbae && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/risingwave
