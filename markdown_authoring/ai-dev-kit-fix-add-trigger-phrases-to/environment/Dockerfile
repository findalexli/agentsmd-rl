FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/ai-dev-kit && \
    cd /workspace/ai-dev-kit && \
    git remote add origin https://github.com/databricks-solutions/ai-dev-kit.git && \
    git fetch --depth=1 origin 75abeed99b401189c53e9463737bc7cc0946e8da && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/ai-dev-kit
