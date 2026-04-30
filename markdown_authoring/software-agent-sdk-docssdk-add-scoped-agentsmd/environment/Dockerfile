FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/software-agent-sdk && \
    cd /workspace/software-agent-sdk && \
    git remote add origin https://github.com/OpenHands/software-agent-sdk.git && \
    git fetch --depth=1 origin dcebff6e3008b79318af7ce30f2806b3505b4e78 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/software-agent-sdk
