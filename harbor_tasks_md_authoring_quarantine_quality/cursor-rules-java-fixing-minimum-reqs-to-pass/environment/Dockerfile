FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/cursor-rules-java && \
    cd /workspace/cursor-rules-java && \
    git remote add origin https://github.com/jabrena/cursor-rules-java.git && \
    git fetch --depth=1 origin 630bedeb90ea615fde88934a596eda74e052e9f1 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/cursor-rules-java
