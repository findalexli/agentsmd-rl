FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/auto-round && \
    cd /workspace/auto-round && \
    git remote add origin https://github.com/intel/auto-round.git && \
    git fetch --depth=1 origin d5a0097dac5b33ca31bee061d0a19b6018dcb8b0 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/auto-round
