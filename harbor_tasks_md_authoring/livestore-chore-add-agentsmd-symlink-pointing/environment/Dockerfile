FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/livestore && \
    cd /workspace/livestore && \
    git remote add origin https://github.com/livestorejs/livestore.git && \
    git fetch --depth=1 origin 71110c35ac9e96b42d09938dddc8e9cc0af9f8fb && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/livestore
