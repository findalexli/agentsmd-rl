FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/thoth && \
    cd /workspace/thoth && \
    git remote add origin https://github.com/plengauer/Thoth.git && \
    git fetch --depth=1 origin f92d35fb428dcd7f779b7c7cf70e8d3291a3fe01 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/thoth
