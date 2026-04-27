FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/pro-workflow && \
    cd /workspace/pro-workflow && \
    git remote add origin https://github.com/rohitg00/pro-workflow.git && \
    git fetch --depth=1 origin 1de15541cfed2b50c9d0d4f0eb575faa1c749759 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/pro-workflow
