FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/kubelb && \
    cd /workspace/kubelb && \
    git remote add origin https://github.com/kubermatic/kubelb.git && \
    git fetch --depth=1 origin 7a6302fd950417f6a1ca6c57fc03660e0400eef4 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/kubelb
