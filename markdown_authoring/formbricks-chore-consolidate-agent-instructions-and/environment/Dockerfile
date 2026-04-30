FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/formbricks && \
    cd /workspace/formbricks && \
    git remote add origin https://github.com/formbricks/formbricks.git && \
    git fetch --depth=1 origin 46be3e7d707782bda942b9e6c13f37ba17925e69 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/formbricks
