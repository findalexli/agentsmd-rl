FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/hyperframes && \
    cd /workspace/hyperframes && \
    git remote add origin https://github.com/heygen-com/hyperframes.git && \
    git fetch --depth=1 origin 2b836cc2242e8725b8159cdb8786e522c3fd0e97 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/hyperframes
