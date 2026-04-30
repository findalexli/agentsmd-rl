FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/go-feature-flag && \
    cd /workspace/go-feature-flag && \
    git remote add origin https://github.com/thomaspoignant/go-feature-flag.git && \
    git fetch --depth=1 origin 3eb862867f927d6f097e1da2ca0773d3fa0266c8 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/go-feature-flag
